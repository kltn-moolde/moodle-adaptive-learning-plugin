# Webhook Integration Guide

## Tổng Quan

Hệ thống webhook nhận sự kiện từ Moodle và tự động sinh gợi ý học tập bằng Q-Learning.

```
┌─────────┐        ┌──────────┐        ┌──────────┐        ┌──────────┐
│ Moodle  │ ────>  │ Webhook  │ ────>  │ Pipeline │ ────>  │ MongoDB  │
│ Event   │  POST  │ Service  │  Async │ Process  │  Save  │ States   │
└─────────┘        └──────────┘        └──────────┘        └──────────┘
                         │
                         v
                   ┌──────────┐
                   │ Q-Learning│
                   │ Recommend │
                   └──────────┘
```

## Kiến Trúc

### 1. Moodle Observer (Plugin)

**File:** `Plugin_zip/local_userlog/classes/observer.php`

- Bắt tất cả events học tập từ Moodle
- Lọc events hợp lệ (quiz, scorm, assign, forum)
- Gửi POST request đến webhook service (non-blocking, timeout 5s)
- Fire and forget - không chờ phản hồi

**Events được bắt:**
- `\mod_quiz\event\attempt_submitted` - Nộp bài quiz
- `\mod_quiz\event\attempt_started` - Bắt đầu quiz
- `\core\event\course_module_viewed` - Xem tài liệu
- `\mod_assign\event\submission_created` - Nộp bài tập
- `\mod_forum\event\post_created` - Tạo post forum

### 2. Webhook Service

**File:** `webhook_service.py`

FastAPI service nhận events và xử lý bất đồng bộ.

**Endpoints:**

```
POST /webhook/moodle-events
- Nhận events từ Moodle
- Return ngay lập tức (202 Accepted)
- Xử lý trong background task

GET /api/recommendations/{user_id}/{module_id}
- Lấy recommendations đã được sinh
- Moodle gọi endpoint này để hiển thị gợi ý

GET /health
- Health check service
```

**Background Processing Flow:**

```python
1. Nhận events từ Moodle
   ↓
2. Validate payload
   ↓
3. Add to background task queue
   ↓
4. Return 202 Accepted (< 100ms)

# Background task:
5. Process logs với LogProcessingPipeline
   - Parse logs → Build 6D states
   - Save states to MongoDB
   ↓
6. For each (user_id, module_id) bị ảnh hưởng:
   - Get current state from MongoDB
   - Generate recommendations với Q-Learning agent
   - Save recommendations to MongoDB
   ↓
7. Done (1-3 seconds)
```

### 3. Log Processing Pipeline

**File:** `pipeline/log_processing_pipeline.py`

Pipeline có sẵn được tích hợp vào webhook:

```python
pipeline = LogProcessingPipeline(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json',
    enable_qtable_updates=False  # Không update Q-table từ webhook
)

# Process logs
result = pipeline.process_logs_from_dict(
    raw_logs=logs,
    save_to_db=True,
    save_logs=True
)
```

**Outputs:**
- States được lưu vào `user_states` collection
- History được lưu vào `state_history` collection
- Raw logs được lưu vào `log_events` collection

### 4. Recommendation Service

**File:** `services/recommendation_service.py`

Sinh gợi ý từ Q-Learning agent:

```python
recommendations = recommendation_service.get_recommendations(
    state=tuple(state),
    cluster_id=cluster_id,
    top_k=3,
    exclude_action_ids=None,
    lo_mastery=None,
    module_idx=module_idx
)
```

**Output Format:**
```json
{
  "user_id": 101,
  "module_id": 54,
  "recommendations": [
    {
      "action": "attempt_quiz",
      "activity_id": 46,
      "activity_name": "Quiz: Kiểm tra giữa kỳ",
      "score": 8.5,
      "reason": "High Q-value action",
      "priority": "high"
    },
    ...
  ],
  "state": [3, 0, 0.5, 0.75, 1, 1],
  "timestamp": "2024-11-22T10:30:00"
}
```

### 5. MongoDB Collections

**Database:** `recommendservice`

**Collections:**

```
user_states:
- Lưu state hiện tại cho mỗi (user_id, module_id)
- Index: (user_id, module_id) unique
- TTL: Không expire

state_history:
- Lưu lịch sử states (time series)
- Index: (user_id, module_id, timestamp)

log_events:
- Raw logs từ Moodle
- Index: (user_id, timestamp)

recommendations:
- Recommendations đã sinh
- Index: (user_id, module_id) unique
- Được update mỗi khi có event mới
```

