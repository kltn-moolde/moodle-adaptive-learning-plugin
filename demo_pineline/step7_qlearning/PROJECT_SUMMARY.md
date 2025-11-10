# 🎓 Q-LEARNING ADAPTIVE LEARNING SYSTEM - TỔNG HỢP DỰ ÁN

## 📌 TỔNG QUAN

Hệ thống gợi ý lộ trình học tập thích ứng sử dụng **Q-Learning**, huấn luyện từ dữ liệu mô phỏng hành vi học sinh, phân cụm theo năng lực học tập.

**Mục tiêu**: Với state hiện tại của học sinh (cụm, module, tiến độ, điểm số, hành động gần nhất, stuck), hệ thống gợi ý **top-K actions** tối ưu để học tiếp.

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### **Pipeline Tổng Thể**

```
┌─────────────────────┐
│ 1. CLUSTER STUDENTS │ → Phân cụm học sinh
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 2. SIMULATE DATA    │ → Mô phỏng trajectories
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 3. TRAIN Q-LEARNING │ → Học Q-table
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 4. API SERVICE      │ → Gợi ý qua REST API
└─────────────────────┘
```

### **Components Chi Tiết**

```
core/
├── state_builder_v2.py      # Xây dựng state 6D
├── action_space.py           # Quản lý 37 actions
├── reward_calculator_v2.py   # Tính reward theo cluster
├── qlearning_agent_v2.py     # Q-Learning agent
├── simulator_v2.py           # Mô phỏng hành vi học sinh
└── student_context.py        # Track context học sinh

services/
├── model_loader.py           # Load model & components
├── cluster_service.py        # Dự đoán cluster
└── recommendation_service.py # Gợi ý actions

api_service.py                # FastAPI REST API
train_qlearning_redesigned.py # Training script
```

---

## 📊 STATE REPRESENTATION (6 CHIỀU)

### **Định Nghĩa State**

State vector **S = [cluster_id, module, progress, score, recent_action, stuck]**

| Dimension | Tên | Giá trị | Ý nghĩa |
|-----------|-----|---------|---------|
| **0** | `cluster_id` | 0-4 | Cụm học sinh (weak/medium/strong) |
| **1** | `current_module` | 0-36 | Module đang học (index) |
| **2** | `module_progress` | 0.25/0.5/0.75/1.0 | Tiến độ module (quartiles) |
| **3** | `avg_score` | 0.25/0.5/0.75/1.0 | Điểm TB (quartiles) |
| **4** | `recent_action` | 0-5 | Hành động gần nhất |
| **5** | `is_stuck` | 0/1 | Có bị stuck không |

### **Action Type Mapping**

```python
ACTION_TYPES = {
    'watch_video': 0,      # Xem video bài giảng
    'do_quiz': 1,          # Làm bài quiz
    'mod_forum': 2,        # Tham gia forum thảo luận
    'review_quiz': 3,      # Xem lại kết quả quiz
    'read_resource': 4,    # Đọc tài liệu
    'do_assignment': 5     # Làm bài tập lớn
}
```

### **Stuck Detection Rules**

Học sinh bị coi là **stuck** (is_stuck = 1) khi:

1. **Quá nhiều lần thử**: `quiz_attempts > 3`
2. **Mất quá nhiều thời gian**: `time_on_module > 2 × median_time`
3. **Điểm số liên tục thấp**: `avg(recent_scores) < 0.5` (với ≥2 điểm)

### **Ví Dụ State**

```python
state = [4, 5, 1.0, 1.0, 3, 0]
# Giải thích:
# - cluster_id=4 → Strong cluster (học sinh giỏi)
# - module=5 → Đang học module index 5
# - progress=1.0 → Đã hoàn thành 100% module
# - score=1.0 → Điểm TB 100%
# - recent_action=3 → Vừa review_quiz
# - stuck=0 → Không bị stuck
```

### **State Space Size**

```python
Total states = 5 clusters × 37 modules × 4 progress × 4 scores × 6 actions × 2 stuck
             = 35,520 possible states
```

**Thực tế**: Chỉ ~22% states xuất hiện trong training (7,779/34,560)

---

## 🎯 ACTION SPACE (37 ACTIONS)

### **Action Structure**

