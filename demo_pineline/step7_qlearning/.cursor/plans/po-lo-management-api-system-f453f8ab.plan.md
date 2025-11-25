<!-- f453f8ab-6b16-461f-84a8-3f9ef2846584 542de6a8-2f8e-4b79-b585-b2df605c2de7 -->
# LO Mastery MongoDB Storage System

## Mục tiêu

- Lưu trữ LO mastery của từng học sinh theo từng course vào MongoDB
- Tích hợp với Moodle API để lấy scores, completion, activity data
- Tạo API endpoints để query và update LO mastery
- Refactor LOMasteryTracker và RewardCalculatorV2 để dùng MongoDB thay vì memory cache
- Tính toán LO mastery từ Moodle data (scores, completion, attempts)

## 1. MongoDB Schema Design

### Collection: `lo_mastery`

```json
{
  "_id": ObjectId,
  "user_id": int,           // Required, indexed
  "course_id": int,         // Required, indexed
  "lo_id": str,             // Required, indexed (e.g., "LO1.1")
  "mastery": float,         // 0.0-1.0
  "last_updated": datetime,
  "last_activity_id": int,  // Activity that last updated this LO
  "update_count": int,      // Number of times updated
  "metadata": {
    "source": "moodle_api" | "calculated" | "manual",
    "calculation_method": "..."
  }
}
```

### Collection: `lo_mastery_history`

```json
{
  "_id": ObjectId,
  "user_id": int,
  "course_id": int,
  "lo_id": str,
  "old_mastery": float,
  "new_mastery": float,
  "activity_id": int,
  "timestamp": datetime,
  "source": "moodle_api" | "calculated" | "manual"
}
```

### Indexes:

- `lo_mastery`: unique index on (user_id, course_id, lo_id)
- `lo_mastery`: index on (user_id, course_id)
- `lo_mastery_history`: index on (user_id, course_id, lo_id, timestamp)

## 2. Service Layer

### File: `services/lo_mastery_repository.py`

- `LOMasteryRepository` class:
  - `get_mastery(user_id: int, course_id: int, lo_id: Optional[str] = None) -> Dict`
    - Get LO mastery for user/course (all LOs or specific LO)
  - `save_mastery(user_id: int, course_id: int, lo_id: str, mastery: float, activity_id: Optional[int] = None) -> bool`
    - Save/update LO mastery
  - `get_all_lo_mastery(user_id: int, course_id: int) -> Dict[str, float]`
    - Get all LO mastery as dict {lo_id: mastery}
  - `save_mastery_batch(user_id: int, course_id: int, mastery_dict: Dict[str, float]) -> bool`
    - Save multiple LOs at once
  - `get_mastery_history(user_id: int, course_id: int, lo_id: Optional[str] = None, limit: int = 100) -> List[Dict]`
    - Get history of mastery changes
  - `calculate_mastery_from_moodle(user_id: int, course_id: int, moodle_client: MoodleAPIClient) -> Dict[str, float]`
    - Calculate LO mastery from Moodle API data (scores, completion, attempts)

## 3. LO Mastery Calculation Logic

### Từ Moodle API data:

1. **Quiz Scores**: 

   - Lấy scores từ `get_user_scores()` hoặc `get_avg_quiz_score()`
   - Map activity_id → LO_ids (từ Po_Lo.json)
   - Mastery = normalized_score (0-1)

2. **Activity Completion**:

   - Lấy completion từ `get_module_progress()` hoặc `get_section_completion()`
   - Completed activities → small mastery boost (0.05-0.1)

3. **Assignment Submissions**:

   - Lấy từ activity logs hoặc grade data
   - Submitted → mastery boost based on grade

4. **Combined Formula**:
   ```
   mastery[LO] = weighted_average(
     quiz_scores[activities_for_LO],
     completion_bonus[activities_for_LO],
     assignment_scores[activities_for_LO]
   )
   ```


