# Clustering Service

Automated student clustering service for Moodle courses with scheduled jobs and MongoDB persistence.

## Features

- 🔄 **Automated Scheduling**: Run clustering jobs on a configurable cron schedule
- 📊 **Event & Action Analysis**: Extract features from Moodle log `event_name` and `action` columns
- 🤖 **AI-Powered Profiling**: LLM-based cluster analysis using Gemini
- 💾 **MongoDB Persistence**: Store clustering results and track user transitions over time
- 🚀 **REST API**: FastAPI endpoints for manual triggers and querying results
- 📈 **Transition Tracking**: Monitor how students move between clusters

## Architecture

```
clustering_service/
├── config.py                  # Configuration (Moodle API, MongoDB, Scheduler)
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── moodle_api/               # Moodle API clients
│   └── custom_api_client.py  # Client for local_userlog_get_logs_course
├── models/                   # MongoDB models
│   ├── course_clusters.py    # Clustering results storage
│   └── user_cluster_history.py  # User transition tracking
├── pipeline/                 # Feature extraction & clustering
│   └── feature_extractor.py  # Extract features from event_name/action
└── scheduler/                # Job scheduling
    ├── job_runner.py         # APScheduler setup
    └── clustering_job.py     # Main clustering pipeline
```

## Installation

1. **Install dependencies**:
```bash
cd clustering_service
pip install -r requirements.txt
```

2. **Configure environment** (optional, or edit `config.py`):
```bash
export MOODLE_URL="http://localhost:8100"
export MOODLE_CUSTOM_TOKEN="86e86e0301d495db032da3b855180f5f"
export MONGO_URI="mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/"
export GEMINI_API_KEY="AIzaSyAPkT1V0fUCq1dqPaWk4qLHcD1GSFyXawU"
export CLUSTER_JOB_SCHEDULE="0 2 * * *"  # Daily at 2AM
export CLUSTER_TARGET_COURSES="5,42,670"  # Comma-separated course IDs
```

3. **Run the service**:
```bash
python main.py
```

The service will start on `http://0.0.0.0:8001`

## API Endpoints

### Manual Triggers

- **POST** `/api/v1/clustering/run/{course_id}` - Trigger clustering for a course
- **POST** `/api/v1/clustering/run-all` - Trigger clustering for all configured courses

### Query Results

- **GET** `/api/v1/clustering/results/{course_id}` - Get latest clustering result
- **GET** `/api/v1/clustering/results/{course_id}/history?limit=10` - Get result history
- **GET** `/api/v1/clustering/history/{course_id}/{user_id}` - Get user's cluster history
- **GET** `/api/v1/clustering/transitions/{course_id}` - Get all transitions for a course

### Scheduler

- **GET** `/api/v1/clustering/jobs` - Get scheduler status and jobs
- **GET** `/health` - Health check

## Usage Examples

### 1. Trigger clustering for course 5
```bash
curl -X POST http://localhost:8001/api/v1/clustering/run/5
```

### 2. Get latest results
```bash
curl http://localhost:8001/api/v1/clustering/results/5
```

Response:
```json
{
  "course_id": 5,
  "run_timestamp": "2025-12-13T10:30:00Z",
  "optimal_k": 4,
  "clusters": [
    {
      "cluster_id": 0,
      "user_ids": [101, 102, 103],
      "size": 3,
      "llm_analysis": "Nhóm sinh viên này có mức độ tương tác cao...",
      "statistics": {
        "mean_features": {...},
        "std_features": {...}
      }
    }
  ],
  "features_used": ["event_quiz_viewed", "action_view", "total_events"],
  "metadata": {
    "total_students": 50,
    "execution_time_seconds": 12.5
  }
}
```

### 3. Get user cluster history
```bash
curl http://localhost:8001/api/v1/clustering/history/5/101
```

