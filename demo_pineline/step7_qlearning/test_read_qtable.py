#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to read and analyze Q-table model data
"""

import pickle
import numpy as np
import json
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.action_space import ActionSpace
    ACTION_SPACE_AVAILABLE = True
except ImportError:
    ACTION_SPACE_AVAILABLE = False
    print("⚠️  Warning: Could not import ActionSpace. Action names will show as numbers.")


# Action mapping (15 actions from the original ACTION_SPACE)
ACTION_NAMES = {
    0: "view_assignment (past)",
    1: "view_content (past)",
    2: "attempt_quiz (past)",
    3: "review_quiz (past)",
    4: "post_forum (past)",
    5: "view_assignment (current)",
    6: "view_content (current)",
    7: "submit_assignment (current)",
    8: "attempt_quiz (current)",
    9: "submit_quiz (current)",
    10: "review_quiz (current)",
    11: "post_forum (current)",
    12: "view_content (future)",
    13: "attempt_quiz (future)",
    14: "post_forum (future)",
}


def get_action_name(action_id: int) -> str:
    """Get action name from ID"""
    if ACTION_SPACE_AVAILABLE:
        try:
            action_space = ActionSpace()
            action = action_space.get_action_by_index(action_id)
            if action:
                return f"{action.action_type} ({action.time_context})"
        except:
            pass
    
    return ACTION_NAMES.get(action_id, f"Action_{action_id}")


def load_qtable(qtable_path: str) -> Dict:
    """
    Load Q-table from pickle file
    
    Args:
        qtable_path: Path to qtable.pkl file
        
    Returns:
        Dictionary containing Q-table data
    """
    with open(qtable_path, 'rb') as f:
        qtable_data = pickle.load(f)
    return qtable_data


def analyze_qtable_structure(qtable_data: Dict):
    """Analyze Q-table structure and print summary"""
    print("=" * 80)
    print("Q-TABLE STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Check what keys are in the data
    print("\n📋 Available Keys:")
    for key in qtable_data.keys():
        print(f"   - {key}")
    
    # Analyze Q-table
    if 'q_table' in qtable_data:
        q_table = qtable_data['q_table']
        print(f"\n📊 Q-Table Statistics:")
        print(f"   - Type: {type(q_table)}")
        print(f"   - Total states: {len(q_table)}")
        
        # Sample some states
        print(f"\n🔍 Sample States (first 5):")
        for i, (state, actions) in enumerate(list(q_table.items())[:5]):
            print(f"\n   State {i+1}: {state}")
            if isinstance(actions, dict):
                print(f"      Actions: {len(actions)} available")
                for action, q_value in list(actions.items())[:3]:
                    print(f"         {action}: {q_value:.4f}")
            else:
                print(f"      Actions: {actions}")
    
    # Analyze metadata
    if 'metadata' in qtable_data:
        metadata = qtable_data['metadata']
        print(f"\n📝 Metadata:")
        for key, value in metadata.items():
            if isinstance(value, (int, float, str, bool)):
                print(f"   - {key}: {value}")
            elif isinstance(value, dict):
                print(f"   - {key}: {len(value)} items")
            elif isinstance(value, list):
                print(f"   - {key}: {len(value)} items")
            else:
                print(f"   - {key}: {type(value)}")
    
    # Analyze training history
    if 'training_history' in qtable_data:
        history = qtable_data['training_history']
        print(f"\n📈 Training History:")
        print(f"   - Episodes: {len(history.get('episodes', []))}")
        if 'rewards' in history:
            rewards = history['rewards']
            print(f"   - Total rewards logged: {len(rewards)}")
            if rewards:
                print(f"   - Reward range: [{min(rewards):.2f}, {max(rewards):.2f}]")
                print(f"   - Average reward: {np.mean(rewards):.2f}")


def parse_state_string(state_str: str) -> tuple:
    """Parse state string to tuple"""
    import ast
    try:
        return ast.literal_eval(state_str)
    except:
        return None


def analyze_state_space(qtable_data: Dict):
    """Analyze state space dimensions"""
    print("\n" + "=" * 80)
    print("STATE SPACE ANALYSIS")
    print("=" * 80)
    
    if 'q_table' not in qtable_data:
        print("❌ No Q-table found in data")
        return
    
    q_table = qtable_data['q_table']
    
    # Parse state strings to tuples
    parsed_states = []
    for state_key in q_table.keys():
        if isinstance(state_key, str):
            parsed = parse_state_string(state_key)
            if parsed:
                parsed_states.append(parsed)
        elif isinstance(state_key, tuple):
            parsed_states.append(state_key)
    
    if not parsed_states:
        print("❌ Could not parse any states")
        return
    
    # Check state dimensions
    state_lengths = set(len(s) for s in parsed_states)
    print(f"\n📏 State Tuple Lengths: {sorted(state_lengths)}")
    
    # Collect unique values for each dimension
    dimension_values = defaultdict(set)
    
    for state in parsed_states:
        for i, value in enumerate(state):
            dimension_values[i].add(value)
    
    print(f"\n🔢 State Dimensions (by position):")
    dimension_names = ["Cluster", "Lesson", "Progress", "Score", "Phase", "Engagement"]
    
    for i in sorted(dimension_values.keys()):
        values = sorted(dimension_values[i])
        name = dimension_names[i] if i < len(dimension_names) else f"Dim{i}"
        print(f"   - {name} (dim {i}): {values[:10]}{'...' if len(values) > 10 else ''} ({len(values)} unique)")
    
    # Calculate theoretical state space for 6D states
    if 6 in state_lengths:
        dim_sizes = [len(dimension_values[i]) for i in range(6)]
        theoretical_size = np.prod(dim_sizes) if dim_sizes else 0
    else:
        theoretical_size = 0
    
    print(f"\n📐 State Space Size:")
    actual_size = len(q_table)
    coverage = (actual_size / theoretical_size * 100) if theoretical_size > 0 else 0
    print(f"   - Theoretical: {theoretical_size:,}")
    print(f"   - Actual (visited): {actual_size:,}")
    print(f"   - Coverage: {coverage:.2f}%")


def analyze_action_space(qtable_data: Dict):
    """Analyze action space and Q-values"""
    print("\n" + "=" * 80)
    print("ACTION SPACE ANALYSIS")
    print("=" * 80)
    
    if 'q_table' not in qtable_data:
        print("❌ No Q-table found in data")
        return
    
    q_table = qtable_data['q_table']
    
    # Collect all actions
    all_actions = set()
    action_counts = defaultdict(int)
    q_value_stats = defaultdict(list)
    
    for state, actions in q_table.items():
        if isinstance(actions, dict):
            for action, q_value in actions.items():
                all_actions.add(action)
                action_counts[action] += 1
                q_value_stats[action].append(q_value)
    
    print(f"\n🎯 Available Actions ({len(all_actions)}):")
    for action in sorted(all_actions):
        action_name = get_action_name(action)
        print(f"   - {action}: {action_name}")
    
    print(f"\n📊 Action Frequency (Top 10):")
    sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
    for action, count in sorted_actions[:10]:  # Top 10
        action_name = get_action_name(action)
        print(f"   - {action_name}: {count:,} states")
    
    print(f"\n💰 Q-Value Statistics by Action (Top 10):")
    # Sort actions by mean Q-value
    action_q_stats = []
    for action in sorted(all_actions):
        if action in q_value_stats:
            values = q_value_stats[action]
            action_q_stats.append((action, np.mean(values), len(values)))
    
    action_q_stats.sort(key=lambda x: x[1], reverse=True)
    
    for action, mean_q, count in action_q_stats[:10]:
        action_name = get_action_name(action)
        values = q_value_stats[action]
        print(f"\n   {action_name}:")
        print(f"      Count: {count}")
        print(f"      Range: [{min(values):.4f}, {max(values):.4f}]")
        print(f"      Mean: {mean_q:.4f}")
        print(f"      Std: {np.std(values):.4f}")


def find_best_actions_by_state(qtable_data: Dict, top_n: int = 10):
    """Find states with highest Q-values"""
    print("\n" + "=" * 80)
    print(f"TOP {top_n} BEST STATE-ACTION PAIRS")
    print("=" * 80)
    
    if 'q_table' not in qtable_data:
        print("❌ No Q-table found in data")
        return
    
    q_table = qtable_data['q_table']
    
    # Collect all state-action pairs with Q-values
    state_action_pairs = []
    for state_key, actions in q_table.items():
        # Parse state string to tuple
        state = parse_state_string(state_key) if isinstance(state_key, str) else state_key
        
        if isinstance(actions, dict):
            for action, q_value in actions.items():
                state_action_pairs.append((state, action, q_value))
    
    # Sort by Q-value
    state_action_pairs.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n🏆 Highest Q-values:")
    for i, (state, action, q_value) in enumerate(state_action_pairs[:top_n], 1):
        action_name = get_action_name(action)
        
        # Handle variable state dimensions
        if isinstance(state, tuple):
            if len(state) >= 6:
                cluster, lesson, progress, score, phase, engagement = state[:6]
                phase_name = {0: "Pre", 1: "Active", 2: "Reflective"}.get(phase, "?")
                engagement_name = {0: "Low", 1: "Medium", 2: "High"}.get(engagement, "?")
                
                print(f"\n   {i}. Q-value: {q_value:.4f}")
                print(f"      State: Cluster={cluster}, Lesson={lesson}, Progress={progress:.2f}, Score={score:.2f}")
                print(f"             Phase={phase_name}, Engagement={engagement_name}")
                if len(state) > 6:
                    print(f"             Extra dims: {state[6:]}")
            else:
                print(f"\n   {i}. Q-value: {q_value:.4f}")
                print(f"      State: {state}")
            print(f"      Action: {action_name}")
        else:
            print(f"\n   {i}. Q-value: {q_value:.4f}")
            print(f"      State: {state}")
            print(f"      Action: {action_name}")


def analyze_learning_patterns(qtable_data: Dict):
    """Analyze learning patterns from Q-table"""
    print("\n" + "=" * 80)
    print("LEARNING PATTERNS ANALYSIS")
    print("=" * 80)
    
    if 'q_table' not in qtable_data:
        print("❌ No Q-table found in data")
        return
    
    q_table = qtable_data['q_table']
    
    # Analyze by learning phase
    phase_actions = defaultdict(lambda: defaultdict(list))
    
    for state_key, actions in q_table.items():
        # Parse state string to tuple
        state = parse_state_string(state_key) if isinstance(state_key, str) else state_key
        
        if isinstance(state, tuple) and len(state) >= 6 and isinstance(actions, dict):
            # Extract phase (dimension 4)
            phase = state[4]
            
            # Get best action for this state
            if actions:
                best_action = max(actions.items(), key=lambda x: x[1])
                phase_actions[phase][best_action[0]].append(best_action[1])
    
    print(f"\n🎓 Best Actions by Learning Phase:")
    phase_names = {0: "Pre-Learning", 1: "Active Learning", 2: "Reflective Learning"}
    
    for phase in sorted(phase_actions.keys()):
        print(f"\n   {phase_names.get(phase, f'Phase {phase}')}:")
        
        # Sort actions by average Q-value
        action_stats = []
        for action, q_values in phase_actions[phase].items():
            action_stats.append((action, len(q_values), np.mean(q_values)))
        
        action_stats.sort(key=lambda x: x[2], reverse=True)
        
        for action, count, avg_q in action_stats[:5]:  # Top 5 per phase
            action_name = get_action_name(action)
            print(f"      - {action_name}: avg Q={avg_q:.4f} (in {count} states)")


def export_qtable_summary(qtable_data: Dict, output_path: str):
    """Export Q-table summary to JSON"""
    print("\n" + "=" * 80)
    print("EXPORTING SUMMARY")
    print("=" * 80)
    
    summary = {
        'metadata': qtable_data.get('metadata', {}),
        'statistics': {
            'total_states': len(qtable_data.get('q_table', {})),
            'total_actions': len(set(
                action
                for actions in qtable_data.get('q_table', {}).values()
                if isinstance(actions, dict)
                for action in actions.keys()
            ))
        }
    }
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        return obj
    
    summary = convert_to_serializable(summary)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Summary exported to: {output_path}")


def main():
    """Main test function"""
    # Path to Q-table
    qtable_path = Path(__file__).parent / 'models' / 'qtable.pkl'
    
    print(f"\n🔍 Loading Q-table from: {qtable_path}")
    
    if not qtable_path.exists():
        print(f"❌ Q-table file not found: {qtable_path}")
        return
    
    try:
        # Load Q-table
        qtable_data = load_qtable(str(qtable_path))
        print("✅ Q-table loaded successfully!")
        
        # Run analyses
        analyze_qtable_structure(qtable_data)
        analyze_state_space(qtable_data)
        analyze_action_space(qtable_data)
        find_best_actions_by_state(qtable_data, top_n=10)
        analyze_learning_patterns(qtable_data)
        
        # Export summary
        output_path = qtable_path.parent / 'qtable_summary.json'
        export_qtable_summary(qtable_data, str(output_path))
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error loading/analyzing Q-table: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
