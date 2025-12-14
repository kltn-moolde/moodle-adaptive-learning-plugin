# Moodle API Client - Implementation Summary

## Cấu hình
- **Moodle URL**: `http://139.99.103.223:9090`
- **Token**: `36603001ec5cfd97c8b91206e102d748`
- **Course ID**: `2` (default)

---

## Các API đã implement ✅

### 1. `get_user_logs(user_id, module_id, start_time, end_time)`
- **API Moodle**: `local_userlog_get_logs`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
  - `moduleid`: Module/Section ID (required)
  - `starttime`: Unix timestamp (optional)
  - `endtime`: Unix timestamp (optional)
- **Trả về**: List of log events
- **Status**: ✅ Hoạt động

### 2. `get_user_scores(user_id, section_id)`
- **API Moodle**: `local_userlog_get_user_scores`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
  - `sectionid`: Section ID (optional)
- **Trả về**: List of quiz scores với các trường:
  - `moduleid`: Module ID
  - `activityid`: Quiz ID
  - `activityname`: Tên quiz
  - `activitytype`: "quiz"
  - `score`: Điểm chuẩn hóa (0-1)
  - `rawscore`: Điểm thô
  - `maxscore`: Điểm tối đa
  - `attempt`: Số lần thử
  - `timecompleted`: Timestamp hoàn thành
- **Status**: ✅ Hoạt động

### 3. `get_module_progress(user_id, module_id)`
- **API Moodle**: `local_userlog_get_completion_rate`
- **Tham số**: 
  - `userid`: User ID
  - `moduleid`: Module ID
- **Trả về**: 
  - `progress`: Tỷ lệ hoàn thành (0-1)
  - `completed_activities`: Danh sách activity đã hoàn thành
  - `total_activities`: Tổng số activity
  - `time_spent`: **⚠️ MOCKUP - luôn trả về 0** (chưa có trong API)
- **Status**: ✅ Hoạt động (ngoại trừ time_spent)

### 4. `get_course_structure()`
- **API Moodle**: `core_course_get_contents` (standard API)
- **Tham số**: 
  - `courseid`: Course ID
- **Trả về**: Course structure với modules và activities
- **Status**: ✅ Hoạt động

### 5. `get_quiz_attempts(user_id)`
- **API Moodle**: `local_userlog_get_quiz_attempts`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Tổng số lần thử quiz
- **Status**: ✅ Hoạt động

### 6. `get_total_quiz_time(user_id)`
- **API Moodle**: `local_userlog_get_total_quiz_time`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Tổng thời gian làm quiz (seconds)
- **Status**: ✅ Hoạt động

### 7. `get_resource_views(user_id)`
- **API Moodle**: `local_userlog_get_resource_views`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Dictionary với số lần xem resource theo loại
- **Status**: ✅ Hoạt động

### 8. `get_learning_days(user_id)`
- **API Moodle**: `local_userlog_get_learning_days`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Số ngày học
- **Status**: ✅ Hoạt động

### 9. `get_avg_quiz_score(user_id)`
- **API Moodle**: `local_userlog_get_avg_quiz_score`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Điểm trung bình quiz (0-1)
- **Status**: ✅ Hoạt động

### 10. `get_section_completion(user_id, section_id)`
- **API Moodle**: `local_userlog_get_section_completion`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
  - `sectionid`: Section ID
- **Trả về**: 
  - `total`: Tổng số activity
  - `completed`: Số activity đã hoàn thành
  - `rate`: Tỷ lệ hoàn thành
- **Status**: ✅ Hoạt động

### 11. `get_grade_status(user_id)`
- **API Moodle**: `local_userlog_get_grade_status`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Grade status information
- **Status**: ✅ Hoạt động

### 12. `get_total_study_time(user_id)`
- **API Moodle**: `local_userlog_get_total_study_time`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Tổng thời gian học (seconds)
- **Status**: ✅ Hoạt động

### 13. `get_user_activity_summary(user_id)`
- **API Moodle**: `local_userlog_get_user_object_activity_summary`
- **Tham số**: 
  - `userid`: User ID
  - `courseid`: Course ID
