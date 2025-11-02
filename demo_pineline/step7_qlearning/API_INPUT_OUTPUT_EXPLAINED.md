# API Input/Output Giải Thích Chi Tiết

## Endpoint: POST /api/recommend

### 📥 INPUT (Request Body)

API nhận vào một JSON object với cấu trúc sau:

```json
{
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
}
```

#### Các trường INPUT:

1. **`features`** (optional, Dict[str, float]):
   - Đây là **thông tin học tập của sinh viên** được chuẩn hóa (normalized) về khoảng [0, 1]
   - Mỗi feature đại diện cho một khía cạnh học tập:
     - `mean_module_grade`: Điểm trung bình các module (0.6 = 60%)
     - `total_events`: Tổng số sự kiện/hoạt động (đã chuẩn hóa = 0.9)
     - `viewed`: Số lần xem tài liệu (0.5 = trung bình)
     - `attempt`: Số lần làm bài (0.2 = ít)
     - `feedback_viewed`: Xem phản hồi (0.8 = cao)
     - `module_count`: Số module đã tham gia (0.3 = ít)
     - `course_module_completion`: Tỷ lệ hoàn thành module (0.8 = 80%)

2. **`state`** (optional, List[float]):
   - Vector trạng thái 12 chiều đã được xử lý
   - **Chỉ dùng khi bạn đã có state vector sẵn** (không cần features)
   - Nếu có `state`, API sẽ bỏ qua `features`

3. **`top_k`** (required, int):
   - Số lượng bài học/hoạt động được gợi ý
   - Ví dụ: `top_k: 5` nghĩa là muốn 5 gợi ý

4. **`exclude_action_ids`** (optional, List[int]):
   - Danh sách ID các hoạt động cần loại trừ
   - Ví dụ: `[64, 70]` nghĩa là không gợi ý 2 hoạt động này

---

### 📤 OUTPUT (Response)

```json
{
    "success": true,
    "student_id": null,
    "cluster_id": 2,
    "cluster_name": "Cluster 2",
    "state_vector": [0.6, 0.467, 0.016, ...],
    "state_description": {...},
    "recommendations": [...],
    "model_info": {...}
}
```

#### Các trường OUTPUT:

1. **`success`** (bool):
   - `true` nếu API xử lý thành công
   - `false` nếu có lỗi

2. **`student_id`** (null):
   - **ĐANG BỊ NULL** vì API không nhận ID sinh viên trong input
   - Để fix: Cần thêm trường `student_id` vào RecommendRequest

3. **`cluster_id`** (int):
   - ID của nhóm sinh viên (cluster) mà hệ thống dự đoán sinh viên này thuộc về
   - Ví dụ: `2` = Sinh viên thuộc Cluster 2
   - Được tính bằng cách so sánh features với cluster_profiles.json

4. **`cluster_name`** (str):
   - Tên mô tả của cluster
   - Ví dụ: "Cluster 2" hoặc "Struggling Learner" (nếu có AI profile)

5. **`state_vector`** (List[float]):
   - Vector 12 chiều đại diện cho trạng thái học tập của sinh viên
   - Được xây dựng từ features bởi `MoodleStateBuilder`
   - Gồm 12 giá trị normalized:
     ```
     [mean_module_grade, total_events, viewed, attempt, 
      feedback_viewed, module_count, course_module_completion, ...]
     ```

6. **`state_description`** (Dict):
   - **Mô tả chi tiết trạng thái** học tập theo 3 nhóm:
   
   **a) Performance (Hiệu suất):**
   ```json
   "performance": {
       "knowledge_level": 0.6,          // Mức độ kiến thức (60%)
       "engagement_level": 0.467,        // Mức độ tham gia (46.7%)
       "struggle_indicator": 0.016       // Chỉ số gặp khó khăn (1.6% - thấp)
   }
   ```

   **b) Activity Patterns (Mẫu hoạt động):**
   ```json
   "activity_patterns": {
       "submission_activity": 0.0,       // Nộp bài: không
       "review_activity": 0.8,           // Xem lại: cao (80%)
       "resource_usage": 0.5,            // Dùng tài liệu: trung bình
       "assessment_engagement": 0.2,     // Làm bài kiểm tra: thấp
       "collaborative_activity": 0.0     // Hoạt động nhóm: không
   }
   ```

   **c) Completion Metrics (Chỉ số hoàn thành):**
   ```json
   "completion_metrics": {
       "overall_progress": 0.3,          // Tiến độ tổng thể: 30%
       "module_completion_rate": 0.8,    // Tỷ lệ hoàn thành module: 80%
       "activity_diversity": 0.143,      // Đa dạng hoạt động: 14.3%
       "completion_consistency": 0.67    // Tính nhất quán: 67%
   }
   ```

