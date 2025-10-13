# Hybrid Q-Learning + Heuristic System

## 🎯 Overview

Implemented **hybrid recommendation system** combining:
1. **Q-Learning** for learned recommendations (when data available)
2. **Heuristic fallback** for unseen states (graceful degradation)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          Recommendation Request                 │
│          (student_state, available_actions)     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  QLearningAgentV2   │
         │  - Get Q-values     │
         └─────────┬───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Check Q-values     │
         │  All Q = 0?         │
         └──────┬──────┬───────┘
                │      │
         YES ◄──┘      └──► NO
          │                 │
          ▼                 ▼
┌──────────────────┐  ┌────────────────┐
│ Heuristic        │  │ Q-Learning     │
│ Recommender      │  │ Sorting        │
│ - Student        │  │ - Sort by      │
│   classification │  │   Q-values     │
│ - Rule-based     │  │                │
│   scoring        │  │                │
└────────┬─────────┘  └───────┬────────┘
         │                     │
         └──────┬──────────────┘
                │
                ▼
      ┌─────────────────────┐
      │  Top-K             │
      │  Recommendations    │
      │  + method label     │
      └─────────────────────┘
```

## 🧠 Heuristic Scoring Formula

For each action, score is calculated as:

```
score = 0.4 × difficulty_match
      + 0.3 × action_type_match  
      + 0.2 × engagement_boost
      + 0.1 × struggle_mitigation
```

### 1. Difficulty Matching (40% weight)
```python
difficulty_score = 1.0 - |difficulty_value - knowledge_level|

# Example:
# Student: knowledge=0.7 (medium-high)
# Action: difficulty='medium' (0.6)
# Score: 1.0 - |0.6 - 0.7| = 0.9 ✓ Good match!
```

### 2. Action Type Matching (30% weight)
```python
if knowledge == 'high':
    quiz_hard → 1.0
    quiz → 0.7
    other → 0.5

elif knowledge == 'low':
    video/read → 1.0
    quiz_easy → 0.8
    other → 0.4
```

### 3. Engagement Boost (20% weight)
```python
if engagement == 'low':
    video/forum → 1.0 (engaging!)
    other → 0.3

elif engagement == 'high':
    any → 0.8 (can do anything)
```

### 4. Struggle Mitigation (10% weight)
```python
if struggle == 'high':
    video/resource → 1.0 (supportive!)
    quiz → 0.4 (challenging)

elif struggle == 'low':
    quiz → 0.7 (can challenge)
```

## 📊 Demo Results

### Test Case 1: High Achiever
**State**: knowledge=0.90, engagement=0.80, struggle=0.10

**WITHOUT Heuristic**: Random ordering
```
1. Announcements (Q=0.0)
2. Quiz medium (Q=0.0)
...
```

**WITH Heuristic**: Intelligent matching
```
1. Quiz - HARD (heuristic=0.93) ✓
2. Quiz - HARD (heuristic=0.93) ✓
3. Quiz - HARD (heuristic=0.93) ✓
```

### Test Case 2: Medium Student
**State**: knowledge=0.50, engagement=0.40, struggle=0.30

**WITH Heuristic**:
```
1. Quiz - MEDIUM (heuristic=0.82) ✓
2. Quiz - MEDIUM (heuristic=0.82) ✓
```

### Test Case 3: Struggling Student
**State**: knowledge=0.20, engagement=0.10, struggle=0.50

**WITH Heuristic**:
```
1. Video (heuristic=0.80) ✓ Supportive!
2. Video (heuristic=0.80) ✓
3. Video (heuristic=0.80) ✓
```

## 🎯 Production Behavior

### Scenario A: Trained State
```python
# Student state matches training data
# → Q-values exist (non-zero)
# → Use Q-Learning recommendations
# → method='q_learning'

recommendations = agent.recommend(state, actions, top_k=5)
# Output: Learned optimal actions
```

### Scenario B: Unseen State
```python
# Student state NOT in training
# → All Q-values = 0
# → Automatic fallback to heuristic
# → method='heuristic'

