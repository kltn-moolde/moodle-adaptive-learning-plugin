# Automated Clustering Service Implementation Plan

## Project Overview
Create a new automated clustering service that runs scheduled jobs to analyze Moodle course data, persist results to MongoDB, and track user cluster transitions over time.

## Architecture Components

### 1. Project Structure
```
clustering_service/
├── config.py                     # MongoDB URI, Moodle tokens, scheduler config
├── main.py                       # FastAPI service entry point
├── moodle_api/
│   ├── __init__.py
│   ├── base_client.py           # Base HTTP client for Moodle API
│   ├── custom_api_client.py     # Client for local_* endpoints (custom token)
│   └── standard_api_client.py   # Client for core_* endpoints (standard token)
├── models/
│   ├── __init__.py
│   ├── course_clusters.py       # MongoDB schema for course clusters
│   ├── user_cluster_history.py  # MongoDB schema for user transitions
│   └── cluster_snapshots.py     # MongoDB schema for pipeline results
├── pipeline/
│   ├── __init__.py
│   ├── feature_extractor.py     # Reuse from moodle_analytics_pipeline
│   ├── feature_selector.py      # Reuse from moodle_analytics_pipeline
│   ├── cluster_finder.py        # Reuse optimal_cluster_finder
│   └── cluster_profiler.py      # Reuse with LLM integration
├── scheduler/
│   ├── __init__.py
│   ├── job_runner.py            # APScheduler configuration
│   └── clustering_job.py        # Main clustering job logic
└── requirements.txt
```

### 2. Moodle API Clients

#### Custom API Client (local_* endpoints)
- Token: `86e86e0301d495db032da3b855180f5f`
- Endpoints:
  - `local_userlog_get_logs_course` - Fetch user activity logs

#### Standard API Client (core_* endpoints)
- Token: `eb4a1ea54118eb52574ac5ede106dbd3`
- Endpoints:
  - `core_enrol_get_enrolled_users` - Get enrolled students (filter role=student)
  - `gradereport_user_get_grade_items?itemmodule=quiz` - Get quiz grades

#### Implementation Details
```python
class MoodleCustomAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
    
    def get_user_logs(self, course_id: int, user_ids: list[int]) -> dict:
        """Fetch logs via local_userlog_get_logs_course"""
        pass

class MoodleStandardAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
    
    def get_enrolled_students(self, course_id: int) -> list[dict]:
        """Get students enrolled in course (role=student filter)"""
        pass
    
    def get_user_quiz_grades(self, course_id: int, user_ids: list[int]) -> dict:
        """Fetch quiz grades via gradereport_user_get_grade_items"""
        pass
```

### 3. MongoDB Persistence Layer

#### Connection Configuration
```python
MONGO_URI = "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/"
DATABASE_NAME = "clustering_service"
```

#### Collections Schema

**course_clusters**
```python
{
    "_id": ObjectId,
    "course_id": int,
    "run_timestamp": datetime,
    "optimal_k": int,
    "clusters": [
        {
            "cluster_id": int,
            "user_ids": [int],
            "size": int,
            "llm_analysis": str,  # Vietnamese cluster description
            "statistics": {
                "mean_features": {},
                "std_features": {}
            }
        }
    ],
    "features_used": [str],
    "metadata": {
        "total_students": int,
        "execution_time_seconds": float
    }
}
```

**user_cluster_history**
```python
{
    "_id": ObjectId,
    "user_id": int,
    "course_id": int,
    "history": [
        {
            "timestamp": datetime,
            "cluster_id": int,
            "transition_type": str,  # "initial", "moved", "stable"
            "previous_cluster_id": int | null
        }
    ],
    "last_updated": datetime
}
```

**cluster_snapshots** (optional - for debugging/auditing)
```python
{
    "_id": ObjectId,
    "course_id": int,
    "timestamp": datetime,
    "raw_features_path": str,  # S3/local path to CSV
    "selected_features": [str],
    "full_pipeline_results": {}
}
```

### 4. Pipeline Integration

Reuse existing modules from `moodle_analytics_pipeline/core/`:
- `FeatureExtractor` - Extract engagement features
- `FeatureSelector` - Variance + correlation filtering
- `OptimalClusterFinder` - KMeans with voting (Elbow/Silhouette/Davies-Bouldin)
- `ClusterProfiler` - LLM-powered analysis (Gemini)

#### Workflow
1. Fetch data from Moodle API
2. Transform to pandas DataFrame (logs + grades)
3. Extract features → Select features → Find optimal K → Profile clusters
4. Persist to MongoDB (course_clusters, user_cluster_history)
5. Track transitions (compare with previous run)

