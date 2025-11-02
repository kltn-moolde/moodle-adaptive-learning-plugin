# 📊 Q-Table Information API Documentation

## Overview

API cung cấp thông tin chi tiết về Q-table và các states để phân tích và testing.

**Base URL:** `http://localhost:8080/api`

---

## Endpoints

### 1. GET `/api/qtable/info` ⭐ NEW

Lấy thông tin metadata và cấu trúc của Q-table.

#### Response:
```json
{
  "qtable_metadata": {
    "total_states": 6577,
    "total_actions": 37,
    "state_dimension": 12,
    "total_state_action_pairs": 52659,
    "sparsity": 0.0,
    "estimated_memory_mb": 1.84
  },
  "state_space": {
    "dimension": 12,
    "total_states": 6577,
    "state_format": "tuple of floats (normalized 0-1)",
    "discretization": "1 decimal places",
    "features": [
      "knowledge_level",
      "engagement_level",
      "struggle_indicator",
      "submission_activity",
      "review_activity",
      "resource_usage",
      "assessment_engagement",
      "collaborative_activity",
      "overall_progress",
      "module_completion_rate",
      "activity_diversity",
      "completion_consistency"
    ]
  },
  "action_space": {
    "total_actions": 37,
    "action_ids": [64, 65, 66, 67, ...],
    "action_format": "integer ID representing course module/activity"
  },
  "hyperparameters": {
    "learning_rate": 0.1,
    "discount_factor": 0.95,
    "epsilon": 0.1,
    "state_decimals": 1
  },
  "training_info": {
    "episodes": 50000,
    "total_updates": 1500000,
    "avg_reward": 69.2179,
    "final_epsilon": 0.1
  }
}
```

#### Usage:
```bash
curl http://localhost:8080/api/qtable/info
```

#### Use Cases:
- ✅ Hiểu cấu trúc Q-table (dimensions, actions, states)
- ✅ Kiểm tra memory usage
- ✅ Xem danh sách features và actions
- ✅ Validate hyperparameters
- ✅ Overview nhanh training info

---

### 2. GET `/api/qtable/summary`

Lấy thông tin tổng quan đầy đủ về Q-table.

#### Response:
```json
{
  "model_info": {
    "n_actions": 37,
    "learning_rate": 0.1,
    "discount_factor": 0.95,
    "epsilon": 0.1,
    "state_decimals": 1
  },
  "training_stats": {
    "episodes": 50000,
    "total_updates": 1500000,
    "avg_reward": 69.21,
    "states_visited": 6577
  },
  "qtable_stats": {
    "total_states": 6577,
    "states_with_nonzero_q": 6577,
    "state_dimension": 12,
    "total_q_values": 52659,
    "q_value_distribution": {
      "zero_count": 0,
      "zero_percentage": 0.0,
      "positive_count": 52659,
      "positive_percentage": 100.0,
      "negative_count": 0,
      "min": 0.0018,
      "max": 88.8361,
      "mean": 10.5087,
      "std": 16.3353
    }
  },
  "dimension_stats": [
    {
      "dimension": 0,
      "unique_values": 4,
      "min": 0.0,
      "max": 0.75,
      "mean": 0.436,
      "std": 0.302
    },
    ...
  ]
}
```

#### Usage:
```bash
curl http://localhost:8080/api/qtable/summary
```

---

### 3. GET `/api/qtable/states/positive`

Lấy danh sách states có Q-value > 0 (sorted by Q-value).

#### Parameters:
- `top_n` (optional, default=50): Số lượng states trả về
- `min_q_value` (optional, default=0.0001): Ngưỡng Q-value tối thiểu

