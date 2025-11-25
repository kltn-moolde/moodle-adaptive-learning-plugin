#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick inspection of Q-table structure
"""

import pickle
from pathlib import Path

# Load Q-table
qtable_path = Path(__file__).parent / 'models' / 'qtable.pkl'

with open(qtable_path, 'rb') as f:
    data = pickle.load(f)

print("=" * 80)
print("Q-TABLE DETAILED INSPECTION")
print("=" * 80)

# Check top-level structure
print("\n📦 Top-level keys:")
for key, value in data.items():
    print(f"   - {key}: {type(value).__name__}")

# Examine q_table structure
if 'q_table' in data:
    q_table = data['q_table']
    print(f"\n📊 Q-Table info:")
    print(f"   - Type: {type(q_table).__name__}")
    print(f"   - Number of states: {len(q_table)}")
    
    # Get first few states
    print(f"\n🔍 First 3 states (detailed):")
    for i, (state, actions) in enumerate(list(q_table.items())[:3]):
        print(f"\n   State {i+1}:")
        print(f"      Key type: {type(state).__name__}")
        print(f"      Key value: {state}")
        if isinstance(state, tuple):
            print(f"      Tuple length: {len(state)}")
            print(f"      Elements: {[type(x).__name__ for x in state]}")
        print(f"      Actions type: {type(actions).__name__}")
        if isinstance(actions, dict):
            print(f"      Number of actions: {len(actions)}")
            print(f"      Sample actions: {list(actions.items())[:3]}")

# Examine config
if 'config' in data:
    config = data['config']
    print(f"\n⚙️  Config:")
    for key, value in config.items():
        print(f"   - {key}: {value}")

# Examine stats
if 'stats' in data:
    stats = data['stats']
    print(f"\n📈 Stats:")
    for key, value in stats.items():
        if isinstance(value, (int, float, str, bool)):
            print(f"   - {key}: {value}")
        elif isinstance(value, (list, dict)):
            print(f"   - {key}: {type(value).__name__} with {len(value)} items")
        else:
            print(f"   - {key}: {type(value).__name__}")

print("\n" + "=" * 80)
