# Chat Service + DIFY Workflows - Hướng dẫn Setup

## 📋 Tổng quan

Hệ thống gồm 2 phần:
1. **Chat Service CRUD API** - REST API đơn giản để lưu/lấy dữ liệu MongoDB
2. **DIFY Workflows** - 2 file .yml chứa logic thông minh (LLM, intent classification)

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────────────────────┐
│                    DIFY Platform                        │
│  ┌──────────────────┐       ┌──────────────────┐      │
│  │  Student Chatbot │       │  Teacher Chatbot │      │
│  │   (workflow.yml) │       │   (workflow.yml) │      │
│  └────────┬─────────┘       └────────┬─────────┘      │
│           │                           │                 │
│           └───────────┬───────────────┘                 │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP Requests
                        ▼
         ┌──────────────────────────────┐
         │   Chat Service CRUD API      │
         │      (FastAPI)               │
         │   http://localhost:5557      │
         └──────────┬───────────────────┘
                    │
                    ▼
         ┌──────────────────────────────┐
         │        MongoDB               │
         │  - chat_conversations        │
         │  - chat_messages             │
         │  - chat_analyzed_context     │
         └──────────────────────────────┘
```

## 🚀 Bước 1: Setup Chat Service (CRUD API)

### 1.1. Cài đặt dependencies

```bash
cd chat_service_crud
pip install -r requirements.txt
```

### 1.2. Cấu hình MongoDB

Tạo file `.env`:
```bash
cp .env.example .env
```

Sửa file `.env`:
```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=chat_db
PORT=5557
```

### 1.3. Chạy MongoDB (nếu chưa có)

**Option A: Docker**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option B: Cài đặt local**
```bash
# macOS
brew install mongodb-community
brew services start mongodb-community

# Ubuntu
sudo apt install mongodb
sudo systemctl start mongodb
```

### 1.4. Khởi động Chat Service

```bash
python main.py
```

Kiểm tra: http://localhost:5557/docs (Swagger UI)

## 📦 Bước 2: Import Workflows vào DIFY

### 2.1. Đăng nhập DIFY

Truy cập DIFY platform của bạn (cloud hoặc self-hosted)

### 2.2. Import Student Chatbot

1. Vào **Studio** → **Create from DSL**
2. Upload file: `dify_workflows/student_chatbot_v2.yml`
3. Click **Import**
4. **Quan trọng**: Cấu hình **Conversation Variables**
   - `user_id`: ID học sinh (lấy từ login system)
   - `course_id`: ID khóa học
   - `current_conversation_id`: Để trống (tự động tạo)

### 2.3. Import Teacher Chatbot

1. Vào **Studio** → **Create from DSL**
2. Upload file: `dify_workflows/teacher_chatbot_v2.yml`
3. Click **Import**
4. Cấu hình **Conversation Variables**
   - `teacher_id`: ID giảng viên
   - `course_id`: ID khóa học
   - `current_conversation_id`: Để trống

### 2.4. Cập nhật URLs trong workflows

Nếu Chat Service không chạy ở `http://139.99.103.223:5557`, cần update URLs:

**Tìm và thay thế trong DIFY UI:**
- `http://139.99.103.223:5557` → `http://YOUR_SERVER:5557`

Hoặc edit file .yml trước khi import:
```bash
# macOS/Linux
sed -i '' 's|http://139.99.103.223:5557|http://localhost:5557|g' dify_workflows/*.yml

# Windows (Git Bash)
sed -i 's|http://139.99.103.223:5557|http://localhost:5557|g' dify_workflows/*.yml
```

## 🔧 Bước 3: Cấu hình Moodle API

### 3.1. Lấy Moodle Token

1. Đăng nhập Moodle với quyền admin
2. **Site administration** → **Plugins** → **Web services** → **Manage tokens**
3. Tạo token mới cho user
4. Copy token

### 3.2. Update URLs trong workflows

**Student Chatbot - Review Quiz:**
- Node: `get_quiz_data`
- URL: `http://YOUR_MOODLE/webservice/rest/server.php?wstoken=YOUR_TOKEN&wsfunction=mod_quiz_get_attempt_review&moodlewsrestformat=json&attemptid=...`

**Student Chatbot - View Grades:**
- Node: `handle_view_grades`
- URL: `http://YOUR_MOODLE/webservice/rest/server.php?wstoken=YOUR_TOKEN&wsfunction=core_grades_get_grades&moodlewsrestformat=json&userid=...&courseid=...`

