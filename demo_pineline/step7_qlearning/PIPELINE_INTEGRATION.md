# Pipeline Integration Guide

## Tổng quan về luồng dữ liệu giữa 2 dự án

Dự án này liên kết chặt chẽ với `moodle_analytics_pipeline` để đảm bảo Q-learning được huấn luyện trên dữ liệu synthetic realististic và API có thể predict cluster cho sinh viên mới.

## Kiến trúc tổng thể

```
┌──────────────────────────────────┐
│  moodle_analytics_pipeline       │
│  ─────────────────────────       │
│                                  │
│  [Real Moodle Data]              │
│         ↓                        │
│  [Feature Extraction]            │
│         ↓                        │
│  [GMM Clustering]                │
│         ↓                        │
│  [Cluster Profiling]             │
│         ↓                        │
│  OUTPUT:                         │
│  • synthetic_students_gmm.csv    │──┐
│    (200 students với cluster_id) │  │
│  • cluster_profiles.json         │──┤
│    (6 clusters với feature_means)│  │
└──────────────────────────────────┘  │
                                      │ SYNC
                                      │ (sync_pipeline_data.py)
┌──────────────────────────────────┐  │
│  step7_qlearning                 │  │
│  ────────────────                │  │
│                                  │◄─┘
│  INPUT:                          │
│  • synthetic_students_gmm.csv    │
│  • cluster_profiles.json         │
│         ↓                        │
│  [Simulate Learning]             │
│    (với cluster-specific         │
│     behaviors)                   │
│         ↓                        │
│  [Train Q-Learning]              │
│    (cluster_id → rewards)        │
│         ↓                        │
│  [Save Model]                    │
│    models/qlearning_model.pkl    │
│         ↓                        │
│  [API Service]                   │
│    • Load cluster_profiles.json  │
│    • Predict cluster_id          │
│      (distance matching)         │
│    • Get recommendations         │
│      (from Q-table)              │
└──────────────────────────────────┘
```

## Chi tiết các bước

### Bước 1: Chạy Pipeline (moodle_analytics_pipeline)

```bash
cd moodle_analytics_pipeline

# Chạy toàn bộ pipeline
python main.py

# HOẶC chạy từng bước riêng lẻ:
python example_usage_gmm.py    # Generate synthetic students
python example_cluster_profiling.py  # Profile clusters
```

**Output:**
- `outputs/gmm_generation/synthetic_students_gmm.csv` - 200 sinh viên synthetic với cluster_id (0-5)
- `outputs/cluster_profiling/cluster_profiles.json` - Profiles của 6 clusters với feature_means

### Bước 2: Sync Data sang Q-Learning

```bash
cd ../step7_qlearning

# Chạy script sync
python sync_pipeline_data.py
```

**Kết quả:**
- Copy `synthetic_students_gmm.csv` → `data/synthetic_students_gmm.csv`
- Copy `cluster_profiles.json` → `data/cluster_profiles.json`
- Verify files compatible

### Bước 3: Simulate & Train Q-Learning

**Option A: Dùng synthetic students từ pipeline (KHUYẾN NGHỊ)**

```bash
# TODO: Sửa simulate_learning_data.py để load từ CSV
python simulate_learning_data.py --source csv --input data/synthetic_students_gmm.csv
```

**Option B: Tự generate (hiện tại)**

```bash
# Simulate 100 students với 30 actions mỗi người
python simulate_learning_data.py --n-students 100 --n-actions 30
```

**Train model:**

```bash
python train_qlearning_v2.py
```

**Output:**
- `data/simulated/latest_simulation.json` - Simulated interactions
- `models/qlearning_model.pkl` - Trained Q-table

### Bước 4: Start API Service

```bash
uvicorn api_service:app --reload --port 8080
```

**API Endpoints:**

1. **GET /api/health** - Kiểm tra service status
   ```bash
   curl http://localhost:8080/api/health
   ```

2. **GET /api/model-info** - Thông tin về model
   ```bash
   curl http://localhost:8080/api/model-info
   ```

3. **POST /api/recommend** - Gợi ý learning actions
   ```bash
   curl -X POST http://localhost:8080/api/recommend \
     -H "Content-Type: application/json" \
     -d '{
       "features": {
         "mean_module_grade": 0.7,
         "module_count": 0.5,
         "total_events": 0.3,
         "viewed": 0.4
       },
       "top_k": 3
     }'
   ```