#### Response:
```json
{
  "success": true,
  "total_states": 50,
  "top_n": 50,
  "min_q_value": 0.0001,
  "states": [
    {
      "rank": 1,
      "features": {
        "knowledge_level": 0.75,
        "engagement_level": 0.75,
        "struggle_indicator": 0.0,
        "submission_activity": 0.5,
        "review_activity": 0.75,
        "resource_usage": 0.75,
        "assessment_engagement": 0.75,
        "collaborative_activity": 0.0,
        "overall_progress": 0.75,
        "module_completion_rate": 0.75,
        "activity_diversity": 0.25,
        "completion_consistency": 0.5
      },
      "q_info": {
        "max_q_value": 88.8361,
        "best_action_id": 64,
        "num_actions": 8,
        "avg_q_value": 55.2341
      }
    },
    ...
  ]
}
```

#### Usage:
```bash
# Get top 10 states
curl "http://localhost:8080/api/qtable/states/positive?top_n=10"

# Get states with Q-value > 50
curl "http://localhost:8080/api/qtable/states/positive?top_n=20&min_q_value=50"
```

#### 💡 Copy-Paste Ready Features:
Features trong response đã ở dạng flat dict, có thể copy trực tiếp để test API `/api/recommend`:

```bash
# Copy features từ response trên và test
curl -X POST http://localhost:8080/api/recommend \
  -H 'Content-Type: application/json' \
  -d '{
    "student_id": 1,
    "features": {
      "knowledge_level": 0.75,
      "engagement_level": 0.75,
      "struggle_indicator": 0.0,
      "submission_activity": 0.5,
      "review_activity": 0.75,
      "resource_usage": 0.75,
      "assessment_engagement": 0.75,
      "collaborative_activity": 0.0,
      "overall_progress": 0.75,
      "module_completion_rate": 0.75,
      "activity_diversity": 0.25,
      "completion_consistency": 0.5
    },
    "top_k": 3
  }'
```

---

### 4. GET `/api/qtable/states/diverse`

Lấy mẫu đa dạng các states từ các mức Q-value khác nhau (top, 75th, 50th, 25th percentile + random).

#### Parameters:
- `n_samples` (optional, default=20): Số lượng samples

#### Response:
```json
{
  "success": true,
  "total_samples": 20,
  "samples": [
    {
      "features": {
        "knowledge_level": 0.75,
        "engagement_level": 0.75,
        ...
      },
      "max_q_value": 88.8361,
      "percentile": "top"
    },
    {
      "features": {...},
      "max_q_value": 45.2134,
      "percentile": "75th"
    },
    {
      "features": {...},
      "max_q_value": 12.5678,
      "percentile": "50th"
    },
    ...
  ]
}
```

#### Usage:
```bash
curl "http://localhost:8080/api/qtable/states/diverse?n_samples=10"
```

---

### 5. GET `/api/qtable/stats`

Lấy thống kê cơ bản (lightweight version).

#### Response:
```json
{
  "total_states": 6577,
  "states_with_positive_q": 6577,
  "episodes_trained": 50000,
  "total_updates": 1500000,
  "avg_reward": 69.2179
}
```

#### Usage:
```bash
curl http://localhost:8080/api/qtable/stats
```

---

## Testing

### Run Test Suite:
```bash
python test_qtable_api.py
```

### Test Individual Endpoints:
```python
import requests

# 1. Get summary
response = requests.get('http://localhost:8080/api/qtable/summary')
print(response.json())

# 2. Get top 5 states
response = requests.get('http://localhost:8080/api/qtable/states/positive?top_n=5')
states = response.json()['states']

# 3. Test recommendation with first state
features = states[0]['features']
response = requests.post('http://localhost:8080/api/recommend', json={
    'student_id': 1,
    'features': features,
    'top_k': 3
})
print(response.json())
```

---

## Use Cases

### 0. Quick Q-Table Overview
```bash
# Get basic info about Q-table structure
curl http://localhost:8080/api/qtable/info | jq '.'

# Check state space
curl http://localhost:8080/api/qtable/info | jq '.state_space'

# Check action space
curl http://localhost:8080/api/qtable/info | jq '.action_space'

# Check hyperparameters
curl http://localhost:8080/api/qtable/info | jq '.hyperparameters'
```

