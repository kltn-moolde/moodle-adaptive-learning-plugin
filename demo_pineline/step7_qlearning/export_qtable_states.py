#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Q-table States
Liệt kê tất cả states có trong Q-table và lưu vào file
"""

import sys
from pathlib import Path
import json
from datetime import datetime

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from services.model_loader import ModelLoader
from core.action_space import ActionSpace

# Configuration
MODEL_PATH = HERE / 'models' / 'qtable.pkl'
COURSE_PATH = HERE / 'data' / 'local' / 'course_structure_5.json'
CLUSTER_PROFILES_PATH = HERE / 'data' / 'cluster_profiles.json'

def export_qtable_states(output_file: str = "qtable_states.json"):
    """
    Export tất cả states trong Q-table ra file
    
    Args:
        output_file: Tên file output (JSON format)
    """
    print("=" * 70)
    print("Exporting Q-table States")
    print("=" * 70)
    
    # Load model
    print("\n1. Loading model...")
    model_loader = ModelLoader(
        model_path=MODEL_PATH,
        course_path=COURSE_PATH,
        cluster_profiles_path=CLUSTER_PROFILES_PATH
    )
    model_loader.load_all(verbose=False)
    
    if not model_loader.agent:
        print("❌ Error: Agent not loaded")
        return
    
    agent = model_loader.agent
    action_space = model_loader.action_space
    state_builder = model_loader.state_builder
    
    q_table = agent.q_table
    
    print(f"✓ Model loaded")
    print(f"  - Q-table size: {len(q_table)} states")
    print(f"  - Total actions: {agent.n_actions}")
    
    # Collect all states with details
    print("\n2. Collecting state information...")
    states_data = []
    
    for state_tuple, q_values in q_table.items():
        # Convert state tuple to list for JSON serialization
        state_list = list(state_tuple)
        
        # Get state description
        try:
            state_desc = state_builder.state_to_string(state_tuple)
        except:
            state_desc = f"State {state_tuple}"
        
        # Get action details
        actions_info = []
        for action_idx, q_value in q_values.items():
            action = action_space.get_action_by_index(action_idx)
            if action:
                actions_info.append({
                    'action_id': action_idx,
                    'action_type': action.action_type,
                    'time_context': action.time_context,
                    'q_value': float(q_value)
                })
            else:
                actions_info.append({
                    'action_id': action_idx,
                    'action_type': 'unknown',
                    'time_context': 'unknown',
                    'q_value': float(q_value)
                })
        
        # Sort actions by Q-value (descending)
        actions_info.sort(key=lambda x: x['q_value'], reverse=True)
        
        # Get best action
        best_action = actions_info[0] if actions_info else None
        max_q_value = best_action['q_value'] if best_action else 0.0
        
        states_data.append({
            'state': state_list,
            'state_description': state_desc,
            'cluster_id': int(state_tuple[0]),
            'module_idx': int(state_tuple[1]),
            'progress_bin': float(state_tuple[2]),
            'score_bin': float(state_tuple[3]),
            'learning_phase': int(state_tuple[4]),
            'engagement_level': int(state_tuple[5]),
            'num_actions': len(actions_info),
            'max_q_value': max_q_value,
            'best_action': best_action,
            'all_actions': actions_info
        })
    
    # Sort states by max_q_value (descending) để dễ xem
    states_data.sort(key=lambda x: x['max_q_value'], reverse=True)
    
    print(f"✓ Collected {len(states_data)} states")
    
    # Prepare summary
    summary = {
        'export_timestamp': datetime.now().isoformat(),
        'total_states': len(states_data),
        'total_actions': agent.n_actions,
        'q_table_stats': agent.get_statistics(),
        'state_dimensions': 6,
        'state_format': '(cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level)'
    }
    
    # Prepare output data
    output_data = {
        'summary': summary,
        'states': states_data
    }
    
    # Save to JSON file
    print(f"\n3. Saving to file: {output_file}...")
    output_path = HERE / output_file
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(states_data)} states to {output_path}")
    
    # Also save a human-readable text file
    text_file = output_path.with_suffix('.txt')
    print(f"\n4. Saving human-readable format to {text_file.name}...")
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("Q-TABLE STATES EXPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Export Time: {summary['export_timestamp']}\n")
        f.write(f"Total States: {summary['total_states']}\n")
        f.write(f"Total Actions: {summary['total_actions']}\n")
        f.write("=" * 70 + "\n\n")
        
        for i, state_data in enumerate(states_data, 1):
            f.write(f"State {i}/{len(states_data)}:\n")
            f.write(f"  State Vector: {state_data['state']}\n")
            f.write(f"  Description: {state_data['state_description']}\n")
            f.write(f"  Cluster ID: {state_data['cluster_id']}\n")
            f.write(f"  Module Index: {state_data['module_idx']}\n")
            f.write(f"  Progress Bin: {state_data['progress_bin']}\n")
            f.write(f"  Score Bin: {state_data['score_bin']}\n")
            f.write(f"  Learning Phase: {state_data['learning_phase']}\n")
            f.write(f"  Engagement Level: {state_data['engagement_level']}\n")
            f.write(f"  Max Q-value: {state_data['max_q_value']:.4f}\n")
            f.write(f"  Number of Actions: {state_data['num_actions']}\n")
            
            if state_data['best_action']:
                f.write(f"  Best Action: {state_data['best_action']['action_type']} ({state_data['best_action']['time_context']}) - Q={state_data['best_action']['q_value']:.4f}\n")
            
            f.write(f"  All Actions ({len(state_data['all_actions'])}):\n")
            for action in state_data['all_actions'][:5]:  # Top 5
                f.write(f"    - Action {action['action_id']}: {action['action_type']} ({action['time_context']}) - Q={action['q_value']:.4f}\n")
            if len(state_data['all_actions']) > 5:
                f.write(f"    ... and {len(state_data['all_actions']) - 5} more actions\n")
            
            f.write("\n" + "-" * 70 + "\n\n")
    
    print(f"✓ Saved human-readable format to {text_file}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Export Summary")
    print("=" * 70)
    print(f"Total states exported: {len(states_data)}")
    print(f"JSON file: {output_path}")
    print(f"Text file: {text_file}")
    print(f"States with Q-values > 0: {sum(1 for s in states_data if s['max_q_value'] > 0)}")
    print(f"States with Q-values = 0: {sum(1 for s in states_data if s['max_q_value'] == 0)}")
    print("=" * 70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export Q-table states to file')
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='qtable_states.json',
        help='Output file name (default: qtable_states.json)'
    )
    
    args = parser.parse_args()
    
    export_qtable_states(output_file=args.output)

