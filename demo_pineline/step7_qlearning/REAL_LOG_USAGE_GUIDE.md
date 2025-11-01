# Hướng Dẫn Sử Dụng: Train Q-Learning từ Log Thô Moodle

## 📋 Tổng Quan

Workflow hoàn chỉnh để chuyển từ **log thô Moodle** sang **Q-Learning model**:

```
Log thô (CSV) → Extract Episodes → Train Q-Learning → Daily Updates → Recommendations
```

---

## 🎯 Workflow Chi Tiết

### **Bước 1: Chuẩn Bị Dữ Liệu**

Bạn cần 2 file CSV từ Moodle:

1. **`log.csv`** - Log hoạt động của học sinh
   ```csv
   id,timecreated,eventname,action,target,userid,courseid,other
   9206091,2022-09-03 13:04:58,\mod_assign\event\course_module_viewed,viewed,course_module,8670,670,
   9206092,2022-09-03 13:04:59,\mod_assign\event\submission_form_viewed,viewed,submission_form,8670,670,{'assignid': '****'}
   ```

2. **`grade.csv`** - Điểm số (optional, để tính reward chính xác hơn)
   ```csv
   id,timecreated,eventname,action,target,userid,courseid,other
   ```

**Đặt file vào:**
```
data/log/log.csv
data/log/grade.csv
```

---

### **Bước 2: Extract Episodes từ Log**

Chuyển log thô thành training episodes (state, action, reward, next_state):

```bash
python3 core/moodle_log_processor.py \
  --log-csv data/log/log.csv \
  --grade-csv data/log/grade.csv \
  --output data/training_episodes_real.json \
  --interaction-types quiz assignment resource
```

**Output:**
```json
[
  {
    "student_id": 8670,
    "timestamp": "2022-09-03T13:04:58",
    "state_before": {
      "avg_grade": 0.5,
      "completion_rate": 0.3,
      "activity_count": 15,
      ...
    },
    "action": {
      "type": "assignment",
      "module": "assign",
      "action": "submit"
    },
    "reward": 1.0,
    "state_after": {
      "avg_grade": 0.55,
      "completion_rate": 0.35,
      ...
    }
  },
  ...
]
```

**Kết quả mẫu từ data của bạn:**
```
✓ Loaded 8754 log entries
✓ Loaded 13995 grade entries
✓ Extracted 3106 interactions from 106 students
✓ Created 3106 training episodes
```

---

### **Bước 3: Train Q-Learning Model**

Train Q-learning agent từ episodes:

```bash
python3 train_qlearning_from_logs.py \
  --data data/training_episodes_real.json \
  --output models/qlearning_from_real_logs.pkl \
  --epochs 10 \
  --lr 0.1 \
  --gamma 0.95
```

**Parameters:**
- `--data`: Path to episodes JSON
- `--output`: Path to save model
- `--epochs`: Số epochs training (mặc định: 10)
- `--lr`: Learning rate α (mặc định: 0.1)
- `--gamma`: Discount factor γ (mặc định: 0.95)
- `--epsilon`: Exploration rate ε (mặc định: 0.1)

**Kết quả mẫu:**
```
Agent parameters:
  Learning rate (α): 0.1
  Discount factor (γ): 0.95
  Exploration rate (ε): 0.1

Epoch 1/5:
  Avg reward: 0.503
  Q-table size: 228 states

Training complete:
  Q-table size: 228 states
  Total updates: 15530
  Avg actions/state: 11.65
```

---

### **Bước 4: Test Model**

Test model với demo workflow:

```bash
python3 demo_workflow.py --model models/qlearning_from_real_logs.pkl
```

**Hoặc get recommendations cho 1 student cụ thể:**

```python
from core.qlearning_agent import QLearningAgent
from core.action_space import ActionSpace
import numpy as np

# Load model
agent = QLearningAgent(n_actions=37)
agent.load('models/qlearning_from_real_logs.pkl')

# Load action space
action_space = ActionSpace('data/course_structure.json')

# Student state (12 dimensions)
student_state = np.array([0.5, 0.4, 0.3, 0.2, 0.5, 0.6, 0.3, 0.8, 0.4, 0.5, 0.1, 0.6])

# Get top-5 recommendations
available_actions = [a.id for a in action_space.get_actions()]
recommendations = agent.recommend_action(student_state, available_actions, top_k=5)

# Print recommendations
for action_id, q_value in recommendations:
    action = action_space.get_action_by_id(action_id)
    print(f"{action.name} (Q={q_value:.2f})")
```

---

### **Bước 5: Daily Updates (Production)**

Update Q-table mỗi ngày với log mới:

```bash
python3 update_daily_qtable.py \
  --model models/qlearning_from_real_logs.pkl \
  --date 2025-11-01 \
  --lr 0.05
```

**Setup cron job** (chạy tự động lúc 00:00 mỗi ngày):

