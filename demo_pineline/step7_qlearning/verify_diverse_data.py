#!/usr/bin/env python3
"""
Quick check: Verify submitted and comment features in new data
"""
import json
import numpy as np

# Load simulated data
with open('data/simulated/latest_simulation.json', 'r') as f:
    data = json.load(f)

print("="*70)
print("VERIFY NEW SIMULATED DATA")
print("="*70)
print()

# Extract state vectors
states_before = []
states_after = []

for interaction in data:
    if 'state_before' in interaction:
        states_before.append(interaction['state_before'])
    if 'state_after' in interaction:
        states_after.append(interaction['state_after'])

all_states = states_before + states_after
print(f"Total states: {len(all_states)}")
print()

# Analyze each dimension
print("STATE DIMENSIONS ANALYSIS:")
print("-"*70)

dim_names = [
    'knowledge_level',
    'engagement_level', 
    'struggle_indicator',
    'submission_activity',      # Dim 3 - WAS 0 BEFORE
    'review_activity',
    'resource_usage',
    'assessment_engagement',
    'collaborative_activity',   # Dim 7 - WAS 0 BEFORE
    'overall_progress',
    'module_completion_rate',
    'activity_diversity',
    'completion_consistency'
]

for dim_idx in range(12):
    values = [s[dim_idx] for s in all_states if len(s) > dim_idx]
    
    unique_vals = len(set(values))
    min_val = min(values)
    max_val = max(values)
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    # Count zeros
    zeros = sum(1 for v in values if v == 0.0)
    zero_pct = zeros / len(values) * 100 if values else 0
    
    status = "✅" if zero_pct < 50 else "⚠️" if zero_pct < 100 else "❌"
    
    print(f"[{dim_idx:2d}] {dim_names[dim_idx]:<25} {status}")
    print(f"     Range: [{min_val:.3f}, {max_val:.3f}]  Mean: {mean_val:.3f}  Std: {std_val:.3f}")
    print(f"     Unique: {unique_vals}  Zeros: {zeros}/{len(values)} ({zero_pct:.1f}%)")
    
    # Highlight critical dimensions
    if dim_idx == 3:
        print(f"     🎯 SUBMISSION: {'DIVERSE!' if zero_pct < 50 else 'STILL ALL ZEROS!'}")
    elif dim_idx == 7:
        print(f"     🎯 COLLABORATIVE: {'DIVERSE!' if zero_pct < 50 else 'STILL ALL ZEROS!'}")
    print()

print("="*70)
print("KEY METRICS:")
print("="*70)

# Check if diverse
dim3_values = [s[3] for s in all_states if len(s) > 3]
dim7_values = [s[7] for s in all_states if len(s) > 7]

dim3_zeros = sum(1 for v in dim3_values if v == 0.0)
dim7_zeros = sum(1 for v in dim7_values if v == 0.0)

dim3_zero_pct = dim3_zeros / len(dim3_values) * 100
dim7_zero_pct = dim7_zeros / len(dim7_values) * 100

print(f"Dimension 3 (submission_activity):")
print(f"  Zeros: {dim3_zeros}/{len(dim3_values)} ({dim3_zero_pct:.1f}%)")
print(f"  Status: {'✅ DIVERSE' if dim3_zero_pct < 50 else '❌ STILL ALL ZEROS'}")
print()

print(f"Dimension 7 (collaborative_activity):")
print(f"  Zeros: {dim7_zeros}/{len(dim7_values)} ({dim7_zero_pct:.1f}%)")
print(f"  Status: {'✅ DIVERSE' if dim7_zero_pct < 50 else '❌ STILL ALL ZEROS'}")
print()

if dim3_zero_pct < 50 and dim7_zero_pct < 50:
    print("🎉 SUCCESS! Data is now diverse!")
    print("   Ready to retrain model with better coverage!")
else:
    print("⚠️  WARNING: Data still not diverse enough")
    print("   Need to check simulate_learning_data.py")

print("="*70)
