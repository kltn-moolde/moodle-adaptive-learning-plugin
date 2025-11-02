#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giải thích chi tiết: API Input → 12D State Vector
===================================================
"""

import numpy as np
import json

# ===================================================================
# INPUT: 7 features từ API request
# ===================================================================
api_input = {
    "student_id": 12345,      
    "features": {
        "mean_module_grade": 0.6,
        "total_events": 0.9,
        "viewed": 0.5,
        "attempt": 0.2,
        "feedback_viewed": 0.8,
        "module_count": 0.3,
        "course_module_completion": 0.8
    },
    "top_k": 5
}

print("="*70)
print("GIẢI THÍCH: API Input → 12D State Vector")
print("="*70)
print()

print("📥 INPUT (7 features):")
print(json.dumps(api_input['features'], indent=2))
print()

# ===================================================================
# TRANSFORMATION PROCESS
# ===================================================================

features = api_input['features']
state = []
explanations = []

print("="*70)
print("🔄 TRANSFORMATION PROCESS")
print("="*70)
print()

# -------------------------------------------------------------------
# 1. STUDENT PERFORMANCE (3 dimensions)
# -------------------------------------------------------------------
print("📊 PART 1: STUDENT PERFORMANCE (3 dimensions)")
print("-" * 70)

# 1.1 Knowledge Level
knowledge_level = features['mean_module_grade']
state.append(knowledge_level)
explanations.append({
    'dim': 0,
    'name': 'knowledge_level',
    'value': knowledge_level,
    'formula': 'mean_module_grade',
    'calculation': f'{knowledge_level}'
})
print(f"  [0] knowledge_level = mean_module_grade")
print(f"      = {knowledge_level}")
print()

# 1.2 Engagement Level
engagement = np.mean([
    features['total_events'],
    features.get('course_module', 0.0),  # Không có trong input → 0
    features['viewed']
])
state.append(engagement)
explanations.append({
    'dim': 1,
    'name': 'engagement_level',
    'value': engagement,
    'formula': 'mean(total_events, course_module, viewed)',
    'calculation': f'mean({features["total_events"]}, 0.0, {features["viewed"]}) = {engagement}'
})
print(f"  [1] engagement_level = mean(total_events, course_module, viewed)")
print(f"      = mean({features['total_events']}, 0.0, {features['viewed']})")
print(f"      = {engagement:.6f}")
print()

# 1.3 Struggle Indicator
attempt_norm = features['attempt']
feedback_norm = features['feedback_viewed']
struggle = attempt_norm * (1 - feedback_norm) * (1 - knowledge_level)
struggle = np.clip(struggle, 0.0, 1.0)
state.append(struggle)
explanations.append({
    'dim': 2,
    'name': 'struggle_indicator',
    'value': struggle,
    'formula': 'attempt * (1 - feedback_viewed) * (1 - knowledge_level)',
    'calculation': f'{attempt_norm} * (1 - {feedback_norm}) * (1 - {knowledge_level}) = {struggle}'
})
print(f"  [2] struggle_indicator = attempt * (1 - feedback_viewed) * (1 - knowledge_level)")
print(f"      = {attempt_norm} * (1 - {feedback_norm}) * (1 - {knowledge_level})")
print(f"      = {struggle:.6f}")
print()

# -------------------------------------------------------------------
# 2. ACTIVITY PATTERNS (5 dimensions)
# -------------------------------------------------------------------
print("🎯 PART 2: ACTIVITY PATTERNS (5 dimensions)")
print("-" * 70)

# 2.1 Submission Activity
submission_keys = ['submitted', 'assessable_submitted', 'submission_created']
submission_values = [features.get(k, 0.0) for k in submission_keys]
submission_activity = np.mean([v for v in submission_values if v > 0]) if any(submission_values) else 0.0
state.append(submission_activity)
explanations.append({
    'dim': 3,
    'name': 'submission_activity',
    'value': submission_activity,
    'formula': f'mean({submission_keys})',
    'calculation': f'Không có keys này trong input → {submission_activity}'
})
print(f"  [3] submission_activity = mean({submission_keys})")
print(f"      Keys không có trong input → {submission_activity}")
print()

# 2.2 Review Activity
review_keys = ['reviewed', 'feedback_viewed', 'attempt_reviewed']
review_values = [features.get(k, 0.0) for k in review_keys]
review_activity = features['feedback_viewed']  # Chỉ có feedback_viewed
state.append(review_activity)
explanations.append({
    'dim': 4,
    'name': 'review_activity',
    'value': review_activity,
    'formula': f'mean({review_keys})',
    'calculation': f'Chỉ có feedback_viewed = {review_activity}'
})
print(f"  [4] review_activity = mean({review_keys})")
print(f"      Chỉ có feedback_viewed trong input = {review_activity}")
print()

# 2.3 Resource Usage
resource_keys = ['course_module_viewed', 'viewed']
resource_usage = features['viewed']
state.append(resource_usage)
explanations.append({
    'dim': 5,
    'name': 'resource_usage',
    'value': resource_usage,
    'formula': f'mean({resource_keys})',
    'calculation': f'Chỉ có viewed = {resource_usage}'
})
print(f"  [5] resource_usage = mean({resource_keys})")
print(f"      Chỉ có viewed trong input = {resource_usage}")
print()

# 2.4 Assessment Engagement
assessment_keys = ['attempt', 'attempt_started', 'attempt_submitted']
assessment_engagement = features['attempt']
state.append(assessment_engagement)
explanations.append({
    'dim': 6,
    'name': 'assessment_engagement',
    'value': assessment_engagement,
    'formula': f'mean({assessment_keys})',
    'calculation': f'Chỉ có attempt = {assessment_engagement}'
})
print(f"  [6] assessment_engagement = mean({assessment_keys})")
print(f"      Chỉ có attempt trong input = {assessment_engagement}")
print()

# 2.5 Collaborative Activity
collaborative_keys = ['comment', 'forum_viewed']
collaborative_values = [features.get(k, 0.0) for k in collaborative_keys]
collaborative_activity = 0.0
state.append(collaborative_activity)
explanations.append({
    'dim': 7,
    'name': 'collaborative_activity',
    'value': collaborative_activity,
    'formula': f'mean({collaborative_keys})',
    'calculation': f'Không có keys này trong input → {collaborative_activity}'
})
print(f"  [7] collaborative_activity = mean({collaborative_keys})")
print(f"      Keys không có trong input → {collaborative_activity}")
print()

# -------------------------------------------------------------------
# 3. COMPLETION METRICS (4 dimensions)
# -------------------------------------------------------------------
print("📈 PART 3: COMPLETION METRICS (4 dimensions)")
print("-" * 70)

# 3.1 Overall Progress
overall_progress = features['module_count']
state.append(overall_progress)
explanations.append({
    'dim': 8,
    'name': 'overall_progress',
    'value': overall_progress,
    'formula': 'module_count',
    'calculation': f'{overall_progress}'
})
print(f"  [8] overall_progress = module_count")
print(f"      = {overall_progress}")
print()

# 3.2 Module Completion Rate
module_completion = features['course_module_completion']
state.append(module_completion)
explanations.append({
    'dim': 9,
    'name': 'module_completion_rate',
    'value': module_completion,
    'formula': 'course_module_completion',
    'calculation': f'{module_completion}'
})
print(f"  [9] module_completion_rate = course_module_completion")
print(f"      = {module_completion}")
print()

# 3.3 Activity Diversity
activity_types = ['submitted', 'viewed', 'created', 'updated', 
                  'downloaded', 'reviewed', 'uploaded']
active_types = sum([1 for k in activity_types if features.get(k, 0.0) > 0.1])
activity_diversity = active_types / len(activity_types)
state.append(activity_diversity)
explanations.append({
    'dim': 10,
    'name': 'activity_diversity',
    'value': activity_diversity,
    'formula': 'active_types / total_types',
    'calculation': f'{active_types} / {len(activity_types)} = {activity_diversity}'
})
print(f"  [10] activity_diversity = active_types / total_types")
print(f"       Kiểm tra {activity_types}")
print(f"       Chỉ có 'viewed'={features['viewed']} > 0.1")
print(f"       = {active_types} / {len(activity_types)} = {activity_diversity:.6f}")
print()

# 3.4 Completion Consistency
module_metrics = [
    features['course_module_completion'],
    features['module_count'],
    features.get('course_module', 0.0)
]
completion_consistency = 1 - np.std(module_metrics)
completion_consistency = np.clip(completion_consistency, 0.0, 1.0)
state.append(completion_consistency)
explanations.append({
    'dim': 11,
    'name': 'completion_consistency',
    'value': completion_consistency,
    'formula': '1 - std([course_module_completion, module_count, course_module])',
    'calculation': f'1 - std({module_metrics}) = {completion_consistency}'
})
print(f"  [11] completion_consistency = 1 - std([course_module_completion, module_count, course_module])")
print(f"       = 1 - std({module_metrics})")
print(f"       = 1 - {np.std(module_metrics):.6f}")
print(f"       = {completion_consistency:.6f}")
print()

# ===================================================================
# OUTPUT: 12D State Vector
# ===================================================================
state_vector = np.array(state, dtype=np.float32)

print("="*70)
print("📤 OUTPUT: 12D State Vector")
print("="*70)
print()

print("state_vector = [")
for i, (val, exp) in enumerate(zip(state_vector, explanations)):
    print(f"    {val:.15f},  # [{i}] {exp['name']}")
print("]")
print()

# ===================================================================
# SO SÁNH VỚI API RESPONSE
# ===================================================================
api_response_state = [
    0.6000000238418579,
    0.46666666865348816,
    0.01600000075995922,
    0.0,
    0.800000011920929,
    0.5,
    0.20000000298023224,
    0.0,
    0.30000001192092896,
    0.800000011920929,
    0.1428571492433548,
    0.6700168251991272
]

print("="*70)
print("🔍 SO SÁNH: Calculated vs API Response")
print("="*70)
print()

print(f"{'Dim':<4} {'Name':<30} {'Calculated':<20} {'API Response':<20} {'Match'}")
print("-" * 95)
for i, exp in enumerate(explanations):
    calc = state_vector[i]
    api_val = api_response_state[i]
    match = "✅" if abs(calc - api_val) < 0.01 else "❌"
    print(f"{i:<4} {exp['name']:<30} {calc:<20.6f} {api_val:<20.6f} {match}")

print()

# ===================================================================
# KEY INSIGHTS
# ===================================================================
print("="*70)
print("💡 KEY INSIGHTS")
print("="*70)
print()

print("1. INPUT → STATE MAPPING:")
print("   ✅ mean_module_grade → knowledge_level (trực tiếp)")
print("   ✅ total_events, viewed → engagement_level (average)")
print("   ✅ attempt, feedback_viewed → struggle_indicator (tính toán)")
print("   ✅ module_count → overall_progress (trực tiếp)")
print("   ✅ course_module_completion → module_completion_rate (trực tiếp)")
print()

print("2. MISSING FEATURES (set to 0):")
print("   ⚠️  submission_activity = 0 (không có submitted/assessable_submitted)")
print("   ⚠️  collaborative_activity = 0 (không có comment/forum_viewed)")
print()

print("3. COMPUTED FEATURES:")
print("   🧮 struggle_indicator = attempt * (1-feedback) * (1-knowledge)")
print("   🧮 engagement_level = mean(total_events, course_module, viewed)")
print("   🧮 activity_diversity = count(active_types) / 7")
print("   🧮 completion_consistency = 1 - std([completion metrics])")
print()

print("4. TẠI SAO Q-VALUES = 0?")
print("   ❌ Training data có submission_activity=0 và collaborative_activity=0")
print("   ❌ API input cũng thiếu 2 features này")
print("   ❌ Nhưng các dimensions KHÁC có giá trị khác nhau")
print("   ❌ → State không match chính xác với Q-table")
print()

print("5. GIẢI PHÁP:")
print("   ✅ Option 1: Thêm submitted/comment features vào API input")
print("   ✅ Option 2: Retrain model với diverse data (có submitted, comment)")
print("   ✅ Option 3: Use epsilon-greedy để fallback khi state mới")
print()

print("="*70)
print("✅ EXPLANATION COMPLETE")
print("="*70)
