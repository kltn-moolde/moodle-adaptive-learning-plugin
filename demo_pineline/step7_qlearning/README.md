# Q-Learning for Moodle Adaptive Learning v2.0

Clean, modular implementation of Q-learning system for personalized learning recommendations.

## 📁 Structure

```
step7_qlearning/
├── core_v2/                    # Core modules
│   ├── __init__.py
│   ├── state_builder.py        # State representation (12 dims)
│   ├── action_space.py         # Learning actions from course
│   ├── reward_calculator.py    # Cluster-based rewards
│   ├── qlearning_agent.py      # Tabular Q-learning
│   └── simulator.py            # Learning behavior simulator
│
├── data/                       # Data files
│   ├── course_structure.json   # Moodle course structure
│   ├── cluster_profiles.json   # Student cluster profiles
│   └── simulated/              # Simulated training data
│
├── models/                     # Trained models
│   └── qlearning_model.pkl     # Q-table + params
│
├── simulate_learning_data.py   # Generate simulated data
├── train_qlearning_v2.py       # Train Q-learning model
└── update_daily_qtable.py      # Daily update pipeline
```

## 🚀 Quick Start

### 1. Generate Simulated Data

```bash
python simulate_learning_data.py --n-students 100 --n-actions 30
```

**Output:** `data/simulated/latest_simulation.json`

### 2. Train Q-Learning Model

```bash
python train_qlearning_v2.py --data data/simulated/latest_simulation.json \
                              --output models/qlearning_model.pkl \
                              --epochs 10
```

**Output:** `models/qlearning_model.pkl`

### 3. Daily Update (Production)

```bash
# Run daily at 12AM
python update_daily_qtable.py --model models/qlearning_model.pkl
```

**Output:** 
- Updated Q-table
- Daily recommendations in `data/recommendations/`

## 🔧 Core Components

### 1. State Builder (`state_builder.py`)

**12-dimensional state representation:**
- Performance (3): knowledge, engagement, struggle
- Activity patterns (5): submission, review, resources, assessment, collaboration
- Completion metrics (4): progress, completion rate, diversity, consistency

**Usage:**
```python
from core_v2 import MoodleStateBuilder

builder = MoodleStateBuilder()
state = builder.build_state(student_features)  # Returns np.array (12,)
```

### 2. Action Space (`action_space.py`)

**Extract learning actions from course:**
- Quiz, Assignment (assessment)
- Resource, Page, URL (content)
- Video, H5P (interactive)
- Forum (collaboration)

**Usage:**
```python
from core_v2 import ActionSpace

action_space = ActionSpace('data/course_structure.json')
actions = action_space.get_actions()  # List[LearningAction]
```

### 3. Reward Calculator (`reward_calculator.py`)

**Cluster-specific reward strategies:**
- **Weak (0-1):** High reward for completing assessments
- **Medium (2-3):** Balanced rewards
- **Strong (4-5):** Reward for speed and high scores

**Usage:**
```python
from core_v2 import RewardCalculator

calculator = RewardCalculator('data/cluster_profiles.json')
reward = calculator.calculate_reward(cluster_id, action, outcome, state)
```

### 4. Q-Learning Agent (`qlearning_agent.py`)

**Tabular Q-learning:**
- ε-greedy exploration
- Q-value updates: `Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]`
- State hashing for continuous states

**Usage:**
```python
from core_v2 import QLearningAgent

agent = QLearningAgent(n_actions=50, learning_rate=0.1)
action = agent.select_action(state, available_actions)
agent.update(state, action, reward, next_state)
```

### 5. Simulator (`simulator.py`)

**Simulate learning behaviors:**
- Cluster-based behavior patterns
- Realistic outcomes (score, time, attempts)
- State transitions

**Usage:**
```python
from core_v2 import LearningSimulator

simulator = LearningSimulator(state_builder, action_space, reward_calc)
interactions = simulator.simulate_batch(n_students=100, n_actions_per_student=30)
```

## 📊 Data Flow

```
1. SIMULATION (offline)
   course_structure.json + cluster_profiles.json
   → simulator.simulate_batch()
   → simulated_data.json

2. TRAINING (offline)
   simulated_data.json
   → agent.train_episode()
   → qlearning_model.pkl

3. DAILY UPDATE (online)
   Moodle logs (12AM)
   → extract_features()
   → state_builder.build_state()
   → agent.update()
   → updated qlearning_model.pkl
   → recommendations.json
```

## 🔄 Daily Pipeline

**Automated workflow (runs at 12AM):**

1. **Fetch logs:** Get yesterday's Moodle logs
2. **Extract features:** Run feature extraction pipeline
3. **Build states:** Convert features → state vectors
4. **Identify interactions:** Map logs → (s, a, r, s')
5. **Update Q-table:** Apply Q-learning updates
6. **Save model:** Backup old + save new
7. **Generate recommendations:** Top-k actions per student

## 📈 Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `learning_rate` (α) | 0.1 | Q-value update rate |
| `discount_factor` (γ) | 0.95 | Future reward importance |
| `epsilon` (ε) | 0.1 | Exploration rate |
| `state_decimals` | 1 | State rounding (reduce sparsity) |

## 🧪 Testing

```bash
# Test individual components
cd core_v2
python state_builder.py
python action_space.py
python reward_calculator.py
python qlearning_agent.py
python simulator.py
```

## 📦 Dependencies

```
numpy
pickle (built-in)
json (built-in)
dataclasses (built-in)
```

## 🎯 Extension Points

### Add new reward strategies:
Edit `reward_calculator.py` → `_cluster_bonus()`

### Add new state features:
Edit `state_builder.py` → `build_state()`

### Add new action types:
Edit `action_space.py` → `MODULE_TYPE_MAPPING`

### Change exploration strategy:
Edit `qlearning_agent.py` → `select_action()`

## 📝 Notes

- **State hashing:** Rounds to 1 decimal to reduce Q-table sparsity
- **Cluster distribution:** Can customize in `simulator.simulate_batch()`
- **Action filtering:** Simulator filters by difficulty/purpose based on cluster
- **Reward clipping:** Rewards clipped to [-2, 5] range

## 🐛 Troubleshooting

**Q-table too large?**
- Increase `state_decimals` in QLearningAgent
- Reduce state dimensions

**Low rewards?**
- Check reward calculation in `reward_calculator.py`
- Adjust cluster bonuses

**Poor recommendations?**
- Increase training data (more students/actions)
- Tune hyperparameters (α, γ, ε)
- Check cluster assignment accuracy

## 📚 References

- Q-Learning: Watkins & Dayan (1992)
- Moodle State Builder: Original implementation
- Cluster Profiles: From KMeans + GMM pipeline