```python
{
    'id': 46,                    # Module ID từ Moodle
    'name': 'Video bài giảng 1', # Tên hoạt động
    'type': 'watch_video',       # Loại action
    'section': 'Tuần 1',         # Phần khóa học
    'purpose': 'content'         # Mục đích
}
```

### **Phân Loại Actions**

| Loại | Số lượng | Ví dụ Module IDs |
|------|----------|------------------|
| **watch_video** | 8 | 46, 58, 66, 74... |
| **do_quiz** | 15 | 47, 59, 67, 75... |
| **read_resource** | 10 | 49, 61, 69, 77... |
| **do_assignment** | 4 | 55, 80, 81, 82 |

### **Dual ID System**

- **Action Index** (0-36): Dùng trong array/list
- **Module ID** (46-82): ID thực từ Moodle

**Mapping quan trọng**:
```python
# API → Q-table: Convert index to module ID
module_ids = [action_space.get_action_by_index(i).id for i in indices]

# Q-table → API: Convert module ID back to index
action_idx = action_space.get_action_by_id(module_id).index
```

---

## 💰 REWARD CALCULATOR (10 COMPONENTS)

### **Cluster Classification**

```python
CLUSTER_THRESHOLDS = {
    'weak': (0.0, 0.6),      # avg_grade < 0.6
    'medium': (0.6, 0.8),    # 0.6 ≤ avg_grade < 0.8
    'strong': (0.8, 1.0)     # avg_grade ≥ 0.8
}
```

**Cluster mapping**:
- Cluster 0 (0.411) → weak
- Cluster 1 (0.812) → medium
- Cluster 2 (0.854) → strong
- Cluster 4 (0.875) → strong
- Cluster 5 (0.658) → medium

### **Reward Components**

#### **1. Base Score Reward** (×10-20)
```python
if outcome['score'] >= 0.7:
    reward += outcome['score'] * scale
    # scale: weak=10, medium=15, strong=20
```

#### **2. Progress Reward** (+5/+10)
```python
if outcome['completed']:
    reward += {weak: 5, medium: 7, strong: 10}
```

#### **3. Stuck State Penalty** (-5/-10/-15)
```python
if is_stuck == 1:
    reward -= {weak: 5, medium: 10, strong: 15}
```

#### **4. Challenge Bonus** (+3/+6/+10)
```python
if success and action_difficulty == 'hard':
    reward += {weak: 10, medium: 6, strong: 3}
```

#### **5. Time Efficiency** (+3, strong only)
```python
if cluster == 'strong' and time < expected_time * 0.8:
    reward += 3.0
```

#### **6. High Score Bonus** (+3/+5/+7)
```python
if score >= 0.9:
    reward += {weak: 7, medium: 5, strong: 3}
```

#### **7. Repetition Penalty** (-2/-3/-5)
```python
if same_action_twice:
    reward -= {weak: 2, medium: 3, strong: 5}
```

#### **8. Action Diversity Bonus** (+0.5/+1.0/+1.5)
```python
if recent_action != current_action_type:
    reward += {weak: 0.5, medium: 1.0, strong: 1.5}
```

#### **9. Beneficial Sequence Logic** (+0.7 to +2.6)
```python
BENEFICIAL_SEQUENCES = {
    (read_resource, quiz): 2.0,      # Đọc → làm quiz
    (watch_video, quiz): 1.5,        # Video → quiz
    (quiz, review_quiz): 1.0,        # Quiz → xem lại
    (read_resource, assignment): 1.5,
    (watch_video, assignment): 1.5,
    (forum, quiz): 1.0
}
# Scaled by cluster: weak×0.7, medium×1.0, strong×1.3
```

#### **10. Repetition Penalty (3x)** (-0.5 to -2.5)
```python
if same_action_3_times_in_row:
    reward -= {weak: 0.5, medium: 1.5, strong: 2.5}
```

### **Reward Range**

- **Minimum**: ~-20 (stuck + low score + repetition)
- **Maximum**: ~+40 (perfect score + sequence + diversity + challenge)
- **Typical**: +10 to +25 (normal learning progress)

---

## 🤖 Q-LEARNING AGENT

### **Algorithm**

**Q-Learning Update Rule**:
```python
Q(s, a) ← Q(s, a) + α × [r + γ × max Q(s', a') - Q(s, a)]
```

