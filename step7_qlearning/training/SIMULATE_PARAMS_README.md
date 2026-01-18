# Simulate Parameters Generation

## Mục đích

File `data_train.py` trích xuất tham số từ dữ liệu khóa học **mẫu (course 670)** để dùng trong simulate students, từ đó huấn luyện Q-Learning agent có căn cứ.

Thay vì random hoàn toàn, simulate sẽ theo các patterns học tập thực tế từ dữ liệu.

## Output

**File**: `simulate_params/simulate_parameters_course_670.json`

Chứa các tham số structured:

### 1. **action_space** (17 actions)
Map chính xác với `ActionSpace` (5 past + 7 current + 3 future):
```json
[
  ["view_assignment", "past"],
  ["view_content", "past"],
  ...
  ["attempt_quiz", "future"],
  ["post_forum", "future"]
]
```

### 2. **action_transition_matrix** 
Xác suất chọn action theo state:
```json
{
  "(cluster, module, progress, score, phase, engagement)": {
    "view_content_current": 0.35,
    "attempt_quiz_current": 0.25,
    ...
  }
}
```

### 3. **time_patterns**
Thời gian trung bình per action_type (để tính `time_on_task`):
```json
{
  "view_content": {
    "mean": 207.0,
    "std": 472.8,
    "min": 0.5,
    "max": 3600.0
  },
  ...
}
```

### 4. **state_distribution**
Phân bố của các state trong dữ liệu thực (prior distribution):
```json
{
  "(3, 0, 1, 0, 0, 1)": 0.0423,
  "(0, 0, 1, 0, 0, 1)": 0.0421,
  ...
}
```

### 5. **engagement_patterns**
P(engagement_level | learning_phase, progress):
```json
{
  "phase_0_progress_1": {
    "0": 0.60,   # Low engagement
    "1": 0.30,   # Medium engagement
    "2": 0.10    # High engagement
  },
  ...
}
```

### 6. **progress_patterns**
Mức độ tiến triển sau mỗi action:
```json
{
  "attempt_quiz": {
    "avg_change": 0.15,
    "std_change": 0.10,
    "improve_prob": 0.65
  },
  ...
}
```

### 7. **score_patterns**
Mức độ cải thiện điểm sau mỗi action:
```json
{
  "submit_quiz": {
    "avg_change": 0.25,
    "std_change": 0.12,
    "improve_prob": 0.80
  },
  ...
}
```

### 8. **learning_phase_distribution**
Phân bố phase toàn bộ học viên:
```json
{
  "0": 0.30,   # Pre-learning
  "1": 0.50,   # Active-learning
  "2": 0.20    # Reflective-learning
}
```

## State Space Mapping

**6D State**: (cluster, module, progress_bin, score_bin, learning_phase, engagement_level)

```
cluster:  0-4    (5 user clusters)
module:   0      (1 module, simplified)
progress: 0-3    (4 bins: 0-25%, 25-50%, 50-75%, 75-100%)
score:    0      (1 bin, simplified)
phase:    0-2    (pre-learning, active, reflective)
engagement: 0-2  (low, medium, high)
```

**Total states**: 5 × 1 × 4 × 1 × 3 × 3 = 180 (theoretical)
**Observed**: 75 states trong dữ liệu

## Action Space Mapping

**17 Actions** (action_type, time_context):

**Past (5)**: view_assignment, view_content, attempt_quiz, review_quiz, post_forum
**Current (7)**: view_assignment, view_content, submit_assignment, attempt_quiz, submit_quiz, review_quiz, post_forum
**Future (3)**: view_content, attempt_quiz, post_forum

## Cách Dùng trong Simulate

Khi sinh synthetic students, tạo trajectory như sau:

```python
# Load parameters
params = json.load(open('simulate_parameters_course_670.json'))

# Khởi tạo state ngẫu nhiên từ prior distribution
state = sample_from(params['state_distribution'])

# Mô phỏng T steps:
for t in range(T):
    # Chọn action từ transition matrix
    action_probs = params['action_transition_matrix'].get(str(state), {})
    action_str = sample_from(action_probs)
    
    # Chuyển đổi action_str -> (action_type, time_context)
    action_type, time_context = parse_action(action_str)
    
    # Tính duration từ time_patterns
    duration = sample_from(
        Normal(
            params['time_patterns'][action_type]['mean'],
            params['time_patterns'][action_type]['std']
        )
    )
    
    # Tính next_state từ progress/score patterns
    next_state = transition_state(
        state, 
        action_type,
        params['progress_patterns'],
        params['score_patterns'],
        params['engagement_patterns']
    )
    
    # Ghi lại transition (state, action, reward, next_state)
    trajectory.append((state, action, reward, next_state))
    state = next_state
```

## Cấu Trúc File

```
demo_pineline/step7_qlearning/
├── training/
│   ├── data_train.py                  ← Script extraction
│   ├── SIMULATE_PARAMS_README.md      ← Doc này
│   └── simulate_params/
│       └── simulate_parameters_course_670.json   ← Output params
```

## Chạy Script

```bash
cd demo_pineline/step7_qlearning
python3 training/data_train.py
```

Output:
```
[*] Loading data from ...
[+] Loaded 13995 logs, 233 grades
[*] Mapping log events to ActionSpace actions...
[+] Mapped 12693/13995 events
[*] Computing 6D state features...
[*] Building state transition sequences...
[+] Built 12671 transitions from 21 users
[*] Extracting simulation parameters...
[+] Done! Wrote simulate_parameters_course_670.json
```

## Summary

**Course 670 Data**:
- 21 students
- 12,693 mapped events → 12,671 transitions
- 75 unique states observed
- 5 clusters, 1 module, 4 progress bins, 3 phases, 3 engagement levels

**Action Distribution**:
- view_content: 207s average (±472s)
- attempt_quiz: 189s average (±454s)
- view_assignment: 64s average (±283s)
- submit_assignment: 6s average (±39s)
- post_forum: 1.5s average (±0.7s)

**Top States**:
- (3, 0, 1, 0, 0, 1): 4.23% - Cluster 3, mid-progress, low score, pre-learning, medium engagement
- (0, 0, 1, 0, 0, 1): 4.21% - Cluster 0, mid-progress, low score, pre-learning, medium engagement

Các state này là các "trạng thái điển hình" của học viên khi học, được dùng làm seed cho simulate.
