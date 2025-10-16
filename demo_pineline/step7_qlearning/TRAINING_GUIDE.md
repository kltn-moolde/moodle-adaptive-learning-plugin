# Q-Learning Training & Evaluation Pipeline

## 📋 Tổng quan

Pipeline hoàn chỉnh để:
1. **Simulate** dữ liệu học sinh dựa trên cluster statistics
2. **Train** Q-Learning agent với dữ liệu simulated
3. **Evaluate** hiệu suất với metrics chi tiết
4. **Visualize** kết quả và insights

## 🔄 Quy trình

```
┌─────────────────────────────────────────────────────────────┐
│                    1. DATA SIMULATION                        │
│  Cluster Stats + Course Structure → Student Profiles        │
│                    + Learning Trajectories                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    2. TRAIN/TEST SPLIT                       │
│         80% Train Set  |  20% Test Set                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    3. Q-LEARNING TRAINING                    │
│  Episodes → Q-table Updates → Policy Learning               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    4. EVALUATION                             │
│  Metrics + Visualizations + Report                          │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
step7_qlearning/
├── core/
│   ├── data_simulator.py          # Simulate student data
│   ├── qlearning_agent_v2.py      # Q-Learning agent
│   └── ...
├── data/
│   ├── course_structure.json      # Course resources
│   ├── features_scaled_report.json # Real student features
│   └── simulated/                 # Generated data
│       ├── train_data.csv
│       ├── test_data.csv
│       └── dataset_summary.json
├── models/
│   └── qlearning_trained.pkl      # Trained model
├── results/
│   ├── training_history.json      # Training metrics
│   ├── evaluation_metrics.json    # Test metrics
│   ├── evaluation_report.txt      # Text report
│   └── visualizations/            # Plots
│       ├── learning_curve.png
│       ├── train_vs_test.png
│       └── metrics_heatmap.png
├── train_qlearning.py             # Training script
└── evaluate_qlearning.py          # Evaluation script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install numpy pandas matplotlib seaborn tqdm scikit-learn
```

### 2. Run Complete Pipeline

```bash
cd demo_pineline/step7_qlearning

# Train (includes data simulation)
python train_qlearning.py

# Evaluate
python evaluate_qlearning.py
```

### 3. View Results

- **Metrics**: `results/evaluation_metrics.json`
- **Report**: `results/evaluation_report.txt`
- **Plots**: `results/visualizations/*.png`

## 📊 Metrics Explained

### Training Metrics

| Metric | Ý nghĩa | Range |
|--------|---------|-------|
| **Episode Reward** | Tổng reward trong 1 episode (1 học sinh) | 0-10 |
| **Episode Length** | Số bước học (resources completed) | 1-15 |
| **Avg Q-value** | Giá trị Q trung bình trong Q-table | -∞ to +∞ |

### Evaluation Metrics

| Metric | Ý nghĩa | Công thức | Good Value |
|--------|---------|-----------|------------|
| **Avg Reward** | Reward trung bình trên tập test | Sum(rewards) / N | > 0.6 |
| **Avg Grade** | Điểm trung bình đạt được | Sum(grades) / N | > 0.7 |
| **Completion Rate** | Tỷ lệ hoàn thành tài nguyên | Completed / Total | > 0.8 |
| **Recommendation Accuracy** | Top-K accuracy (khớp hành động thực tế) | Correct / Total | > 0.5 |
| **Avg Q-value** | Giá trị Q trung bình (indicator of confidence) | Sum(Q) / N | > 0.3 |

### Reward Formula

```python
reward = 0.5 * grade + 0.2 * time_efficiency + 0.3 * completion
```

**Components:**
- `grade`: Điểm đạt được (0-1)
- `time_efficiency`: 1 - (time_spent / 60), shorter = better
- `completion`: 1.0 if completed, 0.0 otherwise

## 🎯 Use Cases

### Use Case 1: Train từ đầu

