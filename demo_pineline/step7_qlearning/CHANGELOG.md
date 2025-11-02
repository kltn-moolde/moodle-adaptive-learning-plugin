# CHANGELOG - Q-Learning API

## [2.0.0] - 2025-11-02

### 🚀 BREAKING CHANGES

#### API Input Format Restructured
- **Structured Format (NEW)**: Input format hiện match với `state_description` output
  - Nested structure với 3 categories: `performance`, `activity_patterns`, `completion_metrics`
  - Consistent naming với state dimensions
  - Better semantic grouping
  
- **Backward Compatibility**: Old flat format vẫn hoạt động
  - Legacy key names được map tự động
  - Không cần update code cũ ngay lập tức

### ✨ Features

#### New Structured Input Format
```json
{
    "features": {
        "performance": {
            "knowledge_level": 0.6,
            "engagement_level": 0.8,
            "struggle_indicator": 0.2
        },
        "activity_patterns": {
            "submission_activity": 0.4,
            "review_activity": 0.7,
            "resource_usage": 0.8,
            "assessment_engagement": 0.6,
            "collaborative_activity": 0.3
        },
        "completion_metrics": {
            "overall_progress": 0.7,
            "module_completion_rate": 0.8,
            "activity_diversity": 0.5,
            "completion_consistency": 0.6
        }
    }
}
```

#### Consistent Field Names
Renamed fields to match state dimensions:
- `engagement_score` → `engagement_level`
- `assessment_performance` → `assessment_engagement`
- `progress_rate` → `overall_progress`
- `completion_rate` → `module_completion_rate`
- `resource_diversity` → `activity_diversity`
- `time_spent_avg` → `completion_consistency`

#### Removed Hardcoded Normalization
- Removed `/20.0` for `submitted_activities` (was converting raw count to 0-1)
- Removed `/10.0` for `comments_count` (was converting raw count to 0-1)
- **Now expects all values pre-normalized to 0-1 range**

### 📝 Documentation

- Added `API_INPUT_FORMAT_GUIDE.md` - Comprehensive format guide
- Added `test_api_structured.py` - Test both formats
- Added `example_api_usage.py` - Real-world examples
- Updated `README.md` with breaking change notice

### 🔧 Changes

#### `core/state_builder.py`
- Refactored `build_state_from_api_features()` to support both formats
- Auto-detect format (nested vs flat)
- Backward compatible key mapping

#### `api_service.py`
- Added Pydantic models: `PerformanceFeatures`, `ActivityPatterns`, `CompletionMetrics`
- Added `StructuredFeatures` model
- Updated `RecommendRequest` to accept `Dict[str, Any]` for flexibility

### ⚠️ Migration Guide

#### For New Projects
Use structured format:
```python
request = {
    "features": {
        "performance": {...},
        "activity_patterns": {...},
        "completion_metrics": {...}
    }
}
```

#### For Existing Projects
Option 1: Keep using flat format (will work)
```python
# Old code still works
request = {
    "features": {
        "knowledge_level": 0.6,
        "engagement_level": 0.8,
        ...
    }
}
```

Option 2: Migrate to structured format
```python
# Gradually update to new format
request = {
    "features": {
        "performance": {
            "knowledge_level": 0.6,
            "engagement_level": 0.8,
            "struggle_indicator": 0.2
        },
        ...
    }
}
```

### 🧪 Testing

Run comprehensive tests:
```bash
# Test both formats
python test_api_structured.py

# Test with examples
python example_api_usage.py

# Original test (still works)
python test_api_example.py
```

### 📊 State Vector Mapping

All 12 dimensions now have consistent names:

| Index | Dimension | Category | Old Name (if renamed) |
|-------|-----------|----------|----------------------|
| 0 | knowledge_level | performance | - |
| 1 | engagement_level | performance | engagement_score |
| 2 | struggle_indicator | performance | - |
| 3 | submission_activity | activity_patterns | - |
| 4 | review_activity | activity_patterns | - |
| 5 | resource_usage | activity_patterns | - |
| 6 | assessment_engagement | activity_patterns | assessment_performance |
| 7 | collaborative_activity | activity_patterns | - |
| 8 | overall_progress | completion_metrics | progress_rate |
| 9 | module_completion_rate | completion_metrics | completion_rate |
| 10 | activity_diversity | completion_metrics | resource_diversity |
| 11 | completion_consistency | completion_metrics | time_spent_avg |

### 🎯 Benefits

1. **Consistency**: Input format matches output `state_description`
2. **Clarity**: Semantic grouping makes it clear what each field represents
3. **Type Safety**: Nested structure provides better validation
4. **Maintainability**: Easier to extend in the future
5. **Backward Compatible**: Existing code continues to work

### 🐛 Bug Fixes

- Fixed inconsistent naming between input and output
- Removed confusing normalization factors (20.0, 10.0)
- All values now consistently in 0-1 range

---

## [1.0.0] - Previous Version

### Initial Features
- Q-Learning recommendation system
- FastAPI endpoint
- State builder from Moodle logs
- Cluster-based student profiling
- Q-table lookup for recommendations

### Known Issues
- Input format not matching output structure
- Hardcoded normalization factors
- Inconsistent field naming
