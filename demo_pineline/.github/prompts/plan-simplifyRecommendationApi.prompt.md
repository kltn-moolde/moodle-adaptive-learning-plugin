# Plan: Simplify Recommendation API

## Goal
Đơn giản hóa API gợi ý học tập - Frontend chỉ cần gọi với `user_id` và `course_id`, backend tự động lấy tất cả thông tin cần thiết.

## Current State

### Existing Collections
- `user_states`: State hiện tại của user theo (user_id, course_id, module_id)
- `state_history`: Lịch sử states theo timeline
- `student_lo_mastery`: LO mastery scores theo (user_id, course_id)

### Current API (Complex)
```
POST /api/recommend
Body: {
  "student_id": 123,
  "course_id": 5,
  "features": {...},  // Nhiều fields phức tạp
  "state": [0, 1, 0.5, 0.7, 2, 3],  // Hoặc state vector
  "lo_mastery": {...}
}
```

## Target State

### New Simplified API
```
GET /api/recommend/{user_id}/{course_id}
Query params (optional):
  - module_id: int (nếu muốn recommend cho module cụ thể)
  - top_k: int (default: 5)
```

**Response:**
```json
{
  "success": true,
  "user_id": 4,
  "course_id": 5,
  "current_state": {
    "cluster_id": 2,
    "module_id": 39,
    "progress": 0.8,
    "score": 0.75,
    "phase": 2,
    "engagement": 3
  },
  "lo_mastery": {
    "LO1.1": 0.65,
    "LO1.2": 0.72,
    ...
  },
  "recommendations": [
    {
      "action_id": 5,
      "action_name": "view_video",
      "module_id": 40,
      "q_value": 0.85,
      "activities": [...],
      "reason": "Based on your current progress..."
    }
  ]
}
```

## Implementation Steps

### Step 1: Add `get_current_state()` to StateRepository
**File:** `services/repository/state_repository.py`

```python
def get_current_state(
    self,
    user_id: int,
    course_id: int,
    module_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Get current state for user in course
    
    Args:
        user_id: User ID
        course_id: Course ID
        module_id: Optional - specific module (if None, get most recent)
        
    Returns:
        State document or None
    """
    query = {"user_id": user_id, "course_id": course_id}
    if module_id is not None:
        query["module_id"] = module_id
    
    # Get most recent state
    state_doc = self.user_states.find_one(
        query,
        sort=[("updated_at", DESCENDING)]
    )
    
    return state_doc
```

### Step 2: Create Smart Recommendation Service
**File:** `services/business/smart_recommendation_service.py` (NEW)

```python
class SmartRecommendationService:
    """
    Smart recommendation service with auto-fetch capabilities
    Simplifies recommendation flow by auto-loading state and mastery
    """
    
    def __init__(
        self,
        state_repository: StateRepository,
        lo_mastery_service: LOMasteryService,
        model_manager: ModelManager
    ):
        self.state_repo = state_repository
        self.lo_mastery_service = lo_mastery_service
        self.model_manager = model_manager
    
    def get_recommendations_simple(
        self,
        user_id: int,
        course_id: int,
        module_id: Optional[int] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Get recommendations with auto-fetched state and mastery
        
        Args:
            user_id: User ID
            course_id: Course ID
            module_id: Optional specific module
            top_k: Number of recommendations
            
        Returns:
            Complete recommendation response
        """
        # 1. Get current state from DB
        state_doc = self.state_repo.get_current_state(
            user_id, course_id, module_id
        )
        
        if not state_doc:
            # No state found - create default for new user
            state = self._create_default_state(user_id, course_id)
        else:
            state = tuple(state_doc['state_tuple'])
        
        # 2. Get LO mastery from service (with cache)
        mastery_data = self.lo_mastery_service.get_student_mastery(
            user_id, course_id, use_cache=True
        )
        
        lo_mastery = mastery_data.get('lo_mastery', {}) if mastery_data else {}
        if not lo_mastery:
            lo_mastery = self._create_default_mastery()
        
        # 3. Get recommendation service for this course
        services = self.model_manager.get_services_for_course(course_id)
        recommendation_service = services['recommendation_service']
        
        # 4. Generate recommendations
        cluster_id = int(state[0])
        module_idx = int(state[1])
        
        recommendations = recommendation_service.get_recommendations(
            state=state,
            cluster_id=cluster_id,
            top_k=top_k,
            lo_mastery=lo_mastery,
            module_idx=module_idx
        )
        
        # 5. Build response
        return {
            'success': True,
            'user_id': user_id,
            'course_id': course_id,
            'current_state': self._format_state(state, state_doc),
            'lo_mastery': lo_mastery,
            'recommendations': recommendations
        }
    
    def _create_default_state(self, user_id, course_id):
        """Create default state for new user"""
        # Default: cluster 2 (medium), module 0, low progress/score, phase 0, engagement 2
        return (2, 0, 0.0, 0.0, 0, 2)
    
    def _create_default_mastery(self):
        """Create default LO mastery"""
        return {f'LO{i}.{j}': 0.4 for i in range(1, 6) for j in range(1, 3)}
    
    def _format_state(self, state, state_doc):
        """Format state for response"""
        return {
            'cluster_id': int(state[0]),
            'module_idx': int(state[1]),
            'progress_bin': float(state[2]),
            'score_bin': float(state[3]),
            'learning_phase': int(state[4]),
            'engagement_level': int(state[5]),
            'module_id': state_doc.get('module_id') if state_doc else None,
            'last_updated': state_doc.get('updated_at') if state_doc else None
        }
```

