# Question Service - Quick Start Guide

## Cài đặt

### 1. Cài đặt dependencies
```bash
cd questionservice
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin MongoDB của bạn
```

### 3. Chạy service

**Development mode** (auto-reload):
```bash
python3 app.py
```

**Production mode** (Gunicorn):
```bash
./start.sh
```

Service sẽ chạy tại `http://localhost:5003`

## Sử dụng nhanh

### 1. Kiểm tra health
```bash
curl http://localhost:5003/health
```

### 2. Tạo câu hỏi từ JSON file
```python
python examples/convert_json_to_xml.py examples/sample_questions.json
```

### 3. Tạo câu hỏi qua API
```bash
curl -X POST http://localhost:5003/api/questions/create \
  -H "Content-Type: application/json" \
  -d @examples/sample_questions.json
```

### 4. Lấy danh sách câu hỏi
```bash
curl "http://localhost:5003/api/questions/?difficulty=easy&page=1&limit=10"
```

### 5. Export sang XML
```bash
curl -X POST http://localhost:5003/api/questions/export/xml \
  -H "Content-Type: application/json" \
  -d '{"question_ids": ["id1", "id2"], "filename": "quiz.xml"}' \
  -o quiz.xml
```

## Test service
```bash
python test_service.py
```

## Docker

### Build và chạy
```bash
docker-compose up -d
```

### Xem logs
```bash
docker-compose logs -f questionservice
```

## Roadmap

- [x] Phase 1: Multiple choice questions
- [ ] Phase 2: AI-powered question generation  
- [ ] Phase 3: Document upload and parsing
- [ ] Phase 4: More question types (essay, true/false, etc.)

## API Documentation

Xem file `README.md` để biết chi tiết về các API endpoints.
