# How to Apply Bug Fixes

## Quick Start

### 1. Stop Current Service (if running)
```bash
# Find the webhook service process
ps aux | grep webhook_service

# Kill the process
kill <PID>
```

### 2. Verify Fixes
```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning

# Run test suite
python3 test_bugfixes.py
```

Expected output:
```
✅ Testing Complete
1. ✓ ActivityRecommender initialized successfully
2. ✓ Found similar state: (2, 1, 0.25, 0.5, 0, 1)
3. ✓ ActivityRecommender is available
```

### 3. Start Webhook Service
```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning

# Start service
python3 webhook_service.py

# Or with uvicorn
uvicorn webhook_service:app --host 0.0.0.0 --port 8200 --reload
```

### 4. Verify Startup
Look for these messages in the startup output:
```
🚀 Initializing Webhook Service
1. ✓ Model loaded
2. ✓ Pipeline ready
3. ✓ Activity recommender ready
4. ✓ Recommendation service ready
5. ✓ MongoDB connected
✅ Webhook Service Ready
```

⚠️ **Important:** If you see:
```
⚠️ Warning: Failed to initialize ActivityRecommender: ...
```
Check that `data/Po_Lo_5.json` exists.

---

## Testing the Fix

### Send Test Event
```bash
curl -X POST http://localhost:8200/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [{
      "userid": 4,
      "courseid": 5,
      "eventname": "\\mod_quiz\\event\\attempt_submitted",
      "component": "mod_quiz",
      "action": "submitted",
      "target": "attempt",
      "objectid": 123,
      "crud": "c",
      "edulevel": 0,
      "contextinstanceid": 39,
      "timecreated": 1733492000
    }]
  }'
```

### Expected Response
```json
{
  "status": "success",
  "message": "Events received and processing started",
  "events_received": 1,
  "processing_started": true
}
```

### Check Logs
Look for:
```
✓ Activity recommender ready
✓ Found similar state: (2, 1, 0.25, 0.5, 0, 1)
← Returning recommendations from similar state: [(10, 0.14), ...]
→ Calling activity_recommender.recommend_activity()...
← Activity recommendation: {'activity_id': 56, 'activity_name': 'bài kiểm tra...'}
```

**No longer see:**
```
⚠️ activity_recommender is None
→ Returning random actions: [(9, 0.0), (8, 0.0), (13, 0.0)]
```

---

## Troubleshooting

### Issue: "activity_recommender is None"
**Solution:** Check that:
1. `data/Po_Lo_5.json` exists
2. File contains valid JSON
3. No exceptions during initialization

### Issue: "State not in Q-table"
**Solution:** This is expected for new states. Verify:
1. System finds similar state: `✓ Found similar state: ...`
2. Q-values are non-zero from similar state
3. Not seeing "Returning random actions"

### Issue: "ModuleNotFoundError: No module named 'core'"
**Solution:**
```bash
export PYTHONPATH=/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning:$PYTHONPATH
```

### Issue: "ModelLoader missing course_id"
**Solution:** Already fixed in webhook_service.py. If still seeing this, update:
```python
model_loader = ModelLoader(
    course_id=5,  # Add this line
    model_path=MODEL_PATH,
    ...
)
```

---

## Rollback Plan

If issues occur after deployment:

1. **Stop service**
   ```bash
   kill $(ps aux | grep webhook_service | grep -v grep | awk '{print $2}')
   ```

2. **Revert changes**
   ```bash
   git checkout HEAD -- webhook_service.py core/rl/agent.py
   ```

3. **Restart with old version**
   ```bash
   python3 webhook_service.py
   ```

---

## Monitoring

### Check Service Health
```bash
curl http://localhost:8200/health
```

### Check MongoDB Recommendations
```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['adaptive_learning']

# Check recent recommendations
recommendations = db.recommendations.find().sort('timestamp', -1).limit(5)
for rec in recommendations:
    print(rec)
```

### Verify Recommendations Have Activity Details
```python
# Should see these fields:
# - activity_id
# - activity_name
# - weak_los
# - reason
# - alternatives
```

---

## Success Criteria

✅ Service starts without errors
✅ ActivityRecommender initialized
✅ Similar state matching works for unseen states
✅ Recommendations include specific activity details
✅ Q-values are non-zero for similar states
✅ MongoDB stores complete recommendation documents

---

## Files Modified

1. `webhook_service.py` - Added ActivityRecommender initialization
2. `core/rl/agent.py` - Added similar state matching
3. `test_bugfixes.py` - Comprehensive test suite (new)
4. `BUGFIX_SUMMARY.md` - Documentation (new)
5. `RESTART_GUIDE.md` - This file (new)
