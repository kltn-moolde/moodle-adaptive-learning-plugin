# 🎓 Enhanced StudentSimulatorV2 - Quick Start

## ✨ Tính năng mới (So với bản cũ)

| Feature | Bản cũ | Bản mới (Enhanced) |
|---------|--------|-------------------|
| **Parameters** | Hardcoded by hand | ✅ Học từ `cluster_profiles.json` |
| **Progress Model** | Linear | ✅ Learning Curve (Logistic/Exponential) |
| **Quiz Tracking** | Average score only | ✅ Attempt-level với improvement history |
| **Action Selection** | Simple ε-greedy | ✅ Policy-based từ Q-table |
| **Reward** | Basic | ✅ Tuned cho RL objectives |

## 🚀 Quick Start

### 1. Cài đặt cơ bản

```python
from core.simulator_v2 import StudentSimulatorV2

# Initialize với tất cả features
simulator = StudentSimulatorV2(
    use_learned_params=True,      # Học từ real data
    learning_curve_type='logistic', # hoặc 'exponential'
    qtable_path='models/qtable.pkl',  # Optional: for policy
    seed=42
)
```

### 2. Simulate 1 học sinh

```python
trajectory = simulator.simulate_trajectory(
    student_id=1001,
    cluster_id=0,  # 0=weak, 1/2/4=strong, 5=medium
    max_steps=50,
    verbose=True
)

print(f"Generated {len(trajectory)} transitions")
print(f"Total reward: {sum(t['reward'] for t in trajectory):.2f}")
```

### 3. Batch simulation

```python
trajectories = simulator.simulate_batch(
    n_students_per_cluster=10,
    max_steps_per_student=100
)

# Save for training
simulator.save_trajectories(trajectories, 'data/training_data.json')
```

## 📊 Learned Parameters

Simulator tự động học các parameters này từ `cluster_profiles.json`:

### Cluster 0 (Weak Learner)
```
✓ Success rate:       0.411  (41% thành công lần đầu)
✓ Stuck probability:  0.150  (15% chance bị stuck)
✓ Progress speed:     0.400  (tiến bộ chậm)
✓ Score range:        (0.26, 0.56)
✓ Preferred actions:  do_assignment, watch_video, do_quiz
```

### Cluster 2 (Strong Learner)
```
✓ Success rate:       0.854  (85% thành công)
✓ Stuck probability:  0.050  (5% bị stuck)
✓ Progress speed:     0.400  (tiến bộ nhanh)
✓ Score range:        (0.70, 1.00)
✓ Preferred actions:  do_assignment, do_quiz, watch_video
```

## 📈 Learning Curve Examples

### Weak Learner Progress
```
Attempt  1 → Progress: 0.007  (slow start)
Attempt  3 → Progress: 0.041
Attempt  5 → Progress: 0.182  (picking up)
Attempt  8 → Progress: 0.500  (midpoint!)
Attempt 10 → Progress: 0.689
Attempt 15 → Progress: 0.952  (plateau)
```

### Strong Learner Progress
```
Attempt  1 → Progress: 0.310  (fast start!)
Attempt  3 → Progress: 0.822  (midpoint at attempt 3)
Attempt  5 → Progress: 0.975  (quickly reaches mastery)
Attempt  7 → Progress: 0.997
```

## 🎯 Use Cases

### 1. Generate Training Data cho Q-Learning

```python
simulator = StudentSimulatorV2(use_learned_params=True)

# Generate 100 students
trajectories = simulator.simulate_batch(
    n_students_per_cluster=20,
    max_steps_per_student=100
)

# Total: 20 * 5 clusters = 100 students
# Save for training
simulator.save_trajectories(trajectories, 'data/qtable_training_data.json')
```

### 2. Test Q-table với Realistic Behavior

```python
simulator = StudentSimulatorV2(
    qtable_path='models/trained_qtable.pkl',
    use_learned_params=True
)

# Simulate và xem Q-table có recommend đúng không
for cluster_id in [0, 1, 2]:
    traj = simulator.simulate_trajectory(
        student_id=1000 + cluster_id,
        cluster_id=cluster_id,
        max_steps=30
    )
    print(f"Cluster {cluster_id}: Avg reward = {np.mean([t['reward'] for t in traj]):.2f}")
```

### 3. Compare Learning Curves

```python
# Logistic curve
sim_logistic = StudentSimulatorV2(learning_curve_type='logistic')
traj_log = sim_logistic.simulate_trajectory(1, 0, max_steps=20)

# Exponential curve  
sim_exp = StudentSimulatorV2(learning_curve_type='exponential')
traj_exp = sim_exp.simulate_trajectory(2, 0, max_steps=20)

# Compare progress patterns
```

## 🧪 Testing

Chạy comprehensive test suite:

```bash
python3 test_enhanced_simulator.py
```

Output:
```
✅ TEST 1: Learned Parameters ✓
✅ TEST 2: Learning Curve Model ✓
✅ TEST 3: Attempt-Level Quiz Tracking ✓
✅ TEST 4: Complete Trajectory ✓
✅ TEST 5: Policy-Based Selection ✓
✅ TEST 6: Batch Simulation ✓
✅ TEST 7: Comparison Tests ✓

🎉 ALL TESTS PASSED!
```

