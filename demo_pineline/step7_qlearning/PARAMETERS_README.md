# Simulation Parameters - Course 670

## 📊 Overview

**4 Core Parameters** extracted from Moodle logs (Course 670, 21 students, 12,671 transitions):

```
simulate_parameters_course_670.json
├── action_space                 # 15 learning actions
├── action_transition_matrix     # 339 states × action probabilities
├── time_patterns                # Duration per action type
└── progress_patterns            # Learning impact per action
```

---

## 1️⃣ **Action Space** (15 Actions)

Organized by action type × time context:

### View Actions (3)
- `view_content` (past, current, future)
- `view_assignment` (past, current)

### Attempt/Submit Actions (5)
- `attempt_quiz` (past, current, future)
- `submit_quiz` (current)
- `submit_assignment` (current)

### Review/Interaction (4)
- `review_quiz` (past, current)
- `post_forum` (past, current, future)

**Format:** `(action_type, time_context)`

---

## 2️⃣ **Action Transition Matrix** 

**What:** P(action | state) - Probability of taking action in each state

**State:** 5D vector `(cluster, module, progress_bin, score_bin, learning_phase)`
- **cluster**: Student behavior cluster (0-4)
- **module**: Which quiz/assignment/forum (0-7)
- **progress_bin**: How far through the module (0-3)
- **score_bin**: Student's current score level (0-3, quartiles)
- **learning_phase**: Stage of learning (0=pre, 1=active, 2=reflective)

**Example:**
```json
{
  "(4, 5, 0, 3, 0)": {
    "view_content_current": 0.45,
    "attempt_quiz_current": 0.55
  },
  "(4, 5, 2, 3, 0)": {
    "submit_quiz_current": 0.70,
    "view_content_future": 0.30
  }
}
```

**339 unique states** observed from real data.

---

## 3️⃣ **Time Patterns**

**What:** How long each action takes (duration in seconds)

| Action | Mean | Std | Min | Max | Interpretation |
|--------|------|-----|-----|-----|-----------------|
| view_content | 207s | 473s | 0 | 3589s | Students read content for ~3-4 min average |
| attempt_quiz | 189s | 454s | 0 | 3572s | Quiz attempts take ~3 min on average |
| view_assignment | 64s | 283s | 0 | 3574s | Reading assignment description ~1 min |
| submit_assignment | 6.3s | 40s | 0 | 308s | Submitting very fast (button click) |
| post_forum | 1.5s | 0.7s | - | - | Quick forum post (limited data) |

**Use in simulation:** Sample duration from Normal(μ, σ) for realistic timing

---

## 4️⃣ **Progress Patterns**

**What:** How each action affects learning progress (progress_bin changes)

| Action | Avg Change | Improve Prob | Impact | Interpretation |
|--------|-----------|----------------|--------|-----------------|
| **attempt_quiz** | **+0.353** | **24.6%** | ⭐⭐⭐ HIGH | Making quizzes is the key to progress |
| **view_assignment** | +0.009 | 12.2% | ⭐⭐ MEDIUM | Reading assignments helps slightly |
| **view_content** | **-0.046** | 5.3% | ⭐ LOW | Re-reading old content can decrease perceived progress |
| **submit_assignment** | 0.0 | 3.5% | ❌ MINIMAL | Submitting doesn't move progress bar |
| **post_forum** | +0.500 | 50.0% | ⭐⭐⭐ (n=2) | Forum posts boost progress (but very rare) |

**Key Insight:** Attempting quizzes → +35% progress bins on average

---

## 📁 Files

```
training/
├── data_train.py                           # Extract parameters from logs
├── visualize_params.py                     # Generate plots
├── simulate_params/
│   └── simulate_parameters_course_670.json # 4 core parameters
└── plots/
    ├── 00_summary_overview.png             # Key statistics
    ├── 01_action_space_overview.png        # 15 actions visualization
    ├── 02_time_patterns.png                # Duration bar chart
    ├── 03_action_transition_matrix.png     # Heatmap of P(action|state)
    └── 04_progress_patterns.png            # Progress impact chart
```

---

## 🚀 How to Use in Simulation

```python
import json

# Load parameters
with open('simulate_params/simulate_parameters_course_670.json') as f:
    params = json.load(f)

# Initialize student in a state
state = (cluster=4, module=5, progress_bin=0, score_bin=3, phase=0)

# Get possible actions
state_str = str(state)
action_probs = params['action_transition_matrix'][state_str]  # {action: prob}

# Sample next action
action = np.random.choice(list(action_probs.keys()), p=list(action_probs.values()))

# Get action duration
action_type = action.split('_')[0]  # e.g., "view" from "view_content_current"
duration = np.random.normal(
    params['time_patterns'][action_type]['mean'],
    params['time_patterns'][action_type]['std']
)

# Update progress
action_name = action_type  # e.g., "view_content"
progress_delta = params['progress_patterns'][action_name]['avg_change']
new_progress = state.progress_bin + progress_delta
```

---

## 📈 Visualization Summary

**All plots in `training/plots/`:**

1. **00_summary_overview.png** → Key statistics & parameters overview
2. **01_action_space_overview.png** → Bar chart of 15 actions by type
3. **02_time_patterns.png** → Action durations (mean ± std)
4. **03_action_transition_matrix.png** → Heatmap P(action | state) for top 12 states
5. **04_progress_patterns.png** → Progress improvement by action type

---

## ✅ Quality Assessment

| Parameter | Data Points | Coverage | Quality |
|-----------|------------|----------|---------|
| action_space | 15 | 100% (all actions mapped) | ⭐⭐⭐⭐⭐ |
| action_transition_matrix | 339 states | Good (average 37 transitions/state) | ⭐⭐⭐⭐ |
| time_patterns | 5 action types | Complete | ⭐⭐⭐⭐ (large std but realistic) |
| progress_patterns | 5 action types | Complete | ⭐⭐⭐⭐ |

**Recommendation:** Use all 4 parameters for simulation. They are empirically grounded and have good data coverage.

---

*Generated: December 6, 2025*
*Source: Course 670 (Moodle logs + grades)*
