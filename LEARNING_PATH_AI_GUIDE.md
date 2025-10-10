# Learning Path AI Explanation - Hướng dẫn đơn giản

## 🎯 Tính năng

- API nhận student state + learning path data
- Gọi Gemini AI để giải thích tại sao gợi ý learning path này  
- Lưu explanation vào MongoDB để không cần gen lại
- Student dashboard có button "Lấy ý kiến từ AI"
- Hiển thị explanation với UI đẹp

## 🚀 Setup và chạy

### 1. Setup Backend (courseservice)

```bash
cd courseservice

# Tạo file .env từ example
cp .env.example .env

# Chỉnh sửa .env, thêm Gemini API key:
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Chạy Flask app
python app.py
```

### 2. Setup Frontend

```bash
cd FE-service-v2

# Chạy React app  
npm start
```

### 3. Test API

```bash
# Test API với script
python test_learning_path_explanation.py

# Hoặc test thủ công với curl
curl -X POST http://localhost:5001/api/learning-path/explain \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "4",
    "course_id": "5", 
    "learning_path": {
      "suggested_action": "do_quiz_same",
      "q_value": 0.75,
      "source_state": {
        "section_id": 2,
        "lesson_name": "Basic Concepts",
        "quiz_level": "medium",
        "complete_rate_bin": 0.6,
        "score_bin": 3
      }
    }
  }'
```

## 📱 Sử dụng

1. Mở Student Dashboard: `http://localhost:3000/dashboard?userId=4&courseId=5`
2. Nhấn button **"Lấy ý kiến từ AI"** 
3. AI sẽ phân tích và hiển thị:
   - Lý do chính tại sao gợi ý này
   - Trạng thái học tập hiện tại
   - Lợi ích khi làm theo gợi ý
   - Các bước tiếp theo cụ thể
   - Lời động viên

## 🔧 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/learning-path/explain` | Generate AI explanation |
| GET | `/api/learning-path/explanations/{userId}/{courseId}` | Get user explanations |
| GET | `/api/learning-path/health` | Health check |

## 💾 MongoDB Collections

```javascript
// learning_path_explanations collection
{
  explanation_id: "md5_hash_of_input",
  user_id: "4",
  course_id: "5",
  learning_path: { ... },
  explanation: {
    reason: "Lý do chính...",
    current_status: "Trạng thái hiện tại...", 
    benefit: "Lợi ích...",
    motivation: "Động viên...",
    next_steps: ["Bước 1", "Bước 2", ...]
  },
  created_at: "2024-01-15T10:30:00",
  source: "gemini_ai"
}
```

## 🎨 UI Features

- Button "Lấy ý kiến từ AI" với loading state
- AI explanation với màu sắc phân loại:
  - 🟣 Lý do chính (tím)
  - 🔵 Trạng thái hiện tại (xanh dương)  
  - 🟢 Lợi ích (xanh lá)
  - 🟠 Các bước tiếp theo (cam)
  - 💜 Lời động viên (gradient)
- Button đóng explanation
- Responsive design

## 🔍 Fallback Logic

Nếu Gemini AI không available:
- Dựa trên `score_bin` để tạo explanation phù hợp
- Score thấp → cần củng cố
- Score cao → tiếp tục thách thức  
- Score trung bình → duy trì nhịp độ

## ⚡ Cache Strategy

- Generate unique ID từ `user_id + course_id + suggested_action + section_id`
- Check MongoDB trước khi gọi AI
- Lưu explanation vào DB sau khi generate
- Tiết kiệm API calls và tăng tốc độ response

Đơn giản, hiệu quả và đáp ứng đầy đủ yêu cầu! 🎉