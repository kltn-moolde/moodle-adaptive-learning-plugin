#!/usr/bin/env python3
"""
Test state lookup từ API response
"""
import pickle
import numpy as np

# Load model
with open('models/qlearning_model.pkl', 'rb') as f:
    data = pickle.load(f)

q_table = data['q_table']
state_decimals = data['state_decimals']

# State từ API response của bạn
api_state = np.array([0.6, 0.467, 0.016, 0.0, 0.8, 0.5, 0.2, 0.0, 0.3, 0.8, 0.143, 0.67])

# Round như agent làm
rounded = np.round(api_state, decimals=state_decimals)
state_key = tuple(rounded)

print("="*70)
print("🔍 STATE LOOKUP TEST")
print("="*70)
print(f"\nAPI state (raw):     {api_state}")
print(f"Rounded (dec={state_decimals}):  {rounded}")
print(f"State key:           {state_key}")
print(f"\n✅ In Q-table:        {state_key in q_table}")

if state_key in q_table:
    qvals = q_table[state_key]
    print(f"   - Actions available: {len(qvals)}")
    print(f"   - Max Q-value: {max(qvals.values()):.4f}")
    print(f"   - Top 3 actions:")
    for i, (aid, qv) in enumerate(sorted(qvals.items(), key=lambda x: x[1], reverse=True)[:3]):
        print(f"      {i+1}. Action {aid}: Q={qv:.4f}")
else:
    print("\n❌ State NOT in Q-table!")
    print("\nSearching for similar states...")
    
    # Find most similar states
    similarities = []
    for stored_state in q_table.keys():
        diff = sum(abs(s - r) for s, r in zip(stored_state, rounded))
        similarities.append((diff, stored_state))
    
    # Sort by similarity
    similarities.sort()
    
    print(f"\nTop 5 most similar states:")
    for i, (diff, stored_state) in enumerate(similarities[:5]):
        print(f"\n{i+1}. Diff = {diff:.2f}")
        print(f"   Stored: {stored_state}")
        print(f"   Yours:  {state_key}")
        print(f"   Differences at dimensions:")
        for dim_idx in range(len(stored_state)):
            if abs(stored_state[dim_idx] - state_key[dim_idx]) > 0.01:
                print(f"      - Dim {dim_idx}: {stored_state[dim_idx]:.2f} vs {state_key[dim_idx]:.2f}")

print("\n" + "="*70)