- **α (learning_rate)**: 0.1 (cluster-adaptive)
- **γ (discount_factor)**: 0.95
- **ε (epsilon)**: 0.3 → 0.01 (ε-greedy exploration)

### **Training Process**

```python
# 1. Load trajectories
trajectories = load_trajectories('data/simulated_trajectories_best.json')

# 2. Initialize agent
agent = QLearningAgentV2(
    n_actions=37,
    learning_rate=0.1,
    discount_factor=0.95,
    epsilon=0.3,
    cluster_adaptive=True
)

# 3. Train
agent.train(
    trajectories=trajectories,
    n_episodes=10000,
    verbose=True
)

# 4. Save Q-table
agent.save_qtable('models/qtable_best.pkl')
```

### **Training Results**

```
Episodes trained: 10,000
Total Q-updates: 1,415,430
Final epsilon: 0.01
Q-table size: 7,779 states
State coverage: 22.51% (7779/34560)
Training time: ~45 minutes
```

### **Q-Table Structure**

```python
q_table = {
    (4, 5, 1.0, 1.0, 3, 0): {  # State tuple
        46: 64.33,              # Module ID → Q-value
        47: 48.94,
        49: 52.11,
        ...
    },
    ...
}
```

**Q-value Range**:
- Min: 0.0 (unexplored state-action)
- Max: 91.0 (highly rewarding path)
- Avg: ~30-50 (typical learned values)

---

## 🔄 SIMULATION (Data Generation)

### **Simulator Flow**

```
For each student (ID, cluster):
  1. Initialize state = [cluster, 0, 0.25, 0.5, 4, 0]
  2. Loop (max 100 steps):
     a. Agent picks action (ε-greedy)
     b. Simulate outcome (score, time, completed)
     c. Calculate reward
     d. Update state
     e. Record transition (s, a, r, s')
     f. If all modules done → break
  3. Save trajectory
```

### **Student Behavior Model**

```python
# Success probability
success_prob = ability * (1 - difficulty) + current_score * 0.3

# Outcome simulation
if random() < success_prob:
    score = random(0.7, 1.0)
    time = expected_time * random(0.8, 1.2)
else:
    score = random(0.3, 0.6)
    time = expected_time * random(1.2, 2.0)
```

### **Cluster Parameters**

| Cluster | Level | Ability | Engagement | Avg Grade |
|---------|-------|---------|------------|-----------|
| 0 | Weak | 0.45 | 0.5 | 0.411 |
| 1 | Medium | 0.75 | 0.8 | 0.812 |
| 2 | Strong | 0.90 | 0.95 | 0.854 |
| 4 | Strong | 0.92 | 0.98 | 0.875 |
| 5 | Medium | 0.65 | 0.7 | 0.658 |

### **Generated Data Stats**

```
Total students: 400 (80 per cluster × 5 clusters)
Total transitions: 44,285
Avg trajectory length: 110.7 steps
Unique states: 7,779
Coverage: 22.51%
File: data/simulated_trajectories_best.json (9.8 MB)
```

---

## 🌐 API SERVICE

### **Endpoints**

#### **1. Health Check**
```http
GET /api/health

Response:
{
  "status": "healthy",
  "model_loaded": true,
  "n_states_in_qtable": 7779
}
```

#### **2. Model Info**
```http
GET /api/model-info

Response:
{
  "model_version": "V2",
  "episodes_trained": 10000,
  "total_updates": 1415430,
  "q_table_size": 7779,
  "n_actions": 37,
  "n_clusters": 5,
  "final_epsilon": 0.01
}
```

