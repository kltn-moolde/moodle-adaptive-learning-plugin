# 📖 Usage Guide

## 📋 Mục lục

1. [API Usage](#api-usage)
2. [Training Guide](#training-guide)
3. [Simulation Guide](#simulation-guide)
4. [Examples](#examples)

---

## 📡 API Usage

### Start Server

```bash
# Development
uvicorn api_service:app --reload --port 8080

# Production
uvicorn api_service:app --host 0.0.0.0 --port 8080 --workers 4
```

### Endpoints

#### 1. Health Check
```bash
curl http://localhost:8080/api/health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "n_actions": 15,
  "n_states_in_qtable": 7779
}
```

#### 2. Get Recommendations

**Request với LO mastery (recommended)**:
```bash
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 123,
    "features": {
      "cluster_id": 2,
      "current_module_id": 67,
      "module_progress": 0.75,
      "avg_score": 0.85,
      "recent_action_type": 1
    },
    "lo_mastery": {
      "LO1.1": 0.4,
      "LO1.2": 0.35,
      "LO2.2": 0.25,
      "LO2.4": 0.4
    },
    "top_k": 3
  }'
```

**Request không có LO mastery**:
```bash
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 456,
    "features": {
      "cluster_id": 0,
      "current_module_id": 65,
      "module_progress": 0.5,
      "avg_score": 0.6,
      "recent_action_type": 0
    },
    "top_k": 5
  }'
```

**Input Validation**:
- **Required fields**: `current_module_id`, `module_progress`, `avg_score`
- **Optional fields**: `cluster_id` (0-4), `recent_action_type` (0-5)
- **Validation rules**:
  - `cluster_id`: int, range 0-4
  - `current_module_id`: int, phải là module ID hợp lệ
  - `module_progress`: float, range [0.0, 1.0]
  - `avg_score`: float, range [0.0, 1.0]
  - `recent_action_type`: int, range 0-5 (0=view_content, 1=submit_quiz, 2=post_forum, 3=review_quiz, 4=read_resource, 5=submit_assignment)
- **Invalid values**: API trả về lỗi 400 với message rõ ràng
- **Unused fields**: Cảnh báo và bị bỏ qua (như `is_stuck`, `quiz_attempts`, etc.)

**Response:**
```json
{
  "success": true,
  "student_id": 123,
  "cluster_id": 2,
  "cluster_name": "Medium",
  "state_vector": [2.0, 0.0, 0.75, 1.0, 1.0, 0.0],
  "state_description": {
    "cluster_id": 2,
    "cluster_name": "Medium",
    "module_index": 2,
    "progress_label": "75%",
    "score_label": "100%",
    "state_format": "6D"
  },
  "recommendations": [
    {
      "action_id": 2,
      "action_type": "attempt_quiz",
      "time_context": "past",
      "module_name": "attempt_quiz (past)",
      "q_value": 42.182,
      "activity_id": 63,
      "activity_name": "bài kiểm tra bài 2 - medium",
      "target_los": [["LO1.5", 0.4]],
      "explanation": "Cải thiện LO1.5 (hiện tại 40.0%) → dự kiến tăng 5.0% (lên 45.0%): Đánh giá kiến thức ứng dụng AI qua các bài kiểm tra ở các mứ... | Độ khó: trung bình",
      "alternatives": []
    }
  ],
  "model_info": {
    "model_version": "V2",
    "n_states_in_qtable": 7779
  }
}
```

#### 3. Get Model Info
```bash
curl http://localhost:8080/api/model-info
```

#### 4. Get Top Positive States
```bash
curl "http://localhost:8080/api/qtable/states/positive?top_n=10"
```

### Python Client Example

```python
import requests

url = "http://localhost:8080/api/recommend"
payload = {
    "student_id": 123,
    "features": {
        "cluster_id": 2,
        "current_module_id": 67,
        "module_progress": 0.75,
        "avg_score": 0.85,
        "recent_action_type": 1
    },
    "lo_mastery": {
        "LO1.1": 0.4,
        "LO1.2": 0.35,
        "LO2.2": 0.25,
        "LO2.4": 0.4
    },
    "top_k": 5
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Cluster: {data['cluster_name']} (ID: {data['cluster_id']})")
print(f"State: {data['state_vector']}")

for i, rec in enumerate(data["recommendations"], 1):
    print(f"\n{i}. {rec['module_name']} (Q={rec['q_value']:.3f})")
    print(f"   Activity: {rec.get('activity_name', 'N/A')} (ID: {rec.get('activity_id', 'N/A')})")
    print(f"   Explanation: {rec.get('explanation', 'N/A')}")
    if rec.get('target_los'):
        print(f"   Target LOs: {rec['target_los']}")
```

---

## 🎓 Training Guide

### Basic Training

```bash
# Training cơ bản
python3 train_qlearning.py \
    --episodes 100 \
    --students 5 \
    --steps 30 \
    --output models/qtable.pkl
```

### Training với Detailed Logging

```bash
# Enable detailed logging để track state transitions
python3 train_qlearning.py \
    --episodes 100 \
    --students 5 \
    --steps 30 \
    --detailed-logging \
    --log-interval 10
```

**Output:**
- Q-table: `models/qtable.pkl`
- Training logs: `data/simulated/training_logs_episode_{N}.json`

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--episodes` | 100 | Number of training episodes |
| `--students` | 5 | Students per cluster |
| `--steps` | 30 | Steps per episode |
| `--output` | `models/qtable.pkl` | Output Q-table path |
| `--detailed-logging` | False | Enable detailed state transition logging |
| `--log-interval` | 10 | Log every N episodes |
| `--log-output` | None | Custom log output path pattern |
| `--quiet` | False | Disable verbose output |

### Training Output

```
Episode 10/100
  Avg reward: 85.3
  Epsilon: 0.951
  Q-table states: 1,200
  Total updates: 4,500
  Avg LO mastery: 0.523
  ✓ Detailed logs saved to data/simulated/training_logs_episode_10.json
```

### Training Log Format

Mỗi log file chứa:
- **Transitions**: Chi tiết từng state transition
- **Statistics**: Exploration rate, reward stats, etc.

```json
{
  "transitions": [
    {
      "step": 1,
      "state": {...},
      "action": {...},
      "q_values": {...},
      "reward": {
        "total": 5.23,
        "breakdown": {
          "completion": 5.0,
          "score_improvement": 1.5,
          "lo_mastery_improvement": 0.23
        }
      },
      "lo_analysis": {...},
      "midterm_prediction": {...}
    }
  ],
  "statistics": {...}
}
```

---

## 🎬 Simulation Guide

### Basic Simulation

```bash
# Simulate với trained model
python3 simulate_learning_path.py \
    --qtable models/qtable_best.pkl \
    --students 3 \
    --steps 30 \
    --output data/simulated/simulation.json
```

### Verbose Simulation

```bash
# Xem chi tiết từng step
python3 simulate_learning_path.py \
    --qtable models/qtable_best.pkl \
    --students 1 \
    --steps 10 \
    --verbose
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--qtable` | `models/qtable_best.pkl` | Path to trained Q-table |
| `--output` | `data/simulated/learning_path_simulation.json` | Output JSON path |
| `--students` | 3 | Number of students per cluster |
| `--steps` | 30 | Number of learning steps per student |
| `--clusters` | `weak medium strong` | Clusters to simulate |
| `--verbose` | False | Print detailed logs |
| `--no-save` | False | Do not save logs to JSON |

### Simulation Output

Mỗi simulation tạo file JSON với:
- **Simulation metadata**: Total students, avg reward, avg midterm
- **Per-student results**: 
  - State transitions chi tiết
  - LO summary và comparison
  - Midterm predictions
  - Statistics

### Example Output

```
Step 1 | Student 1000 (weak)
State: weak | Module module_0 | Progress 25% | Score 50%
       Phase: active | Engagement: medium

→ Action Selected: submit_quiz
  Activity: Quiz tuần 1 (ID: 67)
  Mode: ✅ EXPLOITATION
  Q-value: 2.45

📚 Weak LOs Considered (3):
  - LO1.1: mastery=0.45, weight=0.10
  - LO1.2: mastery=0.50, weight=0.15

📈 LO Mastery Changes:
  - LO1.1: +0.05
  - LO1.2: +0.03

💰 Reward: 5.23
  Breakdown:
    - completion: 5.00
    - score_improvement: 1.50
    - lo_mastery_improvement: 0.23

🎯 Midterm Prediction: 12.5/20 (62.5%)
  Potential improvement: +3.2 points
```

---

## 💡 Examples

### Example 1: Complete Training Workflow

```bash
# 1. Train model với logging
python3 train_qlearning.py \
    --episodes 200 \
    --students 5 \
    --steps 30 \
    --detailed-logging \
    --log-interval 20 \
    --output models/qtable_new.pkl

# 2. Simulate để kiểm tra
python3 simulate_learning_path.py \
    --qtable models/qtable_new.pkl \
    --students 3 \
    --steps 20 \
    --verbose

# 3. Start API server
uvicorn api_service:app --reload --port 8080
```

### Example 2: Python Integration

```python
from core.learning_path_simulator import LearningPathSimulator
from core.lo_mastery_tracker import LOMasteryTracker

# Initialize simulator
simulator = LearningPathSimulator(
    qtable_path='models/qtable_best.pkl',
    verbose=True
)

# Simulate single student
result = simulator.simulate_student(
    student_id=1001,
    cluster='weak',
    n_steps=30
)

# Get LO summary
lo_summary = result['lo_summary']
print(f"Predicted midterm: {lo_summary['midterm_prediction']['predicted_score']}/20")

# Get weak LOs
weak_los = lo_summary['weak_los']
for lo in weak_los:
    print(f"{lo['lo_id']}: mastery={lo['mastery']:.2f}, weight={lo['weight']:.2f}")
```

### Example 3: LO Mastery Tracking

```python
from core.lo_mastery_tracker import LOMasteryTracker

tracker = LOMasteryTracker()

# Initialize student
tracker.initialize_student(1001)

# Update mastery after activity
tracker.update_mastery(
    student_id=1001,
    lo_id='LO1.1',
    new_mastery=0.75,
    activity_id=54,
    timestamp=1
)

# Get weak LOs
weak_los = tracker.get_weak_los(1001, threshold=0.6)
print(f"Weak LOs: {len(weak_los)}")

# Predict midterm
prediction = tracker.predict_midterm_score(1001)
print(f"Predicted: {prediction['predicted_score']:.1f}/20")
print(f"Potential: {prediction['potential_score']:.1f}/20")

# Compare LOs
comparison = tracker.compare_los(1001)
print(f"Excellent: {comparison['statistics']['excellent_count']}")
print(f"Weak: {comparison['statistics']['weak_count']}")
```

### Example 4: API Integration với Moodle

```python
import requests

def get_recommendations_for_student(student_data, lo_mastery=None):
    """Get recommendations from API với activity details"""
    url = "http://localhost:8080/api/recommend"
    
    payload = {
        "student_id": student_data['id'],
        "features": {
            "cluster_id": student_data['cluster_id'],
            "current_module_id": student_data['current_module_id'],
            "module_progress": student_data['module_progress'],
            "avg_score": student_data['avg_score'],
            "recent_action_type": student_data['recent_action_type']
        },
        "top_k": 5
    }
    
    # Thêm LO mastery nếu có
    if lo_mastery:
        payload['lo_mastery'] = lo_mastery
    
    response = requests.post(url, json=payload)
    return response.json()

# Usage
student = {
    'id': 123,
    'cluster_id': 2,
    'current_module_id': 67,
    'module_progress': 0.75,
    'avg_score': 0.85,
    'recent_action_type': 1
}

# LO mastery từ Moodle
lo_mastery = {
    'LO1.1': 0.4,
    'LO1.2': 0.35,
    'LO2.2': 0.25,
    'LO2.4': 0.4
}

result = get_recommendations_for_student(student, lo_mastery)
print(f"Cluster: {result['cluster_name']}")

for rec in result['recommendations']:
    print(f"\n→ {rec['module_name']} (Q={rec['q_value']:.3f})")
    print(f"  📚 Activity: {rec.get('activity_name', 'N/A')}")
    print(f"  💡 {rec.get('explanation', 'N/A')}")
```

---

## 🔍 Debugging

### Check Q-table Coverage

```python
from services.model_loader import ModelLoader

loader = ModelLoader('models/qtable_best.pkl')
agent = loader.agent

stats = agent.get_statistics()
print(f"Q-table size: {stats['q_table_size']} states")
print(f"Total updates: {stats['total_updates']}")
```

### Analyze State Transitions

```python
import json

# Load training log
with open('data/simulated/training_logs_episode_10.json') as f:
    log = json.load(f)

# Analyze transitions
transitions = log['transitions']
print(f"Total transitions: {len(transitions)}")

# Count exploration vs exploitation
explore_count = sum(1 for t in transitions if t['action']['is_exploration'])
exploit_count = len(transitions) - explore_count
print(f"Exploration: {explore_count}, Exploitation: {exploit_count}")

# Average reward
avg_reward = sum(t['reward']['total'] for t in transitions) / len(transitions)
print(f"Average reward: {avg_reward:.2f}")
```

### Check LO Mastery Updates

```python
from core.lo_mastery_tracker import LOMasteryTracker

tracker = LOMasteryTracker()

# Get mastery history
history = tracker.get_mastery_history(1001)
for entry in history[-5:]:  # Last 5 updates
    print(f"{entry['lo_id']}: {entry['old_mastery']:.2f} → {entry['new_mastery']:.2f} "
          f"(Δ={entry['delta']:+.3f})")
```

---

## 📊 Performance Tips

### Training
- **Episodes**: 100-1000 tùy vào độ phức tạp
- **Students**: 3-5 per cluster là đủ
- **Steps**: 20-50 steps per episode
- **Logging**: Chỉ enable khi cần debug (overhead ~10-15%)

### Simulation
- **Students**: 1-3 để test nhanh, 5-10 để analysis
- **Steps**: 20-30 để quick test, 50+ để detailed analysis
- **Verbose**: Chỉ bật khi cần xem chi tiết

### API
- **Response time**: < 50ms với Q-table 7,779 states
- **Concurrent**: Supports multiple requests
- **Caching**: Model loader sử dụng singleton pattern

---

## 🐛 Troubleshooting

### Issue: Q-table not found
```bash
# Train model first
python3 train_qlearning.py --episodes 100
```

### Issue: Missing data files
```bash
# Check required files
ls data/course_structure.json
ls data/cluster_profiles.json
ls data/Po_Lo.json
ls data/midterm_lo_weights.json
```

### Issue: Low Q-values
```bash
# Retrain with more episodes
python3 train_qlearning.py --episodes 500
```

### Issue: Memory error during training
```bash
# Reduce students or steps
python3 train_qlearning.py --students 2 --steps 20
```

---

For architecture details, see **ARCHITECTURE.md**  
For quick start, see **README.md**

