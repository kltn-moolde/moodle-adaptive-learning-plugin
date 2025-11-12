# 🤖 Phase 2: AI Question Generator - Quick Guide

## Tính năng mới

✅ Tạo câu hỏi trắc nghiệm tự động bằng AI
✅ Chỉ cần đưa chủ đề → AI tạo câu hỏi hoàn chỉnh
✅ Hỗ trợ Tiếng Việt và English
✅ Tối ưu cho Google Gemini Free Tier

## API mới (2 endpoints)

### 1. Generate (1-5 câu)
```bash
POST /api/ai/generate

{
  "topic": "Python - List và Dictionary",
  "num_questions": 3,
  "difficulty": "easy",
  "language": "vi",
  "save_to_db": true
}
```

### 2. Generate Batch (max 20 câu)
```bash
POST /api/ai/generate-batch

{
  "topic": "Python - Vòng lặp",
  "total_questions": 10,
  "difficulty": "medium",
  "language": "vi"
}
```

## Chạy service

```bash
# Development mode
python3 app.py

# Production mode (Gunicorn)
./start.sh
```

## Test nhanh

```bash
# Test đầy đủ
python3 test_ai_service.py

# Quick example
python3 examples/quick_ai_example.py
```

## Ví dụ

```python
import requests

response = requests.post(
    'http://localhost:5003/api/ai/generate',
    json={
        'topic': 'Python Basics',
        'num_questions': 3,
        'language': 'vi',
        'save_to_db': True
    }
)

print(response.json()['message'])
# ✓ Generated 3 questions successfully, saved 3 to database
```

## Giới hạn

- **Single**: Max 5 câu/request (~15 seconds)
- **Batch**: Max 20 câu, tự động chia nhỏ (~60 seconds)
- **Free tier**: ~15 requests/minute

## Workflow

```
Topic → AI Generate → Preview → Edit (optional) → Save → Export XML → Moodle
```

## Documentation

- `PHASE2_AI.md` - Hướng dẫn chi tiết
- `PHASE2_COMPLETE.md` - Tổng kết
- `IMPLEMENTATION_SUMMARY.md` - Technical summary

---

🚀 **Phase 2 Complete!** - Ready to use!
