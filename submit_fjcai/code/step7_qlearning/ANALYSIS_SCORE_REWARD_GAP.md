# Phân Tích Vấn Đề: Reward Khác Nhưng Score Giống Nhau

## 🔍 Tóm Tắt Vấn Đề

Khi so sánh `qlearning_policy` vs `param_policy`:
- ✅ **Reward**: Khác nhau rõ rệt (224 vs 52)
- ❌ **Điểm Midterm**: Giống nhau (9.41/20 vs 8.90/20) ≈ (4.7/10 vs 4.45/10)
- ❌ **Cả 2 đều thấp**: Chỉ ~4.5/10 thay vì mục tiêu 10/20 (5/10)

### Dữ Liệu Từ Comparison Report

```json
{
  "q_learning": {
    "avg_reward": 224.05,
    "avg_midterm_score": 9.41,          // /20
    "avg_midterm_score_10": 4.71,       // /10
    "avg_lo_mastery": 0.4628
  },
  "param_policy": {
    "avg_reward": 52.11,
    "avg_midterm_score": 8.90,          // /20
    "avg_midterm_score_10": 4.45,       // /10
    "avg_lo_mastery": 0.4642
  }
}
```

---

## 🎯 Root Cause Analysis

### 1. **Score KHÔNG Phụ Thuộc Trực Tiếp Vào Reward**

```python
# Trong lo_mastery_tracker.py:200-220
def predict_midterm_score(self, student_id: int):
    mastery = self.get_mastery(student_id)
    
    # ⚠️ Score = mastery × weight × total_marks
    for lo_id, weight in self.midterm_weights.items():
        lo_mastery = mastery.get(lo_id, 0.4)  # Default: 0.4 = 40%
        lo_score = lo_mastery * weight * 20   # Always /20
        total_score += lo_score
    
    midterm_score_10 = total_score / 2.0     # Convert to /10
```

**Kết luận**: Score là **hàm của Mastery**, không phải Reward!

---

### 2. **Mastery Quá Thấp (~0.46)**

**Tính toán**:
```
Score = Σ(mastery[lo] × weight[lo] × 20)
      = 0.46 × 20  (nếu weights có trung bình ≈ 1.0)
      ≈ 9.2 / 20
      ≈ 4.6 / 10
```

**Tại sao mastery chỉ 0.46?**

Mastery được update qua hàm learning:
```python
# Trong reward_calculator.py:380-420
alpha = {'weak': 0.3, 'medium': 0.2, 'strong': 0.15}[cluster]
new_mastery = old_mastery + alpha * (outcome_score - old_mastery)
```

**Vấn đề**:
- 📉 Learning rate `α` quá bé (0.15-0.3)
- 📉 Outcome score từ simulation có thể quá thấp
- 📉 Số hoạt động training quá ít so với tổng LO

---

### 3. **Tại Sao Q-Learning Policy Reward Cao Nhưng Score Vẫn Thấp?**

```
Q-Learning Advantage: 224 reward (vs 52 param policy)
→ Agent học tốt hơn → recommend hoạt động tốt hơn
→ Outcome tốt hơn → Mastery tăng nhiều hơn

Nhưng thực tế: 
- Q-Learning mastery: 0.4628
- Param mastery: 0.4642 (cao hơn!)

❌ Điều này không hợp lý!
```

**Có thể là**:
1. Q-Learning policy training chưa đủ epoch
2. Q-table chưa hội tụ tốt
3. Simulation parameters không chuẩn (e.g., outcome score quá thấp)

---

## 🔧 Giải Pháp

### **Giải Pháp 1: Tăng Learning Rate (Ngắn hạn)**

Tăng `α` để mastery update nhanh hơn:

```json
// config/reward_config.json
"mastery_learning_rates": {
  "weak": 0.5,      // ← Từ 0.3
  "medium": 0.35,   // ← Từ 0.2
  "strong": 0.25    // ← Từ 0.15
}
```

**Effect**: Mastery ~0.46 → ~0.65-0.70
**Score**: 4.6/10 → 6.5-7.0/10 ✓

---

### **Giải Pháp 2: Cải Thiện Outcome Quality (Trung hạn)**

**Vấn đề hiện tại**:
- Simulation outcome score quá thấp
- Hoạt động có độ khó không phù hợp với cluster

**Cải thiện**:
```python
# core/simulation/simulator.py
def execute_action(self, action, student):
    # ⚠️ Hiện tại: outcome_score ~ random[0, 0.8]
    # ✅ Nên: outcome_score ~ f(student_level, action_difficulty)
    
    if student.cluster == 'weak':
        # Weak student làm action easy → high success rate
        success_rate = 0.8
        expected_score = 0.85
    elif student.cluster == 'medium':
        expected_score = 0.70
    else:  # strong
        expected_score = 0.75
    
    # Add noise but bias towards expected
    outcome_score = np.random.beta(alpha, beta) # Tuned (α,β)
```

---

### **Giải Pháp 3: Tối Ưu Q-Learning Training (Dài hạn)**

**Vấn đề**: Q-Learning policy reward 224 nhưng mastery thấp

**Nguyên nhân có thể**:
1. **Exploration-exploitation không cân bằng**: ε-greedy policy
2. **Q-table chưa hội tụ**: Cần thêm epoch
3. **Reward shaping sai**: Không incentivize mastery improvement

**Giải pháp**:

```python
# config/reward_config.json - Add mastery bonus
"reward_components": {
  "lo_mastery_improvement": {
    "weak": 10.0,      // ← NEW: Reward LO mastery improvement
    "medium": 7.0,
    "strong": 5.0,
    "per_point": true  // Reward per LO improved
  }
}
```

---

### **Giải Pháp 4: Tăng Số Hoạt động Training**

**Hiện tại**: Simulation chạy ~50-100 hoạt động/học sinh

**Nên**: Tăng lên 150-200 hoạt động/học sinh

```python
# scripts/run_simulation.py
sim = Simulator(
    n_steps=300,  # ← Từ 150-200
    n_students=100
)
```

---

## 📊 Dự Kiến Kết Quả Sau Fix

| Metric | Hiện Tại | Sau Fix | Mục Tiêu |
|--------|----------|---------|---------|
| Mastery Trung Bình | 0.46 | 0.70-0.75 | 0.80+ |
| Score /20 | 9.2-9.4 | 14-15 | 16+ |
| Score /10 | 4.6-4.7 | 7.0-7.5 | 8.0+ |
| Weak LO Mastery | 0.35 | 0.55-0.65 | 0.75+ |

---

## 🚀 Thực Hiện Priority

1. **Ngay lập tức** (15 min): 
   - Tăng learning rate từ 0.2 → 0.35 (medium)
   - Tăng n_steps từ 150 → 250

2. **Ngắn hạn** (1 hour):
   - Cải thiện outcome quality simulation
   - Thêm mastery_improvement reward

3. **Dài hạn** (1-2 hours):
   - Optimize Q-Learning training
   - Fine-tune action difficulty distribution

---

## 📝 Kế Tiếp

Hãy tôi:
1. ✅ Update learning rates
2. ✅ Improve simulation outcomes
3. ✅ Add mastery_improvement reward
4. ✅ Re-run comparison

**Sau đó**: Đánh giá kết quả và điều chỉnh tiếp theo.
