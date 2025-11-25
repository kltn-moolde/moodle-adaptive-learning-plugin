#!/usr/bin/env python3
"""
Export Q-table information and generate test inputs
- Export Q-table statistics to JSON
- Export states with Q-value > 0 as flat format for API testing
"""

import pickle
import json
import sys
import numpy as np
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / 'models' / 'qtable_best.pkl'  # ✅ Updated to trained model
OUTPUT_DIR = HERE / 'qtable_exports'


def load_qtable():
    """Load Q-table from pickle file"""
    if not MODEL_PATH.exists():
        print(f"❌ Model not found at {MODEL_PATH}")
        return None
    
    with open(MODEL_PATH, 'rb') as f:
        data = pickle.load(f)
    
    return data


def get_qtable_summary(data: Dict) -> Dict:
    """
    Tạo summary đầy đủ của Q-table (Updated for new format)
    """
    q_table = data['q_table']
    config = data.get('config', {})
    stats = data.get('stats', {})
    
    # Collect all Q-values
    all_q_values = []
    states_with_nonzero_q = 0
    for state_key, state_actions in q_table.items():
        # Convert string keys to tuples if needed
        if isinstance(state_actions, dict):
            q_vals = list(state_actions.values())
        else:
            q_vals = []
        all_q_values.extend(q_vals)
        if any(abs(q) > 0.0001 for q in q_vals):
            states_with_nonzero_q += 1
    
    # Count Q-values by range
    zero_count = sum(1 for q in all_q_values if abs(q) < 0.0001)
    positive_count = sum(1 for q in all_q_values if q > 0.0001)
    negative_count = sum(1 for q in all_q_values if q < -0.0001)
    
    # State space analysis
    sample_state_key = list(q_table.keys())[0] if q_table else "(0,0,0,0,0,0)"
    # Parse state from string if needed
    if isinstance(sample_state_key, str):
        sample_state = eval(sample_state_key)
    else:
        sample_state = sample_state_key
    state_dim = len(sample_state) if isinstance(sample_state, (list, tuple)) else 0
    
    dimension_stats = []
    if state_dim > 0:
        for dim in range(state_dim):
            values = []
            for state_key in q_table.keys():
                if isinstance(state_key, str):
                    state = eval(state_key)
                else:
                    state = state_key
                if isinstance(state, (list, tuple)) and len(state) > dim:
                    values.append(state[dim])
            if values:
                dimension_stats.append({
                    'dimension': dim,
                    'unique_values': len(set(values)),
                    'min': float(min(values)),
                    'max': float(max(values)),
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values))
                })
    
    summary = {
        'model_info': {
            'n_actions': config.get('n_actions', 0),
            'learning_rate': config.get('learning_rate', 0.1),
            'discount_factor': config.get('discount_factor', 0.95),
            'epsilon': config.get('epsilon', 0.01),
            'cluster_adaptive': config.get('cluster_adaptive', True),
            'cluster_learning_rates': config.get('cluster_learning_rates', {})
        },
        'training_stats': {
            'episodes': stats.get('episodes_trained', 0),
            'total_updates': stats.get('total_updates', 0),
            'avg_reward': 0.0,  # Not available in new format
            'states_visited': len(q_table)
        },
        'qtable_stats': {
            'total_states': len(q_table),
            'states_with_nonzero_q': states_with_nonzero_q,
            'state_dimension': state_dim,
            'total_q_values': len(all_q_values),
            'q_value_distribution': {
                'zero_count': zero_count,
                'zero_percentage': round(zero_count / len(all_q_values) * 100, 2) if all_q_values else 0,
                'positive_count': positive_count,
                'positive_percentage': round(positive_count / len(all_q_values) * 100, 2) if all_q_values else 0,
                'negative_count': negative_count,
                'negative_percentage': round(negative_count / len(all_q_values) * 100, 2) if all_q_values else 0,
                'min': float(min(all_q_values)) if all_q_values else 0,
                'max': float(max(all_q_values)) if all_q_values else 0,
                'mean': float(np.mean(all_q_values)) if all_q_values else 0,
                'std': float(np.std(all_q_values)) if all_q_values else 0
            }
        },
        'dimension_stats': dimension_stats
    }
    
    return summary