## Cluster Prediction

API tự động predict cluster_id cho sinh viên mới bằng cách:

1. **Nhận features** từ request (mean_module_grade, module_count, total_events, viewed, ...)
2. **Load cluster_profiles.json** chứa feature_means của 6 clusters
3. **Tính Euclidean distance** giữa student features và feature_means của mỗi cluster
4. **Chọn cluster gần nhất** (smallest distance)
5. **Trả về cluster_id và cluster_name** trong response

### Ví dụ response với cluster prediction:

```json
{
  "success": true,
  "student_id": null,
  "cluster_id": 0,
  "cluster_name": "Cluster 0",
  "state_vector": [0.2, 0.043, 0.0, ...],
  "state_description": {...},
  "recommendations": [
    {
      "action_id": 73,
      "name": "SGK_CS_Bai4",
      "type": "resource",
      "purpose": "content",
      "difficulty": "medium",
      "q_value": 0.0
    },
    ...
  ],
  "model_info": {
    "model_loaded": true,
    "n_states_in_qtable": 1814,
    "total_updates": 30000
  }
}
```

## Cấu trúc dữ liệu

### synthetic_students_gmm.csv

```csv
userid,mean_module_grade,module_count,total_events,viewed,...,cluster,group
100000,0.27884565689971097,0.05526247884061819,0.00022616742175751714,0.08302041618633693,...,0,nhóm_6
100001,0.30396474805674695,0.44618971089095505,0.0,0.23488734833991093,...,0,nhóm_6
...
```

### cluster_profiles.json

```json
{
  "cluster_stats": {
    "0": {
      "cluster_id": 0,
      "n_students": 8,
      "percentage": 34.78,
      "feature_means": {
        "mean_module_grade": 0.47,
        "module_count": 0.30,
        "total_events": 0.05,
        ...
      },
      "ai_profile": {
        "profile_name": "Cluster 0",
        "description": "...",
        ...
      }
    },
    ...
  }
}
```

## Tại sao cần liên kết 2 dự án?

### Vấn đề trước đây:
1. ❌ Pipeline tạo synthetic students nhưng Q-learning không dùng
2. ❌ Q-learning tự simulate (không giống real data)
3. ❌ API không biết cluster_id → không thể tính reward đúng
4. ❌ Training và inference không consistent

### Giải pháp hiện tại:
1. ✅ Pipeline → synthetic students **VỚI cluster_id**
2. ✅ Q-learning train trên synthetic data → **cluster-aware rewards**
3. ✅ API predict cluster_id bằng **distance matching**
4. ✅ Toàn bộ flow nhất quán từ data → training → inference

## TODO: Improvements

### 1. Simulate from CSV (HIGH PRIORITY)

Hiện tại `simulate_learning_data.py` vẫn tự generate students. Cần sửa để:
- Load từ `synthetic_students_gmm.csv`
- Dùng cluster_id có sẵn
- Simulate theo cluster behaviors

### 2. Validate cluster prediction accuracy

Test xem distance-based matching có chính xác không:
- Lấy real students từ `real_students_with_clusters.csv`
- Predict cluster_id bằng API
- So sánh với cluster_id gốc từ GMM
- Tính accuracy

### 3. Auto-sync on pipeline run

Tự động sync data sau khi pipeline chạy xong:
- Hook vào pipeline output
- Trigger sync script
- Notify Q-learning training

## Troubleshooting

### Sync failed - files not found
```bash
# Kiểm tra pipeline outputs
ls -la ../moodle_analytics_pipeline/outputs/gmm_generation/
ls -la ../moodle_analytics_pipeline/outputs/cluster_profiling/

# Chạy lại pipeline nếu cần
cd ../moodle_analytics_pipeline
python main.py
```

### API không predict cluster
```bash
# Kiểm tra cluster_profiles.json đã load chưa
curl http://localhost:8080/api/health

# Check API logs
# Should see: "Loaded cluster profiles: 6 clusters"
```

### Cluster prediction sai
```bash
# Test với features từ cluster profiles
python3 -c "
import json
with open('data/cluster_profiles.json', 'r') as f:
    profiles = json.load(f)
    cluster_0_means = profiles['cluster_stats']['0']['feature_means']
    # Print sample features để test API
"
```

## References

- Pipeline README: `../moodle_analytics_pipeline/README.md`
- Q-learning README: `README.md`
- API documentation: `api_service.py` docstrings