## Cài Đặt

### Bước 1: Cài Dependencies

```bash
cd demo_pineline/step7_qlearning

# Activate virtual environment
source .venv/bin/activate

# Cài đặt (nếu chưa có)
pip install fastapi uvicorn pymongo requests
```

### Bước 2: Khởi Động Webhook Service

```bash
python webhook_service.py
```

Output:
```
======================================================================
🚀 Initializing Webhook Service
======================================================================

1. Loading Q-Learning model...
  ✓ Model loaded

2. Initializing log processing pipeline...
  ✓ Pipeline ready

3. Initializing recommendation service...
  ✓ Recommendation service ready

4. Connecting to MongoDB...
  ✓ MongoDB connected

======================================================================
✅ Webhook Service Ready
======================================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Bước 3: Test Webhook

Mở terminal mới:

```bash
cd demo_pineline/step7_qlearning
python test_webhook.py
```

Output:
```
======================================================================
🧪 WEBHOOK SERVICE TEST SUITE
======================================================================

1. Testing Health Check
Status: 200
Response: {
  "status": "ok",
  "service": "webhook",
  "pipeline_ready": true,
  "recommendation_service_ready": true,
  "mongodb_connected": true
}

2. Testing Webhook POST
Status: 202
Response: {
  "status": "accepted",
  "message": "Events received and queued for processing",
  "events_received": 1,
  "processing_started": true
}

3. Testing GET Recommendations
Status: 200
Response: {
  "user_id": 101,
  "module_id": 54,
  "recommendations": [...]
}

✅ 3/3 tests passed
```

### Bước 4: Cập Nhật Moodle Plugin

1. Mở file `Plugin_zip/local_userlog/classes/observer.php`

2. Cập nhật URL webhook (dòng 42):

```php
// Development
$url = 'http://localhost:8000/webhook/moodle-events';

// Production (sau khi deploy)
$url = 'https://your-domain.com/webhook/moodle-events';
```

3. Upload plugin lên Moodle:

```bash
# Zip plugin
cd Plugin_zip
zip -r local_userlog.zip local_userlog/

# Upload lên Moodle:
# Site administration → Plugins → Install plugins
```

4. Enable plugin:

```bash
# Site administration → Plugins → Local plugins → User Log
# Check "Enable webhook integration"
```

## Testing với Moodle Thật

### 1. Trigger Event từ Moodle

- Đăng nhập Moodle với tài khoản học sinh
- Vào khóa học (Course ID: 2)
- Làm quiz / xem tài liệu / nộp bài tập

### 2. Kiểm Tra Webhook Logs

Webhook service sẽ in ra console:

```
======================================================================
🔄 Background Processing Started (event_id: moodle_event_...)
======================================================================

📊 Step 1: Processing 1 events with pipeline...
  ✓ States updated for 1 users across 1 modules

🎯 Step 2: Generating recommendations...
  ✓ Recommendations saved for user 101, module 54

======================================================================
✅ Background Processing Complete
======================================================================
  - Events processed: 1
  - States updated: 1
  - Recommendations generated: 1
```

### 3. Lấy Recommendations

```bash
curl http://localhost:8000/api/recommendations/101/54
```

Response:
```json
{
  "user_id": 101,
  "module_id": 54,
  "recommendations": [
    {
      "action": "attempt_quiz",
      "activity_id": 46,
      "activity_name": "Quiz: Kiểm tra giữa kỳ",
      "score": 8.5,
      "q_value": 12.345,
      "priority": "high",
      "reason": "High Q-value - recommended next action"
    },
    {
      "action": "view_content",
      "activity_id": 55,
      "activity_name": "Lesson: Chương 1",
      "score": 7.2,
      "q_value": 10.123,
      "priority": "medium",
      "reason": "Good alternative action"
    }
  ],
  "state": [3, 0, 0.5, 0.75, 1, 1],
  "timestamp": "2024-11-22T10:30:00.123456"
}
```

## Production Deployment

### 1. Deploy với Systemd (Linux)

Tạo file `/etc/systemd/system/webhook.service`:

```ini
[Unit]
Description=Adaptive Learning Webhook Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/demo_pineline/step7_qlearning
Environment="PATH=/path/to/.venv/bin"
ExecStart=/path/to/.venv/bin/python webhook_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable và start:

```bash
sudo systemctl enable webhook
sudo systemctl start webhook
sudo systemctl status webhook
```

