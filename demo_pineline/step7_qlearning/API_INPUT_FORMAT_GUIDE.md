# 📘 API Input Format - Structured vs Flat

## 🎯 OVERVIEW

API hiện hỗ trợ **2 formats**:
1. ✅ **Structured Format (NEW - RECOMMENDED)** - Match với state_description
2. ⚙️ **Flat Format (OLD - BACKWARD COMPATIBLE)** - Legacy support

---

## 📋 FORMAT 1: STRUCTURED (RECOMMENDED)

### Input Structure:
```json
{
    "student_id": 1,
    "features": {
        "performance": {
            "knowledge_level": 0.3,
            "engagement_level": 0.1,
            "struggle_indicator": 0.0
        },
        "activity_patterns": {
            "submission_activity": 0.0,
            "review_activity": 0.75,
            "resource_usage": 0.75,
            "assessment_engagement": 0.75,
            "collaborative_activity": 0.0
        },
        "completion_metrics": {
            "overall_progress": 0.75,
            "module_completion_rate": 0.1,
            "activity_diversity": 0.25,
            "completion_consistency": 0.5
        }
    },
    "top_k": 3
}
```

### Advantages:
✅ **Semantic grouping** - Dễ hiểu và maintain
✅ **Match với output** - `state_description` có cùng cấu trúc
✅ **Type safety** - Rõ ràng từng group là gì
✅ **Future-proof** - Dễ extend thêm features

### Field Descriptions:

#### 1. Performance (3 dimensions):
| Field | Range | Description |
|-------|-------|-------------|
| `knowledge_level` | 0-1 | Mức độ hiểu bài (0=kém, 1=giỏi) |
| `engagement_level` | 0-1 | Mức độ tham gia (0=thụ động, 1=tích cực) |
| `struggle_indicator` | 0-1 | Mức độ khó khăn (0=OK, 1=cần hỗ trợ nhiều) |

#### 2. Activity Patterns (5 dimensions):
| Field | Range | Description |
|-------|-------|-------------|
| `submission_activity` | 0-1 | Hoạt động nộp bài (0=không nộp, 1=nộp đều) |
| `review_activity` | 0-1 | Xem lại tài liệu (0=không xem, 1=xem nhiều) |
| `resource_usage` | 0-1 | Sử dụng tài nguyên (0=ít, 1=nhiều) |
| `assessment_engagement` | 0-1 | Tham gia kiểm tra (0=né tránh, 1=tích cực) |
| `collaborative_activity` | 0-1 | Hoạt động cộng tác (0=cô lập, 1=tương tác nhiều) |

#### 3. Completion Metrics (4 dimensions):
| Field | Range | Description |
|-------|-------|-------------|
| `overall_progress` | 0-1 | Tiến độ tổng thể (0=chậm, 1=nhanh) |
| `module_completion_rate` | 0-1 | Tỷ lệ hoàn thành module (0=bỏ lỡ, 1=đầy đủ) |
| `activity_diversity` | 0-1 | Đa dạng hoạt động (0=đơn điệu, 1=phong phú) |
| `completion_consistency` | 0-1 | Tính nhất quán (0=thất thường, 1=đều đặn) |

---

## 📋 FORMAT 2: FLAT (BACKWARD COMPATIBLE)

### Input Structure:
```json
{
    "student_id": 1,
    "features": {
        "knowledge_level": 0.3,
        "engagement_level": 0.1,
        "struggle_indicator": 0.0,
        "submission_activity": 0.0,
        "review_activity": 0.75,
        "resource_usage": 0.75,
        "assessment_engagement": 0.75,
        "collaborative_activity": 0.0,
        "overall_progress": 0.75,
        "module_completion_rate": 0.1,
        "activity_diversity": 0.25,
        "completion_consistency": 0.5
    },
    "top_k": 3
}
```