```python
from core.data_simulator import StudentDataSimulator
from core.qlearning_agent_v2 import QLearningAgentV2
from train_qlearning import QLearningTrainer

# 1. Simulate data
simulator = StudentDataSimulator(...)
train_df, test_df = simulator.generate_dataset(n_students=100)

# 2. Train agent
agent = QLearningAgentV2.create_from_course(...)
trainer = QLearningTrainer(agent, train_df, test_df)
trainer.train(n_epochs=10)

# 3. Save
agent.save('models/my_model.pkl')
```

### Use Case 2: Load model và test

```python
from core.qlearning_agent_v2 import QLearningAgentV2

# Load trained model
agent = QLearningAgentV2.create_from_course(...)
agent.load('models/qlearning_trained.pkl')

# Get recommendation
state = [0.8, 0.7, ...]  # Student features
recommendations = agent.recommend(state, available_actions, top_k=5)
```

### Use Case 3: Thay đổi hyperparameters

```python
agent = QLearningAgentV2.create_from_course(
    course_json_path,
    n_bins=5,              # Số bins (3, 5, 7)
    learning_rate=0.05,    # Learning rate (0.01-0.5)
    discount_factor=0.95,  # Gamma (0.8-0.99)
    epsilon=0.2            # Exploration rate (0.1-0.5)
)
```

## 📈 Interpreting Results

### Good Performance Indicators

✅ **Learning Curve trending up**: Reward increases over epochs  
✅ **Recommendation Accuracy > 50%**: Agent learns good policy  
✅ **Small train-test gap**: Good generalization  
✅ **Completion Rate > 80%**: Students complete resources  

### Warning Signs

⚠️ **Flat learning curve**: Hyperparameters cần điều chỉnh  
⚠️ **Low recommendation accuracy < 30%**: Q-table chưa học tốt  
⚠️ **Large train-test gap**: Overfitting  
⚠️ **Negative Q-values**: Reward function cần review  

## 🔧 Customization

### 1. Thay đổi reward function

Edit `train_qlearning.py`:

```python
def compute_reward(self, record: pd.Series) -> float:
    grade = record.get('grade', 0.0)
    time_spent = record.get('time_spent', 15)
    
    # Custom weights
    reward = (
        0.7 * grade +           # More weight on grade
        0.1 * time_reward +
        0.2 * completion_reward
    )
    return reward
```

### 2. Thêm cluster-aware training

```python
# In train_episode()
cluster_id = student_df.iloc[0]['cluster']

# Adjust learning rate by cluster
if cluster_id == 'cluster_1':  # Struggling students
    self.agent.alpha = 0.2  # Higher learning rate
else:
    self.agent.alpha = 0.1
```

### 3. Thay đổi số lượng students

```python
train_df, test_df = simulator.generate_dataset(
    n_students=500,           # More students
    train_ratio=0.7,          # 70-30 split
    n_steps_per_student=15    # More steps
)
```

## 🐛 Troubleshooting

### Issue: "Q-table size is very small"

**Solution**: Increase n_bins or training epochs
```python
agent = QLearningAgentV2.create_from_course(..., n_bins=5)
trainer.train(n_epochs=20)
```

### Issue: "Recommendation accuracy is low"

**Solution**: 
1. Check reward function alignment
2. Increase training data
3. Reduce epsilon (less exploration)

### Issue: "Training is slow"

**Solution**:
1. Reduce n_students
2. Reduce n_steps_per_student
3. Use smaller n_bins

## 📚 References

- Q-Learning: Watkins & Dayan (1992)
- State discretization: Sutton & Barto (2018)
- Adaptive learning: Khajah et al. (2016)

## 📝 Notes

- **State space size**: n_bins^12 (e.g., 3^12 = 531,441 states)
- **Training time**: ~5-10 min for 100 students, 10 epochs
- **Memory**: Q-table size depends on visited states (typically < 10% of full space)

## ✨ Next Steps

1. **Add cluster-aware recommendations**: Adjust Q-values by cluster
2. **Implement Deep Q-Learning**: For larger state spaces
3. **Real-time learning**: Update Q-table from real student data
4. **Multi-objective optimization**: Balance multiple goals (grade, time, engagement)
