# Q-Learning Adaptive Learning System - Redesign

## 📊 Overview

Hệ thống Q-Learning được thiết kế lại để hoạt động với **Moodle data thực tế** và **course structure động**.

---

## 🎯 Key Components

### 1. **State Representation** (12 dimensions)

State được trích xuất từ **Moodle behavioral logs** (`features_scaled_report.json`):

```python
State = [
    # === STUDENT PERFORMANCE (3 dims) ===
    knowledge_level,          # mean_module_grade (0-1)
    engagement_level,         # Aggregated từ events (0-1)
    struggle_indicator,       # High attempts + low feedback (0-1)
    
    # === ACTIVITY PATTERNS (5 dims) ===
    submission_activity,      # Submitted events normalized
    review_activity,         # Reviewed + feedback_viewed
    resource_usage,          # Resource/page/url viewed
    assessment_engagement,   # Quiz/assign events
    collaborative_activity,  # Forum/comment events
    
    # === COMPLETION METRICS (4 dims) ===
    overall_progress,        # module_count
    module_completion_rate,  # course_module_completion
    activity_diversity,      # # of activity types tried
    completion_consistency,  # Std dev across modules
]
```

**File:** `core/moodle_state_builder.py`

---

### 2. **Action Space**

Action = **Specific Moodle resource** được gợi ý cho student

```python
Action = {
    'action_id': str,         # Resource ID (unique)
    'action_type': str,       # take_quiz_easy, watch_video, study_resource, ...
    'resource_id': int,       # Moodle resource ID
    'resource_name': str,     # Tên resource
    'resource_type': str,     # modname (quiz, hvp, resource, forum, ...)
    'difficulty': str,        # easy, medium, hard (nếu có)
    'section_id': int,        # Section chứa resource
    'lesson_id': int,         # Lesson chứa resource (nếu có)
    'lesson_name': str        # Tên lesson
}
```

**Action Types:**
- `take_quiz_easy`, `take_quiz_medium`, `take_quiz_hard`
- `watch_video` (hvp)
- `study_resource` (PDF, documents)
- `read_page`, `visit_url`
- `participate_forum`
- `submit_assignment`

**File:** `core/action_space.py`

---

### 3. **Q-Learning Agent**

Q-table structure:
```python
Q: Dict[(state_hash, action_id)] = Q-value
```

**Update rule:**
```
Q(s,a) ← Q(s,a) + α[r + γ·max_a' Q(s',a') - Q(s,a)]
```

**File:** `core/qlearning_agent.py` (cần refactor)

---

## 📂 Course Structure Format

```json
{
  "course_id": "5",
  "contents": [
    {
      "sectionIdOld": 34,
      "name": "Chủ đề 1: MÁY TÍNH VÀ XÃ HỘI TRI THỨC",
      "lessons": [
        {
          "sectionIdNew": 38,
          "name": "Bài 1: Làm quen với Trí tuệ nhân tạo",
          "resources": [
            {
              "id": 62,
              "name": "SGK_CS_Bai1",
              "modname": "resource"
            },
            {
              "id": 63,
              "name": "Video bài giảng bài 1",
              "modname": "hvp"
            },
            {
              "id": 61,
              "name": "bài kiểm tra bài 1 - easy",
              "modname": "quiz"
            },
            {
              "id": 106,
              "name": "bài kiểm tra bài 1 - medium",
              "modname": "quiz"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🔄 Workflow

### Training Phase

```python
# 1. Load data
state_builder = MoodleStateBuilder()
action_space = ActionSpace.load_from_file('course_structure.json')
agent = QLearningAgent(state_builder, action_space)

# 2. Load student history
students = load_student_features('features_scaled_report.json')

# 3. Train Q-table
for episode in range(n_episodes):
    student = sample_student(students)
    state = state_builder.build_state(student)
    
    # Simulate learning trajectory
    for step in range(max_steps):
        # Choose action
        action = agent.choose_action(state)
        
        # Student performs action → outcome
        outcome = simulate_outcome(student, action)
        
        # Update student state
        next_student = update_student(student, action, outcome)
        next_state = state_builder.build_state(next_student)
        
        # Calculate reward
        reward = calculate_reward(outcome)
        
        # Q-Learning update
        agent.update(state, action.action_id, reward, next_state)
        
        state = next_state
```

### Inference Phase

```python
# 1. New student
new_student_data = get_student_from_moodle(student_id)

# 2. Build state
state = state_builder.build_state(new_student_data)

# 3. Get recommendations
completed_actions = [...]  # Actions đã hoàn thành
available_actions = action_space.filter_actions(completed_actions)

recommendations = []
for action in available_actions:
    q_value = agent.get_q_value(state, action.action_id)
    recommendations.append((action, q_value))

# 4. Sort by Q-value
recommendations.sort(key=lambda x: x[1], reverse=True)

# 5. Return top-k
top_k = recommendations[:5]
```

---

## 📊 Ưu điểm của Design mới

| Aspect | Old Design | New Design |
|--------|-----------|------------|
| **State** | 22 dims, course-specific | 12 dims, course-agnostic ✅ |
| **Action** | Abstract activity features | Concrete resource IDs ✅ |
| **Data Source** | Simulated | Real Moodle logs ✅ |
| **Course Structure** | Hardcoded | Dynamic JSON ✅ |
| **Scalability** | Limited | Multi-course ✅ |
| **Interpretability** | Low | High ✅ |

---

## 🚀 Next Steps

### Phase 1: MVP (Current)
- [x] MoodleStateBuilder
- [x] ActionSpace
- [ ] Refactor QLearningAgent
- [ ] Integration test

### Phase 2: Training
- [ ] Load real student data
- [ ] Simulate learning trajectories
- [ ] Train Q-table
- [ ] Evaluate performance

### Phase 3: Deployment
- [ ] API endpoint for recommendations
- [ ] Real-time state extraction
- [ ] A/B testing
- [ ] Monitoring & feedback

---

## 📝 Example Usage

```python
# Demo script
python3 examples/demo_moodle_integration.py
```

Output:
```
=======================================================================
🎓 Q-LEARNING ADAPTIVE LEARNING SYSTEM
   Demo: Moodle State & Action Space
=======================================================================

DEMO 1: STATE EXTRACTION FROM MOODLE LOGS
=======================================================================
Student: 8609
State dimension: 12
State vector: [0.75, 0.6, 0.15, ...]

DEMO 2: ACTION SPACE FROM COURSE STRUCTURE
=======================================================================
Total actions: 7
Action type distribution:
  study_resource: 2
  watch_video: 2
  take_quiz_easy: 1
  take_quiz_medium: 1
  take_quiz_hard: 1

DEMO 3: STATE-ACTION INTERACTION
=======================================================================
High Achiever:
  Knowledge level: 0.90
  Struggle indicator: 0.10
  → Recommendation: Challenge with HARD quiz
  → Action: Action(id=107, type=take_quiz_hard, ...)

✅ All demos completed successfully!
```

---

## 📚 Files

- `core/moodle_state_builder.py` - State extraction
- `core/action_space.py` - Action space builder
- `core/qlearning_agent.py` - Q-Learning agent (cần refactor)
- `core/reward_calculator.py` - Reward function
- `examples/demo_moodle_integration.py` - Demo script
- `README_NEW_DESIGN.md` - This file

---

## 🔧 Dependencies

```bash
pip install numpy
# Moodle data phải ở format JSON
```

---

## 📞 Contact

Issues/Questions: [GitHub Issues](https://github.com/kltn-moolde/moodle-adaptive-learning-plugin/issues)
