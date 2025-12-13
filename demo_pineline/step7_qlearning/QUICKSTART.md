# 🎯 QUICK START: Chạy So Sánh Lại

## 📁 Files Đã Thay Đổi

```
demo_pineline/step7_qlearning/
├── config/
│   └── reward_config.json                    [✅ UPDATED]
│       - Version: 2.0 → 2.1
│       - Added: mastery_learning_rates
│       - Added: lo_mastery_improvement reward
│
├── core/rl/
│   └── reward_calculator.py                  [✅ UPDATED]
│       - Line ~375: Use config learning rates
│       - Line ~422: Add mastery improvement reward
│
└── [NEW FILES]
    ├── ANALYSIS_SCORE_REWARD_GAP.md         [📖 PHÂN TÍCH]
    └── SOLUTION_SUMMARY.md                  [📖 HƯ­ỚNG DẪN]
```

---

## 🚀 Bước 1: Verify Config

```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning

# Kiểm tra reward_config.json
grep -A 5 "mastery_learning_rates" config/reward_config.json
grep -A 5 "lo_mastery_improvement" config/reward_config.json
```

**Expected Output**:
```json
{
  "mastery_learning_rates": {
    "weak": 0.4,
    "medium": 0.3,
    "strong": 0.2
  },
  "lo_mastery_improvement": {
    "weak": 15.0,
    "medium": 10.0,
    "strong": 7.0
  }
}
```

---

## 🚀 Bước 2: Test Nhẹ (5 Phút)

```bash
# Test reward calculator với config mới
python3 << 'EOF'
from core.rl.reward_calculator import RewardCalculatorV2

# Init calculator - sẽ load config mới
calc = RewardCalculatorV2(
    cluster_profiles_path='data/cluster_profiles.json',
    reward_config_path='config/reward_config.json'
)

print("✓ Config loaded successfully!")
print(f"  Mastery learning rates: {calc.config.get('mastery_learning_rates')}")
print(f"  LO mastery improvement rewards: {calc.config.get('reward_components', {}).get('lo_mastery_improvement')}")

# Test LO mastery calculation
test_outcome = {
    'score': 0.8,
    'success': True,
    'completed': True,
    'time': 20
}

total_reward, lo_deltas = calc.calculate_lo_mastery_delta(
    student_id=1,
    activity_id=1,
    outcome=test_outcome,
    cluster_id=0  # 0=weak, 1=medium, 2=strong
)

print(f"\n✓ Test reward calculation:")
print(f"  Student ID: 1, Activity: 1, Cluster: 0 (weak)")
print(f"  Outcome score: 0.8")
print(f"  Total LO reward: {total_reward:.2f}")
print(f"  LO deltas: {lo_deltas}")

EOF
```

---

## 🚀 Bước 3: Chạy Full Pipeline (20-30 Phút)

### 3A. Chạy Q-Learning Pipeline

```bash
python3 scripts/demos/full_pipeline_qlearning.py \
  --n-episodes 100 \
  --n-students 100 \
  --output data/simulated/qlearning_policy_results_v2_fixed.json \
  --verbose
```

**Nên thấy**:
```
✓ RewardCalculatorV2 initialized:
  - Clusters: 5 (weak/medium/strong)
  - Mastery learning rates from config
  - LO mastery improvement rewards enabled
...
```

### 3B. Chạy Param Policy Pipeline

```bash
python3 scripts/demos/full_pipeline_param.py \
  --n-students 100 \
  --output data/simulated/param_policy_results_v2_fixed.json \
  --verbose
```

### 3C. So Sánh Kết Quả

```bash
python3 scripts/utils/compare_policies.py \
  --q-learning data/simulated/qlearning_policy_results_v2_fixed.json \
  --param-policy data/simulated/param_policy_results_v2_fixed.json \
  --output data/simulated/comparison_report_v2_fixed.json \
  --verbose
```

### 3D. Vẽ Biểu Đồ

```bash
python3 scripts/utils/plot_policy_comparison.py \
  --comparison-report data/simulated/comparison_report_v2_fixed.json \
  --output plots/policy_comparison_v2_fixed
```

---

## 📊 Bước 4: So Sánh Kết Quả

