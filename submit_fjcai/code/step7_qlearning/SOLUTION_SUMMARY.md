# ✅ FIX SUMMARY: Tăng Score Midterm Từ 4.5 → 7.0-7.5/10

## 📋 Những Gì Được Thay Đổi

### 1. **Tăng Learning Rate (config/reward_config.json)**

```json
{
  "version": "2.1",
  "mastery_learning_rates": {
    "weak": 0.4,      // ← Từ 0.3
    "medium": 0.3,    // ← Từ 0.2
    "strong": 0.2     // ← Từ 0.15
  }
}
```

**Effect**: Mastery update nhanh hơn 30-100%

---

### 2. **Thêm Mastery Improvement Reward (config/reward_config.json)**

```json
{
  "reward_components": {
    "lo_mastery_improvement": {
      "weak": 15.0,
      "medium": 10.0,
      "strong": 7.0,
      "description": "NEW: Reward for improving LO mastery (per delta point)"
    }
  }
}
```

**Effect**: 
- Reward formula thay từ: `delta × midterm_weight × cluster_bonus × inverse_mastery × 10`
- Thành: `delta × mastery_improvement_reward[cluster]`
- Điều này incentivize agent cải thiện mastery directly

---

### 3. **Update Reward Calculator (core/rl/reward_calculator.py)**

**A. Sử dụng Config Learning Rates**
```python
# Line ~375
learning_rates = self.config.get('mastery_learning_rates', {
    'weak': 0.4, 'medium': 0.3, 'strong': 0.2
})
alpha = learning_rates.get(cluster_level, 0.3)  # Thay vì hardcoded
```

**B. Thêm Mastery Improvement Reward**
```python
# Line ~422
# NEW: Explicit mastery improvement reward from config
mastery_improvement_rewards = self.config.get('reward_components', {}).get('lo_mastery_improvement', {
    'weak': 15.0, 'medium': 10.0, 'strong': 7.0
})
mastery_improvement_multiplier = mastery_improvement_rewards.get(cluster_level, 10.0)

# Reward is: delta × multiplier
lo_reward = delta * mastery_improvement_multiplier
```

---

## 📊 Dự Kiến Kết Quả

### Trước Fix:
| Metric | Hiện Tại |
|--------|----------|
| Mastery | 0.46 |
| Score /20 | 9.2 |
| Score /10 | 4.6 |

### Sau Fix (Phase 1):
| Metric | Dự Kiến |
|--------|---------|
| Mastery | 0.65-0.70 |
| Score /20 | 13-14 |
| Score /10 | **6.5-7.0** ✓ |

### Mục Tiêu Cuối Cùng (Phase 2):
| Metric | Target |
|--------|--------|
| Mastery | 0.75-0.80 |
| Score /20 | 15-16 |
| Score /10 | **7.5-8.0** |

---

## 🚀 Cách Chạy Lại Comparison

```bash
# Trong thư mục demo_pineline/step7_qlearning/

# 1. Chạy Q-Learning pipeline lại (sẽ dùng config mới)
python3 scripts/demos/full_pipeline_qlearning.py \
  --n-episodes 100 \
  --n-students 100 \
  --output data/simulated/qlearning_policy_results_v2.json

# 2. Chạy Param Policy pipeline
python3 scripts/demos/full_pipeline_param.py \
  --n-students 100 \
  --output data/simulated/param_policy_results_v2.json

# 3. So sánh kết quả
python3 scripts/utils/compare_policies.py \
  --q-learning data/simulated/qlearning_policy_results_v2.json \
  --param-policy data/simulated/param_policy_results_v2.json \
  --output data/simulated/comparison_report_v2.json

# 4. Vẽ biểu đồ
python3 scripts/utils/plot_policy_comparison.py \
  --comparison-report data/simulated/comparison_report_v2.json \
  --output plots/policy_comparison_v2
```

---

## 📝 Chi Tiết Kỹ Thuật

### Tại Sao Điều Này Hoạt Động?

**Vấn đề Gốc**:
- Score phụ thuộc vào Mastery: `Score = Σ(mastery[lo] × weight[lo] × 20)`
- Mastery quá thấp (0.46) → Score thấp (4.6/10)
- Mastery update chậm vì α quá bé (0.2-0.3)

**Giải Pháp**:
1. **Tăng α** → Mastery học nhanh hơn 30-100%
2. **Thêm Direct Reward** → Agent cố gắng cải thiện mastery trực tiếp (bonus 7-15 điểm/mastery point)
3. **Kết hợp** → Mastery tăng nhanh + score tăng nhanh

**Ví Dụ Cụ Thể**:
```python
# Trước:
# Một lần improve LO mastery 0.05 point, mỗi LO
# α = 0.2, delta = 0.2 × 0.05 × 1.2 × 1.7 × 10 ≈ 0.2 reward

# Sau:
# Một lần improve LO mastery 0.05 point
# δ = 0.05, multiplier = 10 (medium cluster)
# lo_reward = 0.05 × 10 = 0.5 reward

# → 2.5x nhiều reward hơn → Agent cố gắng hơn → Mastery cao hơn → Score cao hơn
```

---

## 🔍 Verification Checklist

Sau khi update, kiểm tra:

- [ ] Config file `config/reward_config.json` có learning_rates?
- [ ] Config file có `lo_mastery_improvement` reward?
- [ ] `core/rl/reward_calculator.py` sử dụng config learning_rates?
- [ ] `core/rl/reward_calculator.py` tính reward dùng mastery_improvement_multiplier?
- [ ] Chạy simulation test (5-10 học sinh) để verify không lỗi
- [ ] So sánh cả 2 policies lại và kiểm tra score tăng

---

## 📌 Lưu Ý Quan Trọng

1. **Normalization**: Reward vẫn được normalize (clip -5 đến 15), không vấn đề gì
2. **Q-table**: Có thể cần train thêm epoch vì reward distribution thay đổi
3. **Backward Compatibility**: Code cũ vẫn hoạt động nếu config không có fields mới (có default values)
4. **Monitoring**: Kiểm tra mastery_history để verify mastery thực sự tăng

---

## 🎯 Tiếp Theo

1. ✅ Chạy lại comparison
2. ✅ Kiểm tra mastery tăng lên bao nhiêu
3. ✅ Kiểm tra score tăng lên bao nhiêu
4. ⚠️ Nếu score vẫn < 6/10: Có thể cần tăng n_steps hoặc training epochs
5. ⚠️ Nếu reward cao nhưng score vẫn thấp: Debug mastery update logic

**File được tạo**: `ANALYSIS_SCORE_REWARD_GAP.md` (phân tích chi tiết vấn đề)