### Legacy Key Mapping:
Format cũ vẫn hoạt động với key names cũ:
- `engagement_score` → `engagement_level`
- `assessment_performance` → `assessment_engagement`
- `progress_rate` → `overall_progress`
- `completion_rate` → `module_completion_rate`
- `resource_diversity` → `activity_diversity`
- `time_spent_avg` → `completion_consistency`

---

## 🔄 STATE VECTOR MAPPING

Cả 2 formats đều tạo ra **state vector 12 chiều** giống nhau:

```
Index | Dimension Name              | Category
------|----------------------------|------------------
  0   | knowledge_level            | Performance
  1   | engagement_level           | Performance
  2   | struggle_indicator         | Performance
  3   | submission_activity        | Activity Patterns
  4   | review_activity            | Activity Patterns
  5   | resource_usage             | Activity Patterns
  6   | assessment_engagement      | Activity Patterns
  7   | collaborative_activity     | Activity Patterns
  8   | overall_progress           | Completion Metrics
  9   | module_completion_rate     | Completion Metrics
 10   | activity_diversity         | Completion Metrics
 11   | completion_consistency     | Completion Metrics
```

---

## 📤 OUTPUT FORMAT

Output giữ nguyên cấu trúc (không đổi):

```json
{
    "success": true,
    "student_id": 1,
    "cluster_id": 0,
    "cluster_name": "Học sinh cần hỗ trợ tương tác",
    "state_vector": [0.3, 0.1, 0.0, 0.0, 0.75, 0.75, 0.75, 0.0, 0.75, 0.1, 0.25, 0.5],
    "state_description": {
        "performance": {
            "knowledge_level": 0.3,
            "engagement_level": 0.1,
            "struggle_indicator": 0.0
        },
        "activity_patterns": {
            "submission_activity": 0.0,
            "review_activity": 0.75,
            "resource_usage": 0.75,
            "assessment_engagement": 0.75,
            "collaborative_activity": 0.0
        },
        "completion_metrics": {
            "overall_progress": 0.75,
            "module_completion_rate": 0.1,
            "activity_diversity": 0.25,
            "completion_consistency": 0.5
        }
    },
    "recommendations": [...]
}
```

---

## 💡 MIGRATION GUIDE

### From Legacy Format to Structured:

**Before (Old):**
```python
request = {
    "features": {
        "knowledge_level": 0.6,
        "engagement_score": 0.8,  # old name
        "assessment_performance": 0.7,  # old name
        "progress_rate": 0.75,  # old name
        ...
    }
}
```

**After (New - Recommended):**
```python
request = {
    "features": {
        "performance": {
            "knowledge_level": 0.6,
            "engagement_level": 0.8,  # renamed
            "struggle_indicator": 0.0
        },
        "activity_patterns": {
            "assessment_engagement": 0.7,  # renamed
            ...
        },
        "completion_metrics": {
            "overall_progress": 0.75,  # renamed
            ...
        }
    }
}
```

---

## 🧪 TESTING

Run tests:
```bash
# Test with structured format
python test_api_structured.py

# Test comparison between formats
python test_api_structured.py  # includes comparison test
```

---

## 🎯 RECOMMENDATIONS

1. **New projects**: Use **Structured Format**
2. **Existing projects**: Can keep using Flat Format (will keep working)
3. **Migration**: Gradually migrate to Structured Format for better maintainability

---

## ❓ FAQ

**Q: Tại sao cần 2 formats?**
A: Để maintain backward compatibility với code cũ, đồng thời cung cấp format mới tốt hơn.

**Q: Format nào nhanh hơn?**
A: Performance giống nhau, chỉ khác cách organize data.

**Q: Có thể mix 2 formats?**
A: Không, phải chọn 1 trong 2. API tự detect format dựa trên structure.

**Q: Format nào được recommend?**
A: **Structured Format** cho dự án mới, vì:
- Dễ đọc và maintain
- Match với output structure
- Type-safe hơn
- Dễ extend trong tương lai