**Teacher Chatbot - Quiz Generation:**
- Node: `generate_quiz_api`
- URL: `http://YOUR_QUIZ_GEN_SERVICE:5003/api/ai/generate-and-import`

## 🧪 Bước 4: Test Hệ thống

### 4.1. Test Chat Service API

```bash
# Test health check
curl http://localhost:5557/health

# Tạo conversation
curl -X POST http://localhost:5557/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 10,
    "course_id": 5,
    "user_type": "student"
  }'

# Lưu message
curl -X POST http://localhost:5557/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "YOUR_CONVERSATION_ID",
    "role": "user",
    "content": "Hàm bậc 2 là gì?"
  }'

# Lấy messages
curl "http://localhost:5557/api/messages?conversation_id=YOUR_CONVERSATION_ID"
```

### 4.2. Test Student Chatbot trong DIFY

**Test cases:**
1. **General Q&A**: "Hàm bậc 2 là gì?"
2. **Review Quiz**: "Review bài kiểm tra vừa làm" (cần có attemptid)
3. **View Grades**: "Xem điểm của tôi"
4. **Simulation**: "Cho tôi mô phỏng về hàm bậc 2"

### 4.3. Test Teacher Chatbot trong DIFY

**Test cases:**
1. **View Student Knowledge**: "Xem kiến thức của học sinh ID 10"
2. **Generate Quiz**: "Tạo 5 câu hỏi trắc nghiệm về hàm bậc 2, độ khó trung bình"
3. **Class Overview**: "Xem tổng quan lớp học"
4. **Struggling Students**: "Học sinh nào đang gặp khó khăn?"

## 📊 Bước 5: Xem dữ liệu MongoDB

### 5.1. MongoDB Compass (GUI)

1. Download: https://www.mongodb.com/products/compass
2. Connect: `mongodb://localhost:27017`
3. Database: `chat_db`
4. Collections:
   - `chat_conversations`
   - `chat_messages`
   - `chat_analyzed_context`

### 5.2. MongoDB Shell (CLI)

```bash
mongosh

use chat_db

# Xem conversations
db.chat_conversations.find().pretty()

# Xem messages
db.chat_messages.find().sort({timestamp: -1}).limit(10).pretty()

# Xem analyzed context
db.chat_analyzed_context.find().pretty()

# Aggregation: Top keywords
db.chat_analyzed_context.aggregate([
  {$unwind: "$keywords"},
  {$group: {
    _id: "$keywords.keyword",
    count: {$sum: 1},
    avg_confidence: {$avg: "$keywords.confidence"}
  }},
  {$sort: {count: -1}},
  {$limit: 10}
])
```

## 🔄 Bước 6: Workflow thực tế

### Student Workflow

```
User: "Hàm bậc 2 là gì?"
  ↓
[DIFY] Check conversation_id
  ↓ (nếu chưa có)
[DIFY] HTTP Request → POST /api/conversations
  ↓ (lưu conversation_id vào conversation variable)
[DIFY] HTTP Request → POST /api/messages (role: user)
  ↓
[DIFY] LLM → Intent Classification → "general_qa"
  ↓
[DIFY] LLM → Generate Answer
  ↓
[DIFY] HTTP Request → POST /api/messages (role: assistant)
  ↓ (async background)
[DIFY] LLM → Extract Keywords → POST /api/analyzed-context
  ↓
[DIFY] Return response to user
```

### Teacher Workflow

```
Teacher: "Xem kiến thức của học sinh ID 10"
  ↓
[DIFY] Check/Create conversation
  ↓
[DIFY] Save user message
  ↓
[DIFY] LLM → Intent Classification → "view_student_knowledge"
  ↓
[DIFY] LLM → Extract student_id = 10
  ↓
[DIFY] HTTP Request → GET /api/analyzed-context/summary?user_id=10&course_id=5
  ↓
[DIFY] LLM → Format analysis (strengths, weaknesses, recommendations)
  ↓
[DIFY] Save assistant response
  ↓
[DIFY] Return formatted report to teacher
```

## 🐛 Troubleshooting

### Lỗi: MongoDB connection failed

```bash
# Kiểm tra MongoDB có đang chạy không
# macOS
brew services list | grep mongodb

# Ubuntu
sudo systemctl status mongodb

# Kiểm tra port 27017
netstat -an | grep 27017
```

