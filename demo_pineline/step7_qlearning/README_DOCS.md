# 📚 Q-Learning API Documentation Hub

## 📖 Tài Liệu Đầy Đủ

Workspace này chứa các tài liệu giải thích chi tiết về Q-Learning API:

### 1. **QUICK_GUIDE.md** ⭐ (BẮT ĐẦU TỪ ĐÂY)
   - Hướng dẫn nhanh về Input/Output
   - Các ví dụ sử dụng API
   - Giải thích ngắn gọn các trường dữ liệu
   - **Đọc file này trước!**

### 2. **API_INPUT_OUTPUT_EXPLAINED.md** 📘
   - Giải thích chi tiết từng trường input/output
   - Phân tích ý nghĩa state_description
   - Luồng xử lý dữ liệu
   - Case study cụ thể

### 3. **Q_VALUES_ZERO_EXPLAINED.md** 🔍
   - Giải thích TẠI SAO q_values = 0.0
   - 3 nguyên nhân chính
   - Giải pháp chi tiết
   - Hướng dẫn migrate sang DQN

### 4. **test_api_example.py** 🧪
   - Script test API đầy đủ
   - 6 test cases khác nhau
   - So sánh 3 loại sinh viên
   - **Chạy để test API**

### 5. **debug_qtable.py** 🛠️
   - Tool debug Q-table
   - Phân tích coverage
   - Kiểm tra state có trong Q-table không
   - **Chạy để debug vấn đề q_values = 0**

---

## 🚀 Quick Start

### 1. Start API Server
```bash
cd demo_pineline/step7_qlearning
uvicorn api_service:app --reload --port 8080
```

### 2. Test API
```bash
# Option 1: Python script
python test_api_example.py

# Option 2: curl
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

### 3. Debug Q-table
```bash
python debug_qtable.py
```

---

## 🐛 Đã Fix

### ✅ Issue: `student_id` bị NULL

**File:** `api_service.py`

**Changes:**
```python
# Line 34: Thêm student_id vào request
class RecommendRequest(BaseModel):
    student_id: Optional[int] = None  # ← THÊM MỚI
    features: Optional[Dict[str, float]] = None
    ...

# Line 263: Trả về student_id từ request
return RecommendResponse(
    success=True,
    student_id=req.student_id,  # ← THAY ĐỔI (trước: None)
    ...
)
```

**Test:**
```bash
# Before fix:
{
  "student_id": null,  // ❌ NULL
  ...
}

# After fix:
{
  "student_id": 12345,  // ✅ Correct
  ...
}
```

---

## ⚠️ Vấn Đề Còn Lại

### Q-values = 0.0

**Nguyên nhân chính:** State không có trong Q-table (1816 states)

**Giải pháp:**
1. **Ngắn hạn:** Train thêm với diverse states
2. **Dài hạn:** Chuyển sang Deep Q-Network (DQN)

**Chi tiết:** Xem `Q_VALUES_ZERO_EXPLAINED.md`

---

## 📊 API Endpoints

### GET /api/health
Kiểm tra trạng thái service

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "n_actions": 100,
  "n_states_in_qtable": 1816
}
```

### GET /api/model-info
Thông tin chi tiết về model

**Response:**
```json
{
  "model_loaded": true,
  "n_actions": 100,
  "state_dim": 12,
  "n_states_in_qtable": 1816,
  "total_updates": 30000,
  "episodes": 1000,
  "avg_reward": 5.234
}
```

### POST /api/recommend
Gợi ý học tập cho sinh viên

**Request:**
```json
{
  "student_id": 12345,
  "features": {
    "mean_module_grade": 0.6,
    "total_events": 0.9,
    ...
  },
  "top_k": 5,
  "exclude_action_ids": [64, 70]
}
```

**Response:** Xem `QUICK_GUIDE.md` hoặc `API_INPUT_OUTPUT_EXPLAINED.md`

---

## 📁 File Structure