### Step 3: Create New Simplified API Endpoint
**File:** `api/routes/recommendations.py`

Add new endpoint:

```python
@router.get('/recommend/{user_id}/{course_id}')
async def get_recommendations_simple(
    user_id: int,
    course_id: int,
    module_id: Optional[int] = Query(None, description="Specific module (optional)"),
    top_k: int = Query(5, description="Number of recommendations")
):
    """
    🆕 Simplified recommendation API - chỉ cần user_id và course_id
    
    Backend tự động:
    - Lấy current state từ user_states collection
    - Lấy LO mastery từ student_lo_mastery collection
    - Generate recommendations
    
    Args:
        user_id: User ID
        course_id: Course ID
        module_id: Optional - specific module
        top_k: Number of recommendations (default: 5)
        
    Returns:
        Complete recommendation with state and mastery info
        
    Examples:
        GET /api/recommend/4/5
        GET /api/recommend/4/5?module_id=39&top_k=3
    """
    try:
        result = smart_recommendation_service.get_recommendations_simple(
            user_id=user_id,
            course_id=course_id,
            module_id=module_id,
            top_k=top_k
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Error generating recommendations: {str(e)}'
        )
```

### Step 4: Update Dependencies
**File:** `api/dependencies.py`

```python
from services.business.smart_recommendation_service import SmartRecommendationService

# Initialize smart recommendation service
smart_recommendation_service = SmartRecommendationService(
    state_repository=state_repository,
    lo_mastery_service=lo_mastery_service,
    model_manager=model_manager
)
```

### Step 5: Ensure user_states is Updated
**File:** `api/routes/webhook.py`

Make sure when processing logs, we update `user_states`:

```python
# After state update
state_repository.save_state(
    user_id=user_id,
    module_id=module_id,
    state=new_state,
    course_id=course_id,
    save_history=True  # Also save to history
)
```

## Migration Considerations

### Database Schema (Already exists - just verify)
```javascript
// user_states
{
  user_id: 4,
  course_id: 5,
  module_id: 39,
  state: {
    cluster_id: 2,
    module_idx: 1,
    progress_bin: 0.8,
    score_bin: 0.75,
    learning_phase: 2,
    engagement_level: 3
  },
  state_tuple: [2, 1, 0.8, 0.75, 2, 3],
  updated_at: ISODate("2025-12-12T10:30:00Z"),
  metadata: {...}
}

// Indexes (already exists)
{user_id: 1, course_id: 1, module_id: 1} unique
{updated_at: -1}
```

### Backward Compatibility
- Keep old `/api/recommend` POST endpoint for compatibility
- New `/api/recommend/{user_id}/{course_id}` GET endpoint for simplicity
- Frontend can gradually migrate to new API

## Testing Plan

### Test Case 1: User with existing state
```bash
# Sync state và mastery trước
curl -X POST "http://localhost:8080/api/lo-mastery/sync/5?user_id=4"

# Test new API
curl "http://localhost:8080/api/recommend/4/5"

# Expected: Returns recommendations with real state and mastery
```

### Test Case 2: New user (no state)
```bash
curl "http://localhost:8080/api/recommend/999/5"

# Expected: Returns recommendations with default state
```

### Test Case 3: Specific module
```bash
curl "http://localhost:8080/api/recommend/4/5?module_id=39"

# Expected: Returns recommendations for that module
```

## Benefits

### For Frontend
✅ **Đơn giản**: Chỉ cần user_id + course_id
✅ **Ít lỗi**: Không cần construct state vector phức tạp
✅ **Nhanh hơn**: Ít data transfer

### For Backend
✅ **Single source of truth**: Data từ DB, không cần FE gửi
✅ **Consistent**: State luôn sync với DB
✅ **Cacheable**: Lo mastery có cache 5 phút

### For System
✅ **Maintainable**: Logic tập trung ở backend
✅ **Scalable**: Dễ optimize caching/query
✅ **Testable**: Dễ test với DB state

## Timeline

- **Step 1-2**: 30 mins - Add repository method + smart service
- **Step 3**: 15 mins - New API endpoint
- **Step 4**: 5 mins - Update dependencies
- **Step 5**: 10 mins - Verify webhook updates user_states
- **Testing**: 20 mins - Test all scenarios

**Total**: ~1.5 hours

## Success Criteria

✅ New API endpoint `/api/recommend/{user_id}/{course_id}` works
✅ Automatically fetches state from user_states
✅ Automatically fetches LO mastery from student_lo_mastery
✅ Returns same quality recommendations as old API
✅ Handles new users gracefully (default state)
✅ Old API still works (backward compatibility)
