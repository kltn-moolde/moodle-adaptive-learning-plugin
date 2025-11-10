# IMPLEMENTATION GUIDE - Q-Learning System V2
## Hướng dẫn triển khai hệ thống Q-Learning với thiết kế mới

**Date:** November 4, 2025  
**Version:** 2.0  
**Status:** ✅ Core Components Ready

---

## 📋 TÓM TẮT THIẾT KẾ

### State Design (6 chiều)
```python
State = [cluster_id, current_module, module_progress, avg_score, recent_action, is_stuck]
```

| Dimension | Values | Description |
|-----------|--------|-------------|
| cluster_id | [0-5] | 6 clusters (loại bỏ cluster 3 - giáo viên) |
| current_module | [0-N] | Module index (N≈36 modules) |
| module_progress | [0.25, 0.5, 0.75, 1.0] | Quartile bins |
| avg_score | [0.25, 0.5, 0.75, 1.0] | Quartile bins |
| recent_action | [0-5] | 6 action types |
| is_stuck | [0, 1] | Binary stuck indicator |

**State Space Size:** ~34,560 states

### Action Design
- **Keep existing:** Mỗi module/activity là một action
- **Source:** `course_structure.json`
- **Count:** ~36 actions

### Reward Design
- **Cluster-specific:** Weak, Medium, Strong clusters
- **Components:** Completion, Score improvement, Stuck penalty, Difficulty bonus

---

## 🎯 COMPLETED COMPONENTS

### ✅ 1. StateBuilderV2 (`core/state_builder_v2.py`)

**Features:**
- ✅ 6-dimensional state representation
- ✅ Cluster mapping (remove teacher cluster 3)
- ✅ Quartile binning for progress & score
- ✅ Action type mapping from Moodle logs
- ✅ Stuck detection logic
- ✅ Module extraction from course structure

**Usage:**
```python
from core.state_builder_v2 import StateBuilderV2

# Initialize
builder = StateBuilderV2(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json'
)

# Build state
state = builder.build_state(
    cluster_id=0,           # Original cluster ID
    current_module_id=46,   # Module ID from course_structure
    module_progress=0.7,    # 0-1
    avg_score=0.85,         # 0-1
    recent_action_type='do_quiz',
    is_stuck=0
)
# → Output: (0, 0, 0.75, 1.0, 1, 0)

# Get state info
print(builder.state_to_string(state))
# → "Cluster=0, Module=0, Progress=0.75, Score=1.00, Action=do_quiz, Status=OK"
```

**Key Methods:**
- `build_state()` - Build state từ components
- `build_state_from_log_entry()` - Build từ log entry
- `map_action_type()` - Map Moodle events → action types
- `detect_stuck()` - Detect stuck students
- `quartile_bin()` - Bin continuous values

### ✅ 2. RewardCalculatorV2 (`core/reward_calculator_v2.py`)

**Features:**
- ✅ Auto-classify clusters (weak/medium/strong)
- ✅ Cluster-specific reward strategies
- ✅ 7 reward components
- ✅ Simple & complex reward calculation

**Reward Strategy:**

| Cluster | Focus | Completion Reward | Philosophy |
|---------|-------|-------------------|------------|
| **Weak** | Progress & Completion | +10.0 | High motivation, small wins |
| **Medium** | Balanced Growth | +7.0 | Systematic skill building |
| **Strong** | Challenge & Mastery | +5.0 | Hard tasks, efficiency |

**Usage:**
```python
from core.reward_calculator_v2 import RewardCalculatorV2

# Initialize
calc = RewardCalculatorV2(
    cluster_profiles_path='data/cluster_profiles.json'
)

# Simple reward calculation
reward = calc.calculate_reward_simple(
    cluster_id=0,
    completed=True,
    score=0.8,
    previous_score=0.6,
    is_stuck=False,
    difficulty='medium'
)
# → reward ≈ 12.0 (weak cluster + completion + score improvement)

# Get reward strategy description
strategy = calc.get_reward_strategy_description(cluster_id=0)
print(strategy)
```

