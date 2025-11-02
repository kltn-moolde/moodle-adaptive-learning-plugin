# 📘 Quick Guide: API Input/Output

## 🎯 TÓM TẮT NHANH

### INPUT: Gửi thông tin sinh viên
```json
{
  "student_id": 12345,           // ✅ ĐÃ FIX (trước đây bị NULL)
  "features": {                  // Thông tin học tập (normalized 0-1)
    "mean_module_grade": 0.6,    // Điểm TB: 60%
    "total_events": 0.9,         // Hoạt động: cao (90%)
    "viewed": 0.5,               // Xem tài liệu: trung bình
    "attempt": 0.2,              // Làm bài: thấp (20%)
    "feedback_viewed": 0.8,      // Xem feedback: cao
    "module_count": 0.3,         // Số module: ít
    "course_module_completion": 0.8  // Hoàn thành: 80%
  },
  "top_k": 5                     // Muốn 5 gợi ý
}
```

### OUTPUT: Nhận gợi ý học tập
```json
{
  "student_id": 12345,           // ✅ ID sinh viên
  "cluster_id": 2,               // Nhóm học sinh: Cluster 2
  "cluster_name": "Cluster 2",   // Tên nhóm
  
  "state_description": {         // 📊 Phân tích chi tiết
    "performance": {
      "knowledge_level": 0.6,    // Kiến thức: 60% (trung bình)
      "engagement_level": 0.467, // Tham gia: 46.7% (thấp)
      "struggle_indicator": 0.016 // Khó khăn: 1.6% (OK)
    }
  },
  
  "recommendations": [           // 🎯 Top 5 gợi ý
    {
      "action_id": 64,
      "name": "bài kiểm tra bài 2 - hard",
      "type": "quiz",
      "difficulty": "hard",
      "q_value": 0.0
    },
    // ... 4 gợi ý khác
  ]
}
```

---

## 🔑 Ý NGHĨA CÁC TRƯỜNG

### INPUT Features (0-1 normalized):
- **0.0-0.3**: Thấp/Kém
- **0.3-0.7**: Trung bình
- **0.7-1.0**: Cao/Tốt

### OUTPUT State Description:
| Metric | Ý nghĩa | Thấp (<0.3) | Cao (>0.7) |
|--------|---------|-------------|------------|
| `knowledge_level` | Hiểu bài | Cần ôn lại | Nắm vững |
| `engagement_level` | Tham gia | Thụ động | Tích cực |
| `struggle_indicator` | Gặp khó khăn | OK | Cần hỗ trợ |
| `submission_activity` | Nộp bài | Ít nộp | Nộp đều |
| `review_activity` | Xem lại | Ít review | Review nhiều |
| `assessment_engagement` | Làm kiểm tra | Né tránh | Tích cực |
| `overall_progress` | Tiến độ | Chậm | Nhanh |
| `module_completion_rate` | Hoàn thành | Bỏ lỡ | Đầy đủ |

### Recommendations:
- **type**: `quiz`, `forum`, `hvp`, `page`, `resource`...
- **purpose**: `assessment`, `collaboration`, `learning`, `other`
- **difficulty**: `easy`, `medium`, `hard`
- **q_value**: Giá trị ưu tiên (cao = nên làm trước)

---

## 📝 CASE STUDY: Sinh viên ví dụ

### Input features cho sinh viên #12345:
```
mean_module_grade: 0.6      → Điểm TB (60%)
total_events: 0.9           → Hoạt động cao
viewed: 0.5                 → Xem tài liệu vừa phải
attempt: 0.2                → ÍT LÀM BÀI (20%) ⚠️
feedback_viewed: 0.8        → Xem feedback nhiều
module_count: 0.3           → Tham gia ít module
course_module_completion: 0.8 → Hoàn thành tốt (80%)
```

### Phân tích từ output:
✅ **Điểm mạnh:**
- Hoàn thành module tốt (80%)
- Xem lại feedback nhiều (80%)
- Không gặp khó khăn (1.6%)

⚠️ **Điểm yếu:**
- Tham gia thấp (46.7%)
- Ít làm bài kiểm tra (20%)
- Tiến độ chung chậm (30%)

### 💡 Hệ thống gợi ý:
1. **Quiz hard** → Đẩy mạnh assessment
2. **Quiz hard** → Tiếp tục đánh giá
3. **Forum** → Tăng collaboration
4. **Video** → Review kiến thức
5. **Quiz** → Thực hành

### 🎯 Chiến lược:
→ Sinh viên này **cần động lực làm bài kiểm tra** nhiều hơn
→ Thuộc **Cluster 2** (có thể là nhóm "Review nhiều, thực hành ít")

---

## ⚙️ CÁCH CHẠY

### 1. Start API server:
```bash
cd demo_pineline/step7_qlearning
uvicorn api_service:app --reload --port 8080
```

### 2. Test API:
```bash
python test_api_example.py
```

### 3. Hoặc dùng curl:
```bash
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 12345,
    "features": {
      "mean_module_grade": 0.6,
      "total_events": 0.9,
      "viewed": 0.5,
      "attempt": 0.2,
      "feedback_viewed": 0.8,
      "module_count": 0.3,
      "course_module_completion": 0.8
    },
    "top_k": 5
  }'
```

---

## 🐛 ĐÃ FIX

### ✅ Issue 1: `student_id` bị NULL
**Trước:**
```python
return RecommendResponse(
    student_id=None,  # ❌ Luôn NULL
    ...
)
```

**Sau:**
```python
class RecommendRequest(BaseModel):
    student_id: Optional[int] = None  # ✅ Nhận từ request
    ...

return RecommendResponse(
    student_id=req.student_id,  # ✅ Trả về đúng
    ...
)
```

### ⚠️ Issue 2: Q-values = 0.0
**Nguyên nhân:**
- State chưa được training trong Q-table
- Hoặc fallback sang random recommendations

**Giải pháp:**
- Train thêm episodes
- Check: `model_info.n_states_in_qtable` vs số state thực tế
- Log xem state có match với Q-table không

---

## 🔗 Files liên quan

- `api_service.py` - Main API code (✅ đã fix)
- `API_INPUT_OUTPUT_EXPLAINED.md` - Chi tiết đầy đủ
- `test_api_example.py` - Test examples
- `cluster_profiles.json` - Cluster definitions
- `course_structure.json` - Action space
- `models/qlearning_model.pkl` - Trained model
