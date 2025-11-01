# Quick Start: Training Q-Learning từ Log Moodle

## 🚀 3 Bước Đơn Giản

### **1. Extract Training Data**

```bash
python3 core/moodle_log_processor.py \
  --log-csv data/log/log.csv \
  --grade-csv data/log/grade.csv \
  --output data/training_episodes_real.json \
  --interaction-types quiz assignment resource
```

**Input:** CSV logs từ Moodle  
**Output:** `data/training_episodes_real.json` (3106 episodes)

---

### **2. Train Q-Learning Model**

```bash
python3 train_qlearning_from_logs.py \
  --data data/training_episodes_real.json \
  --output models/qlearning_from_real_logs.pkl \
  --epochs 10
```

**Input:** Episodes JSON  
**Output:** `models/qlearning_from_real_logs.pkl` (Q-table với 228 states)

---

### **3. Test & Use**

```bash
# Test model
python3 demo_workflow.py --model models/qlearning_from_real_logs.pkl

# Get recommendations for a student
python3 -c "
from core.qlearning_agent import QLearningAgent
from core.action_space import ActionSpace
import numpy as np

agent = QLearningAgent(n_actions=37)
agent.load('models/qlearning_from_real_logs.pkl')

action_space = ActionSpace('data/course_structure.json')

# Student state (weak student example)
state = np.array([0.3, 0.2, 0.1, 0.0, 0.15, 0.2, 0.3, 0.5, 0.1, 0.2, 0.0, 0.0])

# Get top-5 recommendations
recs = agent.recommend_action(state, list(range(37)), top_k=5)

for action_id, q_val in recs:
    action = action_space.get_action_by_id(action_id)
    print(f'→ {action.name} (Q={q_val:.2f})')
"
```

---

## 📊 Kết Quả từ Data Của Bạn

```
✅ Log entries: 8,754
✅ Students: 106  
✅ Training episodes: 3,106
✅ Q-table states: 228
✅ Avg reward: 0.503
```

---

## 🔄 Daily Updates (Production)

```bash
# Update Q-table mỗi ngày với log mới
python3 update_daily_qtable.py \
  --model models/qlearning_from_real_logs.pkl \
  --date 2025-11-01

# Setup cron job (00:00 daily)
0 0 * * * cd /path/to/step7_qlearning && python3 update_daily_qtable.py --model models/qlearning_from_real_logs.pkl
```

**Lưu ý:** Đây là **INCREMENTAL update**, không phải retrain!

---

## 📖 Chi Tiết Hơn

Đọc file `REAL_LOG_USAGE_GUIDE.md` để biết:
- Cách dữ liệu được xử lý (Log → Sessions → Interactions → Episodes)
- Giải thích State (12 dimensions)
- Giải thích Action (37 activities)  
- Giải thích Reward calculation
- Troubleshooting
- Production deployment

---

## 🎯 Workflow Tổng Quan

```
┌─────────────────────┐
│   Moodle Log CSV    │
│  (8,754 entries)    │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Extract Episodes    │ ← moodle_log_processor.py
│  (3,106 episodes)   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Train Q-Learning    │ ← train_qlearning_from_logs.py
│  (228 states)       │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Daily Updates       │ ← update_daily_qtable.py
│ (Incremental)       │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Recommendations     │
│ (Top-5 per student) │
└─────────────────────┘
```

---

## 🆘 Help

```bash
# Show help
python3 core/moodle_log_processor.py --help
python3 train_qlearning_from_logs.py --help
python3 update_daily_qtable.py --help
```

**Issues?** Check `REAL_LOG_USAGE_GUIDE.md` → Troubleshooting section
