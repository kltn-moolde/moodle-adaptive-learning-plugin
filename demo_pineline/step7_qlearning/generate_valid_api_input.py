#!/usr/bin/env python3
"""
Generate valid API input từ states có trong Q-table
"""
import pickle
import random
import json

print("="*70)
print("GENERATE VALID API INPUT FROM Q-TABLE")
print("="*70)
print()

# Load model
print("[1/3] Loading Q-table...")
with open('models/qlearning_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

q_table = model_data['q_table']
print(f"  ✓ Loaded {len(q_table)} states")
print()

# Pick a random state from Q-table
print("[2/3] Selecting random states from Q-table...")
sample_states = random.sample(list(q_table.keys()), min(5, len(q_table)))

print(f"  ✓ Selected {len(sample_states)} sample states")
print()

# Convert states to API input format
print("[3/3] Converting to API input format...")
print()

dim_names = [
    'knowledge_level',           # 0
    'engagement_level',          # 1
    'struggle_indicator',        # 2
    'submission_activity',       # 3
    'review_activity',          # 4
    'resource_usage',           # 5
    'assessment_engagement',    # 6
    'collaborative_activity',   # 7
    'overall_progress',         # 8
    'module_completion_rate',   # 9
    'activity_diversity',       # 10
    'completion_consistency'    # 11
]

# Reverse mapping: State vector → Features
# Cần reverse engineer từ state_builder.py logic

def state_to_features(state_tuple):
    """
    Reverse engineer state vector back to API features
    
    State structure (12 dims):
    [0] knowledge_level = mean_module_grade
    [1] engagement_level = mean(total_events, course_module, viewed)
    [2] struggle_indicator = attempt * (1 - feedback_viewed) * (1 - knowledge_level)
    [3] submission_activity = mean(submitted, assessable_submitted, ...)
    [4] review_activity = mean(reviewed, feedback_viewed, ...)
    [5] resource_usage = mean(viewed, ...)
    [6] assessment_engagement = mean(attempt, ...)
    [7] collaborative_activity = mean(comment, forum_viewed, ...)
    [8] overall_progress = module_count
    [9] module_completion_rate = course_module_completion
    [10] activity_diversity = active_types / 7
    [11] completion_consistency = 1 - std([completion metrics])
    """
    
    # Extract direct mappings
    mean_module_grade = float(state_tuple[0])
    module_count = float(state_tuple[8])
    course_module_completion = float(state_tuple[9])
    
    # Approximate other features from state
    # engagement = mean(total_events, 0, viewed) → solve for total_events and viewed
    engagement = float(state_tuple[1])
    viewed = float(state_tuple[5])  # resource_usage ≈ viewed
    total_events = max(0.0, engagement * 3 - viewed)  # Approximate
    
    # attempt and feedback_viewed from struggle and assessment
    attempt = float(state_tuple[6])  # assessment_engagement ≈ attempt
    
    # From struggle_indicator: struggle = attempt * (1 - feedback) * (1 - knowledge)
    struggle = float(state_tuple[2])
    if attempt > 0 and mean_module_grade < 1:
        feedback_viewed = 1 - (struggle / (attempt * (1 - mean_module_grade) + 0.001))
        feedback_viewed = max(0.0, min(1.0, feedback_viewed))
    else:
        feedback_viewed = float(state_tuple[4])  # Use review_activity
    
    # NEW: Extract submission and collaborative activities
    submitted = float(state_tuple[3])  # submission_activity
    comment = float(state_tuple[7])    # collaborative_activity
    
    features = {
        "mean_module_grade": round(mean_module_grade, 3),
        "total_events": round(total_events, 3),
        "viewed": round(viewed, 3),
        "attempt": round(attempt, 3),
        "feedback_viewed": round(feedback_viewed, 3),
        "module_count": round(module_count, 3),
        "course_module_completion": round(course_module_completion, 3),
        
        # ✅ ADD DIVERSE FEATURES
        "submitted": round(submitted, 3),
        "assessable_submitted": round(submitted * 0.8, 3),  # Related to submitted
        "comment": round(comment, 3),
        "\\mod_forum\\event\\course_module_viewed": round(comment * 0.6, 3)
    }
    
    return features


print("="*70)
print("🎯 VALID API TEST CASES")
print("="*70)
print()

for i, state in enumerate(sample_states, 1):
    print(f"\n{'='*70}")
    print(f"TEST CASE {i}")
    print(f"{'='*70}")
    
    # Show state vector
    print(f"\n📊 State in Q-table (hashed with decimals=1):")
    for j, (name, val) in enumerate(zip(dim_names, state)):
        marker = "🎯" if j in [3, 7] else "  "
        print(f"  [{j:2d}] {name:<25} {val:.1f} {marker}")
    
    # Get Q-values for this state
    q_values = q_table[state]
    print(f"\n📈 Q-values: {len(q_values)} actions, max Q = {max(q_values.values()):.2f}")
    
    # Convert to API input
    features = state_to_features(state)
    
    api_input = {
        "student_id": 12345,
        "features": features,
        "top_k": 5
    }
    
    print(f"\n✅ API Input (copy & paste this):")
    print(json.dumps(api_input, indent=2))
    
    print(f"\n💡 cURL command:")
    curl_cmd = f"""curl -X POST http://localhost:8080/api/recommend \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(api_input)}'"""
    print(curl_cmd)

print(f"\n{'='*70}")
print("📝 INSTRUCTIONS")
print(f"{'='*70}")
print()
print("1. Copy any of the JSON above")
print("2. Start API: uvicorn api_service:app --reload --port 8080")
print("3. Test với:")
print("   - Postman")
print("   - cURL command")
print("   - Python requests")
print()
print("4. Expected result:")
print("   ✅ success = true")
print("   ✅ q_values > 0 (vì state có trong Q-table)")
print()

# Save to file for easy access
output_file = 'test_cases_valid_states.json'
test_cases = []

for i, state in enumerate(sample_states, 1):
    features = state_to_features(state)
    test_cases.append({
        "test_case": f"Case {i}",
        "state_in_qtable": list(state),
        "api_input": {
            "student_id": 12345,
            "features": features,
            "top_k": 5
        }
    })

with open(output_file, 'w') as f:
    json.dump(test_cases, f, indent=2)

print(f"💾 Saved {len(test_cases)} test cases to: {output_file}")
print()

# Print one recommended case
print(f"{'='*70}")
print("🎯 RECOMMENDED TEST CASE (Best Q-values)")
print(f"{'='*70}")
print()

# Find state with highest average Q-value
best_state = max(sample_states, key=lambda s: sum(q_table[s].values()) / len(q_table[s]))
best_features = state_to_features(best_state)
best_avg_q = sum(q_table[best_state].values()) / len(q_table[best_state])

recommended_input = {
    "student_id": 12345,
    "features": best_features,
    "top_k": 5
}

print(f"State has avg Q-value: {best_avg_q:.2f}")
print(f"\n✅ Copy this:")
print(json.dumps(recommended_input, indent=2))
print()
