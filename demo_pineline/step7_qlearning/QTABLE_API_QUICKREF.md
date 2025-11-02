# 🚀 Q-Table API Quick Reference

## Endpoint Summary

| Endpoint | Purpose | Key Info |
|----------|---------|----------|
| `GET /api/qtable/info` | **Metadata & Structure** | Dimensions, actions, hyperparameters |
| `GET /api/qtable/summary` | **Detailed Analysis** | Q-value distribution, dimension stats |
| `GET /api/qtable/states/positive` | **Get Test States** | Top states with Q>0, ready for testing |
| `GET /api/qtable/states/diverse` | **Diverse Samples** | Stratified samples from percentiles |
| `GET /api/qtable/stats` | **Quick Stats** | Lightweight overview |

---

## Quick Commands

### 1. Get Q-Table Info (Metadata)
```bash
# Full info
curl http://localhost:8080/api/qtable/info | jq '.'

# Just state space features
curl http://localhost:8080/api/qtable/info | jq '.state_space.features'

# Just hyperparameters
curl http://localhost:8080/api/qtable/info | jq '.hyperparameters'

# Just training info
curl http://localhost:8080/api/qtable/info | jq '.training_info'
```

**Response highlights:**
```json
{
  "qtable_metadata": {
    "total_states": 6577,
    "total_actions": 37,
    "state_dimension": 12,
    "sparsity": 0.0,
    "estimated_memory_mb": 1.84
  },
  "state_space": {
    "features": [
      "knowledge_level",
      "engagement_level",
      ...
    ]
  }
}
```

---

### 2. Get Test States
```bash
# Get top 5 states with highest Q-values
curl "http://localhost:8080/api/qtable/states/positive?top_n=5" | jq '.'

# Get top 10 with Q > 50
curl "http://localhost:8080/api/qtable/states/positive?top_n=10&min_q_value=50" | jq '.'

# Save to file
curl "http://localhost:8080/api/qtable/states/positive?top_n=10" > test_states.json
```

---

### 3. Copy State for Testing
```bash
# Get state #1
STATE=$(curl -s "http://localhost:8080/api/qtable/states/positive?top_n=1" | jq '.states[0].features')

# Test recommendation
curl -X POST http://localhost:8080/api/recommend \
  -H 'Content-Type: application/json' \
  -d "{
    \"student_id\": 1,
    \"features\": $STATE,
    \"top_k\": 3
  }" | jq '.'
```

---

### 4. Analyze Q-Table Quality
```bash
# Check training quality
curl http://localhost:8080/api/qtable/summary | jq '.qtable_stats.q_value_distribution'

# Check dimension statistics
curl http://localhost:8080/api/qtable/summary | jq '.dimension_stats[] | select(.dimension < 3)'
```

---

### 5. Export for Analysis
```python
import requests
import pandas as pd

# Get diverse samples
response = requests.get('http://localhost:8080/api/qtable/states/diverse?n_samples=50')
samples = response.json()['samples']

# Convert to DataFrame
df = pd.DataFrame([
    {**s['features'], 'q_value': s['max_q_value'], 'percentile': s['percentile']}
    for s in samples
])

# Analyze
print(df.groupby('percentile')['q_value'].describe())
df.to_csv('qtable_samples.csv', index=False)
```

---

## Common Workflows

### Workflow 1: Understand Q-Table
```bash
# Step 1: Get metadata
curl http://localhost:8080/api/qtable/info | jq '{
  states: .qtable_metadata.total_states,
  actions: .qtable_metadata.total_actions,
  dimension: .qtable_metadata.state_dimension,
  memory_mb: .qtable_metadata.estimated_memory_mb
}'

# Step 2: Check training quality
curl http://localhost:8080/api/qtable/stats | jq '.'
```

### Workflow 2: Generate Test Cases
```bash
# Step 1: Get top states
curl "http://localhost:8080/api/qtable/states/positive?top_n=10" > test_cases.json

# Step 2: Extract features
jq '.states[].features' test_cases.json > features_only.json

# Step 3: Test each one
for i in {0..9}; do
  FEATURES=$(jq ".states[$i].features" test_cases.json)
  echo "Testing state $i..."
  curl -s -X POST http://localhost:8080/api/recommend \
    -H 'Content-Type: application/json' \
    -d "{\"student_id\": $i, \"features\": $FEATURES, \"top_k\": 3}" | jq '.recommendations[0]'
done
```