### Trước Fix:
```json
{
  "q_learning": {
    "avg_reward": 224.05,
    "avg_midterm_score": 9.41,
    "avg_midterm_score_10": 4.71
  },
  "param_policy": {
    "avg_reward": 52.11,
    "avg_midterm_score": 8.90,
    "avg_midterm_score_10": 4.45
  }
}
```

### Sau Fix (Expected):
```json
{
  "q_learning": {
    "avg_reward": 350-400,          // ↑ Tăng vì mastery improvement reward cao
    "avg_midterm_score": 13-14,     // ↑ Tăng 30-50%
    "avg_midterm_score_10": 6.5-7.0 // ↑ Tăng 40-50% (GOAL: 5/10 trở lên) ✓
  },
  "param_policy": {
    "avg_reward": 50-60,
    "avg_midterm_score": 9-10,
    "avg_midterm_score_10": 4.5-5.0
  }
}
```

---

## 🔍 Bước 5: Deep Dive Analysis

### Kiểm tra Mastery Improvement:

```bash
python3 << 'EOF'
import json

# Load comparison report
with open('data/simulated/comparison_report_v2_fixed.json', 'r') as f:
    report = json.load(f)

ql_stats = report['q_learning_stats']
pp_stats = report['param_policy_stats']

print("=" * 60)
print("MASTERY ANALYSIS")
print("=" * 60)
print(f"Q-Learning Mastery: {ql_stats['avg_lo_mastery']:.4f}")
print(f"Param Policy Mastery: {pp_stats['avg_lo_mastery']:.4f}")
print(f"Difference: {ql_stats['avg_lo_mastery'] - pp_stats['avg_lo_mastery']:.4f}")

print(f"\n{'Cluster':<10} {'Q-Learn Mastery':<20} {'Q-Learn Score':<20}")
print("-" * 50)
for cluster in ['weak', 'medium', 'strong']:
    ql_cluster = ql_stats['cluster_stats'].get(cluster, {})
    if ql_cluster:
        print(f"{cluster:<10} {ql_cluster.get('avg_lo_mastery', 0):<20.4f} {ql_cluster.get('avg_midterm_10', 0):<20.2f}")

EOF
```

---

## ⚠️ Troubleshooting

### Problem: "mastery_learning_rates not found"
```python
# ✓ Config file should have default values
learning_rates = self.config.get('mastery_learning_rates', {
    'weak': 0.4, 'medium': 0.3, 'strong': 0.2
})
```

### Problem: "lo_mastery_improvement not found"
```python
# ✓ Config file should have default values
mastery_improvement = self.config.get('reward_components', {}).get('lo_mastery_improvement', {
    'weak': 15.0, 'medium': 10.0, 'strong': 7.0
})
```

### Problem: Score vẫn thấp < 5/10
- [ ] Kiểm tra mastery_learning_rates được dùng?
- [ ] Kiểm tra lo_mastery_improvement reward được áp dụng?
- [ ] Có thể cần tăng n_episodes (từ 100 → 200-300)
- [ ] Có thể cần tăng n_steps/student (từ 150 → 250-300)

---

## 📝 Checklist Thực Hiện

- [ ] Verify config files (Step 1)
- [ ] Test config loading (Step 2, 5 phút)
- [ ] Run Q-Learning (Step 3A, 10 phút)
- [ ] Run Param Policy (Step 3B, 5 phút)
- [ ] Compare policies (Step 3C, 5 phút)
- [ ] Plot graphs (Step 3D, 5 phút)
- [ ] Analyze results (Step 4)
- [ ] Deep dive (Step 5, optional)

---

## 🎯 Expected Timeline

| Phase | Duration | Expected Result |
|-------|----------|-----------------|
| Config Verify | 2 min | ✓ Config loaded |
| Test | 5 min | ✓ Reward calc works |
| Q-Learning | 10 min | ✓ Training complete |
| Param Policy | 5 min | ✓ Policy complete |
| Analysis | 5 min | ✓ Report generated |
| **Total** | **~30 min** | **Score: 6.5-7.0/10** ✓ |

---

## 📞 Hỗ Trợ

- Xem: `ANALYSIS_SCORE_REWARD_GAP.md` (phân tích chi tiết)
- Xem: `SOLUTION_SUMMARY.md` (hướng dẫn giải pháp)
- Check files: 
  - `config/reward_config.json` (learning rates + reward)
  - `core/rl/reward_calculator.py` (implementation)
