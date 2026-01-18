# Code Assessment - Mock Data & Dependencies

## Summary

Đánh giá codebase để xác định các phần đang mock/hardcode và dependencies cần tích hợp với Moodle.

## Mock Data Files Identified

### 1. Po_Lo.json (LO → Activities Mapping)
- **Location**: `data/Po_Lo.json`
- **Status**: Hardcoded
- **Content**: 
  - Programme Outcomes (PO1-PO5)
  - Learning Outcomes (LO1.1 - LO5.2)
  - Activity IDs mapped to each LO
- **Used in**:
  - `core/activity_recommender.py` - Activity recommendations
  - `core/lo_mastery_tracker.py` - LO mastery tracking
  - `core/reward_calculator_v2.py` - Reward calculation
  - `train_qlearning.py` - Training
  - `core/learning_path_simulator.py` - Simulation
- **Issue**: Activity IDs are hardcoded, no automatic mapping from Moodle
- **Solution**: Auto-map from quiz questions + manual override

### 2. midterm_lo_weights.json (Midterm Quiz Weights)
- **Location**: `data/midterm_lo_weights.json`
- **Status**: Hardcoded with manual keyword matching
- **Content**:
  - LO weights (sum to 1.0)
  - Question count per LO
  - Keyword matching rules (manual)
- **Used in**:
  - `core/lo_mastery_tracker.py` - Midterm prediction
  - `core/reward_calculator_v2.py` - Reward calculation
- **Issue**: Weights calculated manually, keyword rules hardcoded
- **Solution**: Auto-calculate from quiz structure + manual override

### 3. cluster_profiles.json
- **Location**: `data/cluster_profiles.json`
- **Status**: Synced from pipeline (via `sync_pipeline_data.py`)
- **Content**: Cluster statistics and profiles
- **Used in**:
  - `core/state_builder_v2.py` - State building
  - `services/cluster_service.py` - Cluster prediction
- **Status**: OK, but needs verification and fallback

### 4. course_structure.json
- **Location**: `data/course_structure.json`
- **Status**: Retrieved from Moodle (has message "Retrieved course contents from Moodle")
- **Content**: Course modules, sections, activities
- **Used in**:
  - `core/state_builder_v2.py` - Module mapping
  - `core/activity_recommender.py` - Activity info
- **Issue**: Needs automated refresh mechanism
- **Solution**: Add sync script with caching

## Dependencies Analysis

### Files Loading JSON Data

1. **core/activity_recommender.py**
   - Loads: `Po_Lo.json`, `course_structure.json`
   - Purpose: Activity recommendations based on LO mastery

2. **core/lo_mastery_tracker.py**
   - Loads: `midterm_lo_weights.json`, `Po_Lo.json`
   - Purpose: Track LO mastery and predict midterm scores

3. **core/reward_calculator_v2.py**
   - Loads: `cluster_profiles.json`, `Po_Lo.json`, `midterm_lo_weights.json`
   - Purpose: Calculate rewards based on LO improvements

4. **core/state_builder_v2.py**
   - Loads: `cluster_profiles.json`, `course_structure.json`
   - Purpose: Build 6D state representation

5. **train_qlearning.py**
   - Loads: `Po_Lo.json`, `cluster_profiles.json`, `midterm_lo_weights.json`
   - Purpose: Training Q-learning agent

6. **core/learning_path_simulator.py**
   - Loads: `Po_Lo.json`
   - Purpose: Simulate learning paths

## Data Flow Issues

### Current Flow (Mock)
```
Hardcoded JSON files → Services → Q-Learning
```

### Target Flow (Real)
```
Moodle API/CSV → Auto-calculators → Manual Override → Services → Q-Learning
```

## Key Improvements Needed

1. **LO Mapping**: Auto-map from quiz questions using similarity matching
2. **Midterm Weights**: Calculate from quiz structure automatically
3. **LO Mastery**: Calculate from real quiz scores, not simulated
4. **Data Refresh**: Automated sync with caching
5. **Fallback**: CSV support when API unavailable
6. **Manual Override**: Allow manual corrections to auto-mappings

## Next Steps

1. Create MoodleService (API + CSV fallback)
2. Create LOMapper (auto + manual)
3. Create MidtermWeightsCalculator (auto + manual)
4. Enhance LOMasteryTracker (real calculations)
5. Create sync scripts (batch + on-demand)
6. Integration and testing

