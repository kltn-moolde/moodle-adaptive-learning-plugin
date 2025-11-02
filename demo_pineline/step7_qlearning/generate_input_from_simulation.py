#!/usr/bin/env python3
"""
Generate CORRECT API input từ simulated data (không reverse engineer)
"""
import json
import random

print("="*70)
print("GENERATE CORRECT API INPUT FROM SIMULATED DATA")
print("="*70)
print()

# Load simulated data
print("[1/2] Loading simulated data...")
with open('data/simulated/latest_simulation.json', 'r') as f:
    simulated_data = json.load(f)

print(f"  ✓ Loaded {len(simulated_data)} interactions")
print()

# Group by student
print("[2/2] Grouping by students...")
students = {}
for interaction in simulated_data:
    student_id = interaction.get('student_id')
    if student_id not in students:
        students[student_id] = []
    students[student_id].append(interaction)

print(f"  ✓ Found {len(students)} students")
print()

# Pick random students
sample_students = random.sample(list(students.keys()), min(5, len(students)))

print("="*70)
print("🎯 VALID API TEST CASES (From Real Simulated Data)")
print("="*70)
print()

valid_cases = []

for i, student_id in enumerate(sample_students, 1):
    interactions = students[student_id]
    
    # Get first interaction (has initial state)
    first_interaction = interactions[0]
    
    # Extract state_before từ interaction
    state_before = first_interaction.get('state_before', [])
    
    if not state_before or len(state_before) != 12:
        continue
    
    print(f"\n{'='*70}")
    print(f"TEST CASE {i} - Student {student_id}")
    print(f"{'='*70}")
    
    dim_names = [
        'knowledge_level',
        'engagement_level',
        'struggle_indicator',
        'submission_activity',
        'review_activity',
        'resource_usage',
        'assessment_engagement',
        'collaborative_activity',
        'overall_progress',
        'module_completion_rate',
        'activity_diversity',
        'completion_consistency'
    ]
    
    print(f"\n📊 State Vector (from simulated data):")
    for j, (name, val) in enumerate(zip(dim_names, state_before)):
        marker = "🎯" if j in [3, 7] else "  "
        print(f"  [{j:2d}] {name:<25} {val:.3f} {marker}")
    
    # Reverse engineer features từ state
    # Sử dụng logic đơn giản hơn, gần với thực tế hơn
    features = {
        "mean_module_grade": round(state_before[0], 3),
        "total_events": round(state_before[1] * 1.5, 3),  # Approximate
        "viewed": round(state_before[5], 3),
        "attempt": round(state_before[6], 3),
        "feedback_viewed": round(state_before[4], 3),
        "module_count": round(state_before[8], 3),
        "course_module_completion": round(state_before[9], 3),
        
        # ✅ DIVERSE FEATURES
        "submitted": round(state_before[3], 3),
        "assessable_submitted": round(state_before[3] * 0.8, 3),
        "comment": round(state_before[7], 3),
        "\\mod_forum\\event\\course_module_viewed": round(state_before[7] * 0.6, 3)
    }
    
    api_input = {
        "student_id": student_id,
        "features": features,
        "top_k": 5
    }
    
    print(f"\n✅ API Input:")
    print(json.dumps(api_input, indent=2))
    
    valid_cases.append({
        "test_case": f"Student {student_id}",
        "state_from_simulation": state_before,
        "api_input": api_input,
        "cluster_id": first_interaction.get('cluster_id'),
        "num_interactions": len(interactions)
    })

# Save all test cases
output_file = 'test_cases_from_simulation.json'
with open(output_file, 'w') as f:
    json.dump(valid_cases, f, indent=2)

print(f"\n{'='*70}")
print(f"💾 Saved {len(valid_cases)} test cases to: {output_file}")
print(f"{'='*70}")
print()

# Print recommended case
if valid_cases:
    recommended = valid_cases[0]
    
    print("="*70)
    print("🎯 RECOMMENDED TEST CASE")
    print("="*70)
    print()
    print(f"Student ID: {recommended['api_input']['student_id']}")
    print(f"Cluster ID: {recommended['cluster_id']}")
    print(f"Interactions: {recommended['num_interactions']}")
    print()
    print("✅ Copy this JSON:")
    print(json.dumps(recommended['api_input'], indent=2))
    print()
    
    print("💡 cURL command:")
    curl_data = json.dumps(recommended['api_input'])
    print(f"curl -X POST http://localhost:8080/api/recommend \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{curl_data}'")
    print()

print("="*70)
print("📝 IMPORTANT")
print("="*70)
print()
print("⚠️  Lưu ý: Input này vẫn CÓ THỂ có q_values=0 vì:")
print()
print("1. State sau khi build có thể khác state_before một chút")
print("   (do floating point rounding)")
print()
print("2. Q-table coverage vẫn chỉ 0.14% (69k/50M states)")
print()
print("🔧 Giải pháp CUỐI CÙNG:")
print()
print("✅ Implement nearest neighbor fallback trong API")
print("   → Luôn trả về recommendations có q_values > 0")
print()