def state_tuple_to_features(state_tuple: Tuple) -> Dict:
    """
    Convert state tuple (6 dims V2) to description for API testing
    
    State V2 indices:
    0: cluster_id (0-4 mapped from original 0,1,2,4,5)
    1: module_idx (0-35 for 36 modules)
    2: progress_bin (0, 0.25, 0.5, 0.75, 1.0)
    3: score_bin (0, 0.25, 0.5, 0.75, 1.0)
    4: action_type (0-5: submit, read, review, forum, quiz, other)
    5: is_stuck (0=False, 1=True)
    """
    if len(state_tuple) != 6:
        raise ValueError(f"Expected 6 dimensions (V2 format), got {len(state_tuple)}")
    
    action_type_names = ['submit', 'read_resource', 'review', 'forum', 'quiz', 'other']
    
    return {
        "cluster_id": int(state_tuple[0]),
        "module_index": int(state_tuple[1]),
        "progress_bin": float(state_tuple[2]),
        "score_bin": float(state_tuple[3]),
        "recent_action_type": action_type_names[int(state_tuple[4])] if 0 <= int(state_tuple[4]) < len(action_type_names) else 'unknown',
        "is_stuck": bool(state_tuple[5])
    }


def export_states_with_positive_q(data: Dict, top_n: int = 50) -> List[Dict]:
    """
    Export states có Q-value > 0, sorted by max Q-value
    
    Returns:
        List of dicts with state and Q-value info
    """
    q_table = data['q_table']
    
    # Find states with positive Q-values
    states_with_q = []
    
    for state_key, actions in q_table.items():
        # Convert string key to tuple if needed
        if isinstance(state_key, str):
            state_tuple = eval(state_key)
        else:
            state_tuple = state_key
            
        max_q = max(actions.values()) if actions else 0
        
        if max_q > 0.0001:  # Only positive Q-values
            # Find best action
            best_action = max(actions.items(), key=lambda x: x[1])
            
            states_with_q.append({
                'state_tuple': state_tuple,
                'max_q_value': float(max_q),
                'best_action_id': int(best_action[0]),
                'best_action_q': float(best_action[1]),
                'num_actions': len(actions),
                'avg_q_value': float(np.mean(list(actions.values())))
            })
    
    # Sort by max Q-value (descending)
    states_with_q.sort(key=lambda x: x['max_q_value'], reverse=True)
    
    # Take top N
    top_states = states_with_q[:top_n]
    
    # Convert to flat features for API testing
    result = []
    for i, state_info in enumerate(top_states):
        features = state_tuple_to_features(state_info['state_tuple'])
        
        result.append({
            'rank': i + 1,
            'features': features,
            'q_info': {
                'max_q_value': state_info['max_q_value'],
                'best_action_id': state_info['best_action_id'],
                'num_actions': state_info['num_actions'],
                'avg_q_value': state_info['avg_q_value']
            }
        })
    
    return result


def export_diverse_states(data: Dict, n_samples: int = 20) -> List[Dict]:
    """
    Export diverse states (covering different ranges of values)
    """
    q_table = data['q_table']
    
    # Find states with positive Q-values
    positive_q_states = []
    for state_key, actions in q_table.items():
        # Convert string key to tuple if needed
        if isinstance(state_key, str):
            state_tuple = eval(state_key)
        else:
            state_tuple = state_key
            
        max_q = max(actions.values()) if actions else 0
        if max_q > 0.0001:
            positive_q_states.append((state_tuple, max_q))
    
    if not positive_q_states:
        return []
    
    # Sort by Q-value
    positive_q_states.sort(key=lambda x: x[1], reverse=True)
    
    # Sample diverse states (stratified by Q-value ranges)
    diverse_samples = []
    
    # Take from different quartiles
    total = len(positive_q_states)
    indices = [
        0,  # Best
        total // 4,  # 75th percentile
        total // 2,  # Median
        3 * total // 4,  # 25th percentile
    ]
    
    for idx in indices:
        if idx < total:
            state_tuple, max_q = positive_q_states[idx]
            features = state_tuple_to_features(state_tuple)
            diverse_samples.append({
                'features': features,
                'max_q_value': float(max_q),
                'percentile': ['top', '75th', '50th', '25th'][indices.index(idx)]
            })
    
    # Add random samples from the rest
    import random
    remaining = [s for i, s in enumerate(positive_q_states) if i not in indices]
    random_samples = random.sample(remaining, min(n_samples - len(diverse_samples), len(remaining)))
    
    for state_tuple, max_q in random_samples:
        features = state_tuple_to_features(state_tuple)
        diverse_samples.append({
            'features': features,
            'max_q_value': float(max_q),
            'percentile': 'random'
        })
    
    return diverse_samples


