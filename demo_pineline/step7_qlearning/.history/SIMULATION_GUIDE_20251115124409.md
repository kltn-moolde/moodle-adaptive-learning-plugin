a# Learning Path Simulation Guide

## Tổng quan

Hệ thống simulation mới cung cấp khả năng minh họa chi tiết toàn bộ quá trình học tập với:

1. **State Transitions**: Theo dõi di chuyển giữa các states
2. **Action Selection**: Hiển thị action được chọn từ state hiện tại (exploration vs exploitation)
3. **Reward Calculation**: Breakdown chi tiết reward components
4. **LO Filtering**: Lọc LO yếu cần học sau khi có action gợi ý
5. **LO Mastery Tracking**: Track mức độ thông thạo LO và dự đoán điểm midterm
6. **Score Prediction**: Dự đoán điểm tăng khi học LO

## Cấu trúc Files

### Core Classes

1. **`core/lo_mastery_tracker.py`** - `LOMasteryTracker`
   - Track LO mastery cho từng học sinh
   - Dự đoán điểm midterm
   - So sánh các LO với nhau
   - Tính điểm tăng dự kiến

2. **`core/state_transition_logger.py`** - `StateTransitionLogger`
   - Log chi tiết state transitions
   - Track action selection (exploration vs exploitation)
   - Log reward breakdown
   - Export to JSON

3. **`core/learning_path_simulator.py`** - `LearningPathSimulator`
   - Simulate toàn bộ quá trình học
   - Tích hợp tất cả components
   - Export results to JSON

### Script

- **`simulate_learning_path.py`** - Script chính để chạy simulation

## Cách Sử Dụng

### Basic Usage

```bash
# Simulate với default settings
python3 simulate_learning_path.py

# Simulate với custom settings
python3 simulate_learning_path.py \
    --qtable models/qtable_best.pkl \
    --output data/simulated/my_simulation.json \
    --students 5 \
    --steps 30 \
    --clusters weak medium strong \
    --verbose
```

### Parameters

- `--qtable`: Path to trained Q-table (default: `models/qtable_best.pkl`)
- `--output`: Output JSON file path (default: `data/simulated/learning_path_simulation.json`)
- `--students`: Number of students per cluster (default: 3)
- `--steps`: Number of learning steps per student (default: 30)
- `--clusters`: Clusters to simulate (default: weak medium strong)
- `--verbose`: Print detailed logs
- `--no-save`: Do not save logs to JSON

### Example

```bash
# Simulate 5 students per cluster, 50 steps each, verbose output
python3 simulate_learning_path.py \
    --students 5 \
    --steps 50 \
    --verbose \
    --output data/simulated/detailed_simulation.json
```

## Output Format

### JSON Structure

```json
{
  "simulation_metadata": {
    "total_students": 9,
    "students_config": [...],
    "avg_reward": 195.66,
    "avg_midterm_score": 14.5
  },
  "students": [
    {
      "student_id": 1000,
      "cluster": "weak",
      "total_steps": 30,
      "total_reward": 180.5,
      "final_state": {
        "module_idx": 2,
        "progress": 0.75,
        "score": 0.65,
        "avg_lo_mastery": 0.58
      },
      "lo_summary": {
        "current_mastery": {...},
        "weak_los": [...],
        "midterm_prediction": {
          "predicted_score": 12.5,
          "predicted_percentage": 62.5,
          "potential_improvement": 3.2,
          "potential_score": 15.7
        },
        "comparison": {...}
      },
      "transitions": [
        {
          "step": 1,
          "state": {...},
          "action": {...},
          "q_values": {...},
          "reward": {...},
          "lo_analysis": {...},
          "midterm_prediction": {...},
          "next_state": {...}
        },
        ...
      ]
    },
    ...
  ]
}
```

### Transition Details

Mỗi transition chứa:

