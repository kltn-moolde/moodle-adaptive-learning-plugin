# 🎓 Q-LEARNING ADAPTIVE LEARNING - HƯỚNG DẪN SỬ DỤNG

## 📋 MỤC LỤC

1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
4. [Thiết kế Q-Table](#thiết-kế-q-table)
5. [Sử dụng cơ bản](#sử-dụng-cơ-bản)
6. [Tùy chỉnh và mở rộng](#tùy-chỉnh-và-mở-rộng)
7. [Best Practices](#best-practices)

---

## 🎯 GIỚI THIỆU

### Hệ thống làm gì?

Gợi ý lộ trình học tập **TỐI ƯU** cho từng sinh viên dựa trên:
- ✅ Profile hiện tại (grades, engagement, consistency)
- ✅ Hành vi học tập trước đó
- ✅ Cấu trúc khóa học (prerequisites, difficulty)
- ✅ Mục tiêu: Maximize learning outcomes

### Tại sao dùng Q-Learning?

| **Tiêu chí** | **Rule-based** | **ML Classifier** | **Q-Learning** ✅ |
|--------------|----------------|-------------------|-------------------|
| Personalization | ❌ Thấp | ⚠️ Trung bình | ✅ **Cao** |
| Adaptability | ❌ Cứng nhắc | ⚠️ Cần retrain | ✅ **Liên tục học** |
| Explainability | ✅ Rõ ràng | ❌ Black-box | ⚠️ Q-values |
| Data requirement | ✅ Ít | ❌ Nhiều | ⚠️ Trung bình |

---

## 🔧 CÀI ĐẶT

### 1. Prerequisites

```bash
Python >= 3.8
```

### 2. Install dependencies

```bash
cd step7_qlearning
pip install -r requirements.txt
```

### 3. Quick test

```bash
python examples/quick_demo.py
```

**Output mong đợi:**
```
🎓 Q-LEARNING ADAPTIVE LEARNING SYSTEM
   Demo: Course Recommendation

============================================================
DEMO: Q-LEARNING TRAINING
============================================================

1. Creating course structure...
   ✓ Course: Demo Course
   ✓ Modules: 2
   ✓ Activities: 5

2. Creating Q-Learning agent...
   ✓ Agent created: QLearningAgent(...)
   ✓ State dimension: 21

...
✅ Demo completed!
```

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Components Overview

```
┌─────────────────────────────────────────────────────────┐
│                   CourseStructure                        │
│  - Modules, Activities                                   │
│  - Prerequisite graph                                    │
│  - Course metadata                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                  StudentProfile                          │
│  - Learning history                                      │
│  - Grades, completion                                    │
│  - Derived features (engagement, consistency)            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│               AbstractStateBuilder                       │
│  Student features + Activity context → State vector      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                  QLearningAgent                          │
│  Q(state, action) → Expected reward                      │
│  Policy: Choose best action to maximize outcome          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 Recommendation                           │
│  "You should learn: Activity X" (Q-value: 0.85)         │
└─────────────────────────────────────────────────────────┘
```

### Dependency Injection

Tất cả components có thể **swap** để customize:

```python
# Default
agent = QLearningAgent(course_structure)

# Custom
agent = QLearningAgent(
    course_structure=course,
    state_builder=MyCustomStateBuilder(course),
    action_space=MyCustomActionSpace(course),
    reward_calculator=MyCustomRewardCalculator(course)
)
```

---

## 🎯 THIẾT KẾ Q-TABLE

### KEY DESIGN: Abstract State Representation

#### ❌ BAD: Hard-coded state

```python
# KHÔNG làm thế này!
state = {
    'completed_act_1_1': True,
    'completed_act_1_2': False,
    'grade_act_1_1': 0.85,
    ...
}
# → Chỉ hoạt động với 1 khóa học cụ thể
# → Không scale được
```

#### ✅ GOOD: Abstract features

```python
# Làm thế này!
state = [
    0.75,  # avg_grade (normalized)
    0.40,  # completion_rate
    0.80,  # engagement_score
    0.65,  # consistency_score
    0.45,  # difficulty của activity tiếp theo
    ...
]
# → Hoạt động với MỌI khóa học
# → Scale tốt
```

### State Structure

#### **Part 1: Student Profile Features (6 features)**

```python
[
    avg_grade,           # 0-1, điểm TB
    completion_rate,     # 0-1, % hoàn thành
    engagement_score,    # 0-1, mức độ tích cực
    consistency_score,   # 0-1, độ đều đặn
    progress,            # 0-1, normalized completed count
    time_since_last,     # 0-1, days since last activity (normalized)
]
```

#### **Part 2: Activity Context Features (11+ features)**

```python
[
    difficulty,              # 0-1, độ khó
    estimated_time,          # 0-1, normalized
    prerequisite_met,        # 0/1, binary
    n_prerequisites,         # 0-1, normalized
    is_optional,             # 0/1, binary
    type_video,              # 0/1, one-hot
    type_quiz,               # 0/1, one-hot
    type_assignment,         # 0/1, one-hot
    ...,                     # other types
    module_position,         # 0-1, vị trí trong course
    activity_depth,          # 0-1, độ sâu trong prerequisite graph
    similar_success_rate,    # 0-1, success với activities tương tự
]
```

#### **Part 3: Optional - Cluster (2 features)**

```python
[
    cluster_0,  # 0/1, thuộc cluster_0 (good students)
    cluster_1,  # 0/1, thuộc cluster_1 (struggling students)
]
```

**Total: ~19-21 features**

### Q-Table Structure

```python
Q-table = Dict[(state_hash, action_id)] = Q-value

# Example:
Q[
    (0.75, 0.40, 0.80, ...),  # State hash (rounded)
    'act_2_3'                 # Action ID
] = 0.82  # Q-value (expected reward)
```

### Why this works across courses?

✅ **Features are generic**
- Không có tên activity cụ thể
- Chỉ dùng: difficulty, type, position, ...

✅ **Relative, not absolute**
- Completion rate (%), không phải count
- Module position (%), không phải module number

✅ **Transfer learning**
- Q-values học được patterns chung
- VD: "Nếu SV yếu (grade<0.5) + activity khó (diff>0.7) → Low reward"
- Pattern này đúng cho MỌI khóa học!

---

## 📚 SỬ DỤNG CƠ BẢN

### 1. Load Course Structure

#### Từ JSON

```python
from data.course_loader import CourseLoader

course = CourseLoader.from_json('examples/course_structure_example.json')
```

#### Từ Database

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='moodle',
    user='user',
    password='pass'
)

course = CourseLoader.from_database(conn, course_id=123)
```

### 2. Create Agent

```python
from core.qlearning_agent import QLearningAgent

agent = QLearningAgent(
    course_structure=course,
    learning_rate=0.1,      # Alpha
    discount_factor=0.95,   # Gamma
    epsilon=0.1             # Exploration rate
)
```

### 3. Training từ Historical Data

```python
from training.trainer import QLearningTrainer

trainer = QLearningTrainer(agent, course)

# Train từ database logs
trainer.train_from_logs(
    db_connection=conn,
    userids=[8609, 8670, 9043, ...],
    n_epochs=50
)

# Save model
agent.save('models/qlearning_model.pkl')
```

### 4. Inference (Recommendation)

```python
# Load student profile
from models.student_profile import StudentProfile

student = StudentProfile(
    student_id='student_999',
    course_id=course.course_id
)

# Add learning history
from models.student_profile import LearningHistory

student.add_activity_history(LearningHistory(
    activity_id='act_1_1',
    completed=True,
    grade=None,
    time_spent_minutes=18
))

# Get recommendation
recommendations = agent.recommend(student, top_k=3)

for rec in recommendations:
    print(f"{rec['activity_name']}: Q={rec['q_value']:.3f}")
```

**Output:**
```
Variables Quiz: Q=0.820
Practice Assignment: Q=0.785
Type Conversion Lab: Q=0.692
```

---

## 🔧 TÙY CHỈNH VÀ MỞ RỘNG

### 1. Custom State Builder

```python
from core.state_builder import AbstractStateBuilder
import numpy as np

class MyStateBuilder(AbstractStateBuilder):
    """Custom state với thêm features"""
    
    def build_state(self, student_profile, target_activity_id=None, 
                    current_timestamp=None):
        # Call parent
        base_state = super().build_state(
            student_profile, target_activity_id, current_timestamp
        )
        
        # Add custom features
        custom_features = [
            self._get_learning_pace(student_profile),
            self._get_quiz_performance(student_profile),
            # ... more features
        ]
        
        return np.concatenate([base_state, custom_features])
    
    def _get_learning_pace(self, student_profile):
        """Tính tốc độ học (activities/week)"""
        # Implementation
        return 0.5
    
    def get_state_dimension(self):
        return super().get_state_dimension() + 2  # +2 custom features
```

### 2. Custom Reward Function

```python
from core.reward_calculator import RewardCalculator

class MyRewardCalculator(RewardCalculator):
    """Custom reward với business rules riêng"""
    
    def calculate_reward(self, student_profile, action_id, outcome):
        reward = 0.0
        
        # Custom rule 1: Bonus for completing on time
        activity = self.course_structure.activities[action_id]
        if outcome.time_spent_minutes <= activity.estimated_minutes * 1.1:
            reward += 0.2
        
        # Custom rule 2: Penalty for skipping optional activities
        if activity.is_optional and not outcome.completed:
            reward -= 0.1
        
        # ... more rules
        
        return np.clip(reward, -1.0, 1.0)
```

### 3. Plugin Architecture

```python
# Sử dụng custom components
agent = QLearningAgent(
    course_structure=course,
    state_builder=MyStateBuilder(course),
    reward_calculator=MyRewardCalculator(course)
)
```

---

## 💡 BEST PRACTICES

### 1. Training

✅ **DO:**
- Split data: 80% train, 20% validation
- Train với nhiều epochs (50-100)
- Monitor reward progression
- Decay epsilon theo thời gian (exploration → exploitation)

❌ **DON'T:**
- Train trên ít sinh viên (<20)
- Overfit bằng cách train quá nhiều epochs
- Ignore terminal states

### 2. State Design

✅ **DO:**
- Normalize tất cả features về [0, 1]
- Dùng relative values (%, ratios)
- Include temporal features (time_since_last)

❌ **DON'T:**
- Hard-code activity IDs
- Use absolute values (counts without normalization)
- Create too many features (>30) → sparse Q-table

### 3. Reward Shaping

✅ **DO:**
- Balance positive và negative rewards
- Clip rewards về [-1, 1]
- Include domain knowledge

❌ **DON'T:**
- Give rewards quá lớn (>10) → unstable
- Ignore intermediate outcomes
- Reward chỉ dựa trên final grade

### 4. Deployment

✅ **DO:**
- Load model 1 lần, cache trong memory
- Validate prerequisites trước khi recommend
- Log all recommendations for analysis

❌ **DON'T:**
- Reload model mỗi request
- Recommend activities với prerequisites chưa hoàn thành
- Deploy without A/B testing

---

## 📊 VALIDATION

### Metrics to track

```python
# 1. Q-value statistics
stats = agent.get_statistics()
print(f"Mean Q-value: {stats['q_value_stats']['mean']:.3f}")

# 2. Recommendation diversity
recommendations = [agent.recommend(student) for student in test_students]
unique_actions = len(set(r[0]['activity_id'] for r in recommendations))

# 3. Success rate (nếu có ground truth)
correct = sum(
    1 for r, gt in zip(recommendations, ground_truth)
    if r[0]['activity_id'] == gt
)
accuracy = correct / len(ground_truth)
```

---

## 🚀 NEXT STEPS

1. ✅ Train model trên dữ liệu thật (15 sinh viên)
2. ✅ Load `cluster_full_statistics.json` làm benchmarks
3. ✅ Integrate với web service (REST API)
4. ✅ A/B testing: Q-Learning vs Random vs Rule-based
5. ✅ Monitor performance và retrain định kỳ

---

## 📞 SUPPORT

Có vấn đề? Check:
- `README.md` - Overview
- `examples/quick_demo.py` - Demo code
- `examples/course_structure_example.json` - Schema
- Unit tests trong `tests/`

**Happy Learning! 🎓**
