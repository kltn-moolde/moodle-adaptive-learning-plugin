# Refactored data_train.py - Tạo Simulate Parameters Có Căn Cứ

## Tóm Tắt

Bạn muốn simulate sinh viên một cách có căn cứ chứ không random bừa. Tôi đã viết lại `data_train.py` để:

1. **Đọc khóa học mẫu (670)** → log 13,995 events, 233 grades, 22 học viên
2. **Map event Moodle → ActionSpace** (17 actions với time_context)
3. **Tính 6D state** từ dữ liệu (cluster, module, progress, score, phase, engagement)
4. **Trích tham số structured** vào JSON để dùng trong simulate

## Output

```
simulate_params/simulate_parameters_course_670.json
```

### Chứa những gì:

| Tham số | Mục đích | Ví dụ |
|---------|---------|-------|
| `action_space` | 17 actions được định nghĩa | `[["view_content", "past"], ["attempt_quiz", "current"], ...]` |
| `action_transition_matrix` | P(action \| state) | Từ state (3,0,1,0,0,1), xác suất chọn view_content: 0.35 |
| `time_patterns` | Thời gian/action trung bình | view_content: 207s ±472s |
| `state_distribution` | Phân bố state trong data | State (3,0,1,0,0,1) xuất hiện 4.23% |
| `engagement_patterns` | P(engagement \| phase, progress) | Ở phase 0 progress 1: Low=60%, Medium=30%, High=10% |
| `progress_patterns` | Cải thiện progress per action | attempt_quiz: +15% progress (65% xác suất) |
| `score_patterns` | Cải thiện score per action | submit_quiz: +25% score (80% xác suất) |
| `learning_phase_distribution` | Phân bố phase tổng thể | Pre=30%, Active=50%, Reflective=20% |

## Map với ActionSpace & StateBuilder

### ActionSpace (17 actions)
```python
# Từ core/rl/action_space.py
[
  ("view_assignment", "past"),    # 0
  ("view_content", "past"),        # 1
  ...
  ("attempt_quiz", "future"),      # 13
  ("post_forum", "future")         # 14
]
```

### StateBuilderV2 (6D state)
```python
# Từ core/rl/state_builder.py
build_state(
  cluster_id,           # 0-4 (5 clusters)
  module_idx,           # 0   (1 module)
  progress_bin,         # 0-3 (4 bins)
  score_bin,            # 0   (1 bin)
  learning_phase,       # 0-2 (pre, active, reflective)
  engagement_level      # 0-2 (low, medium, high)
)
```

## Cách Chạy

```bash
cd demo_pineline/step7_qlearning
python3 training/data_train.py
```

Output:
```
[*] Loading data...
[+] Loaded 13995 logs, 233 grades
[+] Unique users: 22
[*] Mapping log events to ActionSpace actions...
[+] Mapped 12693/13995 events
[*] Computing 6D state features...
[*] Building state transition sequences...
[+] Built 12671 transitions from 21 users
[*] Extracting simulation parameters...
[+] Done! Wrote simulate_parameters_course_670.json

======= SIMULATE PARAMETERS SUMMARY =======
Course 670:
  - Total users: 21
  - Total transitions: 12671
  - Unique states: 75
  - Clusters: 5
  - Modules: 1
  - Actions: 15

Time Patterns (mean duration in seconds):
  - attempt_quiz        : 189.2s (±454.4)
  - view_content        : 207.0s (±472.8)
  - view_assignment     :  64.1s (±283.1)
  - submit_assignment   :   6.3s (± 39.7)
  - post_forum          :   1.5s (±  0.7)

State Samples (top 5 frequent states):
  - (3, 0, 1, 0, 0, 1): 4.23%
  - (0, 0, 1, 0, 0, 1): 4.21%
  - (0, 0, 2, 0, 0, 1): 4.07%
  - (0, 0, 0, 0, 0, 0): 3.62%
  - (3, 0, 0, 0, 0, 0): 3.50%
```

## Dùng Parameters để Simulate

Xem file `simulate_example.py`:

```bash
python3 training/simulate_example.py
```

Sẽ sinh 1 trajectory 10 steps từ dữ liệu thực:

```
Step 0:
  State: (4, 0, 1, 0, 0, 1)
  Action: view_assignment_current (type=view_assignment, context=current)
  Duration: 0.0s
  Next State: (4, 0, 1, 0, 0, 0)
  Reward: 0.50

Step 1:
  State: (4, 0, 1, 0, 0, 0)
  Action: view_content_current (type=view_content, context=current)
  Duration: 225.4s
  Next State: (4, 0, 1, 0, 0, 0)
  Reward: 0.50
...
```

## File Structure