def main():
    """Main execution"""
    print("="*80)
    print("📊 Q-TABLE INFORMATION EXPORTER")
    print("="*80)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Load Q-table
    print(f"\n1️⃣ Loading Q-table from: {MODEL_PATH}")
    data = load_qtable()
    
    if data is None:
        print("❌ Failed to load Q-table")
        return
    
    print("✅ Q-table loaded successfully")
    
    # Generate summary
    print("\n2️⃣ Generating Q-table summary...")
    summary = get_qtable_summary(data)
    
    summary_file = OUTPUT_DIR / 'qtable_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Summary saved to: {summary_file}")
    print(f"   - Total states: {summary['qtable_stats']['total_states']:,}")
    print(f"   - States with Q>0: {summary['qtable_stats']['states_with_nonzero_q']:,}")
    print(f"   - Positive Q-values: {summary['qtable_stats']['q_value_distribution']['positive_count']:,} "
          f"({summary['qtable_stats']['q_value_distribution']['positive_percentage']:.1f}%)")
    
    # Export top states with positive Q
    print("\n3️⃣ Exporting states with positive Q-values (top 50)...")
    top_states = export_states_with_positive_q(data, top_n=50)
    
    top_states_file = OUTPUT_DIR / 'states_with_positive_q.json'
    with open(top_states_file, 'w', encoding='utf-8') as f:
        json.dump(top_states, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Top states saved to: {top_states_file}")
    print(f"   - Total states with Q>0: {len(top_states)}")
    
    if top_states:
        print(f"\n   📋 TOP 3 STATES:")
        for i in range(min(3, len(top_states))):
            state = top_states[i]
            print(f"\n   #{i+1} (Q-value: {state['q_info']['max_q_value']:.4f})")
            print(f"   Features: {json.dumps(state['features'], indent=6)}")
    
    # Export diverse samples
    print("\n4️⃣ Exporting diverse state samples...")
    diverse_states = export_diverse_states(data, n_samples=20)
    
    diverse_file = OUTPUT_DIR / 'diverse_states_samples.json'
    with open(diverse_file, 'w', encoding='utf-8') as f:
        json.dump(diverse_states, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Diverse samples saved to: {diverse_file}")
    print(f"   - Total samples: {len(diverse_states)}")
    
    # Create a simple test file with just features (ready to copy-paste)
    print("\n5️⃣ Creating copy-paste ready test inputs...")
    test_inputs = []
    for i, state in enumerate(top_states[:10]):
        test_inputs.append({
            f"test_case_{i+1}": state['features'],
            "expected_q_value": state['q_info']['max_q_value']
        })
    
    test_file = OUTPUT_DIR / 'test_inputs_ready.json'
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_inputs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test inputs saved to: {test_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("✅ EXPORT COMPLETED!")
    print("="*80)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"\n📄 Files created:")
    print(f"   1. qtable_summary.json          - Q-table statistics")
    print(f"   2. states_with_positive_q.json  - Top 50 states with Q>0")
    print(f"   3. diverse_states_samples.json  - Diverse state samples")
    print(f"   4. test_inputs_ready.json       - Copy-paste ready test inputs")
    
    print(f"\n💡 Usage:")
    print(f"   # View summary")
    print(f"   cat {summary_file}")
    print(f"   ")
    print(f"   # Test with top state")
    print(f"   curl -X POST http://localhost:8080/api/recommend \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"student_id\": 1, \"features\": {json.dumps(top_states[0]['features'])}, \"top_k\": 3}}'")


if __name__ == '__main__':
    main()
