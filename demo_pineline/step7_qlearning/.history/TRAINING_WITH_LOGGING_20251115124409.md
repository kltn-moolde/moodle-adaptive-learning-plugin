# Training với Detailed Logging

## Tổng quan

Hệ thống training đã được tích hợp với **detailed logging** để minh họa chi tiết quá trình học tập trong lúc training. Tính năng này giúp bạn:

1. **Hiểu rõ state transitions** - Xem học sinh di chuyển giữa các states như thế nào
2. **Track action selection** - Xem action nào được chọn (exploration vs exploitation)
3. **Phân tích reward breakdown** - Hiểu reward được tính từ 12 components
4. **LO filtering** - Xem LO nào được ưu tiên sau khi có action
5. **LO mastery tracking** - Track mức độ thông thạo LO
6. **Midterm prediction** - Dự đoán điểm midterm trong quá trình training

## Cách Sử Dụng

### Basic Training (không logging)

```bash
# Training thông thường
python3 train_qlearning.py --episodes 100 --students 5 --steps 30
```

### Training với Detailed Logging

```bash
# Enable detailed logging
python3 train_qlearning.py \
    --episodes 100 \
    --students 5 \
    --steps 30 \
    --detailed-logging \
    --log-interval 10
```

### Parameters

- `--episodes`: Số episodes training (default: 100)
- `--students`: Số học sinh mỗi cluster (default: 5)
- `--steps`: Số steps mỗi episode (default: 30)
- `--output`: Path để lưu Q-table (default: `models/qtable.pkl`)
- `--detailed-logging`: Enable detailed state transition logging
- `--log-interval`: Log mỗi N episodes (default: 10)
- `--log-output`: Path pattern cho log files (use `{episode}` placeholder)
- `--quiet`: Tắt verbose output

### Examples

#### Example 1: Training với logging mỗi 10 episodes

```bash
python3 train_qlearning.py \
    --episodes 100 \
    --students 3 \
    --steps 30 \
    --detailed-logging \
    --log-interval 10
```

Sẽ tạo các files:
- `data/simulated/training_logs_episode_10.json`
- `data/simulated/training_logs_episode_20.json`
- ...
- `data/simulated/training_logs_episode_100.json`

#### Example 2: Custom log output path

```bash
python3 train_qlearning.py \
    --episodes 50 \
    --detailed-logging \
    --log-interval 5 \
    --log-output "logs/episode_{episode}_training.json"
```

#### Example 3: Training nhanh với logging

```bash
python3 train_qlearning.py \
    --episodes 20 \
    --students 2 \
    --steps 10 \
    --detailed-logging \
    --log-interval 5 \
    --quiet
```

## Log File Format

Mỗi log file chứa:

```json
{
  "transitions": [
    {
      "step": 1,
      "student_id": 1,
      "cluster_id": 0,
      "state": {
        "vector": [0, 0, 0.25, 0.5, 1, 1, 0],
        "description": {
          "cluster": "weak",
          "module": "module_0",
          "progress": "25%",
          "score": "50%",
          "phase": "active",
          "engagement": "medium"
        }
      },
      "action": {
        "index": 5,
        "type": "submit_quiz",
        "activity_id": 67,
        "activity_name": "Quiz tuần 2",
        "is_exploration": false
      },
      "q_values": {
        "current_q": 2.45,
        "max_next_q": 3.12
      },
      "reward": {
        "total": 5.23,
        "breakdown": {
          "completion": 5.0,
          "score_improvement": 1.5,
          "lo_mastery_improvement": 0.23
        }
      },
      "lo_analysis": {
        "weak_los": [
          {
            "lo_id": "LO1.1",
            "mastery": 0.45,
            "weight": 0.10
          }
        ],
        "lo_deltas": {
          "LO1.1": 0.05
        }
      },
      "midterm_prediction": {
        "predicted_score": 12.5,
        "predicted_percentage": 62.5,
        "potential_improvement": 3.2
      },
      "next_state": {...}
    }
  ],
  "statistics": {
    "total_steps": 90,
    "exploration_rate": 0.15,
    "exploitation_rate": 0.85,
    "avg_reward": 4.56
  }
}
```

## So sánh với Simulation Script

### `train_qlearning.py` (Training)
- **Mục đích**: Train Q-table
- **Logging**: Optional, chỉ log tại các intervals
- **Focus**: Training performance, Q-table updates
- **Output**: Q-table + optional log files

### `simulate_learning_path.py` (Simulation)
- **Mục đích**: Simulate với trained Q-table
- **Logging**: Always enabled, chi tiết từng step
- **Focus**: Understanding learning process, analysis
- **Output**: Complete simulation results

## Workflow Khuyến Nghị

1. **Training Phase**:
   ```bash
   # Train với logging để hiểu quá trình
   python3 train_qlearning.py \
       --episodes 100 \
       --detailed-logging \
       --log-interval 20
   ```

2. **Analysis Phase**:
   ```bash
   # Simulate với trained model để phân tích chi tiết
   python3 simulate_learning_path.py \
       --qtable models/qtable.pkl \
       --students 5 \
       --steps 50 \
       --verbose
   ```

3. **Iteration**:
   - Xem logs từ training
   - Phân tích simulation results
   - Điều chỉnh hyperparameters
   - Train lại

## Performance Impact

- **Without logging**: Training nhanh, không overhead
- **With logging**: 
  - Overhead: ~10-15% slower
  - Memory: Tăng ~20-30% (do lưu transitions)
  - Disk: ~1-5MB per log file (tùy số students/steps)

## Tips

1. **Log interval**: Không nên quá nhỏ (< 5) vì sẽ tạo nhiều files
2. **Students**: Với detailed logging, nên giảm số students để giảm memory
3. **Steps**: Với nhiều steps, log files sẽ lớn hơn
4. **Analysis**: Sử dụng simulation script để phân tích chi tiết hơn

## Troubleshooting

### Issue: Log files quá lớn
**Solution**: Tăng log interval hoặc giảm số students/steps

### Issue: Training chậm với logging
**Solution**: Chỉ enable logging khi cần, hoặc tăng log interval

### Issue: Memory error
**Solution**: Giảm số students hoặc steps, hoặc tăng log interval

## Summary

Tính năng detailed logging trong training cho phép bạn:

✅ **Hiểu rõ quá trình training** - Xem state transitions, action selection  
✅ **Phân tích reward** - Breakdown chi tiết 12 components  
✅ **Track LO mastery** - Xem LO nào được cải thiện  
✅ **Dự đoán midterm** - Track điểm dự kiến trong training  
✅ **Debug và optimize** - Tìm vấn đề và cải thiện model  

Kết hợp với `simulate_learning_path.py` để có cái nhìn toàn diện về hệ thống!

