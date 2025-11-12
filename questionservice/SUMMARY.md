# Question Service - Tổng quan

## 📋 Giới thiệu

**Question Service** là một microservice độc lập được xây dựng để tạo và quản lý câu hỏi trắc nghiệm cho hệ thống Moodle Adaptive Learning. Service được thiết kế với kiến trúc clean, dễ mở rộng và có khả năng tích hợp AI trong tương lai.

## Tính năng

### Phase 1 (Hoàn thành) ✅
- ✅ Tạo câu hỏi trắc nghiệm (Multiple Choice)
- ✅ Lưu trữ câu hỏi trong MongoDB
- ✅ Quản lý CRUD đầy đủ cho câu hỏi
- ✅ Phân loại câu hỏi theo độ khó (easy/medium/hard)
- ✅ Phân loại theo category và tags
- ✅ Chuyển đổi JSON sang XML định dạng Moodle
- ✅ Export XML để import vào Moodle
- ✅ API RESTful đầy đủ
- ✅ Pagination và filtering
- ✅ Statistics và monitoring

### Phase 2 (Hoàn thành) ✅
- ✅ **AI-Powered Generation**: Tạo câu hỏi tự động bằng Google Gemini
- ✅ **Batch Generation**: Tạo nhiều câu hỏi (tự động chia request)
- ✅ **Multi-language Support**: Tiếng Việt và English
- ✅ **Difficulty Control**: Chọn độ khó câu hỏi
- ✅ **Free Tier Optimized**: Tối ưu cho Gemini free tier
- ✅ **Auto Save**: Lưu trực tiếp vào database

### Phase 3-5 (Tương lai) 🔄
- 🔄 Câu hỏi tự luận (Essay)
- 🔄 Câu hỏi đúng/sai (True/False)
- 🔄 Câu hỏi điền từ (Short Answer)
- 🔄 Upload tài liệu (PDF, DOCX)
- 🔄 Tạo câu hỏi tự động bằng AI (Gemini/OpenAI)
- 🔄 Template system
- 🔄 Batch import/export

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────────────────┐
│                   Question Service                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   Routes   │  │  Services  │  │   Models   │   │
│  │  (API)     │→ │ (Business) │→ │   (Data)   │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│        ↓               ↓                ↓           │
│  ┌────────────────────────────────────────────┐   │
│  │              Utils & Validators            │   │
│  └────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌────────────────────────────────────────────┐   │
│  │            MongoDB Database                │   │
│  └────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Các thành phần chính:

1. **Routes** (`routes/`): Xử lý HTTP requests/responses
2. **Services** (`services/`): Business logic và database operations
3. **Models** (`models/`): Data structures và validation
4. **Utils** (`utils/`): Logger, exceptions, validators

## 🚀 Cài đặt nhanh

### Yêu cầu
- Python 3.11+
- MongoDB (local hoặc cloud)
- pip

### Cài đặt

```bash
cd questionservice

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình
cp .env.example .env
# Chỉnh sửa .env với MongoDB URI và API keys

# Development mode (auto-reload)
python3 app.py

# Production mode (Gunicorn)
./start.sh
```

## 📚 API Documentation

### Base URL
```
http://localhost:5003/api/questions
```

### 1. Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "question-service",
  "version": "1.0.0"
}
```

### 2. Tạo câu hỏi
```bash
POST /api/questions/create
Content-Type: application/json

{
  "name": "Câu hỏi 1",
  "question_type": "multichoice",
  "question_text": "<p>Nội dung câu hỏi?</p>",
  "difficulty": "easy",
  "category": "Python Basics",
  "tags": ["python", "basics"],
  "answers": [
    {
      "text": "Đáp án đúng",
      "fraction": 100,
      "feedback": "Chính xác!"
    },
    {
      "text": "Đáp án sai",
      "fraction": 0,
      "feedback": "Sai rồi"
    }
  ]
}
```

### 3. Tạo nhiều câu hỏi
```bash
POST /api/questions/create-batch
Content-Type: application/json

{
  "questions": [
    { ... },
    { ... }
  ]
}
```

### 4. Lấy danh sách câu hỏi
```bash
GET /api/questions?difficulty=easy&type=multichoice&page=1&limit=10
```

### 5. Lấy chi tiết câu hỏi
```bash
GET /api/questions/{question_id}
```

### 6. Cập nhật câu hỏi
```bash
PUT /api/questions/{question_id}
Content-Type: application/json

{
  "difficulty": "hard",
  "question_text": "<p>Câu hỏi đã sửa</p>"
}
```

### 7. Xóa câu hỏi
```bash
DELETE /api/questions/{question_id}
```

### 8. Export sang XML
```bash
POST /api/questions/export/xml
Content-Type: application/json

{
  "question_ids": ["id1", "id2"],
  "filename": "quiz.xml"
}
```

### 9. Statistics
```bash
GET /api/questions/statistics

Response:
{
  "total": 100,
  "by_difficulty": {
    "easy": 30,
    "medium": 50,
    "hard": 20
  },
  "by_type": {
    "multichoice": 100
  }
}
```

## 🧪 Testing

### Test với script tự động
```bash
python test_service.py
```

### Test thủ công với curl
```bash
# Health check
curl http://localhost:5003/health

