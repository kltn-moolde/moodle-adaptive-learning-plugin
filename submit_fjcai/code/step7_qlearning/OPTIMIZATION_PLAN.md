# 📈 OPTIMIZATION PLAN - Phase 2

## 🎯 Objective
Tăng score từ 4.76/10 → 7.0+/10 (mục tiêu: 5/10 → 8/10)

## ⚠️ Problem Analysis

Kết quả hiện tại:
- Score: 4.76/10 (tăng từ 4.71 nhưng chỉ +1%)
- Weak LOs: 93-100% học sinh vẫn weak
- Reward tăng nhẹ (224 → 226)

**Root cause**: 
1. Q-table trained với config cũ (500 episodes)
2. Cần retrain với config mới (learning rates + mastery reward)
3. Simulation steps quá ít (30 steps)

## 🔧 Optimization Strategy

### Strategy 1: Retrain Q-table (HIGH IMPACT)

**Current**: 500 episodes, reward config cũ
**Target**: 1000+ episodes, reward config mới (v2.1)

```bash
python3 training/train_qlearning.py \
  --episodes 1000 \
  --total-students 100 \
  --cluster-mix 0.2 0.6 0.2 \
  --course-id 5 \
  --steps 50 \
  --output models/qtable_v2_1000.pkl \
  --plot
```

**Expected result**:
- Q-table học với reward strategy mới
- Mastery reward 7-15x lớn hơn → agent cố gắng cải thiện mastery
- Score dự kiến: 5.5-6.5/10

---

### Strategy 2: Increase Simulation Steps (MEDIUM IMPACT)

**Current**: 30 steps/học sinh
**Target**: 50-100 steps/học sinh

```bash
python3 scripts/utils/simulate_learning_path.py \
  --qtable models/qtable_v2_1000.pkl \
  --output data/simulated/qlearning_policy_v2.json \
  --num_students 100 \
  --cluster-mix 0.2 0.6 0.2 \
  --steps 100 \
  --plot
```

**Expected result**:
- Mỗi học sinh có 100 bước để improve LO
- Score dự kiến: 6.0-7.0/10

---

### Strategy 3: Aggressive Learning Rates (EXPERIMENTAL)

**Current**: weak=0.4, medium=0.3, strong=0.2
**Target**: weak=0.5, medium=0.4, strong=0.3

```json
{
  "mastery_learning_rates": {
    "weak": 0.5,
    "medium": 0.4,
    "strong": 0.3
  }
}
```

**Effect**: Mastery update 25% nhanh hơn
**Risk**: Có thể overshoot mastery (> 1.0)

---

## 📊 Testing Plan

| Phase | Action | Time | Expected Score |
|-------|--------|------|-----------------|
| 0 (Current) | None | - | 4.76/10 |
| 1 | Retrain Q (1000 ep) | 30 min | 5.5-6.5/10 |
| 2 | +100 steps | 10 min | 6.0-7.0/10 |
| 3 | +Aggressive rates | 40 min | 7.0-7.5/10 |
| Final | All combined | 90 min | 7.5+/10 |

---

## 🚀 Recommended Next Steps

### Immediate (10 min):
1. Retrain Q-table với 1000 episodes
2. Chạy simulation với steps=100
3. Check score

### If score < 6/10:
1. Thử aggressive learning rates
2. Coi xét other reward components

### If score >= 6/10:
1. Optimize fine-tuning
2. Analysis mastery distribution
3. Compare policies (Q-learning vs Param)

---

## 🔍 Monitoring Metrics

Track các metrics này:

1. **Q-table convergence**: avg Q-value change per episode
2. **Reward distribution**: mean, std, min, max
3. **Mastery improvement**: Δmastery per student
4. **Score distribution**: per cluster, per LO
5. **Weak LO rate**: % học sinh weak trên mỗi LO

---

## 📝 Notes

- Reward config v2.1 có lo_mastery_improvement (7-15)
- Learning rates tăng 30-50%
- Cần retrain Q-table để cách mạng tận dụng
- 1000 episodes + 100 steps dự kiến đạt 7.0+/10

---

**Created**: 2025-12-07
**Status**: Ready to Execute
