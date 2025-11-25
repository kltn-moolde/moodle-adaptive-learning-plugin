#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Transition Logger - Log chi tiết state transitions
=========================================================
Class để log và minh họa quá trình state transitions trong Q-Learning
"""

from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import json


class StateTransitionLogger:
    """
    Log chi tiết state transitions trong quá trình training/inference
    
    Features:
    - Log state transitions với đầy đủ context
    - Track action selection (exploration vs exploitation)
    - Log reward calculation breakdown
    - Track LO filtering và recommendations
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize logger
        
        Args:
            verbose: Print logs to console
        """
        self.verbose = verbose
        self.transitions: List[Dict] = []
        self.step_counter = 0
        
        # Statistics
        self.stats = {
            'total_steps': 0,
            'exploration_count': 0,
            'exploitation_count': 0,
            'state_visits': defaultdict(int),
            'action_distribution': defaultdict(int),
            'reward_sum': 0.0,
            'reward_min': float('inf'),
            'reward_max': float('-inf')
        }
    
    def log_transition(
        self,
        step: int,
        student_id: int,
        cluster_id: int,
        state: Tuple,
        action_idx: int,
        action_type: str,
        activity_id: Optional[int],
        activity_name: Optional[str],
        reward: float,
        reward_breakdown: Optional[Dict] = None,
        next_state: Optional[Tuple] = None,
        q_value: Optional[float] = None,
        max_q_value: Optional[float] = None,
        is_exploration: bool = False,
        weak_los: Optional[List[Tuple[str, float, float]]] = None,
        lo_deltas: Optional[Dict[str, float]] = None,
        midterm_prediction: Optional[Dict] = None,
        timestamp: Optional[int] = None
    ):
        """
        Log một state transition
        
        Args:
            step: Step number
            student_id: Student ID
            cluster_id: Cluster ID
            state: Current state tuple
            action_idx: Selected action index
            action_type: Action type string
            activity_id: Recommended activity ID
            activity_name: Activity name
            reward: Reward value
            reward_breakdown: Breakdown of reward components
            next_state: Next state tuple
            q_value: Q-value for state-action pair
            max_q_value: Max Q-value for next state
            is_exploration: Whether action was exploration
            weak_los: List of weak LOs that were considered
            lo_deltas: Dict of LO mastery deltas
            midterm_prediction: Midterm score prediction
            timestamp: Timestamp/step number
        """
        transition = {
            'step': step,
            'timestamp': timestamp or step,
            'student_id': student_id,
            'cluster_id': cluster_id,
            'state': {
                'vector': list(state),
                'description': self._describe_state(state)
            },
            'action': {
                'index': action_idx,
                'type': action_type,
                'activity_id': activity_id,
                'activity_name': activity_name,
                'is_exploration': is_exploration
            },
            'q_values': {
                'current_q': float(q_value) if q_value is not None else None,
                'max_next_q': float(max_q_value) if max_q_value is not None else None
            },
            'reward': {
                'total': float(reward),
                'breakdown': reward_breakdown or {}
            },
            'lo_analysis': {
                'weak_los': [
                    {
                        'lo_id': lo_id,
                        'mastery': float(mastery),
                        'weight': float(weight)
                    }
                    for lo_id, mastery, weight in (weak_los or [])
                ],
                'lo_deltas': {
                    lo_id: float(delta)
                    for lo_id, delta in (lo_deltas or {}).items()
                }
            },
            'midterm_prediction': midterm_prediction,
            'next_state': {
                'vector': list(next_state) if next_state else None,
                'description': self._describe_state(next_state) if next_state else None
            }
        }
        
        self.transitions.append(transition)
        self.step_counter += 1
        
        # Update statistics
        self.stats['total_steps'] += 1
        self.stats['state_visits'][state] += 1
        self.stats['action_distribution'][action_type] += 1
        self.stats['reward_sum'] += reward
        self.stats['reward_min'] = min(self.stats['reward_min'], reward)
        self.stats['reward_max'] = max(self.stats['reward_max'], reward)
        
        if is_exploration:
            self.stats['exploration_count'] += 1
        else:
            self.stats['exploitation_count'] += 1
        
        # Print if verbose
        if self.verbose:
            self._print_transition(transition)
    
    def _describe_state(self, state: Tuple) -> Dict[str, Any]:
        """Describe state in human-readable format"""
        if not state:
            return {}
        
        cluster_names = {0: 'weak', 1: 'weak', 2: 'medium', 3: 'medium', 4: 'strong', 5: 'strong'}
        progress_labels = {0.25: '25%', 0.5: '50%', 0.75: '75%', 1.0: '100%'}
        phase_labels = {0: 'pre-learning', 1: 'active', 2: 'reflective'}
        engagement_labels = {0: 'low', 1: 'medium', 2: 'high'}
        
        return {
            'cluster': cluster_names.get(state[0], f'cluster_{state[0]}'),
            'module': f'module_{state[1]}',
            'progress': progress_labels.get(state[2], f'{state[2]}'),
            'score': progress_labels.get(state[3], f'{state[3]}'),
            'phase': phase_labels.get(state[4], f'phase_{state[4]}'),
            'engagement': engagement_labels.get(state[5], f'level_{state[5]}'),
            'frustration': state[6] if len(state) > 6 else 0
        }
    
    def _print_transition(self, transition: Dict):
        """Print transition in readable format"""
        step = transition['step']
        state_desc = transition['state']['description']
        action = transition['action']
        reward = transition['reward']['total']
        
        print(f"\n{'='*80}")
        print(f"Step {step} | Student {transition['student_id']} ({state_desc['cluster']})")
        print(f"{'='*80}")
        print(f"State: {state_desc['cluster']} | Module {state_desc['module']} | "
              f"Progress {state_desc['progress']} | Score {state_desc['score']}")
        print(f"       Phase: {state_desc['phase']} | Engagement: {state_desc['engagement']}")
        
        action_type = action['type']
        activity_name = action.get('activity_name', 'N/A')
        is_explore = action.get('is_exploration', False)
        
        print(f"\n→ Action Selected: {action_type}")
        if activity_name != 'N/A':
            print(f"  Activity: {activity_name} (ID: {action.get('activity_id')})")
        print(f"  Mode: {'🔍 EXPLORATION' if is_explore else '✅ EXPLOITATION'}")
        
        # Q-values
        q_vals = transition.get('q_values', {})
        if q_vals.get('current_q') is not None:
            print(f"  Q-value: {q_vals['current_q']:.3f}")
        if q_vals.get('max_next_q') is not None:
            print(f"  Max Q(next): {q_vals['max_next_q']:.3f}")
        
        # Weak LOs
        weak_los = transition.get('lo_analysis', {}).get('weak_los', [])
        if weak_los:
            print(f"\n📚 Weak LOs Considered ({len(weak_los)}):")
            for lo in weak_los[:3]:  # Show top 3
                print(f"  - {lo['lo_id']}: mastery={lo['mastery']:.2f}, weight={lo['weight']:.2f}")
        
        # LO Deltas
        lo_deltas = transition.get('lo_analysis', {}).get('lo_deltas', {})
        if lo_deltas:
            print(f"\n📈 LO Mastery Changes:")
            for lo_id, delta in list(lo_deltas.items())[:3]:  # Show top 3
                sign = '+' if delta >= 0 else ''
                print(f"  - {lo_id}: {sign}{delta:.3f}")
        
        # Reward
        print(f"\n💰 Reward: {reward:.2f}")
        reward_breakdown = transition.get('reward', {}).get('breakdown', {})
        if reward_breakdown:
            print(f"  Breakdown:")
            for component, value in reward_breakdown.items():
                if abs(value) > 0.01:  # Only show significant components
                    print(f"    - {component}: {value:.2f}")
        
        # Midterm prediction
        midterm = transition.get('midterm_prediction')
        if midterm:
            pred_score = midterm.get('predicted_score', 0)
            pred_pct = midterm.get('predicted_percentage', 0)
            print(f"\n🎯 Midterm Prediction: {pred_score:.1f}/{midterm.get('total_marks', 20)} ({pred_pct:.1f}%)")
            if midterm.get('potential_improvement', 0) > 0:
                print(f"  Potential improvement: +{midterm['potential_improvement']:.1f} points")
        
        # Next state
        next_state = transition.get('next_state')
        if next_state and next_state.get('description'):
            next_desc = next_state['description']
            print(f"\n→ Next State: {next_desc['cluster']} | Module {next_desc['module']} | "
                  f"Progress {next_desc['progress']} | Score {next_desc['score']}")
    
    def get_transitions(self) -> List[Dict]:
        """Get all logged transitions"""
        return self.transitions
    
    def get_statistics(self) -> Dict:
        """Get statistics about logged transitions"""
        if self.stats['total_steps'] == 0:
            return self.stats
        
        return {
            **self.stats,
            'avg_reward': self.stats['reward_sum'] / self.stats['total_steps'],
            'exploration_rate': self.stats['exploration_count'] / self.stats['total_steps'],
            'exploitation_rate': self.stats['exploitation_count'] / self.stats['total_steps'],
            'unique_states': len(self.stats['state_visits']),
            'unique_actions': len(self.stats['action_distribution'])
        }
    
    def export_to_json(self, filepath: str):
        """Export all transitions to JSON file"""
        import numpy as np
        
        def convert_numpy_types(obj):
            """Recursively convert numpy types to native Python types"""
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                # Convert tuple keys to string representation
                converted_dict = {}
                for key, value in obj.items():
                    if isinstance(key, tuple):
                        key_str = str(key)
                    else:
                        key_str = key
                    converted_dict[key_str] = convert_numpy_types(value)
                return converted_dict
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_numpy_types(item) for item in obj)
            return obj
        
        output = {
            'transitions': self.transitions,
            'statistics': self.get_statistics()
        }
        
        output_converted = convert_numpy_types(output)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_converted, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Exported {len(self.transitions)} transitions to {filepath}")
    
    def reset(self):
        """Reset logger"""
        self.transitions = []
        self.step_counter = 0
        self.stats = {
            'total_steps': 0,
            'exploration_count': 0,
            'exploitation_count': 0,
            'state_visits': defaultdict(int),
            'action_distribution': defaultdict(int),
            'reward_sum': 0.0,
            'reward_min': float('inf'),
            'reward_max': float('-inf')
        }