- **Trả về**: Activity summary
- **Status**: ✅ Hoạt động

### 14. `get_quiz_questions(quiz_id)`
- **API Moodle**: `local_userlog_get_quiz_questions`
- **Tham số**: 
  - `quizid`: Quiz ID
- **Trả về**: List of quiz questions
- **Status**: ✅ Hoạt động

### 15. `get_grade_course()`
- **API Moodle**: `local_userlog_get_grade_course`
- **Tham số**: 
  - `courseid`: Course ID
- **Trả về**: List of user grades in course
- **Status**: ✅ Hoạt động

---

## Các trường MOCKUP ⚠️

### 1. `get_user_cluster(user_id)` - **TOÀN BỘ FUNCTION LÀ MOCKUP**
- **Lý do**: Chưa có API endpoint cho user clustering
- **Giá trị mockup**: Luôn trả về `3` (cluster trung bình)
- **TODO**: Cần implement API endpoint `mod_adaptivelearning_get_user_cluster`
- **Cấu trúc API cần có**:
  ```python
  # Input
  {
      'userid': int,
      'courseid': int
  }
  
  # Output
  {
      'clusterid': int (0-6),
      'clustername': str,
      'assigned_at': timestamp
  }
  ```

### 2. `time_spent` field trong `get_module_progress()`
- **Lý do**: API `local_userlog_get_completion_rate` chưa trả về trường này
- **Giá trị mockup**: Luôn trả về `0`
- **TODO**: Cần update API để thêm trường `time_spent`
- **Comment trong code**: 
  ```python
  'time_spent': result.get('time_spent', 0)  # MOCKUP: time_spent field
  ```

---

## Cách sử dụng

```python
from services.moodle_api_client import MoodleAPIClient

# Initialize client (đã có default values)
client = MoodleAPIClient()

# Hoặc custom
client = MoodleAPIClient(
    moodle_url="http://139.99.103.223:9090",
    ws_token="36603001ec5cfd97c8b91206e102d748",
    course_id=2
)

# Lấy logs của user (cần module_id)
logs = client.get_user_logs(user_id=2, module_id=1)

# Lấy điểm của user
scores = client.get_user_scores(user_id=2)

# Lấy progress của user trong module
progress = client.get_module_progress(user_id=2, module_id=1)

# Lấy cluster của user (MOCKUP - sẽ trả về 3)
cluster = client.get_user_cluster(user_id=2)

# Batch processing cho nhiều users
user_data = client.get_bulk_user_data(
    user_ids=[2, 3, 4],
    module_id=1
)
```

---

## Testing

Chạy test:
```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/services
python3 moodle_api_client.py
```

---

## Notes

1. **Module ID là required** cho `get_user_logs()` - khác với document ban đầu nói là optional
2. **Section ID** trong `get_user_scores()` tương đương với module ID
3. Tất cả các API calls đều có error handling và trả về giá trị default nếu có lỗi
4. API client sử dụng `requests` library để call REST API của Moodle
5. Tất cả timestamp đều dùng Unix timestamp format

---

## Checklist Implementation

- ✅ Basic API client setup
- ✅ Authentication với token
- ✅ Error handling
- ✅ get_user_logs
- ✅ get_user_scores  
- ✅ get_module_progress
- ✅ get_course_structure
- ✅ All helper methods (quiz_attempts, quiz_time, etc.)
- ⚠️ get_user_cluster (MOCKUP)
- ⚠️ time_spent field (MOCKUP)
- ✅ Batch processing
- ✅ Testing function
- ✅ Documentation

---

## TODO - Cần implement trong tương lai

1. **API cho user clustering**:
   - Function name: `mod_adaptivelearning_get_user_cluster`
   - Return cluster ID (0-6) cho user

2. **Thêm time_spent vào completion_rate API**:
   - Update `local_userlog_get_completion_rate` để tính và trả về thời gian học

3. **Caching** (optional):
   - Cache course structure để không phải fetch nhiều lần
   - Cache user cluster assignments

4. **Rate limiting** (optional):
   - Implement rate limiting cho batch requests
   - Retry logic cho failed requests