# Tạo câu hỏi từ file JSON
curl -X POST http://localhost:5003/api/questions/create-batch \
  -H "Content-Type: application/json" \
  -d @examples/sample_questions.json

# Lấy danh sách
curl "http://localhost:5003/api/questions?page=1&limit=5"
```

### Convert JSON to XML (standalone)
```bash
python examples/convert_json_to_xml.py examples/sample_questions.json
```

## 🐳 Docker

### Build và chạy
```bash
docker-compose up -d
```

### Xem logs
```bash
docker-compose logs -f questionservice
```

### Stop
```bash
docker-compose down
```

## 📁 Cấu trúc thư mục

```
questionservice/
├── app.py                      # Main application
├── config.py                   # Configuration
├── database.py                 # MongoDB connection
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker config
├── docker-compose.yml          # Docker Compose
├── start.sh                    # Startup script
├── test_service.py            # Test script
├── README.md                   # Full documentation
├── QUICKSTART.md              # Quick start guide
├── ARCHITECTURE.md            # Architecture guide
├── SUMMARY.md                 # This file
│
├── models/                     # Data models
│   ├── __init__.py
│   └── question.py
│
├── routes/                     # API routes
│   ├── __init__.py
│   └── question_routes.py
│
├── services/                   # Business logic
│   ├── __init__.py
│   ├── question_generator.py
│   └── xml_converter.py
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── logger.py
│   ├── exceptions.py
│   └── validators.py
│
└── examples/                   # Examples
    ├── sample_questions.json
    └── convert_json_to_xml.py
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# MongoDB
MONGO_URI=mongodb://...

# AI (future)
GEMINI_API_KEY=...
OPENAI_API_KEY=...

# Service
MAX_QUESTIONS_PER_REQUEST=100
UPLOAD_FOLDER=/tmp/questionservice
MAX_UPLOAD_SIZE=10485760
```

## 🎨 JSON Format

### Multiple Choice Question
```json
{
  "name": "Question Name",
  "question_type": "multichoice",
  "question_text": "<p>Question HTML</p>",
  "difficulty": "easy|medium|hard",
  "category": "Category Name",
  "tags": ["tag1", "tag2"],
  "answers": [
    {
      "text": "Answer text",
      "fraction": 100,  // 100 = correct, 0 = incorrect
      "feedback": "Feedback text"
    }
  ]
}
```

## 🔮 Roadmap

### Phase 1: Multiple Choice ✅ (Hoàn thành)
- [x] CRUD operations
- [x] JSON to XML conversion
- [x] API endpoints
- [x] Validation
- [x] MongoDB integration

### Phase 2: More Question Types 🔄
- [ ] True/False questions
- [ ] Short Answer questions
- [ ] Essay questions
- [ ] Matching questions

### Phase 3: AI Integration 🔄
- [ ] Gemini API integration
- [ ] OpenAI API integration
- [ ] Question generation from text
- [ ] Custom prompts

### Phase 4: Document Processing 🔄
- [ ] PDF upload & parsing
- [ ] DOCX upload & parsing
- [ ] Auto question generation from documents
- [ ] Content extraction

### Phase 5: Advanced Features 🔄
- [ ] Question templates
- [ ] Batch import/export
- [ ] Question versioning
- [ ] Collaboration features
- [ ] Analytics & insights

## 🔐 Security (Future)

- [ ] API authentication
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] CORS configuration
- [ ] JWT tokens

## 📊 Monitoring

### Logs
```bash
tail -f logs/app.log
```

### Statistics
```bash
curl http://localhost:5003/api/questions/statistics
```

## 🤝 Tích hợp với Moodle

1. Tạo câu hỏi qua API
2. Export sang XML
3. Import XML vào Moodle:
   - Moodle → Course → Question Bank
   - Import questions → Moodle XML format
   - Upload XML file

## 💡 Best Practices

1. **Validation**: Luôn validate input trước khi lưu
2. **Logging**: Log tất cả operations quan trọng
3. **Error Handling**: Sử dụng custom exceptions
4. **Pagination**: Luôn phân trang khi list data
5. **Indexing**: Tạo indexes cho MongoDB
6. **Testing**: Test kỹ trước khi deploy

## 🐛 Troubleshooting

### Service không start được
```bash
# Check Python version
python3 --version

# Check dependencies
pip install -r requirements.txt

# Check MongoDB connection
# Verify MONGO_URI in .env
```

### Không connect được MongoDB
```bash
# Check MongoDB URI
echo $MONGO_URI

# Test connection
mongosh "your_mongodb_uri"
```

### Import lỗi
```bash
# Make sure you're in the right directory
cd questionservice

# Activate virtual environment
source venv/bin/activate
```

## 📞 Support

- Documentation: `README.md`, `QUICKSTART.md`, `ARCHITECTURE.md`
- Examples: `examples/`
- Test: `python test_service.py`

## 📝 License

MIT License

---

**Lưu ý**: Đây là Phase 1 với focus vào Multiple Choice questions. Các phase sau sẽ thêm AI integration và nhiều loại câu hỏi khác.
