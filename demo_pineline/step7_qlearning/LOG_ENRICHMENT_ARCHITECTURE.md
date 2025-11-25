# Log Enrichment Architecture

## Problem

Khi Moodle gửi log thô như `course_viewed`, log này **KHÔNG** có `module_id` cụ thể:

```json
{
  "userid": 5,
  "courseid": 5,
  "eventname": "\\core\\event\\course_viewed",
  "contextinstanceid": 5,  // ← Đây là course_id, KHÔNG phải module_id
  "timecreated": 1763795984
}
```

**Vấn đề:**
- Log không có `module_id` → Không thể build state cho module nào
- Thiếu thông tin: `progress`, `score`, `time_spent`
- Kết quả: "Built 0 states" ❌

---

## Solution: Log Enrichment

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Receive Log from Moodle                                     │
│  ┌────────────────────────────────────────────────────┐        │
│  │ course_viewed (NO module_id)                       │        │
│  └────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. LogEvent.from_dict() - Detection                            │
│  ┌────────────────────────────────────────────────────┐        │
│  │ if 'course' in eventname and 'viewed' in eventname:│        │
│  │     return None  # Needs enrichment                │        │
│  └────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. LogPreprocessor.enrich_course_level_log()                   │
│  ┌────────────────────────────────────────────────────┐        │
│  │ FOR EACH module in course:                         │        │
│  │   - Call Moodle API: get_module_progress()         │        │
│  │   - Call Moodle API: get_user_scores()             │        │
│  │   - Generate synthetic log event with:             │        │
│  │     * module_id ✓                                  │        │
│  │     * progress ✓                                   │        │
│  │     * score ✓                                      │        │
│  │     * time_spent ✓                                 │        │
│  └────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Result: N Module-Specific Events                            │
│  ┌────────────────────────────────────────────────────┐        │
│  │ Event 1: user=5, module=54, progress=0.6, score=0.8│        │
│  │ Event 2: user=5, module=55, progress=0.4, score=0.7│        │
│  │ Event 3: user=5, module=56, progress=0.2, score=0.5│        │
│  │ ...                                                 │        │
│  │ Event N: user=5, module=N, progress=X, score=Y     │        │
│  └────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. StateBuilder - Build States                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │ FOR EACH enriched event:                           │        │
│  │   - Build 6D state                                 │        │
│  │   - Save to MongoDB                                │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
│  ✓ Built N states (one per module) ✅                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### 1. LogEvent.from_dict() - Detection

**File:** `core/log_models.py`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> Optional['LogEvent']:
    """Returns None if course-level event needs enrichment"""
    
    # Detect course-level events
    if raw_action and 'course' in raw_action.lower() and 'viewed' in raw_action.lower():
        print(f"  ⚠️  Course-level event detected: {raw_action} - needs enrichment")
        return None  # Signal: need enrichment
    
    # If no module_id, skip
    if module_id is None:
        print(f"  ⚠️  Skipping log without module_id: {raw_action}")
        return None
    
    # Normal event - proceed
    return cls(user_id, cluster_id, module_id, ...)
```

### 2. LogPreprocessor - Enrichment

**File:** `core/log_preprocessor.py`

```python
def enrich_course_level_log(self, raw_log: Dict) -> List[Dict]:
    """
    Expand course_viewed → N module events
    
    For each module in course:
    1. Get progress: moodle_client.get_module_progress(user_id, module_id)
    2. Get scores: moodle_client.get_user_scores(user_id, section_id)
    3. Generate synthetic log with all data
    """
    enriched_logs = []
    user_id = raw_log.get('userid')
    
    for module_info in self.modules:
        module_id = module_info['id']
        
        # API call 1: Get progress
        progress_data = self.moodle_client.get_module_progress(user_id, module_id)
        
        # API call 2: Get scores
        scores = self.moodle_client.get_user_scores(user_id)
        
        # Create enriched log
        enriched_log = {
            'userid': user_id,
            'module_id': module_id,  # ✓ Now has module_id
            'progress': progress_data.get('progress', 0.0),  # ✓ Has progress
            'score': avg_score,  # ✓ Has score
            'time_spent': progress_data.get('time_spent', 0),  # ✓ Has time
            'eventname': 'module_progress_updated',  # Synthetic event
            ...
        }
        
        enriched_logs.append(enriched_log)
    
    return enriched_logs
```

### 3. LogPreprocessor.parse_raw_logs() - Integration

```python
def parse_raw_logs(self, raw_logs: List[Dict]) -> List[LogEvent]:
    events = []
    
    for raw_log in raw_logs:
        event = LogEvent.from_dict(raw_log)
        
        # If None → course-level event
        if event is None:
            if self.moodle_client:
                # Enrich into N module events
                enriched_logs = self.enrich_course_level_log(raw_log)
                enriched_logs_to_process.extend(enriched_logs)
            continue
        
        # Normal event
        events.append(event)
    
    # Process enriched logs
    for enriched_log in enriched_logs_to_process:
        event = LogEvent.from_dict(enriched_log)
        if event:
            events.append(event)
    
    return events
```

### 4. LogProcessingPipeline - Connection

**File:** `pipeline/log_processing_pipeline.py`

```python
# Initialize Moodle API client
self.moodle_client = MoodleAPIClient(...)

