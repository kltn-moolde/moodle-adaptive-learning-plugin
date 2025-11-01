# Cluster Classification System

## Tổng Quan

Hệ thống **tự động phân loại** clusters thành 3 mức độ (weak/medium/strong) dựa trên **mean_module_grade** từ file `cluster_profiles.json`, thay vì hardcode cluster IDs.

## Cách Hoạt Động

### 1. Load Cluster Profiles

```python
# File: data/cluster_profiles.json
{
  "cluster_stats": {
    "0": {
      "feature_means": {
        "mean_module_grade": 0.411,
        ...
      },
      "ai_profile": {
        "name": "Học sinh cần hỗ trợ tương tác"
      }
    },
    ...
  }
}
```

### 2. Auto-Classification

`RewardCalculator` tự động phân loại khi khởi tạo:

```python
calculator = RewardCalculator('data/cluster_profiles.json')
# Output:
# === AUTO-CLASSIFY CLUSTERS ===
# Cluster 3: grade=0.000 → weak     | Học sinh có vai trò quản trị/hỗ trợ khóa học
# Cluster 0: grade=0.411 → weak     | Học sinh cần hỗ trợ tương tác
# Cluster 5: grade=0.658 → medium   | Học sinh theo dõi hiệu suất và thành tích
# Cluster 1: grade=0.812 → medium   | Học sinh Tự giác và Theo dõi Tiến độ
# Cluster 2: grade=0.854 → strong   | Học sinh Chủ động Hoàn thành Nhiệm vụ
# Cluster 4: grade=0.875 → strong   | Học sinh Nghiên cứu Chủ động
```

### 3. Classification Logic

```python
# Sort clusters by mean_module_grade
grade_data.sort(key=lambda x: x[1])

# Split into 3 groups
n = len(grade_data)
weak_threshold = n // 3      # Bottom 33%
strong_threshold = 2 * n // 3  # Top 33%

if i < weak_threshold:
    level = 'weak'
elif i < strong_threshold:
    level = 'medium'
else:
    level = 'strong'
```

## Current Classification (6 Clusters)

| Cluster ID | Grade | Level | Profile |
|------------|-------|-------|---------|
| 3 | 0.000 | **weak** | Học sinh có vai trò quản trị/hỗ trợ khóa học |
| 0 | 0.411 | **weak** | Học sinh cần hỗ trợ tương tác |
| 5 | 0.658 | **medium** | Học sinh theo dõi hiệu suất và thành tích |
| 1 | 0.812 | **medium** | Học sinh Tự giác và Theo dõi Tiến độ |
| 2 | 0.854 | **strong** | Học sinh Chủ động Hoàn thành Nhiệm vụ |
| 4 | 0.875 | **strong** | Học sinh Nghiên cứu Chủ động |

## Reward Strategy by Level

### Weak Clusters (grade < 0.5)

**Strategy**: Khuyến khích hoàn thành bài tập, dù khó

- ✅ High reward (+0.8) for completing assessments (score > 0.5)
- ✅ Reward (+0.3) for reviewing content (resource, page, hvp)
- 🎯 Focus: **Completion** over speed

**Example**: Cluster 0, 3
- Student struggles with content
- Needs more time and support
- Reward any progress, even if slow

### Medium Clusters (0.5 <= grade < 0.8)

**Strategy**: Cân bằng giữa completion và quality

- ✅ Reward (+0.5) for good assessment scores (> 0.7)
- ✅ Reward (+0.2) for high knowledge level (> 0.6)
- 🎯 Focus: **Quality** over quantity

**Example**: Cluster 1, 5
- Student has solid foundation
- Can handle moderate challenges
- Reward consistent performance

### Strong Clusters (grade >= 0.8)

**Strategy**: Khuyến khích tốc độ và độ chính xác cao

- ✅ High reward (+0.6) for excellent scores (> 0.8)
- ✅ Speed bonus (+0.5) for first-attempt success (attempts=1, score > 0.7)
- ✅ Challenge bonus (+0.7) for hard activities (difficulty='hard', score > 0.7)
- 🎯 Focus: **Excellence** and **Efficiency**