### Lỗi: DIFY không kết nối được Chat Service

1. Kiểm tra Chat Service đang chạy: `curl http://localhost:5557/health`
2. Kiểm tra firewall/network
3. Nếu DIFY chạy Docker, dùng `host.docker.internal` thay vì `localhost`

### Lỗi: Intent classification không chính xác

- Tăng temperature của LLM (0.3 → 0.5)
- Bổ sung thêm examples vào system prompt
- Kiểm tra conversation history có được truyền đủ không

### Lỗi: Keywords không được extract

- Kiểm tra node Extract Keywords có chạy không (check logs)
- Verify POST `/api/analyzed-context` có nhận được data không
- Xem MongoDB collection `chat_analyzed_context` có records mới không

## 📝 API Documentation

### Chat Service Endpoints

**Swagger UI**: http://localhost:5557/docs

**Conversations:**
- `POST /api/conversations` - Tạo conversation
- `GET /api/conversations` - Lấy danh sách (có filter)
- `GET /api/conversations/{id}` - Lấy 1 conversation
- `DELETE /api/conversations/{id}` - Xóa conversation

**Messages:**
- `POST /api/messages` - Tạo message
- `GET /api/messages?conversation_id={id}` - Lấy messages của conversation
- `GET /api/messages/{id}` - Lấy 1 message
- `DELETE /api/messages/{id}` - Xóa message

**Analyzed Context:**
- `POST /api/analyzed-context` - Lưu phân tích từ LLM
- `GET /api/analyzed-context?user_id={id}&course_id={id}` - Lấy contexts
- `GET /api/analyzed-context/summary?user_id={id}&course_id={id}` - Tổng hợp phân tích

## 🎯 Workflow Features

### Student Chatbot Features

✅ **General Q&A**: Trả lời câu hỏi về kiến thức
✅ **Review Quiz**: Xem lại bài kiểm tra (dynamic attemptid)
✅ **View Grades**: Xem điểm số (dynamic userid, courseid)
✅ **Simulation Links**: Hướng dẫn mô phỏng PhET
✅ **Keyword Extraction**: Tự động phân tích và lưu keywords
✅ **MongoDB Storage**: Lưu toàn bộ conversations

### Teacher Chatbot Features

✅ **Student Analysis**: Phân tích kiến thức từ keywords đã extract
✅ **Quiz Generation**: Tạo câu hỏi động (dynamic topic, num, difficulty)
✅ **Class Overview**: Tổng quan lớp học từ aggregation
✅ **Struggling Students**: Tìm học sinh cần hỗ trợ
✅ **MongoDB Analytics**: Dùng aggregation pipeline

## 🔐 Security Notes

⚠️ **Production checklist:**

1. **MongoDB**: Enable authentication
```bash
mongod --auth
```

2. **Chat Service**: Add API key authentication
```python
# main.py
from fastapi.security import APIKeyHeader
API_KEY = os.getenv("API_KEY")
```

3. **DIFY**: Enable conversation rate limiting

4. **Moodle Token**: Store trong environment variables, không hardcode

5. **CORS**: Chỉ allow origins cần thiết
```python
allow_origins=["https://your-dify-domain.com"]
```

## 📈 Monitoring

### Health Checks

```bash
# Chat Service
curl http://localhost:5557/health

# MongoDB
mongosh --eval "db.adminCommand('ping')"
```

### Logs

```bash
# Chat Service logs (stdout)
python main.py 2>&1 | tee chat_service.log

# MongoDB logs
tail -f /usr/local/var/log/mongodb/mongo.log  # macOS
tail -f /var/log/mongodb/mongodb.log          # Ubuntu
```

### Metrics

Check MongoDB collections size:
```javascript
db.chat_conversations.countDocuments()
db.chat_messages.countDocuments()
db.chat_analyzed_context.countDocuments()
```

---

## 🎉 Hoàn thành!

Bây giờ bạn có:
- ✅ Chat Service CRUD API chạy port 5557
- ✅ 2 DIFY workflows đã import
- ✅ MongoDB với 3 collections
- ✅ Tích hợp với Moodle API

**Next steps:**
1. Test với real users
2. Monitor performance và logs
3. Tune LLM temperature nếu cần
4. Scale MongoDB nếu data lớn (sharding, replica set)