**Reward Components:**
1. Completion reward (cluster-adaptive)
2. Score improvement bonus
3. Stuck penalty
4. Progression bonus (difficulty-based)
5. Time efficiency bonus (for strong clusters)
6. High score bonus
7. Failure penalty

---

## 🔧 NEXT STEPS - IMPLEMENTATION ROADMAP

### Phase 1: Data Processing (1-2 days)

#### 1.1 Log Processor V2
**File:** `core/moodle_log_processor_v2.py`

**Tasks:**
- [ ] Parse `log.csv` với new state builder
- [ ] Track student trajectory (state sequences)
- [ ] Calculate stuck indicators
- [ ] Extract action sequences

**Implementation:**
```python
class MoodleLogProcessorV2:
    def __init__(self, log_path, grade_path, state_builder, reward_calc):
        pass
    
    def process_logs(self) -> List[Dict]:
        """
        Process logs and generate (state, action, reward, next_state) tuples
        
        Returns:
            List of transitions: [
                {
                    'student_id': int,
                    'timestamp': int,
                    'state': tuple,
                    'action': int,
                    'reward': float,
                    'next_state': tuple,
                    'done': bool
                }
            ]
        """
        pass
    
    def get_student_trajectory(self, student_id) -> List[Tuple]:
        """Get complete learning trajectory for a student"""
        pass
```

#### 1.2 Student Context Tracker
**File:** `core/student_context.py`

**Tasks:**
- [ ] Track student progress per module
- [ ] Calculate avg_score dynamically
- [ ] Maintain recent_action history
- [ ] Calculate quiz_attempts, time_on_module

**Implementation:**
```python
class StudentContext:
    def __init__(self, student_id, cluster_id):
        self.student_id = student_id
        self.cluster_id = cluster_id
        self.current_module = None
        self.module_progress = {}  # module_id -> progress
        self.scores = []  # List of scores
        self.recent_actions = []  # Last N actions
        self.quiz_attempts = {}  # module_id -> attempts
        self.module_start_times = {}
    
    def update(self, log_entry, grade_entry):
        """Update context from log/grade entry"""
        pass
    
    def get_current_state(self, state_builder) -> tuple:
        """Build current state"""
        pass
```

### Phase 2: Simulation V2 (2-3 days)

#### 2.1 Student Simulator V2
**File:** `core/simulator_v2.py`

**Tasks:**
- [ ] Model student behavior per cluster
- [ ] Simulate action outcomes (score, time, completion)
- [ ] Generate realistic trajectories
- [ ] Integrate with state_builder_v2 & reward_calculator_v2

**Implementation:**
```python
class StudentSimulatorV2:
    def __init__(self, cluster_id, cluster_profile, state_builder, reward_calc):
        self.cluster_id = cluster_id
        self.ability = self._sample_ability(cluster_profile)
        self.engagement = self._sample_engagement(cluster_profile)
        self.state_builder = state_builder
        self.reward_calc = reward_calc
    
    def simulate_trajectory(self, n_steps=100) -> List[Dict]:
        """
        Simulate student learning trajectory
        
        Returns:
            List of (state, action, reward, next_state, done)
        """
        trajectory = []
        state = self._init_state()
        
        for step in range(n_steps):
            action = self._select_action(state)
            outcome = self._perform_action(action, state)
            next_state = self._update_state(state, action, outcome)
            reward = self._calculate_reward(state, action, outcome, next_state)
            done = self._check_done(next_state)
            
            trajectory.append({
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'done': done,
                'outcome': outcome
            })
            
            if done:
                break
            
            state = next_state
        
        return trajectory
    
    def _perform_action(self, action, state):
        """Simulate outcome based on cluster & ability"""
        # Success probability
        success_prob = (self.ability * 0.5 + 
                       (1 - action['difficulty_level']) * 0.3 + 
                       state[3] * 0.2)  # avg_score influence
        
        success = np.random.random() < success_prob
        
        if success:
            score = np.random.uniform(0.7, 1.0)
            time = action['expected_time'] * np.random.uniform(0.8, 1.2)
        else:
            score = np.random.uniform(0.3, 0.6)
            time = action['expected_time'] * np.random.uniform(1.2, 2.0)
        
        return {
            'success': success,
            'score': score,
            'time': time,
            'completed': success
        }
```