```bash
# Edit crontab
crontab -e

# Add line
0 0 * * * cd /path/to/step7_qlearning && python3 update_daily_qtable.py --model models/qlearning_from_real_logs.pkl
```

**Flow daily update:**
1. Load Q-table hiện tại (228 states)
2. Fetch logs mới (VD: 50 interactions)
3. Extract features → Calculate state
4. **Incremental update**: Q[s][a] += α * (r + γ * max Q[s',a'] - Q[s][a])
5. Save Q-table (VD: 235 states, +7 new states discovered)
6. Generate recommendations

**⚠️ LƯU Ý:** Đây là **INCREMENTAL**, không phải retrain từ đầu!

---

## 📊 Hiểu Rõ Dữ Liệu

### **State (12 dimensions)**

Trạng thái học sinh được tính từ lịch sử log:

```python
state = [
    avg_grade,              # 0.0-1.0: Điểm trung bình
    completion_rate,        # 0.0-1.0: Tỷ lệ hoàn thành
    activity_count,         # Normalize: /100
    forum_posts,            # Normalize: /10
    quiz_attempts,          # Normalize: /20
    resource_views,         # Normalize: /50
    avg_time_per_activity,  # Normalize: /3600 (giờ)
    days_since_last,        # Inverse: 1/(days+1)
    session_count,          # Normalize: /30
    avg_session_duration,   # Normalize: /7200 (2h)
    late_submissions,       # Normalize: /5
    streak_days            # Normalize: /30
]
```

**Ví dụ:**
```python
# Student vừa phải
[0.55, 0.40, 0.15, 0.02, 0.25, 0.30, 0.20, 0.80, 0.13, 0.25, 0.02, 0.06]

# Student giỏi
[0.85, 0.75, 0.50, 0.10, 0.50, 0.60, 0.15, 0.95, 0.30, 0.40, 0.00, 0.20]

# Student yếu
[0.30, 0.20, 0.05, 0.00, 0.10, 0.15, 0.30, 0.50, 0.05, 0.15, 0.04, 0.00]
```

### **Action (37 activities)**

Actions được map từ `course_structure.json`:

```python
# Quiz actions (22)
action_id=48: "Bài kiểm tra cuối kỳ"
action_id=27: "Bài kiểm tra giữa kỳ"

# HVP interactive (6)
action_id=66: "Video tương tác"

# Resources (6)
action_id=54: "Tài liệu học tập"

# Others: forum, qbank, lti
```

### **Reward**

Reward được tính dựa trên:

1. **Base reward**: Hoàn thành = +1.0, Xem = +0.5
2. **Score bonus**: +0-2.0 (từ điểm số)
3. **Cluster bonus**: +0-0.8 (tùy cluster)
4. **Difficulty bonus**: +0-0.5
5. **Engagement bonus**: +0-0.3
6. **Time efficiency**: +0-0.2
7. **Penalty**: -0.2 per extra attempt

**Ví dụ:**
```python
# Student yếu làm quiz khó → reward cao
cluster_id=0 (yếu), quiz, score=0.7, attempts=2
→ reward = 1.0 + 1.4 + 0.8 + 0.35 = 3.55

# Student giỏi làm quiz dễ → reward thấp
cluster_id=4 (giỏi), quiz, score=0.9, attempts=1
→ reward = 1.0 + 1.8 + 0.6 + 0.1 = 3.50
```

---

## 🔄 Cách Dữ Liệu Được Xử Lý

### **1. Log → Sessions**

Nhóm log thành sessions (gap > 30 phút):

```
Student 8670:
  Session 0: 13:04:58 - 13:30:00 (5 events)
  Session 1: 14:58:38 - 15:04:18 (20 events)
  Session 2: 10:13:31 - 10:16:03 (15 events)
```

### **2. Sessions → Interactions**

Extract key interactions:

```python
# Quiz submit
Event: \mod_quiz\event\attempt_submitted
→ Interaction: {type: 'quiz', action: 'submit'}

# Assignment submit
Event: \mod_assign\event\assessable_submitted
→ Interaction: {type: 'assignment', action: 'submit'}

# Resource view
Event: \mod_resource\event\course_module_viewed
→ Interaction: {type: 'resource', action: 'view'}
```

### **3. Interactions → Episodes**

Tạo training episodes:

```python
for interaction in interactions:
    # State BEFORE (30 days lookback)
    state_before = calculate_features(
        student_id,
        before_timestamp=interaction.timestamp - 1s
    )
    
    # Action
    action = map_to_action_space(interaction)
    
    # Reward
    reward = estimate_reward(interaction)
    
    # State AFTER
    state_after = calculate_features(
        student_id,
        before_timestamp=interaction.timestamp + 1s
    )
    
    episode = (state_before, action, reward, state_after)
```

---

## 🛠️ Troubleshooting

### **Problem 1: Không có episodes nào được tạo**

**Nguyên nhân:** Log không có quiz/assignment submit events

