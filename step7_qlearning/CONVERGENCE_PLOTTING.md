# Convergence Analysis & Plotting Guide

## Overview

Hệ thống training Q-Learning giờ đã được tích hợp với công cụ **convergence visualization** để theo dõi chi tiết quá trình training.

## Features

### 1. **Biểu đồ Reward Convergence**
- Hiển thị progression của reward theo từng episode
- Moving average để smooth dữ liệu
- Trend line để phát hiện convergence
- Statistics box với metrics quan trọng

### 2. **Biểu đồ Epsilon Decay**
- Linear scale: thấy rõ epsilon giảm
- Log scale: hiển thị exponential decay
- Threshold lines (ε=0.5, 0.1, 0.01)

### 3. **Biểu đồ Q-table Growth**
- Size progression: số states phát hiện được
- Growth rate: states mới per episode
- Cumulative updates: tổng lần cập nhật
- Convergence indicators

### 4. **Combined View**
- Tất cả metrics trên 1 hình
- Convergence status indicator (✓ CONVERGED or ⟳ CONVERGING)
- Summary statistics

## Cách chạy

### 1. Training với Convergence Plots

```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning

# Basic training with plots
PYTHONPATH=$PWD:$PYTHONPATH python3 training/train_qlearning.py \
  --course-id 670 \
  --episodes 100 \
  --total-students 30 \
  --cluster-mix 0.2 0.6 0.2 \
  --steps 30 \
  --plot
```

### 2. Chi tiết hơn

```bash
# Full training with detailed logging + plots
PYTHONPATH=$PWD:$PYTHONPATH python3 training/train_qlearning.py \
  --course-id 670 \
  --episodes 100 \
  --total-students 30 \
  --cluster-mix 0.2 0.6 0.2 \
  --steps 30 \
  --detailed-logging \
  --log-interval 10 \
  --plot
```

### 3. Demo với Synthetic Data

```bash
# Quick demo without needing to train
PYTHONPATH=$PWD:$PYTHONPATH python3 scripts/utils/plot_training_convergence.py \
  --course-id 670 \
  --demo
```

## Output Files

Biểu đồ được lưu tại: `plots/convergence/`

```
plots/convergence/
├── reward_convergence.png      # Reward progression & convergence
├── epsilon_decay.png           # Epsilon decay schedule
├── qtable_growth.png           # Q-table size & updates
└── convergence_combined.png    # Tất cả metrics combined
```

## Interpretting the Plots

### Reward Convergence Plot

```
✓ Good: Reward tăng nhanh ở đầu, sau đó hội tụ
✗ Bad: Reward vẫn tăng/giảm oscillate nhiều episode cuối
```

**Metrics:**
- **Best Reward**: Reward cao nhất ghi được
- **Final Reward**: Reward ở episode cuối
- **Recent MA**: Trung bình 20 episodes gần nhất
- **Convergence Score**: % variance giảm (0-100%)

### Epsilon Decay Plot

```
✓ Expected: Exponential decay từ 1.0 → 0.01
- Nếu linear scale: curve từ từ flatten
- Nếu log scale: line chéo xuống
```

### Q-table Growth Plot

```
✓ Good: Initial spike (discovery), sau đó flatten (convergence)
✗ Bad: Tăng liên tục (chưa hội tụ)
```

**Indicators:**
- **State Discovery**: "Converged ✓" nếu growth rate < 0.5 states/ep
- **Q-table Stability**: "High ✓" nếu >15/20 episodes cuối không tìm state mới

### Combined View

```
✓ CONVERGED: Reward hội tụ, epsilon thấp, Q-table ổn định
⟳ CONVERGING: Vẫn đang học, agent vẫn explore
```

## Example Output

```
TRAINING CONVERGENCE SUMMARY
────────────────────────────────────────────────────────────────────────────────
Episodes: 100  |  Best Reward: 195.25 @ ep78  |  Final Reward: 193.52  |  Recent MA: 192.45
States: 498    |  Epsilon: 0.246  |  Convergence: 87.3%  |  Status: ✓ CONVERGED
```

## Thông số quan trọng

| Metric | Ý nghĩa | Giá trị tốt |
|--------|---------|-----------|
| Best Reward | Reward cao nhất | High (200+) |
| Final Reward | Reward cuối | Near best |
| Convergence Score | % hội tụ | >80% |
| Q-table States | Số states | Stable (không tăng) |
| Epsilon | Exploration rate | <0.1 ở cuối |

## Khi nào có thể dừng training?

1. **Reward hội tụ**: Final ≈ Best (trong 5%)
2. **Q-table ổn định**: 10+ episodes liên tiếp không có state mới
3. **Convergence score**: >80%
4. **Epsilon thấp**: <0.05 (exploitation dominant)

## Troubleshooting

### Lỗi: "Could not import plotting module"
```bash
# Cài matplotlib nếu chưa có
pip install matplotlib seaborn
```

### Lỗi: "No display found"
Bình thường trên server - plots vẫn được save vào file

### Plots không hiển thị
- Kiểm tra `plots/convergence/` xem files có được tạo không
- Nếu có, dùng image viewer để xem

## Advanced: Custom Plotting

Tạo custom plots từ training logs:

```python
from scripts.utils.plot_training_convergence import plot_from_training_stats

# Load training data
rewards = [...]  # list of rewards
epsilon_hist = [...]  # list of epsilon values
q_sizes = [...]  # list of q-table sizes
updates = [...]  # cumulative updates

plot_from_training_stats(
    episode_rewards=rewards,
    epsilon_history=epsilon_hist,
    q_table_size_history=q_sizes,
    total_updates_history=updates,
    course_id=670,
    output_dir='plots/my_analysis'
)
```

## Integration with Training

Plotting tự động chạy khi:
```bash
python3 training/train_qlearning.py ... --plot
```

Hoặc chạy riêng sau khi training xong:
```bash
python3 scripts/utils/plot_training_convergence.py --course-id 670 --demo
```