#### 2.2 Batch Simulation
**File:** `simulate_v2.py`

**Tasks:**
- [ ] Generate N students per cluster
- [ ] Run simulations in parallel
- [ ] Save trajectories to JSON
- [ ] Generate simulation report

### Phase 3: Q-Learning Training V2 (2-3 days)

#### 3.1 Q-Learning Agent V2
**File:** `core/qlearning_agent_v2.py`

**Tasks:**
- [ ] Initialize Q-table with new state space
- [ ] Implement Q-learning update
- [ ] Handle sparse states
- [ ] Save/load Q-table

**Implementation:**
```python
class QLearningAgentV2:
    def __init__(self, n_actions, alpha=0.1, gamma=0.95, epsilon=0.1):
        self.n_actions = n_actions
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = {}  # state -> [Q(s,a) for all actions]
    
    def get_q_value(self, state, action):
        """Get Q(s,a)"""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.n_actions)
        return self.q_table[state][action]
    
    def update(self, state, action, reward, next_state, done):
        """Q-learning update"""
        current_q = self.get_q_value(state, action)
        
        if done:
            target_q = reward
        else:
            next_max_q = np.max(self.get_q_values(next_state))
            target_q = reward + self.gamma * next_max_q
        
        # Update
        new_q = current_q + self.alpha * (target_q - current_q)
        self.q_table[state][action] = new_q
    
    def select_action(self, state):
        """ε-greedy action selection"""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            return np.argmax(self.get_q_values(state))
    
    def get_best_action(self, state):
        """Get best action (no exploration)"""
        return np.argmax(self.get_q_values(state))
```

#### 3.2 Training Script
**File:** `train_qlearning_v2.py`

**Tasks:**
- [ ] Load simulated trajectories
- [ ] Train Q-learning agent
- [ ] Monitor convergence
- [ ] Save trained Q-table
- [ ] Generate training report

### Phase 4: Visualization (3-4 days)

#### 4.1 Trajectory Visualizer
**File:** `visualize_trajectory.py`

**Tasks:**
- [ ] Plot student path through modules
- [ ] Animate learning journey
- [ ] Show state transitions
- [ ] Color by score/progress
- [ ] Mark stuck events

**Features:**
```python
# 1. Interactive trajectory plot
plot_student_journey(trajectory, course_structure)
# - X-axis: Time/Step
# - Y-axis: Module
# - Color: Score
# - Size: Progress
# - Markers: Stuck events

# 2. Progress heatmap
plot_progress_heatmap(trajectory)
# - Rows: Weeks
# - Columns: Modules
# - Color: Completion %

# 3. State transition graph
plot_state_transitions(trajectory)
# - Nodes: States
# - Edges: Actions
# - Color: Rewards
```

#### 4.2 Comparison Visualizer
**File:** `visualize_comparison.py`

**Tasks:**
- [ ] Compare multiple students
- [ ] Compare with optimal path
- [ ] Compare across clusters
- [ ] Side-by-side trajectories

#### 4.3 Dashboard
**File:** `dashboard.py`

**Tasks:**
- [ ] Interactive web dashboard (Plotly Dash)
- [ ] Student selector
- [ ] Real-time animation
- [ ] Playback controls
- [ ] Metrics overlay

### Phase 5: API Integration (2 days)

#### 5.1 Update API Service
**File:** `api_service.py`

**Tasks:**
- [ ] Update `/recommend` endpoint với state_v2
- [ ] Add `/visualize/trajectory` endpoint
- [ ] Add `/debug/state-v2` endpoint
- [ ] Backward compatibility

