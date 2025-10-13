#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspect Trained Q-Table
========================
Check Q-table sau training để hiểu coverage
"""

import sys
import pickle
from pathlib import Path
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent))


def main():
    # Load trained agent
    model_path = Path(__file__).parent / 'trained_agent_real_data.pkl'
    
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    
    q_table = data['q_table']
    
    print("\n" + "="*70)
    print("🔍 TRAINED Q-TABLE INSPECTION")
    print("="*70)
    
    print(f"\nTotal entries: {len(q_table)}")
    
    # Extract unique states
    states = set()
    state_action_count = defaultdict(int)
    
    for key_str in q_table.keys():
        # Parse key string manually
        # Format: "((1, 2, 0, ...), '52')"
        parts = key_str.strip('()').split('), ')
        state_str = parts[0].strip('(')
        action_str = parts[1].strip("'")
        
        # Convert state tuple
        state_vals = [int(x.strip()) for x in state_str.replace('np.int64(', '').replace(')', '').split(',') if x.strip()]
        state = tuple(state_vals)
        
        states.add(state)
        state_action_count[state] += 1
    
    print(f"Unique states: {len(states)}")
    nonzero_count = sum(1 for v in q_table.values() if v != 0)
    print(f"Non-zero Q-values: {nonzero_count}/{len(q_table)}")
    
    # Show top-10 states by action count
    print(f"\nTop-10 states by action coverage:")
    sorted_states = sorted(state_action_count.items(), key=lambda x: x[1], reverse=True)
    
    for i, (state, count) in enumerate(sorted_states[:10], 1):
        # Get Q-values for this state
        q_values = []
        for key_str, q_val in q_table.items():
            parts = key_str.strip('()').split('), ')
            state_str = parts[0].strip('(')
            state_vals = [int(x.strip()) for x in state_str.replace('np.int64(', '').replace(')', '').split(',') if x.strip()]
            key_state = tuple(state_vals)
            
            if key_state == state:
                q_values.append(q_val)
        
        mean_q = sum(q_values) / len(q_values) if q_values else 0
        nonzero = sum(1 for q in q_values if q != 0)
        
        print(f"\n{i}. State: {state[:3]}...")
        print(f"   Actions: {count}, Non-zero Q: {nonzero}, Mean Q: {mean_q:.4f}")
    
    # Check specific test states
    print(f"\n" + "="*70)
    print("TEST STATES CHECK")
    print("="*70)
    
    test_states = [
        (1, 2, 0, 1, 1, 1, 2, 0, 2, 0, 1, 2),  # Student 1
        (2, 1, 0, 1, 1, 1, 2, 0, 2, 0, 1, 2),  # Student 2  
        (1, 1, 0, 1, 1, 1, 2, 0, 2, 0, 1, 2),  # Student 3 (guessed)
    ]
    
    for i, test_state in enumerate(test_states, 1):
        print(f"\nTest student {i}: {test_state[:3]}...")
        
        # Check if state exists
        if test_state in states:
            print(f"  ✅ State in Q-table")
            
            # Get Q-values
            q_values = []
            for key_str, q_val in q_table.items():
                parts = key_str.strip('()').split('), ')
                state_str = parts[0].strip('(')
                action_str = parts[1].strip("'")
                state_vals = [int(x.strip()) for x in state_str.replace('np.int64(', '').replace(')', '').split(',') if x.strip()]
                key_state = tuple(state_vals)
                
                if key_state == test_state:
                    q_values.append((action_str, q_val))
            
            # Show top-3
            q_values.sort(key=lambda x: x[1], reverse=True)
            print(f"  Top-3 Q-values:")
            for action_id, q_val in q_values[:3]:
                print(f"    Action {action_id}: {q_val:.4f}")
        else:
            print(f"  ❌ State NOT in Q-table")


if __name__ == '__main__':
    main()