### Workflow 3: Validate Recommendations
```python
import requests

# Get a known good state
response = requests.get('http://localhost:8080/api/qtable/states/positive?top_n=1')
state = response.json()['states'][0]

expected_q = state['q_info']['max_q_value']
expected_action = state['q_info']['best_action_id']
features = state['features']

# Test recommendation
response = requests.post('http://localhost:8080/api/recommend', json={
    'student_id': 1,
    'features': features,
    'top_k': 5
})

result = response.json()
actual_q = result['recommendations'][0]['q_value']
actual_action = result['recommendations'][0]['activity_id']

# Validate
assert abs(expected_q - actual_q) < 0.01, f"Q mismatch: {expected_q} vs {actual_q}"
assert expected_action == actual_action, f"Action mismatch: {expected_action} vs {actual_action}"
print("✅ Validation passed!")
```

---

## Response Examples

### `/api/qtable/info`
```json
{
  "qtable_metadata": {
    "total_states": 6577,
    "total_actions": 37,
    "sparsity": 0.0
  },
  "state_space": {
    "dimension": 12,
    "features": ["knowledge_level", ...]
  },
  "hyperparameters": {
    "learning_rate": 0.1,
    "epsilon": 0.1
  }
}
```

### `/api/qtable/states/positive`
```json
{
  "success": true,
  "total_states": 5,
  "states": [
    {
      "rank": 1,
      "features": {
        "knowledge_level": 0.75,
        "engagement_level": 0.75,
        ...
      },
      "q_info": {
        "max_q_value": 88.8361,
        "best_action_id": 51
      }
    }
  ]
}
```

---

## Python Helper Functions

```python
import requests

API_BASE = "http://localhost:8080/api"

def get_qtable_info():
    """Get Q-table metadata"""
    return requests.get(f"{API_BASE}/qtable/info").json()

def get_top_states(n=10, min_q=0):
    """Get top N states"""
    return requests.get(
        f"{API_BASE}/qtable/states/positive",
        params={'top_n': n, 'min_q_value': min_q}
    ).json()

def test_recommendation(features, top_k=3):
    """Test recommendation with features"""
    return requests.post(
        f"{API_BASE}/recommend",
        json={'student_id': 1, 'features': features, 'top_k': top_k}
    ).json()

def validate_state(state_dict):
    """Validate a state from Q-table"""
    features = state_dict['features']
    expected_q = state_dict['q_info']['max_q_value']
    
    result = test_recommendation(features, top_k=1)
    actual_q = result['recommendations'][0]['q_value']
    
    return abs(expected_q - actual_q) < 0.01

# Usage
info = get_qtable_info()
print(f"Q-Table has {info['qtable_metadata']['total_states']:,} states")

states = get_top_states(5)
for state in states['states']:
    is_valid = validate_state(state)
    print(f"State #{state['rank']}: {'✅' if is_valid else '❌'}")
```

---

## Tips

1. **Use `/info` first** - Quick overview of Q-table structure
2. **Use `/stats` for health check** - Fast lightweight endpoint
3. **Use `/summary` for analysis** - Detailed statistics and distributions
4. **Use `/states/positive` for testing** - Get real states with known Q-values
5. **Use `/states/diverse` for coverage** - Test across different Q-value ranges

---

## Testing Checklist

- [ ] Get Q-table info: `curl http://localhost:8080/api/qtable/info`
- [ ] Check stats: `curl http://localhost:8080/api/qtable/stats`
- [ ] Get top 10 states: `curl "http://localhost:8080/api/qtable/states/positive?top_n=10"`
- [ ] Copy a state's features
- [ ] Test recommendation with copied features
- [ ] Compare expected vs actual Q-value
- [ ] Verify Q-values match (within 0.01)

---

## Troubleshooting

**Connection refused:**
```bash
# Start server first
cd /path/to/step7_qlearning
uvicorn api_service:app --reload --port 8080
```

**503 Service Unavailable:**
```
Model not loaded - check if qlearning_agent_moodle.pkl exists
```

**Empty states list:**
```
All Q-values are zero - model might not be trained properly
```
