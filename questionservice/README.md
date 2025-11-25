# Question Service

Service tạo và quản lý câu hỏi trắc nghiệm cho hệ thống Moodle Adaptive Learning.

## Tính năng

### Phase 1 (Hiện tại) ✅
- ✅ Tạo câu hỏi trắc nghiệm (Multiple Choice)
- ✅ Chuyển đổi JSON sang XML định dạng Moodle
- ✅ Quản lý ngân hàng câu hỏi
- ✅ Phân loại câu hỏi theo độ khó
- ✅ Export XML để import vào Moodle

### Phase 2 (Hiện tại) ✅
- ✅ **AI-Powered Generation**: Tạo câu hỏi tự động bằng Google Gemini
- ✅ **Batch Generation**: Tạo nhiều câu hỏi cùng lúc
- ✅ **Multi-language**: Tiếng Việt và English
- ✅ **Free Tier Optimized**: Tối ưu cho Gemini free tier

### Phase 3-5 (Tương lai) 🔄
- 🔄 Tạo câu hỏi tự luận (Essay)
- 🔄 Tạo câu hỏi đúng/sai (True/False)
- 🔄 Tạo câu hỏi điền từ (Short Answer)
- 🔄 Upload tài liệu và tự động tạo câu hỏi bằng AI
- 🔄 Tùy chỉnh prompt để tạo câu hỏi

## Cấu trúc dự án

```
questionservice/
├── app.py                  # Main application
├── config.py              # Configuration
├── database.py            # MongoDB connection
├── requirements.txt       # Dependencies
├── Dockerfile            # Container configuration
├── routes/               # API routes
│   └── question_routes.py
├── services/             # Business logic
│   ├── question_generator.py
│   └── xml_converter.py
├── models/               # Data models
│   └── question.py
└── utils/                # Utilities
    ├── logger.py
    ├── exceptions.py
    └── validators.py
```

## API Endpoints

### Question Management (Phase 1)

### 1. Tạo câu hỏi từ JSON
```http
POST /api/questions/create
Content-Type: application/json

{
  "questions": [
    {
      "name": "Question 1",
      "question_type": "multichoice",
      "question_text": "<p>Câu hỏi của bạn?</p>",
      "difficulty": "easy",
      "answers": [
        {
          "text": "Đáp án A",
          "fraction": 100,
          "feedback": "Đúng!"
        },
        {
          "text": "Đáp án B",
          "fraction": 0,
          "feedback": "Sai rồi"
        }
      ]
    }
  ]
}
```

### 2. Export XML
```http
POST /api/questions/export/xml
Content-Type: application/json

{
  "question_ids": ["123", "456"],
  "filename": "quiz_export.xml"
}
```

### 3. Lấy danh sách câu hỏi
```http
GET /api/questions?difficulty=easy&type=multichoice&page=1&limit=10
```

### 4. Lấy chi tiết câu hỏi
```http
GET /api/questions/{question_id}
```

### 5. Cập nhật câu hỏi
```http
PUT /api/questions/{question_id}
Content-Type: application/json

{
  "question_text": "Câu hỏi đã sửa",
  "difficulty": "medium"
}
```

### 6. Xóa câu hỏi
```http
DELETE /api/questions/{question_id}
```

### AI Generation (Phase 2)

### 7. Generate Questions with AI
```http
POST /api/ai/generate
Content-Type: application/json

{
  "topic": "Python Programming - Biến và Kiểu dữ liệu",
  "num_questions": 3,
  "difficulty": "easy",
  "language": "vi",
  "save_to_db": true
}
```

### 8. Generate Batch with AI
```http
POST /api/ai/generate-batch
Content-Type: application/json

{
  "topic": "Python - Vòng lặp",
  "total_questions": 10,
  "difficulty": "medium",
  "language": "vi",
  "save_to_db": false
}
```

## Cài đặt và Chạy

### Local Development
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Development mode (auto-reload)
python3 app.py

# Production mode (Gunicorn)
./start.sh
```

### Production with Gunicorn
```bash
# Using gunicorn.conf.py
gunicorn -c gunicorn.conf.py "app:create_app()"

# Or use management scripts:
./start.sh    # Start service
./stop.sh     # Stop service
./restart.sh  # Restart service
./status.sh   # Check status
```

### Docker
```bash
# Build image
docker build -t questionservice .

# Run container
docker run -d -p 5003:5003 \
  -e MONGO_URI="your_mongodb_uri" \
  -e GEMINI_API_KEY="your_api_key" \
  --name questionservice \
  questionservice
```

### Docker Compose
```bash
docker-compose up -d
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MONGO_URI | MongoDB connection string | localhost |
| GEMINI_API_KEY | Google Gemini API key | - |
| MAX_QUESTIONS_PER_REQUEST | Max questions per request | 100 |
| UPLOAD_FOLDER | Upload directory | /tmp/questionservice |

## Định dạng JSON

### Multiple Choice Question
```json
{
  "name": "Question Name",
  "question_type": "multichoice",
  "question_text": "<p>Question text in HTML</p>",
  "difficulty": "easy|medium|hard",
  "answers": [
    {
      "text": "Answer text",
      "fraction": 100,  // 100 for correct, 0 for incorrect
      "feedback": "Feedback text"
    }
  ]
}
```

## Roadmap

- [x] Phase 1: Multiple choice questions
- [x] Phase 2: AI-powered question generation
- [ ] Phase 3: Document upload and parsing
- [ ] Phase 4: Other question types
- [ ] Phase 5: Advanced AI features

## License

MIT
