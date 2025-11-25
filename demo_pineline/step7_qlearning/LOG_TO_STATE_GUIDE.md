# Log-to-State Pipeline Documentation
# ======================================
# Hệ thống xử lý logs từ Moodle → 6D States cho Q-Learning

## 📋 Tổng quan

Pipeline này chuyển đổi raw logs từ Moodle thành 6D states cho hệ thống gợi ý học tập dựa trên Q-Learning.

### 🔄 Luồng xử lý chính

```
Moodle Logs → LogPreprocessor → LogToStateBuilder → StateRepository (MongoDB)
     ↓              ↓                    ↓                    ↓
Raw Events   Aggregation          6D States           Persistence
```

### 📊 6D State Dimensions

1. **cluster_id** (0-4): Student cluster (weak/medium/strong learner)
2. **module_idx** (0-5): Current module index
3. **progress_bin** (0.25/0.5/0.75/1.0): Progress quartile
4. **score_bin** (0.25/0.5/0.75/1.0): Score quartile
5. **learning_phase** (0/1/2): Pre-learning/Active/Reflective
6. **engagement_level** (0/1/2): Low/Medium/High engagement

---

## 🏗️ Kiến trúc hệ thống

### Phase 0: Data Models

**File**: `core/log_models.py`

- **LogEvent**: Single log event từ Moodle
- **UserLogSummary**: Aggregated summary cho (user, module)
- **ActionType**: Standardized action types

**Key features**:
- Action type normalization (quiz_attempt → attempt_quiz)
- Score normalization (0-100 → 0-1)
- Automatic validation

### Phase 1: Log Preprocessing

**File**: `core/log_preprocessor.py`

**Class**: `LogPreprocessor`

**Chức năng**:
- Parse raw logs → LogEvent objects
- Aggregate by (user_id, module_id)
- Calculate metrics (avg_score, progress, time_on_task)
- Filter excluded clusters (teachers)

**Usage**:
```python
preprocessor = LogPreprocessor(
    course_structure_path='data/course_structure.json',
    recent_window=10
)

# Parse logs
events = preprocessor.parse_raw_logs(raw_logs)

# Aggregate
summaries = preprocessor.aggregate_by_user_module(events)
```

### Phase 2: State Building

**File**: `core/log_to_state_builder.py`

**Class**: `LogToStateBuilder`

**Chức năng**:
- Convert UserLogSummary → 6D state
- Calculate learning phase from action patterns
- Calculate engagement level from activity quality
- Provide human-readable explanations

**Usage**:
```python
builder = LogToStateBuilder(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json'
)

# Build states from logs
states = builder.build_states_from_logs(raw_logs)

# Get state for specific user/module
state = builder.build_state_for_user(raw_logs, user_id=101, module_id=54)

# Get explanation
explanation = builder.get_state_explanation(state, verbose=True)
```

### Phase 3: MongoDB Persistence

**File**: `services/state_repository.py`

**Class**: `StateRepository`

**Collections**:
- `user_states`: Current state for each (user_id, module_id)
- `state_history`: Historical states (time series)
- `log_events`: Raw log events (optional)

**Usage**:
```python
repo = StateRepository()

# Save state
repo.save_state(user_id=101, module_id=54, state=(2,0,0.5,0.75,1,1))

# Get current state
state = repo.get_state(user_id=101, module_id=54)

# Get all states for user
user_states = repo.get_user_states(user_id=101)

# Get state history
history = repo.get_state_history(user_id=101, module_id=54, limit=10)
```

### Phase 4: Moodle API Integration

**File**: `services/moodle_api_client.py`

**Class**: `MoodleAPIClient`

**Required Custom Moodle Functions**:

1. `mod_adaptivelearning_get_user_logs`
   ```php
   // Input: userid, courseid, starttime, endtime, moduleid (optional)
   // Output: Array of log events
   ```

2. `mod_adaptivelearning_get_user_cluster`
   ```php
   // Input: userid, courseid
   // Output: clusterid (0-6)
   ```

3. `mod_adaptivelearning_get_module_progress`
   ```php
   // Input: userid, moduleid
   // Output: progress (0-1), completed_activities, time_spent
   ```

4. `mod_adaptivelearning_get_user_scores`
   ```php
   // Input: userid, courseid, moduleid (optional)
   // Output: Array of scores with activity IDs
   ```

5. `mod_adaptivelearning_get_course_structure`
   ```php
   // Input: courseid
   // Output: Full course structure JSON
   ```

**Usage**:
```python
client = MoodleAPIClient(
    moodle_url='https://moodle.example.com',
    ws_token='your_token',
    course_id=2
)

# Get user logs
logs = client.get_user_logs(user_id=101)

# Get user cluster
cluster = client.get_user_cluster(user_id=101)

# Get module progress
progress = client.get_module_progress(user_id=101, module_id=54)
```

