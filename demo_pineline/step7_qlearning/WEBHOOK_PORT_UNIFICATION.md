# Webhook Integration - Port Unification

## Vấn Đề Ban Đầu

- **API Service**: port **8080** (`api_service.py`)
- **Webhook Service**: port **8000** (`webhook_service.py`)  
→ Phải chạy 2 services riêng biệt

## Giải Pháp: Tích Hợp Vào Cùng Port 8080 ✅

Đã tích hợp webhook vào `api_service.py` để:
- ✅ Chỉ chạy 1 service duy nhất
- ✅ Cùng port 8080
- ✅ Dễ deploy và quản lý

## Changes Made

### 1. api_service.py (Updated) ⭐

**Thêm imports:**
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from pipeline.log_processing_pipeline import LogProcessingPipeline
from services.state_repository import StateRepository
```

**Thêm Pydantic models:**
```python
class MoodleLogEvent(BaseModel): ...
class WebhookPayload(BaseModel): ...
class WebhookResponse(BaseModel): ...
```

**Khởi tạo webhook components:**
```python
pipeline = LogProcessingPipeline(...)
state_repository = StateRepository()
```

**Thêm webhook endpoints:**
```python
@app.post('/webhook/moodle-events')  # Nhận events từ Moodle
@app.get('/api/recommendations/{user_id}/{module_id}')  # Trả recommendations
```

**Background processing:**
```python
async def process_events_async(logs, event_id):
    # Step 1: Process với pipeline → Update states
    # Step 2: Generate recommendations với Q-Learning
    # Step 3: Save to MongoDB
```

### 2. observer.php (Updated)

**URL webhook:**
```php
// OLD: port 8000
$url = 'http://localhost:8000/webhook/moodle-events';

// NEW: port 8080 (same as API)
$url = 'http://localhost:8080/webhook/moodle-events';
```

### 3. test_webhook.py (Updated)

**URLs:**
```python
# OLD
WEBHOOK_URL = "http://localhost:8000/webhook/moodle-events"

# NEW
WEBHOOK_URL = "http://localhost:8080/webhook/moodle-events"
```

## Architecture Now

```
┌─────────────────────────────────────────────────────────────┐
│                    API SERVICE (Port 8080)                  │
│                                                             │
│  Original Endpoints:                                        │
│  ├─ GET  /api/health                                        │
│  ├─ GET  /api/model-info                                    │
│  ├─ POST /api/recommend                                     │
│  └─ GET  /api/qtable/states/positive                        │
│                                                             │
│  NEW Webhook Endpoints:                                     │
│  ├─ POST /webhook/moodle-events         ⭐ NEW             │
│  └─ GET  /api/recommendations/{user}/{module}  ⭐ NEW      │
│                                                             │
│  Components:                                                │
│  ├─ Q-Learning Agent                                        │
│  ├─ Recommendation Service                                  │
│  ├─ LogProcessingPipeline      ⭐ NEW                       │
│  └─ StateRepository            ⭐ NEW                       │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Start Service (Single Command)

```bash
cd demo_pineline/step7_qlearning
python api_service.py
```

**Output:**
```
======================================================================
🚀 Starting Adaptive Learning API Server (with Webhook)
======================================================================
📊 Model: /path/to/models/qtable.pkl
🎯 Q-table states: 12345
🌐 Server: http://localhost:8080
📖 Docs: http://localhost:8080/docs
🔗 Webhook: http://localhost:8080/webhook/moodle-events
======================================================================
```

### Test Webhook

```bash
# Terminal 2
python test_webhook.py
```

### API Endpoints

#### Original API Endpoints
```bash
# Health check
curl http://localhost:8080/api/health

# Get recommendations (for students)
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"state": [3,0,0.5,0.75,1,1], "top_k": 3}'
```

#### NEW Webhook Endpoints
```bash
# Webhook (from Moodle)
curl -X POST http://localhost:8080/webhook/moodle-events \
  -H "Content-Type: application/json" \
  -d '{"logs": [{"userid": 101, ...}]}'

# Get recommendations (from webhook)
curl http://localhost:8080/api/recommendations/101/54
```

## Flow Comparison

### OLD (2 Services)

```
Moodle → observer.php → Webhook Service (port 8000) → MongoDB
                                                      ↓
Student → API Service (port 8080) → Q-Learning → Response
```

### NEW (1 Service) ✅

```
Moodle → observer.php ─┐
                       │
                       ├→ API Service (port 8080) → MongoDB
                       │   ├─ Webhook endpoints
                       │   ├─ API endpoints
Student → Browser   ────┘   └─ Q-Learning
```

## Benefits

### ✅ Đơn giản hơn
- Chỉ 1 service thay vì 2
- Chỉ 1 port thay vì 2
- Dễ quản lý process

### ✅ Deploy dễ hơn
- 1 systemd service thay vì 2
- 1 Docker container thay vì 2
- Ít resource hơn

### ✅ Maintain dễ hơn
- Code tập trung 1 file
- Shared components (model_loader, recommendation_service)
- Logs ở 1 chỗ

## Configuration

### Development (Local)
```python
# api_service.py
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
```

```php
// observer.php
$url = 'http://localhost:8080/webhook/moodle-events';
```

### Production
```python
# systemd service
uvicorn api_service:app --host 0.0.0.0 --port 8080 --workers 4
```

```php
// observer.php
$url = 'https://your-domain.com/webhook/moodle-events';
```

## Migration Steps

Nếu bạn đã deploy webhook service riêng (port 8000):

### Bước 1: Stop old webhook service
```bash
# Stop webhook_service.py nếu đang chạy
pkill -f webhook_service.py

# Hoặc với systemd
sudo systemctl stop webhook
```

### Bước 2: Update observer.php
```php
// Change port 8000 → 8080
$url = 'http://localhost:8080/webhook/moodle-events';
```

### Bước 3: Restart API service
```bash
# Stop old API service
pkill -f api_service.py

# Start new unified service
python api_service.py
```

### Bước 4: Test
```bash
python test_webhook.py
```

## Files

### Modified
- ✅ `api_service.py` - Added webhook endpoints
- ✅ `observer.php` - Changed port 8000 → 8080
- ✅ `test_webhook.py` - Changed port 8000 → 8080

### Deprecated (No longer needed)
- ❌ `webhook_service.py` - Merged into api_service.py
- ℹ️ Still kept for reference, but not used

## Summary

**Before:**
```bash
python api_service.py      # Port 8080
python webhook_service.py  # Port 8000
```

**After:**
```bash
python api_service.py      # Port 8080 (includes webhook)
```

**Easier, simpler, better!** ✅

---

**Status:** ✅ Completed
**Port:** 8080 (unified)
**Services:** 1 (combined)
