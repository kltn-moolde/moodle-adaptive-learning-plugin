# Phase 2: AI-Powered Question Generation 🤖

## Tổng quan

Phase 2 thêm khả năng tạo câu hỏi tự động bằng Google Gemini AI. Chỉ cần đưa chủ đề, AI sẽ tự động tạo câu hỏi trắc nghiệm hoàn chỉnh.

## Tính năng

✅ **AI Generation**: Tạo câu hỏi từ chủ đề bằng Gemini AI
✅ **Batch Generation**: Tạo nhiều câu hỏi (tự động chia nhỏ request)
✅ **Multi-language**: Hỗ trợ Tiếng Việt và English
✅ **Difficulty Control**: Chọn độ khó (easy/medium/hard)
✅ **Free Tier Optimized**: Tối ưu cho Gemini free tier (max 5 câu/request)
✅ **Auto Save**: Tùy chọn lưu trực tiếp vào database

## API Endpoints

### 1. Generate Questions (Single Request)

**Endpoint**: `POST /api/ai/generate`

**Request**:
```json
{
  "topic": "Python Programming - Biến và Kiểu dữ liệu",
  "num_questions": 3,
  "difficulty": "easy",
  "language": "vi",
  "save_to_db": true
}
```

**Parameters**:
- `topic` (required): Chủ đề câu hỏi
- `num_questions` (optional): Số câu hỏi (1-5, default: 3)
- `difficulty` (optional): easy|medium|hard (default: medium)
- `language` (optional): vi|en (default: vi)
- `save_to_db` (optional): Lưu vào DB hay không (default: false)

**Response**:
```json
{
  "message": "Generated 3 questions successfully, saved 3 to database",
  "questions": [...],
  "saved_ids": ["id1", "id2", "id3"]
}
```

### 2. Generate Batch (Multiple Requests)

**Endpoint**: `POST /api/ai/generate-batch`

Tự động chia nhỏ thành nhiều request để tạo nhiều câu hỏi hơn.

**Request**:
```json
{
  "topic": "Python - Vòng lặp và Điều kiện",
  "total_questions": 10,
  "difficulty": "medium",
  "language": "vi",
  "save_to_db": false
}
```

**Parameters**:
- `topic` (required): Chủ đề
- `total_questions` (optional): Tổng số câu (max 20, default: 10)
- `difficulty`, `language`, `save_to_db`: Như trên

## Sử dụng

## 🧪 Testing

### Chạy service trước

```bash
# Development
python3 app.py

# Or Production
./start.sh
```

### Test với script tự động

```bash
python3 test_ai_service.py
```

### 2. Test với curl

```bash
# Generate 3 câu hỏi về Python
curl -X POST http://localhost:5003/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Programming - Biến và Kiểu dữ liệu",
    "num_questions": 3,
    "difficulty": "easy",
    "language": "vi",
    "save_to_db": true
  }'

# Generate batch 10 câu hỏi
curl -X POST http://localhost:5003/api/ai/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python - Vòng lặp",
    "total_questions": 10,
    "difficulty": "medium",
    "language": "vi"
  }'
```

### 3. Sử dụng với Python

```python
import requests

# Generate questions
response = requests.post(
    'http://localhost:5003/api/ai/generate',
    json={
        'topic': 'Python Basics',
        'num_questions': 3,
        'difficulty': 'easy',
        'language': 'vi',
        'save_to_db': True
    }
)

result = response.json()
print(f"Generated: {len(result['questions'])} questions")
print(f"Saved IDs: {result['saved_ids']}")
```

## Giới hạn Free Tier

Google Gemini Free Tier:
- ✅ ~15 requests/minute
- ✅ 1 million tokens/day
- ✅ Max 5 câu/request (do token limit)

**Giải pháp**:
- Single request: Max 5 câu
- Batch request: Tự động chia nhỏ (ví dụ: 10 câu = 2 requests x 5 câu)

## Ví dụ Output

### Input
```json
{
  "topic": "Python - List và Tuple",
  "num_questions": 3,
  "difficulty": "medium",
  "language": "vi"
}
```

### Output
```json
{
  "message": "Generated 3 questions successfully",
  "questions": [
    {
      "name": "Khác biệt giữa List và Tuple",
      "question_type": "multichoice",
      "question_text": "<p>Điểm khác biệt chính giữa List và Tuple trong Python là gì?</p>",
      "difficulty": "medium",
      "category": "Python - List và Tuple",
      "tags": ["python", "list", "tuple"],
      "answers": [
        {
          "text": "List có thể thay đổi (mutable), Tuple không thể thay đổi (immutable)",
          "fraction": 100,
          "feedback": "Đúng! List có thể thay đổi sau khi tạo, còn Tuple thì không."
        },
        {
          "text": "List nhanh hơn Tuple",
          "fraction": 0,
          "feedback": "Sai. Tuple thực ra nhanh hơn List do không thể thay đổi."
        },
        {
          "text": "Tuple dùng [] còn List dùng ()",
          "fraction": 0,
          "feedback": "Sai. Ngược lại - List dùng [], Tuple dùng ()."
        },
        {
          "text": "Không có sự khác biệt",
          "fraction": 0,
          "feedback": "Sai. Có nhiều khác biệt quan trọng giữa chúng."
        }
      ]
    }
  ]
}
```

## Tips

1. **Chủ đề cụ thể**: Càng cụ thể càng tốt
   - ❌ "Python"
   - ✅ "Python - List và Dictionary"

2. **Số lượng hợp lý**: 
   - Single request: 3-5 câu
   - Batch request: 10-20 câu

3. **Lưu vào DB**: 
   - `save_to_db: true` → Lưu luôn
   - `save_to_db: false` → Chỉ xem trước

4. **Thời gian chờ**: 
   - Single: ~10-20 giây
   - Batch (10 câu): ~30-60 giây

## Workflow đề xuất

```
1. Generate AI → Xem trước
   save_to_db: false

2. Review & Edit → Manual edit nếu cần
   
3. Save to DB → Lưu các câu đã chọn
   POST /api/questions/create-batch

4. Export XML → Import vào Moodle
   POST /api/questions/export/xml
```

## Error Handling

### Error: "Gemini API key is required"
```bash
# Kiểm tra .env
cat .env | grep GEMINI_API_KEY
```

### Error: Timeout
```bash
# AI đang xử lý lâu, tăng timeout:
curl -X POST ... --max-time 120
```

### Error: "Invalid JSON response"
- AI có thể trả về format không chuẩn
- Service tự động làm sạch response
- Nếu vẫn lỗi, thử lại với topic khác

## So sánh Phase 1 vs Phase 2

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| Input | Manual JSON | Topic string |
| Creation | Manual | AI Auto |
| Time | Instant | 10-60s |
| Quality | Your quality | AI quality |
| Quantity | Unlimited | 5 per request |
| Cost | Free | Free (with limits) |

## Next Steps

Sau khi có câu hỏi từ AI:
1. Review và edit nếu cần
2. Export sang XML
3. Import vào Moodle
4. Sử dụng trong quiz/assignment

---

**Note**: Phase 2 bổ sung thêm AI generation, không thay thế Phase 1. Bạn vẫn có thể tạo câu hỏi manual như Phase 1.
