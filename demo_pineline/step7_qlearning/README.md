# Q-Learning Adaptive Learning Path Recommendation System

## 📋 Mô tả

Hệ thống gợi ý lộ trình học tập sử dụng Q-Learning, được thiết kế để hoạt động với **BẤT KỲ khóa học nào** thông qua abstract state representation.

## 🏗️ Kiến trúc

```
step7_qlearning/
├── README.md                          # Hướng dẫn này
├── requirements.txt                   # Dependencies
│
├── models/                            # Core models
│   ├── __init__.py
│   ├── course_structure.py            # CourseStructure, Activity, Module
│   ├── student_profile.py             # StudentProfile, LearningHistory
│   └── outcome.py                     # LearningOutcome
│
├── core/                              # Q-Learning core
│   ├── __init__.py
│   ├── state_builder.py               # AbstractStateBuilder
│   ├── action_space.py                # ActionSpace
│   ├── reward_calculator.py           # RewardCalculator
│   └── qlearning_agent.py             # QLearningAgent
│
├── data/                              # Data loaders
│   ├── __init__.py
│   ├── course_loader.py               # CourseLoader (JSON, Database)
│   └── student_data_loader.py         # StudentDataLoader
│
├── training/                          # Training pipeline
│   ├── __init__.py
│   ├── trajectory_generator.py        # TrajectoryGenerator
│   └── trainer.py                     # QLearningTrainer
│
├── utils/                             # Utilities
│   ├── __init__.py
│   ├── feature_extractor.py           # FeatureExtractor
│   └── validators.py                  # DataValidator, LogicValidator
│
├── examples/                          # Example usage
│   ├── course_structure_example.json  # Example course
│   ├── train_example.py               # Training example
│   └── inference_example.py           # Inference example
│
└── tests/                             # Unit tests
    ├── __init__.py
    ├── test_state_builder.py
    └── test_qlearning_agent.py
```

## 🎯 Đặc điểm

### 1. **Tổng quát hóa (Generalization)**
- State representation không phụ thuộc vào khóa học cụ thể
- Dùng features tương đối thay vì absolute values
- Q-table dựa trên abstract features

### 2. **Dễ mở rộng (Extensibility)**
- Interface-based design
- Plugin architecture cho reward functions
- Customizable state features

### 3. **Dễ bảo trì (Maintainability)**
- Clear separation of concerns
- Comprehensive documentation
- Unit tests

## 🚀 Quick Start

### 1. Cài đặt

```bash
cd step7_qlearning
pip install -r requirements.txt
```

### 2. Chuẩn bị course structure

```python
# Tạo file course_structure.json theo schema
{
  "course_id": "course_123",
  "modules": [...],
  "activities": [...]
}
```

### 3. Training

```python
from core.qlearning_agent import QLearningAgent
from training.trainer import QLearningTrainer
from data.course_loader import CourseLoader

# Load course
course = CourseLoader.from_json('course_structure.json')

# Create agent
agent = QLearningAgent(course)

# Train
trainer = QLearningTrainer(agent, course)
trainer.train_from_logs(db_connection, userids=[...])

# Save
agent.save('models/qlearning_course_123.pkl')
```

### 4. Inference

```python
# Load trained model
agent = QLearningAgent.load('models/qlearning_course_123.pkl')

# Get recommendation
student_profile = {...}
recommendation = agent.recommend(student_profile)

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
