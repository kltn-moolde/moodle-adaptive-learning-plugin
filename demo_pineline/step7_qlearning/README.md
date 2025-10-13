# Q-Learning Adaptive Learning System

## � Overview

Hệ thống gợi ý học tập thích ứng sử dụng **Q-Learning** để học policy tối ưu cho từng student dựa trên:
- **State**: Behavioral features từ Moodle logs (12 dimensions)
- **Action**: Specific resources từ course structure (quiz, video, PDF, ...)
- **Reward**: Learning outcomes (grades, completion, engagement)

**Key Features:**
- ✅ State từ real Moodle data (`features_scaled_report.json`)
- ✅ Action space động từ course structure JSON
- ✅ Support multiple difficulty levels (easy/medium/hard)
- ✅ Course-agnostic design
- ✅ Modular & extensible

---

## 🏗️ Architecture

```
step7_qlearning/
├── README.md                          # This file
├── README_NEW_DESIGN.md               # Detailed design doc
├── requirements.txt                   # Dependencies
│
├── core/                              # Q-Learning engine
│   ├── moodle_state_builder.py        # State từ Moodle logs (12 dims)
│   ├── action_space.py                # Action space từ course JSON
│   ├── qlearning_agent.py             # Q-Learning agent (cần refactor)
│   └── reward_calculator.py           # Reward calculation
│
├── models/                            # Data models (legacy, cần cleanup)
│   ├── course_structure.py            # CourseStructure class
│   ├── student_profile.py             # StudentProfile class
│   └── outcome.py                     # LearningOutcome class
│
└── examples/                          # Demo scripts
    ├── demo_moodle_integration.py     # ⭐ Main demo
    ├── course_structure_example.json  # Example course
    └── quick_demo.py                  # Old demo (legacy)
```

## 🎯 Key Concepts

### 1. **State (12 dimensions)**
Trích xuất từ Moodle `features_scaled_report.json`:
- Student Performance: knowledge_level, engagement, struggle
- Activity Patterns: submission, review, resource usage, assessment, collaboration
- Completion Metrics: progress, completion rate, diversity, consistency

### 2. **Action (Dynamic)**
Mỗi action = 1 Moodle resource cụ thể:
- `take_quiz_easy`, `take_quiz_medium`, `take_quiz_hard`
- `watch_video`, `study_resource`, `participate_forum`
- Dynamic từ course structure JSON

### 3. **Reward**
Based on learning outcomes:
- Grade improvement
- Completion rate
- Time efficiency
- Engagement quality

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd demo_pineline/step7_qlearning
pip install -r requirements.txt
```

### 2. Run Demo

```bash
cd examples
python3 demo_moodle_integration.py
```

**Output:**
- State extraction từ Moodle logs
- Action space từ course structure
- Recommendation logic demo

### 3. Usage Example

```python
from core.moodle_state_builder import MoodleStateBuilder
from core.action_space import ActionSpace

# Load student data
student_data = {
    'userid': 8609,
    'mean_module_grade': 0.75,
    'total_events': 0.6,
    'engagement': 0.8,
    # ... more features
}

# Build state
state_builder = MoodleStateBuilder()
state = state_builder.build_state(student_data)
print(f"State: {state}")  # 12-dim vector

# Load course structure
action_space = ActionSpace.load_from_file('course_structure.json')
print(f"Total actions: {action_space.get_action_space_size()}")

# Get recommendations (rule-based for now)
if state[2] > 0.6:  # High struggle
    recommendations = action_space.get_actions_by_difficulty('easy')
else:
    recommendations = action_space.get_actions_by_difficulty('medium')

for action in recommendations[:3]:
    print(f"  {action}")
```

---

## 📚 Documentation

- **[README_NEW_DESIGN.md](README_NEW_DESIGN.md)** - Chi tiết thiết kế mới
- **[CHANGELOG.md](CHANGELOG.md)** - Lịch sử thay đổi
- **[TODO.md](TODO.md)** - Công việc còn lại

---

## 🎯 Next Steps

### Phase 1: Core Refactoring ✅ (Completed)
- [x] Design new State (12 dims từ Moodle)
- [x] Design new Action (resource IDs)
- [x] Implement MoodleStateBuilder
- [x] Implement ActionSpace
- [x] Demo script

### Phase 2: Integration (In Progress)
- [ ] Refactor QLearningAgent
- [ ] Create training pipeline
- [ ] Test với real data
- [ ] Validate recommendations

### Phase 3: Deployment (Future)
- [ ] API endpoint
- [ ] Moodle plugin integration
- [ ] Monitoring
- [ ] A/B testing

---

## 🤝 Contributing

1. Check [TODO.md](TODO.md) for open tasks
2. Follow existing code style
3. Add tests for new features
4. Update documentation

---

## 📄 License

MIT License

---

## 📞 Contact

Issues: [GitHub Issues](https://github.com/kltn-moolde/moodle-adaptive-learning-plugin/issues)

print(f"Recommended: {recommendation['activity_name']}")
print(f"Confidence: {recommendation['q_value']:.2f}")
```

## 📚 Chi tiết

Xem documentation trong từng module để biết thêm chi tiết.

## 🧪 Testing

```bash
pytest tests/
```

## 📄 License

MIT