```
step7_qlearning/
├── api_service.py                     ✅ Main API (ĐÃ FIX)
├── QUICK_GUIDE.md                     📘 Quick reference
├── API_INPUT_OUTPUT_EXPLAINED.md      📖 Detailed docs
├── Q_VALUES_ZERO_EXPLAINED.md         🔍 Debug guide
├── test_api_example.py                🧪 Test suite
├── debug_qtable.py                    🛠️ Debug tool
├── README_DOCS.md                     📚 This file
│
├── core/
│   ├── qlearning_agent.py            🤖 Q-Learning agent
│   ├── state_builder.py              🏗️ State builder
│   └── action_space.py               🎯 Action space
│
├── models/
│   └── qlearning_model.pkl           💾 Trained model
│
└── data/
    ├── course_structure.json         📄 Course data
    └── cluster_profiles.json         👥 Cluster profiles
```

---

## 🎓 Learning Path

### Nếu bạn là Developer:
1. Đọc `QUICK_GUIDE.md` → Hiểu cơ bản
2. Đọc `API_INPUT_OUTPUT_EXPLAINED.md` → Hiểu chi tiết
3. Chạy `test_api_example.py` → Test thực tế
4. Đọc `Q_VALUES_ZERO_EXPLAINED.md` → Debug vấn đề
5. Chạy `debug_qtable.py` → Analyze Q-table

### Nếu bạn là Data Scientist:
1. Đọc `Q_VALUES_ZERO_EXPLAINED.md` → Hiểu vấn đề model
2. Chạy `debug_qtable.py` → Phân tích Q-table
3. Xem `qlearning_agent.py` → Hiểu thuật toán
4. Đọc `API_INPUT_OUTPUT_EXPLAINED.md` → Hiểu features

### Nếu bạn là Tester:
1. Đọc `QUICK_GUIDE.md` → Hiểu cách dùng API
2. Chạy `test_api_example.py` → Test cases
3. Test với các edge cases khác
4. Report bugs

---

## 🔧 Troubleshooting

### 1. API không kết nối được
```bash
# Check server đang chạy?
lsof -i :8080

# Restart server
cd demo_pineline/step7_qlearning
uvicorn api_service:app --reload --port 8080
```

### 2. Q-values đều = 0
```bash
# Debug Q-table
python debug_qtable.py

# Xem giải pháp
cat Q_VALUES_ZERO_EXPLAINED.md
```

### 3. Cluster prediction sai
```bash
# Check cluster_profiles.json
cat data/cluster_profiles.json

# Test với features khác nhau
python test_api_example.py
```

### 4. student_id bị NULL
```bash
# Đảm bảo đã pull code mới nhất
git pull

# Hoặc check api_service.py line 34, 263
grep -n "student_id" api_service.py
```

---

## 📞 Support

### Issues đã biết:
- ✅ **student_id NULL** → Đã fix
- ⚠️ **q_values = 0** → Xem Q_VALUES_ZERO_EXPLAINED.md
- ⚠️ **Q-table coverage thấp** → Train thêm

### Liên hệ:
- **GitHub Issues:** [moodle-adaptive-learning-plugin](https://github.com/kltn-moolde/moodle-adaptive-learning-plugin)
- **Docs:** Xem các file .md trong thư mục này

---

## 🎯 Next Steps

### Short-term (1-2 tuần):
1. ✅ Fix student_id NULL → **DONE**
2. ⏳ Add logging để debug state matching
3. ⏳ Train với more diverse states
4. ⏳ Optimize state hashing

### Long-term (1-2 tháng):
1. 🔄 Migrate to Deep Q-Network (DQN)
2. 🔄 Add confidence scores
3. 🔄 Implement A/B testing
4. 🔄 Add real-time learning

---

## 📚 References

- **Q-Learning:** [Sutton & Barto - Reinforcement Learning](http://incompleteideas.net/book/the-book-2nd.html)
- **DQN:** [Playing Atari with Deep RL](https://arxiv.org/abs/1312.5602)
- **FastAPI:** [Official Docs](https://fastapi.tiangolo.com/)
- **Moodle LMS:** [Developer Docs](https://docs.moodle.org/dev/)

---

**Last updated:** 2025-11-02  
**Version:** 1.0 (student_id fix)  
**Status:** ✅ Production Ready (with known limitations)
