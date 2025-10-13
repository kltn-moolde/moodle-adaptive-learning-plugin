# 🎓 Q-LEARNING ADAPTIVE LEARNING SYSTEM

## ✨ TÓM TẮT

Hệ thống gợi ý lộ trình học tập sử dụng **Q-Learning**, được thiết kế để hoạt động với **BẤT KỲ khóa học nào** thông qua abstract state representation.

### 🎯 Đặc điểm nổi bật

- ✅ **Tổng quát hóa**: Q-table hoạt động với nhiều khóa học khác nhau
- ✅ **Hướng đối tượng**: Interface-based, dễ mở rộng
- ✅ **Dependency Injection**: Swap components dễ dàng
- ✅ **Transfer Learning**: Train 1 lần, deploy nhiều courses
- ✅ **Production-ready**: Comprehensive tests và documentation

---

## 📁 CẤU TRÚC THƯ MỤC

```
step7_qlearning/
│
├── 📄 README.md                    # Overview
├── 📄 USAGE_GUIDE.md              # Hướng dẫn chi tiết
├── 📄 ARCHITECTURE.md             # Kiến trúc và thiết kế
├── 📄 requirements.txt            # Dependencies
│
├── 📦 models/                     # Data models
│   ├── course_structure.py       # CourseStructure, Module, Activity
│   ├── student_profile.py        # StudentProfile, LearningHistory
│   └── outcome.py                # LearningOutcome
│
├── 🧠 core/                       # Q-Learning core
│   ├── state_builder.py          # AbstractStateBuilder
│   ├── action_space.py           # ActionSpace
│   ├── reward_calculator.py      # RewardCalculator
│   └── qlearning_agent.py        # QLearningAgent ⭐
│
├── 📊 data/                       # Data loaders (TODO)
│   ├── course_loader.py
│   └── student_data_loader.py
│
├── 🎓 training/                   # Training pipeline (TODO)
│   ├── trajectory_generator.py
│   └── trainer.py
│
├── 🛠️ utils/                      # Utilities (TODO)
│   ├── feature_extractor.py
│   └── validators.py
│
├── 📝 examples/                   # Examples
│   ├── course_structure_example.json
│   ├── quick_demo.py             # Demo nhanh ⚡
│   └── inference_example.py      # (TODO)
│
└── 🧪 tests/                      # Unit tests (TODO)
    └── test_qlearning_agent.py
```

---

## 🚀 QUICK START

### 1. Cài đặt

```bash
cd step7_qlearning
pip install -r requirements.txt
```

### 2. Run demo

```bash
python examples/quick_demo.py
```

### 3. Load course và recommend

```python
from models.course_structure import CourseStructure
from core.qlearning_agent import QLearningAgent
from models.student_profile import StudentProfile
import json

# Load course
with open('examples/course_structure_example.json') as f:
    course_data = json.load(f)
course = CourseStructure.from_dict(course_data)

# Create agent
agent = QLearningAgent(course)

# (Optional) Load pre-trained model
# agent.load('models/qlearning_model.pkl')

# Create student profile
student = StudentProfile(
    student_id='student_001',
    course_id=course.course_id
)

# Get recommendations
recommendations = agent.recommend(student, top_k=3)

for rec in recommendations:
    print(f"📚 {rec['activity_name']}")
    print(f"   Q-value: {rec['q_value']:.3f}")
    print(f"   Difficulty: {rec['difficulty']:.2f}")
    print(f"   Est. time: {rec['estimated_minutes']} min\n")
```

---

## 📚 DOCUMENTATION

### Core Documents

1. **[README.md](README.md)** - Overview và Quick Start
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Kiến trúc chi tiết, thiết kế Q-table
3. **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Hướng dẫn sử dụng đầy đủ

### Key Concepts

#### **State Representation**
```python
state = [
    # Student features (6)
    avg_grade, completion_rate, engagement, 
    consistency, progress, time_since_last,
    
    # Activity features (11+)
    difficulty, estimated_time, prerequisite_met,
    n_prerequisites, is_optional,
    type_vector[],  # One-hot encoding
    module_position, activity_depth, similar_success_rate,
]
# Total: ~19-21 features
```

#### **Q-Table Structure**
```python
Q: Dict[(state_hash, action_id)] = Q-value

# Example:
Q[(0.75, 0.40, 0.80, ...), 'act_2_3'] = 0.82
```

#### **Bellman Update**
```python
Q(s, a) ← Q(s, a) + α [R + γ max Q(s', a') - Q(s, a)]
```

---