- **State**: Current state vector và description
- **Action**: Selected action, activity, exploration/exploitation mode
- **Q-values**: Current Q-value và max Q-value của next state
- **Reward**: Total reward và breakdown (12 components)
- **LO Analysis**: Weak LOs considered, LO mastery deltas
- **Midterm Prediction**: Predicted score và potential improvement
- **Next State**: Next state vector và description

## Features

### 1. State Transition Tracking

Mỗi step log:
- State hiện tại (6D/7D vector)
- Action được chọn
- Q-value của action
- Reward breakdown
- State tiếp theo

### 2. Action Selection

Hiển thị:
- Action index và type
- Activity được recommend
- Exploration vs Exploitation mode
- Q-value comparison

### 3. LO Filtering

Sau khi có action gợi ý:
- Lọc ra LO yếu (mastery < threshold)
- Ưu tiên LO quan trọng cho midterm (high weight)
- Hiển thị LO được target bởi activity

### 4. LO Mastery Tracking

Track:
- Mastery của từng LO
- Delta sau mỗi activity
- History của changes
- Comparison giữa các LO

### 5. Midterm Score Prediction

Dự đoán:
- Điểm hiện tại dựa trên LO mastery
- Điểm tiềm năng nếu cải thiện weak LOs
- Breakdown theo từng LO
- Expected improvement

## Integration với Training

Simulator có thể được sử dụng trong training để:

1. **Visualize training process**: Xem state transitions trong quá trình train
2. **Debug reward calculation**: Kiểm tra reward breakdown
3. **Analyze LO improvements**: Track LO mastery changes
4. **Validate recommendations**: Kiểm tra action selection logic

## Future Enhancements

1. **Database Integration**: Chuyển từ JSON sang database
2. **Real-time Visualization**: Dashboard để xem simulation
3. **Batch Processing**: Simulate nhiều students song song
4. **A/B Testing**: So sánh different strategies
5. **Export Formats**: CSV, Excel, etc.

## Troubleshooting

### Issue: Q-table not found
**Solution**: Train Q-table trước:
```bash
python3 train_qlearning.py
```

### Issue: Missing data files
**Solution**: Đảm bảo có các files:
- `data/Po_Lo.json`
- `data/midterm_lo_weights.json`
- `data/cluster_profiles.json`
- `data/course_structure.json`

### Issue: Simulation too slow
**Solution**: Giảm số students hoặc steps:
```bash
python3 simulate_learning_path.py --students 1 --steps 10
```

## Examples

### Example 1: Single Student Simulation

```python
from core.learning_path_simulator import LearningPathSimulator

simulator = LearningPathSimulator(
    qtable_path='models/qtable_best.pkl',
    verbose=True
)

result = simulator.simulate_student(
    student_id=1001,
    cluster='weak',
    n_steps=30
)

print(f"Total reward: {result['total_reward']}")
print(f"Predicted midterm: {result['lo_summary']['midterm_prediction']['predicted_score']}")
```

### Example 2: Custom Analysis

```python
from core.lo_mastery_tracker import LOMasteryTracker

tracker = LOMasteryTracker()

# Initialize student
tracker.initialize_student(1001)

# Update mastery
tracker.update_mastery(1001, 'LO1.1', 0.75, activity_id=54)

# Get weak LOs
weak_los = tracker.get_weak_los(1001, threshold=0.6)

# Predict midterm
prediction = tracker.predict_midterm_score(1001)

# Compare LOs
comparison = tracker.compare_los(1001)
```

## Summary

Hệ thống simulation mới cung cấp:

✅ **Chi tiết state transitions** - Hiểu rõ quá trình di chuyển giữa states  
✅ **Action selection logic** - Xem action được chọn như thế nào  
✅ **Reward breakdown** - Hiểu reward được tính ra sao  
✅ **LO filtering** - Xem LO nào được ưu tiên  
✅ **LO mastery tracking** - Track mức độ thông thạo  
✅ **Midterm prediction** - Dự đoán điểm và improvement  
✅ **JSON export** - Dễ dàng phân tích và nâng cấp sang database  

Tất cả thông tin được lưu vào JSON để dễ dàng phân tích và nâng cấp sang database sau này!