## 📦 Output Format

Mỗi transition trong trajectory:

```python
{
    'state': (0, 0, 0.25, 0.50, 2, False),  # (cluster, module_idx, progress, score, action, stuck)
    'action': 46,                            # Module ID
    'action_type': 'do_quiz',               # Human-readable action
    'reward': 2.5,                          # Reward value
    'next_state': (0, 0, 0.35, 0.52, 2, False),
    'module_progress': 0.35,                # Current module progress [0-1]
    'avg_score': 0.52,                      # Average score [0-1]
    'is_stuck': False,                      # Stuck state flag
    'is_terminal': False,                   # Episode end flag
    'completed': False,                     # Module completed flag
    'timestamp': datetime(2024, 1, 1, 9, 15)
}
```

## 🔧 Advanced Configuration

### Custom Learning Curve

```python
# Modify curve parameters for specific cluster
simulator.learning_curve_params['weak']['k'] = 0.4  # Steeper learning

# Re-run simulation
trajectory = simulator.simulate_trajectory(1, 0, max_steps=20)
```

### Custom Reward Function

```python
# Simulator uses RewardCalculatorV2
# Modify trong core/reward_calculator_v2.py nếu cần
```

### Disable Specific Features

```python
# Không dùng learned params
simulator = StudentSimulatorV2(use_learned_params=False)

# Không dùng learning curve (linear progress)
# → Chỉ cần không set learning_curve_type
```

## 📊 Comparison với Old Simulator

| Metric | Old Simulator | Enhanced Simulator |
|--------|--------------|-------------------|
| Progress pattern | Linear | Realistic curve (slow → fast → plateau) |
| Score improvement | Random | Learning-based improvement |
| Action selection | Fixed ε-greedy | Policy-based hoặc learned ε |
| Parameters | Manual tuning | Auto-learned từ data |
| Validation | Difficult | Match với real logs |

## 🎯 Integration với Training Pipeline

```python
# 1. Generate training data
simulator = StudentSimulatorV2(use_learned_params=True, seed=42)
trajectories = simulator.simulate_batch(n_students_per_cluster=50)
simulator.save_trajectories(trajectories, 'data/training_trajectories.json')

# 2. Train Q-learning agent
from core.qlearning_agent_v2 import QLearningAgentV2
agent = QLearningAgentV2()
agent.train_from_trajectories('data/training_trajectories.json')
agent.save_qtable('models/trained_qtable.pkl')

# 3. Test với simulator using trained Q-table
test_simulator = StudentSimulatorV2(
    qtable_path='models/trained_qtable.pkl',
    use_learned_params=True
)
test_trajectories = test_simulator.simulate_batch(n_students_per_cluster=10)

# 4. Evaluate
evaluate_trajectories(test_trajectories)
```

## 📚 Documentation

- **Chi tiết đầy đủ**: [`ENHANCED_SIMULATOR_DOCS.md`](ENHANCED_SIMULATOR_DOCS.md)
- **API Reference**: Trong code comments
- **Examples**: `test_enhanced_simulator.py`

## ❓ FAQ

### Q: Tại sao learning curve quan trọng?
**A**: Learning curve mô phỏng cách người học thật tiến bộ - chậm lúc đầu, nhanh ở giữa, plateau cuối. Linear progress không realistic.

### Q: Attempt-level tracking khác gì với average score?
**A**: Thay vì chỉ lưu average, ta lưu từng attempt → thấy được improvement pattern → realistic hơn.

### Q: Khi nào cần Q-table?
**A**: 
- **Training**: Không cần Q-table, dùng heuristic
- **Testing/Production**: Cần Q-table để test policy learned

### Q: Learned params có chính xác không?
**A**: Tùy quality của `cluster_profiles.json`. Nếu data tốt → params accurate. Test bằng cách compare với real logs.

### Q: Có thể tune parameters không?
**A**: Có! Set `use_learned_params=False` và modify trong `_initialize_cluster_params()`.

## 🚨 Common Issues

### Issue: Q-table không load được
```
⚠ Q-table không tìm thấy tại: models/qtable.pkl
```
**Solution**: Train Q-table trước hoặc bỏ `qtable_path` parameter.

### Issue: Learned params không hợp lý
```
Cluster 0: success=0.99  # Too high for weak learner
```
**Solution**: Kiểm tra `cluster_profiles.json` có đúng format không.

### Issue: Progress quá nhanh/chậm
```
Progress sau 5 attempts: 0.99  # Too fast
```
**Solution**: Adjust learning curve parameters trong `_initialize_learning_curves()`.

## 🎉 Success Metrics

Sau khi implement, kiểm tra:

- ✅ Learned params reasonable cho mỗi cluster
- ✅ Learning curve smooth và realistic
- ✅ Scores improve qua attempts
- ✅ Action distribution match với cluster level
- ✅ Trajectories có thể train Q-learning thành công

## 🔗 Next Steps

1. Generate large training dataset (1000+ students)
2. Train Q-learning với dataset này
3. Evaluate trained Q-table với test simulator
4. Deploy recommendations to production
5. A/B test với real students

---

**Version**: 2.0 Enhanced  
**Status**: ✅ Production Ready  
**Last Updated**: 2024-11-06
