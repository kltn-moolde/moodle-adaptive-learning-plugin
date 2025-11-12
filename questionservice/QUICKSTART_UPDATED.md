# Question Service - Quick Start (Updated)

## ✅ Circular Import Fixed!

Service đã được fix lỗi đệ quy vô hạn. Giờ có thể chạy production với Gunicorn.

## Cấu hình nhanh

### 1. Cài đặt
```bash
cd questionservice
pip install -r requirements.txt
```

### 2. Cấu hình MongoDB & Gemini
Chỉnh sửa file `.env`:
```bash
# MongoDB (Required)
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/questionservice

# Gemini AI (Required for AI features)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Chạy Service

#### Development Mode (Flask dev server)
```bash
python3 app.py
# Runs on http://localhost:5003
# Auto-reload enabled
```

#### Production Mode (Gunicorn) - RECOMMENDED
```bash
./start.sh      # Start
./status.sh     # Check status  
./stop.sh       # Stop
./restart.sh    # Restart
```

## API Endpoints

### Phase 1: Manual Questions

```bash
# 1. Tạo câu hỏi
curl -X POST http://localhost:5003/api/questions/create \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [{
      "name": "Python Basics",
      "question_text": "What is Python?",
      "difficulty": "easy",
      "answers": [
        {"text": "A language", "fraction": 100},
        {"text": "A snake", "fraction": 0}
      ]
    }]
  }'

# 2. Export XML
curl -X POST http://localhost:5003/api/questions/export/xml \
  -H "Content-Type: application/json" \
  -d '{"question_ids": ["..."], "filename": "quiz.xml"}'

# 3. List questions
curl http://localhost:5003/api/questions?difficulty=easy

# 4. Get question
curl http://localhost:5003/api/questions/{id}

# 5. Update question
curl -X PUT http://localhost:5003/api/questions/{id} \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "medium"}'

# 6. Delete question
curl -X DELETE http://localhost:5003/api/questions/{id}
```

### Phase 2: AI Generation

```bash
# 7. Generate with AI (single request)
curl -X POST http://localhost:5003/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python - Biến và Kiểu dữ liệu",
    "num_questions": 3,
    "difficulty": "easy",
    "language": "vi",
    "save_to_db": true
  }'

# 8. Generate batch (auto-split for large requests)
curl -X POST http://localhost:5003/api/ai/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python - Vòng lặp",
    "total_questions": 10,
    "difficulty": "medium",
    "language": "vi",
    "save_to_db": false
  }'
```

## Service Management

### Start/Stop/Status
```bash
./start.sh      # Start with Gunicorn (4 workers)
./stop.sh       # Stop all workers
./restart.sh    # Restart service
./status.sh     # Check if running
```

### Health Check
```bash
curl http://localhost:5003/health
# Response: {"status":"healthy","service":"question-service","version":"1.0.0"}
```

## Architecture

### Application Factory Pattern
```python
# app.py uses factory pattern to avoid circular imports
def create_app():
    app = Flask(__name__)
    
    # Import blueprints INSIDE function (key fix!)
    from routes.question_routes import question_bp
    from routes.ai_routes import ai_bp
    
    app.register_blueprint(question_bp)
    app.register_blueprint(ai_bp)
    return app

# For Gunicorn
app = create_app()
```

### Key Features
- ✅ **No circular imports** - blueprints imported inside factory
- ✅ **Production ready** - Gunicorn with 4 workers
- ✅ **AI powered** - Google Gemini integration
- ✅ **Moodle compatible** - XML export format
- ✅ **Clean architecture** - Models, Services, Routes, Utils

## Limits (Free Tier)
- Max 5 questions per AI request (Gemini free tier)
- Batch generation auto-splits large requests
- 60 requests per minute (Gemini limit)

## Troubleshooting

### Service won't start
```bash
# Check if already running
./status.sh

# Check logs
tail -f logs/error.log  # if logging to file
# or
docker logs questionservice  # if using Docker
```

### MongoDB connection failed
```bash
# Verify .env configuration
cat .env | grep MONGO_URI

# Test connection
python3 -c "from pymongo import MongoClient; print(MongoClient('YOUR_URI').server_info())"
```

### Port 5003 already in use
```bash
# Find process using port
lsof -i :5003

# Kill it
kill -9 <PID>
```

## Examples

See `examples/` directory:
- `quick_ai_example.py` - Generate questions with AI
- `convert_json_to_xml.py` - Convert manual questions
- `sample_questions.json` - Sample data
- `sample_questions_moodle.xml` - Sample output

## Documentation

- `README.md` - Full documentation
- `ARCHITECTURE.md` - System design
- `DEPLOYMENT.md` - Production deployment
- `PHASE2_AI.md` - AI features guide
- `CIRCULAR_IMPORT_FIX.md` - Fix explanation
- `COMMANDS.md` - All API commands

## Support

Questions? Check:
1. Logs: `logs/error.log` (or stdout in Gunicorn)
2. Health endpoint: `curl http://localhost:5003/health`
3. Status: `./status.sh`
