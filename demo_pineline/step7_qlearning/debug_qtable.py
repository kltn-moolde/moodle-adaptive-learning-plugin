#!/usr/bin/env python3
"""
Script để kiểm tra Q-table và debug vấn đề Q-values = 0
"""
import pickle
import sys
import numpy as np
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / 'models' / 'qlearning_model.pkl'


def load_qtable():
    """Load Q-table from pickle file"""
    if not MODEL_PATH.exists():
        print(f"❌ Model not found at {MODEL_PATH}")
        return None
    
    with open(MODEL_PATH, 'rb') as f:
        data = pickle.load(f)
    
    return data


def analyze_qtable(data):
    """Phân tích Q-table chi tiết"""
    print("\n" + "="*70)
    print("📊 Q-TABLE ANALYSIS")
    print("="*70)
    
    q_table = data['q_table']
    training_stats = data.get('training_stats', {})
    
    # Basic stats
    print(f"\n1️⃣ BASIC STATISTICS:")
    print(f"   - Total states in Q-table: {len(q_table):,}")
    print(f"   - Total actions: {data['n_actions']}")
    print(f"   - State decimals: {data['state_decimals']}")
    print(f"   - Learning rate: {data['learning_rate']}")
    print(f"   - Discount factor: {data['discount_factor']}")
    print(f"   - Epsilon: {data['epsilon']}")
    
    # Training stats
    print(f"\n2️⃣ TRAINING HISTORY:")
    print(f"   - Episodes trained: {training_stats.get('episodes', 'N/A'):,}")
    print(f"   - Total Q-table updates: {training_stats.get('total_updates', 'N/A'):,}")
    print(f"   - Average reward: {training_stats.get('avg_reward', 'N/A'):.4f}")
    print(f"   - States visited: {training_stats.get('states_visited', 'N/A'):,}")
    
    # Actions per state
    actions_per_state = [len(actions) for actions in q_table.values()]
    print(f"\n3️⃣ ACTIONS PER STATE:")
    print(f"   - Min actions: {min(actions_per_state)}")
    print(f"   - Max actions: {max(actions_per_state)}")
    print(f"   - Average actions: {np.mean(actions_per_state):.2f}")
    print(f"   - Median actions: {np.median(actions_per_state):.2f}")
    
    # Q-value distribution
    all_q_values = []
    for state_actions in q_table.values():
        all_q_values.extend(state_actions.values())
    
    if all_q_values:
        print(f"\n4️⃣ Q-VALUE DISTRIBUTION:")
        print(f"   - Total Q-values: {len(all_q_values):,}")
        print(f"   - Min Q-value: {min(all_q_values):.4f}")
        print(f"   - Max Q-value: {max(all_q_values):.4f}")
        print(f"   - Mean Q-value: {np.mean(all_q_values):.4f}")
        print(f"   - Std Q-value: {np.std(all_q_values):.4f}")
        
        # Count zeros
        zero_count = sum(1 for q in all_q_values if abs(q) < 0.0001)
        print(f"   - Q-values = 0: {zero_count:,} ({zero_count/len(all_q_values)*100:.1f}%)")
    
    # State space analysis
    print(f"\n5️⃣ STATE SPACE COVERAGE:")
    
    # Get state dimensions
    sample_state = list(q_table.keys())[0]
    state_dim = len(sample_state)
    print(f"   - State dimension: {state_dim}")
    
    # Analyze each dimension
    for dim in range(state_dim):
        values = [state[dim] for state in q_table.keys()]
        unique_values = len(set(values))
        print(f"   - Dimension {dim}: {unique_values} unique values (range: {min(values):.1f} - {max(values):.1f})")
    
    return q_table