**Giải pháp:**
```bash
# Check log có events gì
python3 -c "
import pandas as pd
df = pd.read_csv('data/log/log.csv')
print(df['eventname'].value_counts().head(20))
"

# Thử thêm interaction types khác
python3 core/moodle_log_processor.py \
  --interaction-types quiz assignment resource forum
```

### **Problem 2: Q-table size quá nhỏ**

**Nguyên nhân:** Không đủ diverse states

**Giải pháp:**
```bash
# Giảm precision khi hash state
# Edit core/qlearning_agent.py
# state_tuple = tuple(np.round(state, 1))  # 1 decimal → 0 decimal
```

### **Problem 3: Reward luôn giống nhau**

**Nguyên nhân:** Chưa có grade data

**Giải pháp:**
```python
# Update _estimate_reward() in moodle_log_processor.py
# Parse 'other' field để lấy score thực tế

def _estimate_reward(self, interaction):
    # Try get score from 'other' field
    other = interaction.get('other', {})
    
    if 'grade' in other:
        score = float(other['grade']) / 100.0
        return 1.0 + score * 2.0
    
    # Fallback
    return 1.0 if interaction['action'] == 'submit' else 0.5
```

### **Problem 4: Training quá lâu**

**Giải pháp:**
```bash
# Giảm epochs
python3 train_qlearning_from_logs.py --epochs 3

# Hoặc sample data
python3 -c "
import json
import random

with open('data/training_episodes_real.json') as f:
    episodes = json.load(f)

sampled = random.sample(episodes, min(1000, len(episodes)))

with open('data/training_episodes_sampled.json', 'w') as f:
    json.dump(sampled, f)
"

python3 train_qlearning_from_logs.py --data data/training_episodes_sampled.json
```

---

## 📈 Production Deployment

### **1. Setup Server**

```bash
# Clone repo
git clone <repo>
cd demo_pineline/step7_qlearning

# Install dependencies
pip install -r requirements.txt

# Setup directories
mkdir -p data/log models data/recommendations
```

### **2. Initial Training**

```bash
# Process all historical logs
python3 core/moodle_log_processor.py \
  --log-csv data/log/log_all_history.csv \
  --output data/training_episodes_initial.json

# Train initial model
python3 train_qlearning_from_logs.py \
  --data data/training_episodes_initial.json \
  --output models/qlearning_production.pkl \
  --epochs 20
```

### **3. Setup Daily Updates**

```bash
# Create update script
cat > /path/to/daily_update.sh << 'EOF'
#!/bin/bash
cd /path/to/step7_qlearning
source venv/bin/activate

# Fetch today's logs from Moodle API
python3 scripts/fetch_daily_logs.py --date $(date +%Y-%m-%d)

# Update Q-table
python3 update_daily_qtable.py \
  --model models/qlearning_production.pkl \
  --date $(date +%Y-%m-%d) \
  --lr 0.05

# Send recommendations to API
python3 scripts/send_recommendations.py
EOF

chmod +x /path/to/daily_update.sh

# Add to cron
crontab -e
# Add: 0 1 * * * /path/to/daily_update.sh >> /var/log/qlearning_update.log 2>&1
```

### **4. Monitor**

```bash
# Check Q-table growth
python3 -c "
import pickle
with open('models/qlearning_production.pkl', 'rb') as f:
    agent = pickle.load(f)
print(f'Q-table size: {len(agent.q_table)} states')
print(f'Total updates: {agent.training_stats[\"total_updates\"]}')
"

# Check logs
tail -f /var/log/qlearning_update.log
```

---

## 🎯 Expected Performance

**Từ data của bạn (106 students, 3106 interactions):**

```
Initial Training:
  - Episodes: 3106
  - Q-table size: 228 states
  - Avg actions/state: 11.65
  - Training time: ~30 seconds
  - Avg reward: 0.503

After 1 week (daily updates):
  - Q-table size: ~250-280 states
  - Total updates: ~20,000
  - New states/day: ~3-5

After 1 month:
  - Q-table size: ~350-400 states
  - Total updates: ~50,000
  - Convergence: ~70-80%
```

---

## 📚 References

- **Q-Learning**: `core/qlearning_agent.py`
- **State Builder**: `core/state_builder.py`
- **Log Processor**: `core/moodle_log_processor.py`
- **Cluster Classification**: `CLUSTER_CLASSIFICATION.md`
- **Main README**: `README.md`

---

## ✅ Quick Start Summary

```bash
# 1. Extract episodes
python3 core/moodle_log_processor.py \
  --log-csv data/log/log.csv \
  --grade-csv data/log/grade.csv \
  --output data/training_episodes_real.json

# 2. Train model
python3 train_qlearning_from_logs.py \
  --data data/training_episodes_real.json \
  --output models/qlearning_from_real_logs.pkl \
  --epochs 10

# 3. Test
python3 demo_workflow.py --model models/qlearning_from_real_logs.pkl

# 4. Daily updates
python3 update_daily_qtable.py \
  --model models/qlearning_from_real_logs.pkl
```

**Done! 🚀**
