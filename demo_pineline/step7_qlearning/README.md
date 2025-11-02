# Q-Learning Adaptive Learning System

Hệ thống gợi ý học tập thích ứng sử dụng Q-Learning, dựa trên dữ liệu logs từ Moodle.

## 🆕 BREAKING CHANGE: New API Input Format

**API hiện hỗ trợ 2 formats:**
1. ✅ **Structured Format (NEW - RECOMMENDED)** - Nested structure matching state dimensions
2. ⚙️ **Flat Format (OLD - BACKWARD COMPATIBLE)** - Legacy support

📘 **Chi tiết**: Xem [API_INPUT_FORMAT_GUIDE.md](./API_INPUT_FORMAT_GUIDE.md)

🧪 **Testing**: Chạy `python test_api_structured.py` để test cả 2 formats

## 📁 Cấu trúc thư mục

```
step7_qlearning/
├── api_service.py              # 🚀 API chính - Chạy server FastAPI
├── train_qlearning_from_logs.py  # 🎓 Train model từ logs
├── test_api.py                 # ✅ Test API
├── quick_test.py               # 🧪 Test nhanh
├── requirements.txt            # 📦 Dependencies
│
├── core/                       # 📚 Core modules
│   ├── qlearning_agent.py     # Q-Learning agent
│   ├── state_builder.py       # Xây dựng state từ features
│   ├── action_space.py        # Định nghĩa actions
│   ├── reward_calculator.py   # Tính reward
│   └── moodle_log_processor.py # Xử lý Moodle logs
│
├── data/                       # 💾 Data files
│   ├── course_structure.json  # Cấu trúc khóa học
│   ├── log/                   # Raw logs từ Moodle
│   │   ├── log.csv
│   │   └── grade.csv
│   └── training_episodes_real.json  # Episodes đã xử lý
│
└── models/                     # 🤖 Trained models
    └── qlearning_from_real_logs.pkl  # Model đã train
```

## 🚀 Hướng dẫn sử dụng

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Train model (nếu chưa có hoặc muốn train lại)

```bash
python train_qlearning_from_logs.py
```

Model sẽ được lưu tại: `models/qlearning_from_real_logs.pkl`

### 3. Chạy API server

```bash
python api_service.py
```

Server sẽ chạy tại: `http://localhost:8000`

### 4. Test API

```bash
# Test cơ bản
python quick_test.py

# Hoặc test đầy đủ
python test_api.py
```

## 📡 API Endpoints

### 1. **GET /** - Service info
```bash
curl http://localhost:8000/
```

### 2. **GET /health** - Health check
```bash
curl http://localhost:8000/health
```

### 3. **GET /model-info** - Thông tin model
```bash
curl http://localhost:8000/model-info
```

### 4. **POST /recommend** - Lấy gợi ý học tập ⭐

**Request:**
```json
{
  "student_features": {
    "userid": 8670,
    "mean_module_grade": 0.75,
    "total_events": 0.6,
    "course_module": 0.5,
    "viewed": 0.7,
    "attempt": 0.3,
    "feedback_viewed": 0.4,
    "submitted": 0.6,
    "reviewed": 0.3,
    "course_module_viewed": 0.5,
    "module_count": 0.4,
    "course_module_completion": 0.5,
    "created": 0.2,
    "updated": 0.1,
    "downloaded": 0.3
  },
  "top_k": 5
}
```

**Response:**
```json
{
  "student_id": 8670,
  "state_vector": [0.75, 0.58, ...],
  "state_description": {
    "knowledge_level": "good",
    "engagement_level": "high",
    ...
  },
  "recommendations": [
    {
      "action_id": 12,
      "action_name": "Complete Quiz 3",
      "action_type": "assessment",
      "module_type": "quiz",
      "q_value": 0.85,
      "url": null
    }
  ],
  "model_info": {
    "n_states_in_qtable": 1500,
    "total_training_updates": 50000,
    "episodes_trained": 1000
  }
}
```

## 🧪 Test nhanh

```bash
# Test với curl
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "student_features": {
      "userid": 8670,
      "mean_module_grade": 0.75,
      "total_events": 0.6,
      "viewed": 0.7
    },
    "top_k": 3
  }'
```

## 🎯 State Features

Hệ thống sử dụng **12 features** để xây dựng state:

### Performance (3 dims)
- `knowledge_level`: Điểm trung bình (0-1)
- `engagement_level`: Mức độ tương tác
- `struggle_indicator`: Chỉ số gặp khó khăn

### Activity Patterns (5 dims)
- `submission_activity`: Hoạt động nộp bài
- `review_activity`: Xem lại và feedback
- `resource_usage`: Sử dụng tài nguyên
- `assessment_engagement`: Tham gia đánh giá
- `collaborative_activity`: Hoạt động nhóm

### Completion Metrics (4 dims)
- `overall_progress`: Tiến độ tổng thể
- `module_completion_rate`: Tỷ lệ hoàn thành
- `activity_diversity`: Đa dạng hoạt động
- `completion_consistency`: Tính nhất quán

## 📊 Input Features từ Moodle

Các features cần cung cấp (normalized 0-1):

```python
{
    "mean_module_grade": float,      # Điểm TB module (0-1)
    "total_events": float,           # Tổng số events (normalized)
    "course_module": float,          # Course module interactions
    "viewed": float,                 # View events
    "attempt": float,                # Quiz attempts
    "feedback_viewed": float,        # Feedback views
    "submitted": float,              # Submissions
    "reviewed": float,               # Reviews
    "course_module_viewed": float,   # Module views
    "module_count": float,           # Số lượng modules
    "course_module_completion": float, # Tỷ lệ hoàn thành
    "created": float,                # Create events
    "updated": float,                # Update events
    "downloaded": float              # Download events
}
```

## 🔧 Cấu hình

Trong `api_service.py`:

```python
API_HOST = "0.0.0.0"
API_PORT = 8800
MODEL_PATH = "models/qlearning_from_real_logs.pkl"
COURSE_STRUCTURE_PATH = "data/course_structure.json"
```

## 📚 Documentation

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## ⚠️ Lưu ý

1. **Model phải được train trước** khi chạy API:
   ```bash
   python train_qlearning_from_logs.py
   ```

2. **Features phải được normalized** (0-1) trước khi gửi đến API

3. **Course structure** phải có sẵn trong `data/course_structure.json`

## 🔄 Workflow hoàn chỉnh

```
1. Chuẩn bị dữ liệu
   → data/log/log.csv
   → data/log/grade.csv
   → data/course_structure.json

2. Train model
   → python train_qlearning_from_logs.py
   → models/qlearning_from_real_logs.pkl

3. Chạy API
   → python api_service.py

4. Test
   → python test_api.py
   → Hoặc call API từ frontend/service khác
```

## 🐛 Troubleshooting

### Model not found
```bash
python train_qlearning_from_logs.py
```

### Course structure not found
Đảm bảo file `data/course_structure.json` tồn tại

### Port đã được sử dụng
Thay đổi port trong `api_service.py` hoặc:
```bash
API_PORT=8001 python api_service.py
```

## 📞 Support

Nếu có vấn đề, kiểm tra:
1. Log file: `api.log`
2. Test basic: `python quick_test.py`
3. Health check: `curl http://localhost:8080/health`