**Example**: Cluster 2, 4
- Advanced students
- Complete tasks quickly with high accuracy
- Ready for challenging content

## Ưu Điểm

### 1. **Linh Động**
- Không hardcode cluster IDs
- Tự động adapt khi có data mới
- Dễ dàng mở rộng thêm clusters

### 2. **Data-Driven**
- Dựa trên `mean_module_grade` thực tế
- Reflect student performance chính xác
- Có thể verify bằng AI profile names

### 3. **Dễ Maintain**
- Chỉ cần update `cluster_profiles.json`
- Không cần sửa code
- Clear separation of data and logic

## Cách Sử Dụng

### Get Cluster Level

```python
from core.reward_calculator import RewardCalculator

calculator = RewardCalculator('data/cluster_profiles.json')

# Get level for any cluster
level = calculator.get_cluster_level(cluster_id=0)
# Output: 'weak'

level = calculator.get_cluster_level(cluster_id=2)
# Output: 'strong'
```

### Calculate Reward

```python
from core.action_space import LearningAction

# Define action
action = LearningAction(
    id=48,
    name="Bài kiểm tra cuối kỳ",
    type='quiz',
    section='General',
    purpose='assessment',
    difficulty='hard'
)

# Define outcome
outcome = {
    'completed': True,
    'score': 0.9,
    'time_spent': 20,
    'attempts': 1
}

# Calculate reward (tự động dùng cluster level)
reward = calculator.calculate_reward(
    cluster_id=0,  # weak cluster
    action=action,
    outcome=outcome,
    state=current_state
)
# → Higher reward for weak student completing hard quiz
```

## Khi Nào Cần Update?

### 1. New Cluster Data
Khi có dữ liệu mới từ Moodle pipeline:

```bash
# Re-run clustering
python pipeline/step3_kmean_cluster/cluster.py

# Update cluster_profiles.json
# → RewardCalculator sẽ tự động re-classify
```

### 2. Different Thresholds
Nếu muốn thay đổi cách phân loại (VD: top 40% là strong thay vì 33%):

```python
# Edit _classify_clusters() in reward_calculator.py
weak_threshold = n // 3  # Change this
strong_threshold = 2 * n // 3  # Change this
```

### 3. More Cluster Levels
Nếu muốn thêm level (VD: very_weak, weak, medium, strong, very_strong):

```python
# Edit _classify_clusters() and _cluster_bonus()
if i < n // 5:
    level = 'very_weak'
elif i < 2 * n // 5:
    level = 'weak'
# ... etc
```

## Validation

### Check Classification

```python
# In demo_workflow.py or any script
from core.reward_calculator import RewardCalculator

calc = RewardCalculator('data/cluster_profiles.json')
# → Prints classification table automatically

# Verify levels
for i in range(6):
    level = calc.get_cluster_level(i)
    print(f'Cluster {i}: {level}')
```

### Expected Output

```
=== AUTO-CLASSIFY CLUSTERS ===
Cluster 3: grade=0.000 → weak     | Học sinh có vai trò quản trị/hỗ trợ khóa học
Cluster 0: grade=0.411 → weak     | Học sinh cần hỗ trợ tương tác
Cluster 5: grade=0.658 → medium   | Học sinh theo dõi hiệu suất và thành tích
Cluster 1: grade=0.812 → medium   | Học sinh Tự giác và Theo dõi Tiến độ
Cluster 2: grade=0.854 → strong   | Học sinh Chủ động Hoàn thành Nhiệm vụ
Cluster 4: grade=0.875 → strong   | Học sinh Nghiên cứu Chủ động
```

## Tổng Kết

✅ **Tự động**: Phân loại dựa trên data thực tế  
✅ **Linh động**: Không hardcode cluster IDs  
✅ **Data-driven**: Sử dụng `mean_module_grade` từ cluster_profiles.json  
✅ **Dễ maintain**: Chỉ cần update data file  
✅ **Scalable**: Dễ dàng mở rộng thêm clusters hoặc levels  

🚀 **Ready for production!**