# Pass to state_builder → preprocessor
self.state_builder.preprocessor.moodle_client = self.moodle_client
```

---

## API Endpoints Used

### get_module_progress(user_id, module_id)

**Moodle Function:** `local_userlog_get_completion_rate`

**Returns:**
```json
{
  "progress": 0.6,           // Completion rate (0-1)
  "completed_activities": [...],
  "total_activities": 10,
  "time_spent": 3600         // Seconds
}
```

### get_user_scores(user_id, section_id)

**Moodle Function:** `local_userlog_get_user_scores`

**Returns:**
```json
{
  "scores": [
    {"quiz_id": 46, "grade": 8.5, "max_grade": 10},
    {"quiz_id": 47, "grade": 9.0, "max_grade": 10}
  ]
}
```

---

## Flow Example

### Input: 1 Course-Level Event

```json
{
  "userid": 5,
  "courseid": 5,
  "eventname": "\\core\\event\\course_viewed",
  "contextinstanceid": 5,
  "timecreated": 1763795984
}
```

### Detection

```
LogEvent.from_dict() → detects 'course_viewed' → returns None
```

### Enrichment

```
LogPreprocessor.enrich_course_level_log()
├─ Call API: get_module_progress(5, 54) → progress=0.6, time=1800s
├─ Call API: get_module_progress(5, 55) → progress=0.4, time=1200s
├─ Call API: get_module_progress(5, 56) → progress=0.2, time=600s
├─ Call API: get_user_scores(5) → [quiz1: 0.8, quiz2: 0.7, ...]
└─ Generate N events (one per module)
```

### Output: N Module-Specific Events

```json
[
  {
    "userid": 5,
    "module_id": 54,
    "eventname": "module_progress_updated",
    "progress": 0.6,
    "score": 0.8,
    "time_spent": 1800,
    "timecreated": 1763795984
  },
  {
    "userid": 5,
    "module_id": 55,
    "eventname": "module_progress_updated",
    "progress": 0.4,
    "score": 0.7,
    "time_spent": 1200,
    "timecreated": 1763795984
  },
  ...
]
```

### Result

```
✓ Built N states (one per module)
✓ Saved N states to MongoDB
✓ Generated N recommendations
```

---

## Configuration

### Enable Enrichment

**api_service.py:**

```python
# Initialize pipeline with Moodle API credentials
pipeline = LogProcessingPipeline(
    cluster_profiles_path="data/cluster_profiles.json",
    course_structure_path="data/course_structure.json",
    moodle_url="http://localhost:8100",  # ← Required for enrichment
    moodle_token="...",                   # ← Required
    course_id=5,                          # ← Required
    mongo_uri="...",
    enable_qtable_updates=True
)
```

### Disable Enrichment (Skip Course-Level Events)

```python
# Without Moodle credentials → enrichment disabled
pipeline = LogProcessingPipeline(
    cluster_profiles_path="data/cluster_profiles.json",
    course_structure_path="data/course_structure.json",
    # No moodle_url/token → enrichment disabled
    mongo_uri="...",
)
```

---

## Testing

### Run Test Suite

```bash
cd demo_pineline/step7_qlearning
python test_log_enrichment.py
```

### Expected Output

```
Test: Course-Level Event Enrichment
====================================

1. Input: Course-level event
   {
     "eventname": "\\core\\event\\course_viewed",
     "contextinstanceid": 5  // NO module_id
   }

2. Detection: Course-level event detected → needs enrichment

3. Enrichment: Calling Moodle API...
   - Module 54: progress=0.6, score=0.8, time=1800s
   - Module 55: progress=0.4, score=0.7, time=1200s
   - Module 56: progress=0.2, score=0.5, time=600s
   ...

4. Result: 6 enriched events generated

5. Processing: Building states...
   ✓ Built 6 states
   ✓ Saved 6 states

Summary:
✓ Input: 1 course-level event
✓ Output: 6 module-specific events
✓ Enrichment: SUCCESS
```

---

## Benefits

### Before (Without Enrichment)

```
Input: course_viewed event
→ No module_id
→ Built 0 states ❌
→ No recommendations
```

### After (With Enrichment)

```
Input: course_viewed event
→ Detect course-level event
→ Call Moodle API for all modules
→ Built N states ✅
→ Generate N recommendations ✅
```

---

## Performance

### API Calls per Course-Level Event

- **N modules** × 1 API call = N calls
- Example: 6 modules → 6 API calls
- Each call: ~100-200ms
- Total enrichment time: ~600-1200ms

### Optimization

**Future:** Batch API endpoint
```python
# Instead of N calls:
get_module_progress(user_id, module_id)  # × N

# Use single call:
get_all_module_progress(user_id)  # × 1
```

---

## Troubleshooting

### "Built 0 states"

**Cause:** Course-level event without enrichment

**Solution:**
1. Check Moodle API credentials in `api_service.py`
2. Verify `moodle_client` is passed to pipeline
3. Check Moodle API is running: `http://localhost:8100`

### "⚠️ Moodle API not available"

**Cause:** MoodleAPIClient not initialized

**Solution:**
```python
# api_service.py
pipeline = LogProcessingPipeline(
    ...,
    moodle_url="http://localhost:8100",  # ← Add this
    moodle_token="...",                   # ← Add this
    course_id=5                           # ← Add this
)
```

### "Enriched 0 events"

**Cause:** No modules found in course structure

**Solution:**
1. Check `data/course_structure.json` exists
2. Verify modules are visible: `visible=1, uservisible=true`

---

## Summary

| Component | Responsibility |
|-----------|---------------|
| `LogEvent.from_dict()` | Detect course-level events → return None |
| `LogPreprocessor.enrich_course_level_log()` | Call Moodle API → expand to N events |
| `LogPreprocessor.parse_raw_logs()` | Integrate enrichment into pipeline |
| `LogProcessingPipeline` | Pass `moodle_client` to preprocessor |
| `MoodleAPIClient` | Provide API methods: `get_module_progress()`, `get_user_scores()` |

**Key Insight:** 
- 1 course-level event (no module_id) → N module-specific events (with module_id, progress, score)
- StateBuilder can now build states for all modules from a single course_viewed event
- Recommendations generated for all modules where user is active

✅ **Solution complete!**