### 2. Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhook/ {
        proxy_pass http://localhost:8000/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 10s;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
    }
}
```

### 3. HTTPS với Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Monitoring

```bash
# Logs
tail -f /var/log/webhook/webhook.log

# Health check
watch -n 5 curl http://localhost:8000/health

# MongoDB stats
mongo recommendservice --eval "db.stats()"
```

## Troubleshooting

### Webhook không nhận events

```bash
# Check service status
systemctl status webhook

# Check logs
journalctl -u webhook -f

# Test từ Moodle server
curl -X POST http://webhook-url/webhook/moodle-events \
  -H "Content-Type: application/json" \
  -d '{"logs": [...], "event_id": "test"}'
```

### MongoDB connection error

```bash
# Check MongoDB running
systemctl status mongod

# Test connection
python -c "from pymongo import MongoClient; \
  client = MongoClient('mongodb://localhost:27017'); \
  print(client.server_info())"
```

### Q-Learning model không load

```bash
# Check model file exists
ls -lh models/qtable.pkl

# Test load model
python -c "import pickle; \
  with open('models/qtable.pkl', 'rb') as f: \
    agent = pickle.load(f); \
    print(f'Q-table size: {len(agent.q_table)}')"
```

### Background tasks chạy chậm

```bash
# Increase workers
uvicorn webhook_service:app --workers 4 --port 8000

# Monitor processing time
grep "Background Processing Complete" /var/log/webhook/*.log | \
  awk '{print $NF}' | sort -n
```

## Performance

### Latency

- Webhook response: < 100ms (return ngay)
- Background processing: 1-3 seconds
- Get recommendations: < 50ms (read from MongoDB)

### Throughput

- Events per second: ~100 (single worker)
- Events per second: ~400 (4 workers)

### Scaling

Để scale horizontally:

```bash
# Multiple workers
uvicorn webhook_service:app --workers 4

# Multiple instances + load balancer
# nginx upstream round-robin
```

## API Reference

### POST /webhook/moodle-events

**Request:**
```json
{
  "logs": [
    {
      "userid": 101,
      "courseid": 2,
      "eventname": "\\mod_quiz\\event\\attempt_submitted",
      "component": "mod_quiz",
      "action": "submitted",
      "target": "attempt",
      "objectid": 46,
      "crud": "c",
      "edulevel": 2,
      "contextinstanceid": 54,
      "timecreated": 1700000000,
      "grade": 8.5,
      "success": 1
    }
  ],
  "event_id": "moodle_event_unique_id",
  "timestamp": 1700000000
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Events received and queued for processing",
  "events_received": 1,
  "processing_started": true,
  "event_id": "moodle_event_unique_id"
}
```

### GET /api/recommendations/{user_id}/{module_id}

**Response (200 OK):**
```json
{
  "user_id": 101,
  "module_id": 54,
  "recommendations": [...],
  "state": [3, 0, 0.5, 0.75, 1, 1],
  "timestamp": "2024-11-22T10:30:00"
}
```

### GET /health

**Response:**
```json
{
  "status": "ok",
  "service": "webhook",
  "pipeline_ready": true,
  "recommendation_service_ready": true,
  "mongodb_connected": true,
  "model_loaded": true,
  "timestamp": "2024-11-22T10:30:00"
}
```

## Security

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook/moodle-events")
@limiter.limit("100/minute")
async def receive_moodle_events(...):
    ...
```

### Authentication

```python
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-token":
        raise HTTPException(status_code=401)
    return x_api_key

@app.post("/webhook/moodle-events", dependencies=[Depends(verify_token)])
async def receive_moodle_events(...):
    ...
```

## Kết Luận

Hệ thống webhook đã được tích hợp hoàn chỉnh với:

✅ Moodle observer gửi events tự động
✅ FastAPI webhook nhận và xử lý bất đồng bộ
✅ Pipeline có sẵn cập nhật states
✅ Q-Learning sinh recommendations
✅ MongoDB lưu trữ states + recommendations
✅ API để Moodle lấy recommendations

**Flow hoàn chỉnh:**

1. Học sinh làm quiz trên Moodle
2. Moodle observer bắt event → POST webhook (100ms)
3. Webhook xử lý background (1-3s):
   - Update state vào MongoDB
   - Sinh recommendations
4. Moodle gọi GET /api/recommendations → hiển thị cho học sinh

**Next steps:**

- Deploy lên production server
- Thêm monitoring + alerting
- A/B testing recommendations
- Fine-tune Q-Learning agent
