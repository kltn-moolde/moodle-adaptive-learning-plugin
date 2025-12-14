# Log-to-State Pipeline 🚀

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Demo
```bash
python demo_log_to_state.py
```

### 3. Run Tests
```bash
python test/test_log_pipeline.py
```

---

## File Structure

```
core/
├── log_models.py              # Data models
├── log_preprocessor.py        # Log preprocessing
└── log_to_state_builder.py   # Main builder

services/
├── state_repository.py        # MongoDB persistence
└── moodle_api_client.py      # Moodle API

pipeline/
└── log_processing_pipeline.py # Orchestrator

test/
└── test_log_pipeline.py       # Tests

demo_log_to_state.py           # Demo script
LOG_TO_STATE_GUIDE.md          # Full documentation
IMPLEMENTATION_SUMMARY.md      # Implementation summary
```

---

## Usage Examples

### Example 1: Process Logs from Dict
```python
from pipeline.log_processing_pipeline import LogProcessingPipeline

# Initialize
pipeline = LogProcessingPipeline(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json'
)

# Process logs
logs = [
    {
        'user_id': 101,
        'cluster_id': 2,
        'module_id': 54,
        'action': 'attempt_quiz',
        'timestamp': 1700000000,
        'score': 0.85
    }
]

result = pipeline.process_logs_from_dict(logs, save_to_db=True)
print(f"Built {result['states_built']} states")
```

### Example 2: Get Current State
```python
# Get state
state = pipeline.get_current_state(user_id=101, module_id=54)
print(f"State: {state}")

# Get explanation
explanation = pipeline.get_state_with_explanation(user_id=101, module_id=54)
print(explanation['interpretation'])
```

### Example 3: Batch Processing
```python
# Process last 7 days
result = pipeline.batch_process_daily(
    user_ids=[101, 102, 103],
    lookback_days=7
)
```

---

## 6D State Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| cluster_id | 0-4 | Student cluster (0=weak, 2=medium, 4=strong) |
| module_idx | 0-5 | Current module index |
| progress_bin | 0.25/0.5/0.75/1.0 | Progress quartile |
| score_bin | 0.25/0.5/0.75/1.0 | Score quartile |
| learning_phase | 0/1/2 | Pre/Active/Reflective learning |
| engagement_level | 0/1/2 | Low/Medium/High engagement |

**Total State Space**: 4,320 states

---

## Required Moodle APIs

Implement these 5 custom functions in your Moodle plugin:

1. ✅ `mod_adaptivelearning_get_user_logs` - Get user learning logs
2. ✅ `mod_adaptivelearning_get_user_cluster` - Get user cluster ID
3. ✅ `mod_adaptivelearning_get_module_progress` - Get module progress
4. ✅ `mod_adaptivelearning_get_user_scores` - Get user scores
5. ✅ `mod_adaptivelearning_get_course_structure` - Get course structure

See `services/moodle_api_client.py` for detailed API specs.

---

## MongoDB Setup

**Database**: `recommendservice`

**Collections**:
- `user_states` - Current states
- `state_history` - Historical states
- `log_events` - Raw logs (optional)

**Connection**:
```bash
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/database"
```

---

## Environment Variables

```bash
export MONGO_URI="mongodb+srv://..."
export MOODLE_URL="https://moodle.example.com"
export MOODLE_TOKEN="your_token"
export COURSE_ID="2"
```

---

## Documentation

📖 **LOG_TO_STATE_GUIDE.md** - Complete guide (architecture, deployment, API)
📋 **IMPLEMENTATION_SUMMARY.md** - Implementation details & next steps
🏗️ **ARCHITECTURE.md** - System architecture
📚 **USAGE_GUIDE.md** - Q-Learning usage guide

---

## Support

For issues or questions:
1. Check `LOG_TO_STATE_GUIDE.md` for detailed documentation
2. Run demo: `python demo_log_to_state.py`
3. Check tests: `python test/test_log_pipeline.py`

---

## License

MIT License - See LICENSE file for details