7. **`recommendations`** (List[Dict]):
   - Danh sách top_k hoạt động được gợi ý (sắp xếp theo Q-value)
   - Mỗi recommendation gồm:
   ```json
   {
       "action_id": 64,                  // ID hoạt động trong Moodle
       "name": "bài kiểm tra bài 2 - hard",  // Tên hoạt động
       "type": "quiz",                   // Loại: quiz, forum, hvp...
       "purpose": "assessment",          // Mục đích: assessment, collaboration...
       "difficulty": "hard",             // Độ khó: easy, medium, hard
       "q_value": 0.0                    // Giá trị Q (ưu tiên)
   }
   ```

8. **`model_info`** (Dict):
   - Thông tin về model Q-Learning:
   ```json
   {
       "model_loaded": true,             // Model đã load thành công
       "n_states_in_qtable": 1816,      // Số state trong Q-table
       "total_updates": 30000,          // Tổng số lần cập nhật Q-table
       "episodes": 1000                  // Số episode đã training
   }
   ```

---

## 🔍 Luồng Xử Lý

```
INPUT features 
    ↓
StateBuilder → state_vector (12 chiều)
    ↓
find_closest_cluster() → cluster_id & cluster_name
    ↓
Q-Learning Agent → top_k recommendations (dựa trên Q-values)
    ↓
OUTPUT response
```

---

## ⚠️ Vấn Đề Hiện Tại

### 1. **`student_id` bị NULL**

**Nguyên nhân:** 
- API không nhận `student_id` trong request
- Code hiện tại: `student_id=None` (line 263)

**Giải pháp:**
```python
# Thêm vào RecommendRequest (line 34):
class RecommendRequest(BaseModel):
    student_id: Optional[int] = None  # 👈 THÊM DÒNG NÀY
    features: Optional[Dict[str, float]] = None
    ...

# Cập nhật response (line 262):
return RecommendResponse(
    success=True,
    student_id=req.student_id,  # 👈 THAY ĐỔI TỪ None
    ...
)
```

### 2. **Q-values đều = 0.0**

**Nguyên nhân:**
- State này chưa được training đủ trong Q-table
- Hoặc model fallback sang random recommendations

**Giải pháp:**
- Training thêm episodes
- Kiểm tra xem state có trong Q-table không

---

## 💡 Cách Sử Dụng Đúng

### Test với student_id:
```json
POST http://localhost:8080/api/recommend
{
    "student_id": 12345,
    "features": {
        "mean_module_grade": 0.75,
        "total_events": 0.8,
        "viewed": 0.6,
        "attempt": 0.5,
        "feedback_viewed": 0.9,
        "module_count": 0.4,
        "course_module_completion": 0.85
    },
    "top_k": 3,
    "exclude_action_ids": [64, 70]
}
```

### Hoặc dùng state vector trực tiếp:
```json
{
    "student_id": 12345,
    "state": [0.75, 0.8, 0.6, 0.5, 0.9, 0.4, 0.85, 0.0, 0.5, 0.7, 0.3, 0.8],
    "top_k": 3
}
```

---

## 📊 Ý Nghĩa Output Trong Thực Tế

Với output ví dụ của bạn:

### Student Profile (từ state_description):
- **Kiến thức:** Trung bình (60%)
- **Tham gia:** Thấp (46.7%)
- **Không gặp khó khăn** (1.6%)
- **Xem lại nhiều** (80%) nhưng **ít làm bài kiểm tra** (20%)
- **Tiến độ chậm** (30%) mặc dù **hoàn thành module tốt** (80%)

### Recommendations:
Hệ thống gợi ý 5 hoạt động:
1. **bài kiểm tra bài 2 - hard** → Tăng assessment engagement
2. **bài kiểm tra bài 3 - hard** → Tiếp tục đánh giá
3. **Announcements (forum)** → Tăng collaborative activity
4. **Video bài giảng bài 2** → Review kiến thức
5. **bài kiểm tra bài 1 - hard** → Củng cố cơ bản

### Cluster 2:
Sinh viên thuộc nhóm "Cluster 2" - có thể là nhóm:
- Có kiến thức cơ bản
- Cần động lực làm bài kiểm tra
- Review nhiều nhưng thiếu thực hành

---

## 🛠️ Next Steps

1. ✅ **Fix student_id NULL** (xem code fix bên dưới)
2. ✅ **Kiểm tra Q-values** (train thêm hoặc log chi tiết)
3. ✅ **Thêm metadata** (timestamp, confidence score...)
4. ✅ **Logging** để debug cluster prediction