### 1. Analyze Q-Table Quality
```bash
# Check training quality
curl http://localhost:8080/api/qtable/summary | jq '.qtable_stats.q_value_distribution'

# Output:
# {
#   "positive_count": 52659,
#   "positive_percentage": 100.0,
#   "mean": 10.5087,
#   "max": 88.8361
# }
```

### 2. Generate Test Data
```bash
# Get top 10 states for testing
curl "http://localhost:8080/api/qtable/states/positive?top_n=10" | jq '.states[].features' > test_inputs.json
```

### 3. Validate Recommendations
```python
import requests

# Get state with known Q-value
response = requests.get('http://localhost:8080/api/qtable/states/positive?top_n=1')
state = response.json()['states'][0]
expected_q = state['q_info']['max_q_value']

# Test recommendation
response = requests.post('http://localhost:8080/api/recommend', json={
    'student_id': 1,
    'features': state['features'],
    'top_k': 1
})

actual_q = response.json()['recommendations'][0]['q_value']

# Compare
assert abs(expected_q - actual_q) < 0.01, "Q-values should match!"
```

### 4. Export for Analysis
```python
import requests
import pandas as pd

# Get all positive states
response = requests.get('http://localhost:8080/api/qtable/states/positive?top_n=100')
states = response.json()['states']

# Convert to DataFrame
df = pd.DataFrame([
    {**s['features'], 'q_value': s['q_info']['max_q_value']}
    for s in states
])

# Analyze
print(df.describe())
df.to_csv('qtable_states.csv', index=False)
```

---

## Response Codes

- `200 OK`: Success
- `503 Service Unavailable`: Model not loaded
- `500 Internal Server Error`: Server error

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              api_service.py                      │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Q-Table Endpoints                       │  │
│  │  • GET /api/qtable/info                  │  │
│  │  • GET /api/qtable/summary               │  │
│  │  • GET /api/qtable/states/positive       │  │
│  │  • GET /api/qtable/states/diverse        │  │
│  │  • GET /api/qtable/stats                 │  │
│  └──────────────────────────────────────────┘  │
│                    ↓                             │
│  ┌──────────────────────────────────────────┐  │
│  │  services/qtable_service.py              │  │
│  │  • get_qtable_info()                     │  │
│  │  • get_summary()                         │  │
│  │  • get_states_with_positive_q()          │  │
│  │  • get_diverse_samples()                 │  │
│  │  • get_statistics()                      │  │
│  └──────────────────────────────────────────┘  │
│                    ↓                             │
│  ┌──────────────────────────────────────────┐  │
│  │  core/qlearning_agent.py                 │  │
│  │  • q_table (Dict)                        │  │
│  │  • training_stats (Dict)                 │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Files

- `api_service.py` - Main API with new Q-table endpoints
- `services/qtable_service.py` - Q-table analysis service (clean separation)
- `test_qtable_api.py` - Comprehensive test suite
- `QTABLE_API_DOCS.md` - This documentation

---

## Quick Start

1. **Start API:**
   ```bash
   uvicorn api_service:app --reload --port 8080
   ```

2. **Test endpoints:**
   ```bash
   python test_qtable_api.py
   ```

3. **Get test data:**
   ```bash
   curl "http://localhost:8080/api/qtable/states/positive?top_n=10" | jq '.'
   ```

4. **Use for testing:**
   ```bash
   # Get a state
   STATE=$(curl -s "http://localhost:8080/api/qtable/states/positive?top_n=1" | jq '.states[0].features')
   
   # Test recommendation
   curl -X POST http://localhost:8080/api/recommend \
     -H 'Content-Type: application/json' \
     -d "{\"student_id\": 1, \"features\": $STATE, \"top_k\": 3}"
   ```