## 4. API Endpoints

### File: `api_service.py` (thêm endpoints)

#### LO Mastery Management:

- `GET /api/lo-mastery/{user_id}/{course_id}` - Lấy tất cả LO mastery cho user/course
- `GET /api/lo-mastery/{user_id}/{course_id}/{lo_id}` - Lấy mastery cho LO cụ thể
- `PUT /api/lo-mastery/{user_id}/{course_id}/{lo_id}` - Update mastery cho LO
- `POST /api/lo-mastery/{user_id}/{course_id}/sync` - Sync từ Moodle API (tính toán lại từ Moodle data)
- `GET /api/lo-mastery/{user_id}/{course_id}/history` - Lấy lịch sử thay đổi mastery
- `GET /api/lo-mastery/{user_id}/{course_id}/weak-los` - Lấy danh sách LO yếu (mastery < threshold)

## 5. Refactor Existing Components

### File: `core/lo_mastery_tracker.py`

- Thay `mastery_cache` (memory) bằng `LOMasteryRepository` (MongoDB)
- `__init__` nhận `lo_mastery_repository: Optional[LOMasteryRepository] = None`
- `get_mastery()` load từ MongoDB thay vì cache
- `update_mastery()` save vào MongoDB và history

### File: `core/reward_calculator_v2.py`

- Thay `lo_mastery_cache` (memory) bằng `LOMasteryRepository` (MongoDB)
- `__init__` nhận `lo_mastery_repository: Optional[LOMasteryRepository] = None`
- `get_lo_mastery_state()` load từ MongoDB
- `calculate_lo_mastery_delta()` update vào MongoDB

## 6. Moodle API Integration

### File: `services/lo_mastery_calculator.py`

- `LOMasteryCalculator` class:
  - `calculate_from_moodle_scores(user_id: int, course_id: int, moodle_client: MoodleAPIClient, po_lo_service: POLOService) -> Dict[str, float]`
    - Tính LO mastery từ Moodle quiz scores
  - `calculate_from_completion(user_id: int, course_id: int, moodle_client: MoodleAPIClient, po_lo_service: POLOService) -> Dict[str, float]`
    - Tính LO mastery từ activity completion
  - `calculate_combined(user_id: int, course_id: int, moodle_client: MoodleAPIClient, po_lo_service: POLOService) -> Dict[str, float]`
    - Combine scores + completion để tính mastery

## 7. Background Sync Service (Optional)

### File: `services/lo_mastery_sync_service.py`

- `LOMasterySyncService` class:
  - `sync_user(user_id: int, course_id: int) -> Dict`
    - Sync LO mastery cho 1 user từ Moodle API
  - `sync_course(course_id: int, user_ids: Optional[List[int]] = None) -> Dict`
    - Sync LO mastery cho nhiều users trong course
  - Có thể chạy định kỳ (cron job) hoặc trigger từ webhook

## Implementation Order

1. Tạo MongoDB schema và indexes trong `LOMasteryRepository`
2. Tạo `LOMasteryRepository` với CRUD operations
3. Tạo `LOMasteryCalculator` để tính từ Moodle API data
4. Tạo API endpoints cho LO mastery
5. Refactor `LOMasteryTracker` để dùng MongoDB
6. Refactor `RewardCalculatorV2` để dùng MongoDB
7. Tích hợp sync service (optional)
8. Testing với real Moodle API data

## Files to Create/Modify

**New Files:**

- `services/lo_mastery_repository.py`
- `services/lo_mastery_calculator.py`
- `services/lo_mastery_sync_service.py` (optional)

**Modified Files:**

- `api_service.py` - Thêm endpoints cho LO mastery
- `core/lo_mastery_tracker.py` - Dùng MongoDB thay vì memory
- `core/reward_calculator_v2.py` - Dùng MongoDB thay vì memory
- `services/state_repository.py` - Thêm collection constants