#### 5.2 API Request/Response Format
```python
# Request
{
    "student_id": "123",
    "cluster_id": 0,  # Original cluster ID
    "current_module_id": 46,
    "module_progress": 0.7,
    "avg_score": 0.85,
    "recent_action": "do_quiz",
    "quiz_attempts": 2,
    "time_on_module": 45,
    "recent_scores": [0.8, 0.75, 0.85]
}

# Response
{
    "student_id": "123",
    "current_state": {
        "cluster": 0,
        "module": 0,
        "progress": 0.75,
        "score": 1.0,
        "action": "do_quiz",
        "stuck": 0
    },
    "state_string": "Cluster=0, Module=0, Progress=0.75, Score=1.00, Action=do_quiz, Status=OK",
    "recommended_actions": [
        {
            "action_id": 50,
            "module_name": "Quiz: Functions",
            "q_value": 12.5,
            "expected_reward": 8.2,
            "reasoning": "Weak cluster benefits from completion-focused tasks"
        }
    ],
    "cluster_strategy": {
        "level": "weak",
        "focus": "Completion and Progress"
    }
}
```

---

## 📊 TESTING & VALIDATION

### Unit Tests
- [ ] `test_state_builder_v2.py`
- [ ] `test_reward_calculator_v2.py`
- [ ] `test_simulator_v2.py`
- [ ] `test_qlearning_agent_v2.py`

### Integration Tests
- [ ] End-to-end trajectory simulation
- [ ] API endpoint testing
- [ ] Visualization rendering

### Validation Metrics
- [ ] State coverage > 70%
- [ ] Q-value convergence
- [ ] Cluster differentiation (different policies)
- [ ] Recommendation quality (test set)

---

## 📚 FILE STRUCTURE

```
step7_qlearning/
├── core/
│   ├── state_builder_v2.py          ✅ DONE
│   ├── reward_calculator_v2.py      ✅ DONE
│   ├── moodle_log_processor_v2.py   ⏳ TODO
│   ├── student_context.py           ⏳ TODO
│   ├── simulator_v2.py              ⏳ TODO
│   ├── qlearning_agent_v2.py        ⏳ TODO
│   └── action_space.py              ✅ KEEP (minimal changes)
├── simulate_v2.py                   ⏳ TODO
├── train_qlearning_v2.py            ⏳ TODO
├── visualize_trajectory.py          ⏳ TODO
├── visualize_comparison.py          ⏳ TODO
├── dashboard.py                     ⏳ TODO
├── api_service.py                   🔄 UPDATE
├── REDESIGN_SPECIFICATION.md        ✅ DONE
└── IMPLEMENTATION_GUIDE.md          ✅ DONE (this file)
```

---

## 🎯 SUCCESS CRITERIA

### Week 1-2: Core (✅ DONE)
- ✅ StateBuilderV2 working
- ✅ RewardCalculatorV2 working
- ✅ Design document complete

### Week 3: Data & Simulation
- [ ] Log processor processes real data
- [ ] Simulator generates realistic trajectories
- [ ] Trajectories saved and validated

### Week 4: Training & Visualization
- [ ] Q-learning trained on simulated data
- [ ] Q-table shows positive values
- [ ] Basic visualization working

### Week 5: Integration
- [ ] API updated and tested
- [ ] Dashboard deployed
- [ ] Documentation complete

---

## 🚀 QUICK START (For Next Developer)

1. **Setup:**
```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning
pip install -r requirements.txt
```

2. **Test existing components:**
```bash
python3 core/state_builder_v2.py
python3 core/reward_calculator_v2.py
```

3. **Next task: Implement Log Processor V2**
```bash
# Create file
touch core/moodle_log_processor_v2.py

# Follow template in Phase 1.1 above
```

---

## 📖 REFERENCES

- **Design Spec:** `REDESIGN_SPECIFICATION.md`
- **Original Code:** `core/state_builder.py`, `core/reward_calculator.py`
- **Data:** `data/log/log.csv`, `data/cluster_profiles.json`

---

**Last Updated:** November 4, 2025  
**Status:** Core components ready ✅ | Simulation pending ⏳