def show_sample_states(q_table, n=5):
    """Show sample states với Q-values cao nhất"""
    print(f"\n6️⃣ TOP {n} STATES (by max Q-value):")
    
    # Calculate max Q-value per state
    state_max_q = []
    for state_hash, actions in q_table.items():
        if actions:
            max_q = max(actions.values())
            state_max_q.append((state_hash, max_q, len(actions)))
    
    # Sort by max Q-value
    state_max_q.sort(key=lambda x: x[1], reverse=True)
    
    for i, (state_hash, max_q, n_actions) in enumerate(state_max_q[:n], 1):
        print(f"\n   {i}. State: {state_hash}")
        print(f"      - Max Q-value: {max_q:.4f}")
        print(f"      - Actions learned: {n_actions}")
        
        # Show top 3 actions
        actions = q_table[state_hash]
        top_actions = sorted(actions.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"      - Top actions:")
        for action_id, q_val in top_actions:
            print(f"         • Action {action_id}: Q={q_val:.4f}")


def test_input_state(q_table, state_decimals):
    """Test state từ user input"""
    print("\n7️⃣ TEST YOUR STATE:")
    print("   Enter state vector (comma-separated, 12 values)")
    print("   Example: 0.6,0.467,0.016,0.0,0.8,0.5,0.2,0.0,0.3,0.8,0.143,0.67")
    print("   (or press Enter to use example)")
    
    user_input = input("\n   Your state: ").strip()
    
    if not user_input:
        # Use example
        state = [0.6, 0.467, 0.016, 0.0, 0.8, 0.5, 0.2, 0.0, 0.3, 0.8, 0.143, 0.67]
        print(f"   → Using example state")
    else:
        try:
            state = [float(x.strip()) for x in user_input.split(',')]
        except:
            print("   ❌ Invalid input")
            return
    
    # Hash state
    state_arr = np.array(state)
    state_hash = tuple(np.round(state_arr, decimals=state_decimals))
    
    print(f"\n   Original state: {state}")
    print(f"   Hashed state:   {state_hash}")
    
    # Check if in Q-table
    if state_hash in q_table:
        print(f"\n   ✅ STATE FOUND IN Q-TABLE!")
        actions = q_table[state_hash]
        print(f"   - Actions learned: {len(actions)}")
        
        if actions:
            print(f"   - Q-value range: {min(actions.values()):.4f} to {max(actions.values()):.4f}")
            
            # Show top 5 actions
            top_actions = sorted(actions.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\n   Top 5 recommended actions:")
            for i, (action_id, q_val) in enumerate(top_actions, 1):
                print(f"      {i}. Action {action_id}: Q={q_val:.4f}")
    else:
        print(f"\n   ❌ STATE NOT IN Q-TABLE")
        print(f"   → API will fallback to random recommendations (q_value = 0.0)")
        
        # Find nearest states
        print(f"\n   🔍 Finding nearest states...")
        distances = []
        for known_state in list(q_table.keys())[:1000]:  # Sample 1000 states
            dist = np.sqrt(sum((a - b)**2 for a, b in zip(state_hash, known_state)))
            distances.append((known_state, dist))
        
        distances.sort(key=lambda x: x[1])
        
        print(f"\n   Closest states in Q-table:")
        for i, (nearest_state, dist) in enumerate(distances[:3], 1):
            print(f"      {i}. Distance={dist:.3f}: {nearest_state}")


def main():
    print("\n🔍 Q-TABLE DEBUGGER")
    
    # Load Q-table
    data = load_qtable()
    if data is None:
        return
    
    # Analyze
    q_table = analyze_qtable(data)
    
    # Show samples
    show_sample_states(q_table, n=5)
    
    # Test state
    test_input_state(q_table, data['state_decimals'])
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print("\n💡 RECOMMENDATIONS:")
    
    n_states = len(q_table)
    if n_states < 5000:
        print("   ⚠️  Q-table has few states (<5000)")
        print("   → Consider training with more diverse data")
    
    if data.get('training_stats', {}).get('episodes', 0) < 5000:
        print("   ⚠️  Few training episodes (<5000)")
        print("   → Train for more episodes")
    
    print("\n   📖 See Q_VALUES_ZERO_EXPLAINED.md for detailed solutions")


if __name__ == "__main__":
    main()