### 5. Scheduler Configuration

#### APScheduler Setup
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# Default: Daily at 2AM
scheduler.add_job(
    func=run_clustering_job,
    trigger=CronTrigger(hour=2, minute=0),
    id='daily_clustering',
    args=[course_id]
)
```

#### Environment Variables
```python
CLUSTER_JOB_SCHEDULE = os.getenv("CLUSTER_JOB_SCHEDULE", "0 2 * * *")  # Cron format
CLUSTER_JOB_ENABLED = os.getenv("CLUSTER_JOB_ENABLED", "true")
CLUSTER_JOB_RETRY_ATTEMPTS = int(os.getenv("CLUSTER_JOB_RETRY_ATTEMPTS", "3"))
```

#### Retry Logic
- Exponential backoff: 1min, 5min, 15min
- Retry on: API timeout, MongoDB connection errors
- Skip on: Invalid course_id, zero students

### 6. FastAPI Service

#### Endpoints
```python
# Manual trigger
POST /api/v1/clustering/run/{course_id}

# Get latest results
GET /api/v1/clustering/results/{course_id}

# Get user cluster history
GET /api/v1/clustering/history/{course_id}/{user_id}

# Get scheduler status
GET /api/v1/clustering/jobs
```

#### Implementation
```python
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI(title="Clustering Service")

@app.post("/api/v1/clustering/run/{course_id}")
async def trigger_clustering(course_id: int):
    """Manually trigger clustering for a course"""
    try:
        result = await run_clustering_job(course_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Implementation Phases

### Phase 1: MVP (Priority)
1. **Moodle API Clients** - Fetch students, logs, grades
2. **Pipeline Integration** - Reuse existing feature extraction + clustering
3. **MongoDB Persistence** - Basic schemas (course_clusters, user_cluster_history)
4. **Simple Scheduler** - APScheduler with daily interval
5. **FastAPI Wrapper** - Manual trigger endpoint only

### Phase 2: Enhancements
1. **Transition Analysis** - Detect cluster movements, identify patterns
2. **Alerts** - Notify on significant cluster shifts
3. **Historical Trends** - Visualize cluster evolution over time
4. **Multi-course Support** - Parallel jobs for multiple courses
5. **Caching Layer** - Redis for frequent queries

### Phase 3: Advanced Features
1. **Predictive Modeling** - Forecast cluster transitions
2. **A/B Testing** - Compare intervention strategies
3. **Dashboard** - React/Vue frontend for visualization
4. **Export API** - Generate reports (PDF/CSV)

## Configuration File Template

```python
# clustering_service/config.py

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_PATH = PROJECT_ROOT / 'outputs'

# Moodle API
MOODLE_URL = os.getenv("MOODLE_URL", "http://localhost:8100")
MOODLE_CUSTOM_TOKEN = os.getenv("MOODLE_CUSTOM_TOKEN", "86e86e0301d495db032da3b855180f5f")
MOODLE_STANDARD_TOKEN = os.getenv("MOODLE_STANDARD_TOKEN", "eb4a1ea54118eb52574ac5ede106dbd3")

# MongoDB
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/"
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "clustering_service")

# LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAPkT1V0fUCq1dqPaWk4qLHcD1GSFyXawU")

# Scheduler
CLUSTER_JOB_SCHEDULE = os.getenv("CLUSTER_JOB_SCHEDULE", "0 2 * * *")
CLUSTER_JOB_ENABLED = os.getenv("CLUSTER_JOB_ENABLED", "true").lower() == "true"
CLUSTER_JOB_RETRY_ATTEMPTS = int(os.getenv("CLUSTER_JOB_RETRY_ATTEMPTS", "3"))

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
```

## Dependencies (requirements.txt)

```
# Web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# MongoDB
motor==3.3.2
pymongo==4.6.0

# Scheduler
APScheduler==3.10.4

# Moodle API
requests==2.31.0
httpx==0.25.2

# Data processing (reuse from moodle_analytics_pipeline)
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2

# LLM
google-generativeai==0.3.1

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

## Next Steps

1. **Create clustering_service/ folder structure**
2. **Implement Moodle API clients** (custom + standard)
3. **Set up MongoDB connection and schemas**
4. **Integrate moodle_analytics_pipeline modules**
5. **Build clustering job logic**
6. **Configure APScheduler**
7. **Create FastAPI endpoints**
8. **Test with real course data**
9. **Deploy and monitor**

## Questions to Address

- run clustering specific course_ids
- Archive full history