#### **3. Recommend** (Main API)
```http
POST /api/recommend

Request (Option 1 - Gửi state trực tiếp):
{
  "student_id": "SV001",
  "state": [4, 5, 1.0, 1.0, 3, 0],
  "top_k": 3
}

Request (Option 2 - Gửi features, API tự build state):
{
  "student_id": "SV001",
  "features": {
    "avg_grade": 0.875,
    "completion_rate": 0.95,
    "quiz_scores": [0.8, 0.9, 0.85]
  },
  "top_k": 3
}

Response:
{
  "success": true,
  "student_id": "SV001",
  "cluster_id": 4,
  "cluster_name": "Strong learner",
  "state_vector": [4, 5, 1.0, 1.0, 3, 0],
  "state_description": {
    "cluster": "Strong",
    "module": "Module 5",
    "progress": "100%",
    "score": "100%",
    "recent_action": "review_quiz",
    "stuck": false
  },
  "recommendations": [
    {
      "rank": 1,
      "action_id": 46,
      "action_index": 0,
      "name": "Video bài giảng tiếp theo",
      "type": "watch_video",
      "q_value": 64.33,
      "section": "Tuần 2"
    },
    {
      "rank": 2,
      "action_id": 49,
      "action_index": 3,
      "name": "Đọc tài liệu",
      "type": "read_resource",
      "q_value": 52.11,
      "section": "Tuần 2"
    },
    {
      "rank": 3,
      "action_id": 47,
      "action_index": 1,
      "name": "Quiz kiểm tra",
      "type": "do_quiz",
      "q_value": 48.94,
      "section": "Tuần 2"
    }
  ],
  "model_info": {
    "model_version": "V2",
    "n_states_in_qtable": 7779
  }
}
```

---

## 📂 INPUT/OUTPUT FILES

### **Input Data**

#### **1. Course Structure** (`data/course_structure.json`)
```json
{
  "id": 2,
  "fullname": "Lập trình Web",
  "contents": [
    {
      "id": 7,
      "name": "Tuần 1",
      "modules": [
        {
          "id": 46,
          "name": "Video bài giảng 1",
          "modname": "hvp",
          "visible": 1,
          "uservisible": true
        }
      ]
    }
  ]
}
```

#### **2. Cluster Profiles** (`data/cluster_profiles.json`)
```json
{
  "n_clusters": 6,
  "cluster_stats": {
    "0": {
      "avg_grade": 0.411,
      "student_count": 145
    },
    "1": {
      "avg_grade": 0.812,
      "student_count": 203
    }
  }
}
```

#### **3. Simulated Trajectories** (`data/simulated_trajectories_best.json`)
```json
{
  "1000": [
    {
      "state": [0, 0, 0.25, 0.5, 4, 0],
      "action": 46,
      "reward": 12.5,
      "next_state": [0, 0, 0.5, 0.6, 0, 0],
      "is_terminal": false,
      "timestamp": "2024-01-01T10:00:00",
      "module_id": 46
    }
  ]
}
```

### **Output Models**

#### **1. Q-Table Model** (`models/qtable_best.pkl`)
```python
{
    'q_table': {
        (4, 5, 1.0, 1.0, 3, 0): {46: 64.33, 47: 48.94, ...},
        ...
    },
    'config': {
        'n_actions': 37,
        'learning_rate': 0.1,
        'discount_factor': 0.95
    },
    'stats': {
        'episodes_trained': 10000,
        'total_updates': 1415430,
        'final_epsilon': 0.01,
        'q_table_size': 7779
    }
}
```

---

## 🚀 CÁCH SỬ DỤNG

### **1. Setup Environment**

```bash
# Clone repo
cd step7_qlearning

# Install dependencies
pip install -r requirements.txt
```

### **2. Generate Training Data**

```bash
# Mô phỏng 400 học sinh (80/cluster × 5 clusters)
python3 generate_large_simulation_data.py --preset production

# Output: data/simulated_trajectories_best.json
```

### **3. Train Q-Learning Model**

```bash
# Train với 10,000 episodes
python3 train_qlearning_redesigned.py

# Output: models/qtable_best.pkl
# Training time: ~45 minutes
```

### **4. Start API Server**

```bash
# Start FastAPI server
uvicorn api_service:app --reload --port 8080

# Server running at: http://localhost:8080
# API docs: http://localhost:8080/docs
```

### **5. Test API**

```bash
# Test với state vector
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "SV001",
    "state": [4, 5, 1.0, 1.0, 3, 0],
    "top_k": 3
  }'

# Hoặc test với Python
python3 test_qtable_api.py
```

---

## 📊 KẾT QUẢ & ĐÁNH GIÁ

### **Model Performance**

| Metric | Value |
|--------|-------|
| **Q-table Coverage** | 22.51% (7,779/34,560 states) |
| **Avg Actions/State** | 1.95 actions |
| **States with Q>0** | 2,847 states (36.6%) |
| **Max Q-value** | 91.0 |
| **Training Episodes** | 10,000 |
| **Convergence** | ε: 0.3 → 0.01 |

