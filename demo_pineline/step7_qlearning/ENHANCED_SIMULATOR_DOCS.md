# Enhanced StudentSimulatorV2 - Documentation

## 🎯 Tổng quan

StudentSimulatorV2 đã được nâng cấp với các tính năng mới để mô phỏng chính xác hành vi học sinh thực tế:

### ✨ Tính năng mới

1. **Học tham số từ dữ liệu thật** (`cluster_profiles.json`)
   - Success rate, progress speed, stuck probability
   - Action exploration entropy
   - Preferred actions distribution
   - Score ranges dựa trên mean grades

2. **Learning Curve Model** (Logistic/Exponential)
   - Progress không còn tuyến tính
   - Tăng nhanh ban đầu, sau đó plateau
   - Cluster-specific curve parameters
   - Realistic learning patterns

3. **Attempt-Level Quiz Tracking**
   - Lưu lịch sử từng attempt per module
   - Score improvement qua các attempts
   - Learning curve áp dụng cho scores
   - Realistic retry patterns

4. **Policy-Based Action Selection**
   - Sử dụng Q-table để select actions
   - ε-greedy policy với learned Q-values
   - Fallback to heuristic nếu không có Q-table
   - Match với RL objectives

5. **Reward Tuning**
   - Realistic reward calculation
   - Match với training objectives
   - Cluster-specific reward patterns

## 📊 Cách sử dụng

### 1. Basic Usage - Learned Parameters

```python
from core.simulator_v2 import StudentSimulatorV2

# Initialize với learned parameters
simulator = StudentSimulatorV2(
    course_structure_path='data/course_structure.json',
    cluster_profiles_path='data/cluster_profiles.json',
    use_learned_params=True,  # Học từ data thật
    learning_curve_type='logistic',  # hoặc 'exponential'
    seed=42
)

# Simulate single student
trajectory = simulator.simulate_trajectory(
    student_id=1001,
    cluster_id=0,  # Weak learner
    max_steps=50,
    verbose=True
)
```

### 2. With Q-table Policy

```python
# Initialize với Q-table for policy-based selection
simulator = StudentSimulatorV2(
    qtable_path='models/test_agent_stats.pkl',  # Path to Q-table
    use_learned_params=True,
    learning_curve_type='logistic'
)

# Actions sẽ được chọn dựa trên Q-values
trajectory = simulator.simulate_trajectory(
    student_id=1002,
    cluster_id=2,  # Strong learner
    max_steps=50
)
```

### 3. Batch Simulation

```python
# Simulate nhiều students
trajectories = simulator.simulate_batch(
    n_students_per_cluster=10,
    max_steps_per_student=100,
    verbose=True
)

# Save for training
simulator.save_trajectories(trajectories, 'data/training_data.json')
```

## 🔬 Learning Curve Details

### Logistic Curve
```
Progress(n) = L / (1 + exp(-k * (n - x0)))
```
- **L**: Maximum value (1.0)
- **k**: Steepness (0.3 weak, 0.5 medium, 0.8 strong)
- **x0**: Midpoint attempts (8 weak, 5 medium, 3 strong)

### Exponential Curve
```
Progress(n) = a * (1 - exp(-b * n))
```
- **a**: Asymptote (0.85 weak, 0.92 medium, 0.97 strong)
- **b**: Growth rate (0.12 weak, 0.15 medium, 0.20 strong)

## 📈 Learned Parameters từ cluster_profiles.json

### Extraction Process

1. **Success Rate**: `mean_module_grade / 100`
2. **Stuck Probability**: `quiz_reviewed / quiz_submitted * 0.5`
3. **Progress Speed**: `0.5 / (1 + total_events / 100)`
4. **Action Exploration**: Shannon entropy của event distribution
5. **Preferred Actions**: Top 3 actions theo frequency

### Cluster Classification

```python
if success_rate > 0.75 and stuck_prob < 0.15:
    level = 'strong'
elif success_rate > 0.6 and stuck_prob < 0.25:
    level = 'medium'
else:
    level = 'weak'
```

## 🎮 Attempt-Level Tracking

Mỗi module có tracking dict:
```python
module_attempts = {
    'attempts': 5,              # Số lần attempt
    'scores': [0.4, 0.5, 0.6, 0.7, 0.75],  # Lịch sử scores
    'last_score': 0.75          # Score gần nhất
}
```

Score improvement:
```python
new_score = previous_score + (max_score - previous_score) * mastery * random(0.3, 0.7)
```

## 🤖 Policy-Based Action Selection

