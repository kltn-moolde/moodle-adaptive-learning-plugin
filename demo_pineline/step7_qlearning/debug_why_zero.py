#!/usr/bin/env python3
"""
Debug: Tại sao state từ generate_valid_api_input.py vẫn có q_value = 0?
"""
import pickle
import numpy as np
from core.state_builder import MoodleStateBuilder

print("="*70)
print("DEBUG: WHY Q-VALUES STILL = 0?")
print("="*70)
print()

# Load model
print("[1/4] Loading Q-table...")
with open('models/qlearning_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

q_table = model_data['q_table']
print(f"  ✓ Loaded {len(q_table)} states")
print()

# Initialize state builder
print("[2/4] Initializing state builder...")
state_builder = MoodleStateBuilder()
print(f"  ✓ State dimension: 12")
print()

# Test input từ API
print("[3/4] Testing API input...")
api_input_features = {
    "mean_module_grade": 1.0,
    "total_events": 1.7,
    "viewed": 1.0,
    "attempt": 0.5,
    "feedback_viewed": 0.9,
    "module_count": 1.0,
    "course_module_completion": 1.0,
    "submitted": 0.5,
    "assessable_submitted": 0.4,
    "comment": 0.3,
    "\\mod_forum\\event\\course_module_viewed": 0.18
}

print("API Input Features:")
for k, v in api_input_features.items():
    print(f"  {k}: {v}")
print()

# Build state từ features
print("[4/4] Building state and checking Q-table...")
state_vector = state_builder.build_state(api_input_features)

print(f"\n📊 State Vector (raw):")
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

for i, (name, val) in enumerate(zip(dim_names, state_vector)):
    marker = "🎯" if i in [3, 7] else "  "
    print(f"  [{i:2d}] {name:<25} {val:.6f} {marker}")
print()

# Hash state với decimals=1
state_hash = state_builder.hash_state(state_vector, decimals=1)
print(f"🔑 Hashed State (decimals=1):")
print(f"   {state_hash}")
print()

# Check if in Q-table
if state_hash in q_table:
    print(f"✅ STATE FOUND IN Q-TABLE!")
    q_values = q_table[state_hash]
    print(f"   Actions: {len(q_values)}")
    print(f"   Max Q-value: {max(q_values.values()):.2f}")
    print(f"   Mean Q-value: {sum(q_values.values())/len(q_values):.2f}")
else:
    print(f"❌ STATE NOT IN Q-TABLE")
    print()
    
    # Find why not
    print("🔍 Analyzing the issue...")
    print()
    
    # Check each dimension
    print("Checking each dimension in Q-table:")
    
    # Sample 1000 states from Q-table
    sample_states = list(q_table.keys())[:1000]
    
    for dim_idx in range(12):
        values_in_qtable = set(s[dim_idx] for s in sample_states)
        input_value = state_hash[dim_idx]
        
        is_in = input_value in values_in_qtable
        status = "✅" if is_in else "❌"
        
        print(f"  [{dim_idx:2d}] {dim_names[dim_idx]:<25} {status}")
        print(f"       Input: {input_value:.1f}")
        print(f"       Q-table has: {sorted(values_in_qtable)}")
        
        if not is_in:
            # Find closest
            closest = min(values_in_qtable, key=lambda x: abs(x - input_value))
            print(f"       ⚠️  Closest: {closest:.1f} (diff: {abs(closest - input_value):.1f})")
        print()
    
    # Try to find nearest state
    print("="*70)
    print("🔍 FINDING NEAREST STATES IN Q-TABLE")
    print("="*70)
    print()
    
    distances = []
    for qtable_state in list(q_table.keys())[:5000]:  # Sample 5000
        dist = np.linalg.norm(np.array(state_hash) - np.array(qtable_state))
        distances.append((dist, qtable_state))
    
    distances.sort(key=lambda x: x[0])
    
    print(f"Top 5 nearest states:")
    for i, (dist, nearest_state) in enumerate(distances[:5], 1):
        print(f"\n  {i}. Distance: {dist:.3f}")
        print(f"     State: {nearest_state}")
        
        # Compare dimensions
        print(f"     Differences:")
        for j in range(12):
            if state_hash[j] != nearest_state[j]:
                print(f"       Dim {j} ({dim_names[j]}): {state_hash[j]:.1f} vs {nearest_state[j]:.1f}")
        
        # Show Q-values
        q_vals = q_table[nearest_state]
        print(f"     Q-values: {len(q_vals)} actions, max={max(q_vals.values()):.2f}")

print()
print("="*70)
print("💡 ANALYSIS")
print("="*70)
print()

print("❓ TẠI SAO Q-VALUES = 0?")
print()
print("Có 2 khả năng:")
print()
print("1. ❌ State không có trong Q-table (exact match)")
print("   → API fallback về random recommendations với q_value=0")
print()
print("2. ⚠️  Generate script tạo features không chính xác")
print("   → State sau khi build khác với state gốc trong Q-table")
print()

print("🔧 GIẢI PHÁP:")
print()
print("1. ✅ Implement nearest neighbor fallback trong API")
print("   → Tìm state gần nhất trong Q-table")
print()
print("2. ✅ Giảm state_decimals: 1 → 0")
print("   → Tăng khả năng match (11^12 → 2^12 states)")
print()
print("3. ✅ Lấy state trực tiếp từ simulated data")
print("   → Không cần reverse engineer")
print()