### Phase 5: Pipeline Orchestrator

**File**: `pipeline/log_processing_pipeline.py`

**Class**: `LogProcessingPipeline`

**Modes**:
1. **Manual**: Process specific user/module on demand
2. **Batch**: Process multiple users (daily/hourly)
3. **Real-time**: Process logs as they arrive (webhook)

**Usage**:

#### Mode 1: Process from dict (manual/batch)
```python
pipeline = LogProcessingPipeline(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json'
)

# Process raw logs
result = pipeline.process_logs_from_dict(raw_logs, save_to_db=True)
```

#### Mode 2: Process from Moodle API
```python
pipeline = LogProcessingPipeline(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json',
    moodle_url='https://moodle.example.com',
    moodle_token='your_token',
    course_id=2
)

# Fetch and process from Moodle
result = pipeline.process_logs_from_moodle(
    user_ids=[101, 102, 103],
    start_time=datetime.now() - timedelta(days=7)
)
```

#### Mode 3: Daily batch processing
```python
# Scheduled daily job
result = pipeline.batch_process_daily(
    user_ids=None,  # All users
    lookback_days=1
)
```

#### Mode 4: Single user on-demand
```python
state = pipeline.process_single_user(user_id=101, module_id=54)
```

---

## 🚀 Deployment Guide

### 1. Requirements

**Python packages**:
```bash
pip install pymongo requests numpy
```

**Data files**:
- `data/cluster_profiles.json`: Cluster definitions
- `data/course_structure.json`: Course structure from Moodle
- `data/Po_Lo.json`: LO mappings (optional, for LO mastery)

**MongoDB**:
- Database: `recommendservice`
- Collections: `user_states`, `state_history`, `log_events`

### 2. Configuration

**Environment variables**:
```bash
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/database"
export MOODLE_URL="https://moodle.example.com"
export MOODLE_TOKEN="your_webservice_token"
export COURSE_ID="2"
```

**Config file**: `config.py`
```python
class Config:
    MONGO_URI = os.getenv("MONGO_URI", "...")
    DATABASE_NAME = "recommendservice"
    MOODLE_URL = os.getenv("MOODLE_URL")
    MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")
    COURSE_ID = int(os.getenv("COURSE_ID", 2))
```

### 3. Initialize Pipeline

```python
from pipeline.log_processing_pipeline import LogProcessingPipeline

pipeline = LogProcessingPipeline(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json',
    moodle_url=Config.MOODLE_URL,
    moodle_token=Config.MOODLE_TOKEN,
    course_id=Config.COURSE_ID
)
```

### 4. Run Pipeline

**Option A: Batch processing (cron job)**
```bash
# Run daily at midnight
0 0 * * * python -c "from pipeline.log_processing_pipeline import LogProcessingPipeline; pipeline = LogProcessingPipeline(...); pipeline.batch_process_daily()"
```

**Option B: Real-time webhook**
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/logs', methods=['POST'])
def process_logs():
    logs = request.json['logs']
    result = pipeline.process_logs_from_dict(logs)
    return {'status': 'success', 'result': result}
```

**Option C: API endpoint**
```python
@app.route('/api/state/<int:user_id>/<int:module_id>', methods=['GET'])
def get_state(user_id, module_id):
    state = pipeline.get_current_state(user_id, module_id)
    explanation = pipeline.get_state_with_explanation(user_id, module_id)
    return {
        'state': state,
        'explanation': explanation
    }
```

---

## 🧪 Testing

### Run unit tests
```bash
cd test
python test_log_pipeline.py
```

### Test individual components
```bash
# Test log models
python core/log_models.py

# Test log preprocessor
python core/log_preprocessor.py

# Test state builder
python core/log_to_state_builder.py

# Test repository (requires MongoDB)
python services/state_repository.py

# Test pipeline
python pipeline/log_processing_pipeline.py
```

### Manual testing
```python
# 1. Create sample logs
sample_logs = [
    {
        'user_id': 101,
        'cluster_id': 2,
        'module_id': 54,
        'action': 'attempt_quiz',
        'timestamp': 1700000000,
        'score': 0.85,
        'progress': 0.6
    }
]

# 2. Process logs
pipeline = LogProcessingPipeline(...)
result = pipeline.process_logs_from_dict(sample_logs)

# 3. Get state
state = pipeline.get_current_state(user_id=101, module_id=54)
print(f"State: {state}")