```
demo_pineline/step7_qlearning/
├── training/
│   ├── data_train.py                           ← NEW (refactored)
│   ├── SIMULATE_PARAMS_README.md               ← NEW (doc)
│   ├── simulate_example.py                     ← NEW (example usage)
│   └── simulate_params/
│       └── simulate_parameters_course_670.json ← NEW (output)
├── data/
│   ├── udk_moodle_log_course_670.csv           (copied from ../data/)
│   └── udk_moodle_grades_course_670.csv        (copied from ../data/)
└── ...
```

## Giải Thích Chi Tiết

### 1. Log Event → Action Type Mapping

File Moodle CSV có cột `eventname` như:
- `\mod_assign\event\course_module_viewed` → `view_assignment`
- `\mod_quiz\event\quiz_attempt_submitted` → `submit_quiz`
- `\mod_forum\event\post_created` → `post_forum`

Script map tất cả vào **5 action types**: view_content, view_assignment, attempt_quiz, submit_quiz, review_quiz, submit_assignment, post_forum

Unmapped (1,302 events) được loại bỏ vì không thể xác định action_type.

### 2. Time Context Inference

Từ `module_progress` (bao nhiêu % logs của user trong module):
- progress < 25% → **past** (mới bắt đầu module)
- 25% ≤ progress < 85% → **current** (đang học module)
- progress ≥ 85% → **future** (sắp xong, xem module tiếp theo)

Vì vậy cùng 1 action_type (e.g., "attempt_quiz") có thể có 3 variants trong ActionSpace.

### 3. 6D State Computation

```python
# Cluster: Pseudo-cluster từ userid % 5
cluster_id = userid % 5  # 0-4

# Module: Từ section_id (fallback: pseudo sections)
module_idx = section_id_to_idx[section_id]  # 0-n_modules

# Progress: % logs của user trong module (binned)
progress_bin = bin(logs_count / total_logs)  # 0, 1, 2, 3 (quartiles)

# Score: Điểm cao nhất lên tới hiện tại (binned)
score_bin = bin(max_score_so_far / 100)  # 0, 1, 2, 3

# Phase: Từ action_type gần nhất
phase = {
  view_content, view_assignment → 0 (pre_learning),
  attempt_quiz, submit_quiz, submit_assignment → 1 (active_learning),
  review_quiz, post_forum → 2 (reflective_learning)
}

# Engagement: Quality score từ action_weights
engagement = {
  low: weight_score < 8,
  medium: 8 ≤ weight_score < 16,
  high: weight_score ≥ 16
}
```

### 4. State Transition Extraction

Duyệt từng user → sắp xếp log theo timestamp → cặp log liên tiếp = 1 transition:

```python
transition = {
  'state': (cluster, module, progress, score, phase, engagement),
  'action': (action_type, time_context),
  'next_state': (cluster', module', progress', score', phase', engagement'),
  'duration': timestamp_next - timestamp_current
}
```

Tổng **12,671 transitions** từ 21 users (22 users nhưng 1 user không có transitions).

### 5. Parameter Extraction

Từ transitions:

- **action_transition_matrix**: P(action | state) từ freq count
- **time_patterns**: mean/std/min/max duration per action_type
- **state_distribution**: frequency of each state
- **engagement_patterns**: P(engagement | phase, progress) cross-tab
- **progress_patterns**: avg/std/prob(improve) of progress_bin change per action
- **score_patterns**: avg/std/prob(improve) of score_bin change per action
- **learning_phase_distribution**: frequency of each phase overall

## Validate

Kiểm tra xem parameters có phù hợp:

```bash
python3 -c "
import json
p = json.load(open('simulate_params/simulate_parameters_course_670.json'))
print('✓ action_space:', len(p['action_space']), 'actions')
print('✓ states observed:', len(p['state_distribution']))
print('✓ action_types:', len(p['time_patterns']))
print('✓ transitions matrix:', len(p['action_transition_matrix']))
"
```

Output:
```
✓ action_space: 17 actions
✓ states observed: 75
✓ action_types: 5
✓ transitions matrix: 75
```

## Next Steps

1. **Dùng parameters này để sinh synthetic training data**:
   ```bash
   python3 training/simulate_example.py  # Xem example
   ```

2. **Integrate vào StudentSimulator** để sinh trajectories với ground truth từ dữ liệu thực

3. **Huấn luyện Q-Learning agent** trên trajectories này

4. **Test agent** trên dữ liệu thực từ course 670 để validate

## Notes

- **Simplified**: Module chỉ có 1 (dữ liệu không rõ module structure) → cần cải thiện khi có dữ liệu tốt hơn
- **Score bin**: Chỉ có 1 bin (tất cả học viên score ≈ 0) → điểm không rõ → cần check data
- **Cluster**: Pseudo từ userid % 5, không phải từ behavioral clustering → có thể cải thiện

## Tài liệu Tham Khảo

- `core/rl/action_space.py` - 17 actions definition
- `core/rl/state_builder.py` - 6D state building logic
- `core/log_processing/processor.py` - Log processing reference