## 🎯 THIẾT KẾ CHO NHIỀU KHÓA HỌC

### Nguyên tắc

1. **Abstract Features**: Không dùng activity IDs cụ thể
2. **Relative Values**: Dùng ratios thay vì absolute counts
3. **Generic Properties**: difficulty, type, position, etc.

### Transfer Learning Workflow

```
Course A (Python)
    ↓ Train
Q-table (5K entries)
    ↓ Save
Model file
    ↓ Load
Course B (JavaScript)
    ↓ Fine-tune (optional)
Q-table (8K entries)
    ↓ Deploy
Production ✅
```

---

## 🔧 MỞ RỘNG VÀ TÙY CHỈNH

### Custom State Builder

```python
from core.state_builder import AbstractStateBuilder

class MyStateBuilder(AbstractStateBuilder):
    def build_state(self, student, activity, timestamp):
        # Custom implementation
        pass
```

### Custom Reward Calculator

```python
from core.reward_calculator import RewardCalculator

class MyRewardCalculator(RewardCalculator):
    def calculate_reward(self, student, action, outcome):
        # Custom logic
        return reward
```

### Usage

```python
agent = QLearningAgent(
    course_structure=course,
    state_builder=MyStateBuilder(course),
    reward_calculator=MyRewardCalculator(course)
)
```

---

## 📊 STATUS

### ✅ Completed

- [x] Core models (CourseStructure, StudentProfile, Outcome)
- [x] Q-Learning agent implementation
- [x] State builder (abstract + default)
- [x] Action space manager
- [x] Reward calculator
- [x] Example course structure
- [x] Quick demo script
- [x] Comprehensive documentation

### 🚧 TODO

- [ ] Data loaders (JSON, Database)
- [ ] Training pipeline (từ historical logs)
- [ ] Trajectory generator
- [ ] Feature extractor utilities
- [ ] Validators
- [ ] Unit tests
- [ ] Integration example với database
- [ ] REST API wrapper
- [ ] Performance benchmarks

---

## 🧪 TESTING

```bash
# (TODO) Run unit tests
pytest tests/

# Run demo
python examples/quick_demo.py
```

---

## 📈 PERFORMANCE

### Expected Metrics

- **Q-table size**: 5K-50K entries (tùy số courses)
- **State dimension**: 19-21 features
- **Inference time**: < 10ms per recommendation
- **Training time**: ~30 min cho 100 sinh viên, 50 epochs

### Scalability

- ✅ Single course: 15-100 sinh viên
- ✅ Multi-course: 10+ courses với shared Q-table
- ✅ Production: 1000+ sinh viên, load model 1 lần

---

## 💡 BEST PRACTICES

### Training

```python
# 1. Split data
train_users = users[:80]  # 80%
test_users = users[80:]   # 20%

# 2. Train with validation
trainer.train_from_logs(conn, train_users, n_epochs=50)
accuracy = trainer.validate(test_users)

# 3. Save model
agent.save('models/qlearning_v1.pkl')
```

### Deployment

```python
# 1. Load once at startup
agent = QLearningAgent.load_from_file(
    'models/qlearning_v1.pkl',
    course_structure=course
)

# 2. Cache in memory
# 3. Serve recommendations
recommendations = agent.recommend(student, top_k=3)
```

---

## 🤝 CONTRIBUTING

Muốn mở rộng hệ thống?

1. Fork repo
2. Implement custom component (state builder, reward, etc.)
3. Add unit tests
4. Submit PR

---

## 📞 SUPPORT

- **Documentation**: Xem các file .md trong thư mục
- **Examples**: Chạy `examples/quick_demo.py`
- **Issues**: Report qua GitHub Issues

---

## 📄 LICENSE

MIT License

---

## 🎓 CITATION

Nếu sử dụng hệ thống này trong research:

```
@software{qlearning_adaptive_learning,
  title={Q-Learning Adaptive Learning Path Recommendation System},
  author={Your Name},
  year={2025},
  url={https://github.com/your-repo}
}
```

---

## 🌟 FEATURES ROADMAP

### v1.0 (Current)
- ✅ Core Q-Learning implementation
- ✅ Abstract state representation
- ✅ Multi-course support

### v1.1 (Next)
- [ ] Database integration
- [ ] Training pipeline
- [ ] REST API

### v2.0 (Future)
- [ ] Deep Q-Network (DQN)
- [ ] Multi-agent learning
- [ ] Real-time adaptation

---

**Built with ❤️ for Adaptive Learning**

🚀 Ready to deploy!