# 4. Get explanation
explanation = pipeline.get_state_with_explanation(user_id=101, module_id=54)
print(explanation['interpretation'])
```

---

## 📝 Log Format Requirements

### Expected Input Format

**Raw log event**:
```json
{
    "user_id": 101,
    "cluster_id": 2,
    "module_id": 54,
    "action": "quiz_attempt_started",
    "timestamp": 1700000000,
    "score": 85.0,
    "progress": 0.6,
    "time_spent": 300,
    "success": true
}
```

**Alternative field names** (auto-mapped):
- `userid` → `user_id`
- `cmid`, `contextinstanceid` → `module_id`
- `eventname`, `action_type` → `action`
- `timecreated`, `time` → `timestamp`
- `grade` → `score`

### Action Types

Standardized action types:
- `view_content`: View course content
- `view_assignment`: View assignment requirements
- `attempt_quiz`: Start quiz attempt
- `submit_quiz`: Submit quiz
- `review_quiz`: Review quiz results
- `submit_assignment`: Submit assignment
- `post_forum`: Post to forum
- `view_forum`: View forum
- `download_resource`: Download resources

---

## 🔧 Troubleshooting

### Issue 1: MongoDB connection failed
```
Error: pymongo.errors.ServerSelectionTimeoutError
```
**Solution**: Check MONGO_URI, network connection, and MongoDB Atlas whitelist

### Issue 2: Cluster ID not found
```
ValueError: Cluster 3 is excluded
```
**Solution**: Cluster 3 (teachers) is excluded by default. Update `excluded_clusters=[3]` if needed.

### Issue 3: Module not found
```
KeyError: module_id 54
```
**Solution**: Update `course_structure.json` from Moodle or re-fetch using API

### Issue 4: State always returns (3, 0, 0.25, 0.25, 0, 0)
**Reason**: No logs found or default values used
**Solution**: Check log data, time range, and user/module IDs

---

## 📊 State Interpretation Guide

### Learning Phase
- **0 (Pre-learning)**: Exploring, reading, watching videos
- **1 (Active-learning)**: Practicing, attempting quizzes, doing assignments
- **2 (Reflective-learning)**: Reviewing, discussing, consolidating knowledge

### Engagement Level
- **0 (Low)**: 0-7 weighted action points
- **1 (Medium)**: 8-15 weighted action points
- **2 (High)**: 16+ weighted action points

**Action weights**:
- view_content: 1
- attempt_quiz: 4
- submit_quiz: 5
- post_forum: 3
- etc.

### Example Interpretations

**State**: `(2, 0, 0.5, 0.75, 1, 1)`
```
Cluster: Medium learner (2)
Module: 0 (first subsection)
Progress: 50% complete
Score: 75% average
Phase: Active-learning (practicing)
Engagement: Medium (steady participation)

→ Recommendation: Continue with current pace, suggest more practice activities
```

**State**: `(0, 2, 0.25, 0.5, 0, 0)`
```
Cluster: Weak learner (0)
Module: 2
Progress: 25% (just started)
Score: 50% (struggling)
Phase: Pre-learning (still exploring)
Engagement: Low (needs motivation)

→ Recommendation: Suggest easier content, provide more guidance
```

---

## 🔄 Integration with Q-Learning

### Use states for recommendation
```python
from core.qlearning_agent_v2 import QLearningAgentV2
from core.action_space import ActionSpace

# Get current state
state = pipeline.get_current_state(user_id=101, module_id=54)

# Load Q-Learning agent
agent = QLearningAgentV2(n_actions=15)
agent.load('models/qtable_trained.pkl')

# Get action recommendations
action_space = ActionSpace()
available_actions = list(range(15))

recommendations = agent.recommend_action(
    state=state,
    available_actions=available_actions,
    top_k=3
)

# Map to activities
for action_id, q_value in recommendations:
    action = action_space.get_action_by_index(action_id)
    print(f"Action: {action.name}, Q-value: {q_value:.3f}")
```

---

## 📚 References

- **StateBuilderV2**: `core/state_builder_v2.py`
- **ActionSpace**: `core/action_space.py`
- **RewardCalculatorV2**: `core/reward_calculator_v2.py`
- **QLearningAgentV2**: `core/qlearning_agent_v2.py`
- **ActivityRecommender**: `core/activity_recommender.py`

---

## 🎯 Next Steps

1. **Implement Moodle Custom APIs** (5 functions listed above)
2. **Set up MongoDB database** (`recommendservice`)
3. **Configure environment variables** (MONGO_URI, MOODLE_URL, etc.)
4. **Test pipeline with sample data**
5. **Deploy batch processing** (cron job or scheduler)
6. **Integrate with API service** (FastAPI/Flask)
7. **Monitor and optimize** (check state distributions, processing time)

---

## 📧 Support

For questions or issues, refer to:
- `ARCHITECTURE.md`: System architecture
- `USAGE_GUIDE.md`: Q-Learning usage guide
- `CODE_ASSESSMENT.md`: Code quality assessment