Response:
```json
{
  "user_id": 101,
  "course_id": 5,
  "history": [
    {
      "timestamp": "2025-12-01T02:00:00Z",
      "cluster_id": 0,
      "transition_type": "initial",
      "previous_cluster_id": null
    },
    {
      "timestamp": "2025-12-08T02:00:00Z",
      "cluster_id": 1,
      "transition_type": "moved",
      "previous_cluster_id": 0
    }
  ]
}
```

### 4. Check scheduler status
```bash
curl http://localhost:8001/api/v1/clustering/jobs
```

## Pipeline Workflow

1. **Fetch Data**: Get logs via Moodle API (`local_userlog_get_logs_course`)
2. **Feature Extraction**: Create features from `event_name` and `action` columns
   - Event frequency (e.g., `event_quiz_viewed`, `event_course_viewed`)
   - Action counts (e.g., `action_view`, `action_submit`)
   - Event-action combinations (e.g., `combo_quiz_viewed_view`)
   - Temporal features (activity by hour, day of week)
3. **Feature Selection**: Variance + correlation filtering
4. **Clustering**: KMeans with optimal k detection (Elbow, Silhouette, Davies-Bouldin)
5. **Profiling**: LLM-powered cluster analysis (Vietnamese)
6. **Persistence**: Save to MongoDB (course_clusters, user_cluster_history)

## Configuration

Key settings in `config.py`:

```python
# Moodle API
MOODLE_URL = "http://localhost:8100"
MOODLE_CUSTOM_TOKEN = "86e86e0301d495db032da3b855180f5f"
MOODLE_LOG_LIMIT = 1000000

# MongoDB
MONGO_URI = "mongodb+srv://..."
DATABASE_NAME = "clustering_service"

# Clustering
MIN_STUDENTS_FOR_CLUSTERING = 10
MIN_CLUSTERS = 2
MAX_CLUSTERS = 10
MIN_VARIANCE_THRESHOLD = 0.01
MAX_CORRELATION_THRESHOLD = 0.95

# Scheduler
CLUSTER_JOB_SCHEDULE = "0 2 * * *"  # Cron format
CLUSTER_JOB_ENABLED = True
CLUSTER_JOB_RETRY_ATTEMPTS = 3
CLUSTER_TARGET_COURSES = "5"  # Comma-separated

# LLM
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "AIzaSyA..."
ENABLE_LLM_PROFILING = True
```

## Dependencies

This service reuses modules from `moodle_analytics_pipeline`:
- `FeatureSelector` - Variance + correlation filtering
- `OptimalClusterFinder` - KMeans with voting
- `ClusterProfiler` - LLM-powered analysis

Make sure `moodle_analytics_pipeline` is in the parent directory.

## MongoDB Collections

### course_clusters
```json
{
  "course_id": 5,
  "run_timestamp": "2025-12-13T02:00:00Z",
  "optimal_k": 4,
  "clusters": [...],
  "features_used": [...],
  "metadata": {...}
}
```

### user_cluster_history
```json
{
  "user_id": 101,
  "course_id": 5,
  "history": [
    {
      "timestamp": "2025-12-13T02:00:00Z",
      "cluster_id": 0,
      "transition_type": "initial",
      "previous_cluster_id": null
    }
  ],
  "last_updated": "2025-12-13T02:00:00Z"
}
```

## Logging

Logs are written to console with configurable level:

```bash
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

## Troubleshooting

**Issue**: No logs found for course
- Check if course ID is correct
- Verify Moodle API token has access to `local_userlog_get_logs_course`

**Issue**: Insufficient students
- Default minimum is 10 students
- Adjust `MIN_STUDENTS_FOR_CLUSTERING` in config

**Issue**: LLM profiling not working
- Check `GEMINI_API_KEY` is set
- Set `ENABLE_LLM_PROFILING=False` to disable

**Issue**: Scheduler not running
- Check `CLUSTER_JOB_ENABLED=True`
- Verify cron format in `CLUSTER_JOB_SCHEDULE`

## License

MIT