recommendations = agent.recommend(state, actions, top_k=5)
# Output: Rule-based intelligent recommendations
```

### Scenario C: Partially Trained
```python
# Some Q-values non-zero
# → Use Q-Learning (no fallback)
# → Mixed Q-values (some 0, some >0)
# → method='q_learning'
```

## 🔧 API Usage

### Basic Usage
```python
from core import QLearningAgentV2

# Load trained agent
agent = QLearningAgentV2.create_from_course('course.json', n_bins=3)
agent.load('trained_agent.pkl')

# Get recommendations
state = agent.state_builder.build_state(student_features)
actions = agent.action_space.get_all_actions()

# WITH heuristic fallback (recommended)
recommendations = agent.recommend(
    state, 
    actions, 
    top_k=5,
    use_heuristic_fallback=True  # Default
)

# Check recommendation method
for rec in recommendations:
    print(f"{rec['resource_name']}: {rec['recommendation_method']}")
    # Output: "Video Tutorial: heuristic" or "Quiz: q_learning"
```

### Without Fallback (Testing)
```python
# For comparison or debugging
recommendations = agent.recommend(
    state,
    actions,
    top_k=5,
    use_heuristic_fallback=False
)
# Will return Q=0 recommendations if state unseen
```

## 📈 Performance Metrics

### Coverage
- **Q-table size**: 463 entries
- **Training updates**: 300
- **Unique states explored**: ~11 discrete states
- **Heuristic fallback rate**: ~100% for new students (expected with small dataset)

### Recommendation Quality

| Student Type | Q-Learning | Heuristic | Improvement |
|--------------|------------|-----------|-------------|
| High | Random (Q=0) | Hard quizzes (0.93) | ✅ Excellent |
| Medium | Random (Q=0) | Medium quizzes (0.82) | ✅ Good |
| Low/Struggling | Random (Q=0) | Videos (0.80) | ✅ Supportive |

## ✅ Advantages

1. **Graceful Degradation**: System works even with limited training data
2. **No Cold Start Problem**: New students get intelligent recommendations
3. **Explainable**: Heuristic scores show WHY recommendations made
4. **Adaptive**: Automatically switches between Q-Learning and heuristics
5. **Production-Ready**: No special handling needed for edge cases

## ⚠️ Limitations

1. **Heuristic Overuse**: With small dataset (15 students), most recommendations use heuristic
2. **Difficulty Coverage**: Course must have difficulty labels in resource names
3. **Rule Maintenance**: Heuristic rules need manual tuning
4. **No Online Learning**: Heuristic doesn't learn from feedback (Q-Learning does)

## 🚀 Deployment Recommendations

### For Production (Immediate)
```python
# Always enable heuristic fallback
agent.recommend(state, actions, use_heuristic_fallback=True)

# Monitor recommendation methods
method_counts = {'q_learning': 0, 'heuristic': 0}
for rec in recommendations:
    method_counts[rec['recommendation_method']] += 1

# Log metrics
log_metrics({
    'heuristic_ratio': method_counts['heuristic'] / len(recommendations),
    'q_table_coverage': len(agent.Q),
})
```

### For Improvement (Long-term)
1. **Collect More Data**: 100+ students → better Q-table coverage
2. **Online Learning**: Update Q-table with real feedback
3. **Hybrid Scoring**: Blend Q-values + heuristic scores even when both available
4. **Deep Q-Network**: Neural network for better generalization

## 📊 Success Metrics

Track these in production:
```python
{
    'recommendation_method_ratio': {
        'q_learning': 0.15,  # Target: increase to 80%
        'heuristic': 0.85    # Target: decrease to 20%
    },
    'avg_heuristic_score': 0.82,  # Quality of heuristic recs
    'user_engagement': 0.67,       # Click-through rate
    'learning_outcomes': 0.75,     # Grade improvement
}
```

## 🎓 Conclusion

Hybrid system provides **best of both worlds**:
- ✅ Q-Learning when data available (learned optimization)
- ✅ Heuristic fallback when data missing (intelligent defaults)
- ✅ Production-ready with graceful degradation
- ✅ No cold start problem
- ✅ Explainable recommendations

**Recommendation**: Deploy with monitoring, collect data, retrain monthly.