### **Top 5 Most Valuable States**

```python
State (4, 22, 1.0, 1.0, 3, 0):
  Max Q-value: 91.0
  Actions learned: 37
  Interpretation: Strong student, module 22, 100% progress/score

State (2, 34, 0.75, 1.0, 0, 0):
  Max Q-value: 88.5
  Actions learned: 35
```

### **Recommendation Quality**

**Test Case**: Strong student (cluster 4), 100% progress
```
Input state: [4, 5, 1.0, 1.0, 3, 0]

Top-3 Recommendations:
1. watch_video (Q=64.33) - Học nội dung mới
2. read_resource (Q=52.11) - Đọc tài liệu
3. do_quiz (Q=48.94) - Kiểm tra hiểu biết

✓ Logic: Video → Reading → Quiz (beneficial sequence)
✓ Diversity: 3 loại action khác nhau
✓ No repetition: Không trùng recent_action
```

### **API Performance**

- **Latency**: ~50-100ms/request
- **Throughput**: ~100 requests/second
- **Model size**: 2.8 MB (qtable_best.pkl)
- **Memory usage**: ~150 MB (loaded in RAM)

---

## 🐛 CRITICAL BUGS FIXED

### **Bug 1: Q-value Always 0.0**

**Vấn đề**: Recommendations trả về q_value=0.0 dù state có max_q=91.0

**Nguyên nhân**: 
- Q-table dùng **module IDs** (46, 47...) làm keys
- Code gửi **action indices** (0, 1, 2...) → `q_table.get(0)` = None

**Giải pháp**:
```python
# OLD (broken)
q_values = {idx: agent.q_table[state].get(idx, 0) for idx in [0,1,2...]}

# NEW (fixed)
module_ids = [action_space.get_action_by_index(i).id for i in [0,1,2...]]
q_values = {mid: agent.q_table[state].get(mid, 0) for mid in module_ids}
```

### **Bug 2: max(q_values) Wrong**

**Vấn đề**: `max(q_values)` trả về max KEY thay vì max VALUE

**Giải pháp**:
```python
# OLD: max(q_values) → max KEY (e.g., 91 if module_id=91)
# NEW: max(q_values.values()) → max Q-VALUE
```

---

## 📚 TÀI LIỆU THAM KHẢO

### **File Documents Quan Trọng**

1. **API_INPUT_CURRENT.md** - Format API input hiện tại
2. **QTABLE_API_DOCS.md** - Tài liệu API chi tiết
3. **TRAINING_SUCCESS_REPORT.md** - Báo cáo kết quả training
4. **ENHANCED_SIMULATOR_DOCS.md** - Hướng dẫn simulator

### **Core Modules**

- `core/qlearning_agent_v2.py` (539 lines) - Q-Learning algorithm
- `core/state_builder_v2.py` (404 lines) - State representation
- `core/reward_calculator_v2.py` (440 lines) - Reward function
- `core/simulator_v2.py` (1000+ lines) - Student simulator

### **Training & Deployment**

- `train_qlearning_redesigned.py` - Training script
- `api_service.py` - FastAPI server
- `generate_large_simulation_data.py` - Data generation

---

## 🔮 FUTURE IMPROVEMENTS

1. **Multi-objective Rewards**: Cân bằng completion rate vs retention
2. **Transfer Learning**: Học từ cluster này sang cluster khác
3. **Online Learning**: Cập nhật Q-table real-time từ user feedback
4. **Deep Q-Network**: Thay Q-table bằng neural network
5. **Personalization**: Học riêng cho từng học sinh (không chỉ cluster)

---

## 📞 SUPPORT

**Author**: Q-Learning V2 Team  
**Version**: 2.0  
**Last Updated**: November 2025

**Quick Commands**:
```bash
# Generate data
python3 generate_large_simulation_data.py --preset production

# Train model
python3 train_qlearning_redesigned.py

# Start server
uvicorn api_service:app --reload --port 8080

# Test API
python3 test_qtable_api.py
```

---

**🎯 TÓM TẮT**: Hệ thống Q-Learning hoàn chỉnh với 7,779 states đã học, 10 reward components thông minh, API REST nhanh (~100ms), và khả năng gợi ý actions tối ưu dựa trên cluster + state hiện tại của học sinh! 🚀