### Với Q-table:
```python
if random() < epsilon:
    # Explore: random action
    action = random_action()
else:
    # Exploit: best Q-value
    action = argmax(Q[state, :])
```

### Không có Q-table:
- Fallback to heuristic ε-greedy
- Progress-based action selection
- Cluster-specific preferences

## 📊 Output Format

Mỗi transition có:
```python
{
    'state': (cluster, module_idx, progress, score, action, stuck),
    'action': module_id,
    'action_type': 'do_quiz',
    'reward': 2.5,
    'next_state': (...),
    'module_progress': 0.75,
    'avg_score': 0.68,
    'is_stuck': False,
    'is_terminal': False,
    'completed': True
}
```

## 🧪 Testing

Chạy comprehensive test:
```bash
python3 test_enhanced_simulator.py
```

Tests bao gồm:
1. ✓ Learned parameters extraction
2. ✓ Learning curve computation
3. ✓ Attempt-level tracking
4. ✓ Full trajectory simulation
5. ✓ Policy-based selection (if Q-table available)
6. ✓ Batch simulation
7. ✓ Comparison with/without features

## 📝 Example Results

### Learned Parameters (Cluster 0 - Weak)
```
Success rate:        0.411
Stuck probability:   0.150
Progress speed:      0.400
Completion rate:     0.726
Action exploration:  0.332
Score range:         (0.261, 0.561)
Preferred actions:   do_assignment, watch_video, do_quiz
```

### Learning Curve Progress
```
WEAK Learner:
  Attempt | Expected Progress | Increment
  --------|-------------------|----------
     1    |      0.007        |   0.007
     2    |      0.017        |   0.010
     3    |      0.041        |   0.024
     5    |      0.182        |   0.088
     8    |      0.500        |   0.144  (midpoint!)
    10    |      0.689        |   0.094
    15    |      0.952        |   0.061  (plateau)
```

### Trajectory Sample
```
Step  1: watch_video     → Progress: 0.015, Score: 0.500, Reward: +0.00
Step  2: read_resource   → Progress: 0.035, Score: 0.500, Reward: +0.00
Step  3: do_quiz         → Progress: 0.122, Score: 0.421, Reward: +0.00
Step  4: do_quiz         → Progress: 0.258, Score: 0.485, Reward: +3.26  (improved!)
Step  5: do_assignment   → Progress: 0.437, Score: 0.531, Reward: +3.18
```

## 🎯 Use Cases

### 1. Training Data Generation
```python
# Generate realistic training data
simulator = StudentSimulatorV2(use_learned_params=True)
trajectories = simulator.simulate_batch(n_students_per_cluster=50)
simulator.save_trajectories(trajectories, 'data/training_data.json')
```

### 2. Q-table Validation
```python
# Test Q-table với realistic student behavior
simulator = StudentSimulatorV2(
    qtable_path='models/qtable.pkl',
    use_learned_params=True
)
trajectory = simulator.simulate_trajectory(student_id=1, cluster_id=0)
# Kiểm tra xem Q-table có recommend đúng actions không
```

### 3. A/B Testing
```python
# So sánh different reward functions
sim_v1 = StudentSimulatorV2(reward_version='v1')
sim_v2 = StudentSimulatorV2(reward_version='v2')

traj_v1 = sim_v1.simulate_trajectory(1, 0)
traj_v2 = sim_v2.simulate_trajectory(1, 0)

# Compare outcomes
```

## 🔧 Configuration

### Cluster Parameters
- Tự động học từ `cluster_profiles.json`
- Hoặc dùng manual parameters (`use_learned_params=False`)

### Learning Curve
- `logistic`: Smooth S-curve (recommended)
- `exponential`: Fast start, gradual slowdown

### Q-table Policy
- Optional: provide `qtable_path`
- Automatically falls back to heuristic

## ⚠️ Notes

1. **Q-table format**: Phải là pickle file với dict `{state: {action: q_value}}`
2. **Seed**: Set seed để reproducible results
3. **Performance**: Learned params slower nhưng chính xác hơn
4. **Validation**: Luôn kiểm tra output trajectories match với real data

## 📚 References

- Learning Curve: Ebbinghaus (1885), Anderson (2000)
- Q-Learning: Watkins & Dayan (1992)
- Student Modeling: Corbett & Anderson (1995)

## 🚀 Next Steps

1. ✅ Integrate với Q-learning training pipeline
2. ✅ Generate large-scale training data
3. ✅ Validate against real student logs
4. ⏳ Deploy for real-time recommendations
5. ⏳ A/B testing in production

---

**Version**: 2.0 (Enhanced)  
**Last Updated**: 2024-11-06  
**Author**: AI-Assisted Development
