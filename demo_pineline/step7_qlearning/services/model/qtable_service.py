#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Table Service
===============
Service layer for Q-table analysis and export
"""

import sys
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Add parent directory to path for imports
HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from core.rl.action_space import ActionSpace


class QTableService:
    """Service for Q-table analysis and information extraction"""
    
    def __init__(self, agent=None, action_space=None):
        """
        Initialize Q-Table Service
        
        Args:
            agent: QLearningAgent instance with loaded Q-table
            action_space: ActionSpace instance for action name lookup
        """
        self.agent = agent
        self.action_space = action_space if action_space else ActionSpace()
        self.action_space = action_space if action_space else ActionSpace()
    
    def _get_action_name(self, action_id: int) -> str:
        """
        Get human-readable action name from action ID
        
        Args:
            action_id: Action index (0-based)
        
        Returns:
            Action name string
        """
        if self.action_space:
            action = self.action_space.get_action_by_index(action_id)
            if action:
                return f"{action.action_type} ({action.time_context})"
        return f"action_{action_id}"
    
    def get_qtable_info(self) -> Dict:
        """
        Get Q-table metadata and structure information (6D state space)
        
        Returns:
            Dict with Q-table info including dimensions, actions, hyperparameters
        """
        if not self.agent:
            return {'error': 'No agent loaded'}
        
        q_table = self.agent.q_table
        
        # Get unique states and actions
        all_states = list(q_table.keys())
        all_actions = set()
        for state_actions in q_table.values():
            all_actions.update(state_actions.keys())
        
        # Get state dimension
        state_dim = len(all_states[0]) if all_states else 0
        
        # Get action space info
        action_list = sorted(list(all_actions))
        
        # Create action mapping with names
        action_mapping = {}
        for action_id in action_list:
            action_mapping[action_id] = self._get_action_name(action_id)
        
        # Get hyperparameters
        hyperparams = {
            'learning_rate': self.agent.learning_rate,
            'discount_factor': self.agent.discount_factor,
            'epsilon': self.agent.epsilon
        }
        
        # Get training info from stats
        training_info = {
            'episodes_trained': self.agent.stats.get('episodes_trained', 0),
            'total_updates': self.agent.stats.get('total_updates', 0),
            'q_table_size': self.agent.stats.get('q_table_size', len(q_table))
        }
        
        # Get Q-table size info
        total_state_action_pairs = sum(len(actions) for actions in q_table.values())
        
        return {
            'qtable_metadata': {
                'total_states': len(all_states),
                'total_actions': len(action_list),
                'state_dimension': state_dim,
                'total_state_action_pairs': total_state_action_pairs,
                'sparsity': round(
                    1 - (total_state_action_pairs / (len(all_states) * len(action_list))),
                    4
                ) if all_states and action_list else 0
            },
            'state_space': {
                'dimension': state_dim,
                'total_states': len(all_states),
                'state_format': '6D tuple: (cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level)',
                'features': [
                    'cluster_id (0-4: weak/medium/strong)',
                    'module_idx (0-5: current module)',
                    'progress_bin (0.25/0.5/0.75/1.0: module progress quartiles)',
                    'score_bin (0.25/0.5/0.75/1.0: score quartiles)',
                    'learning_phase (0-2: pre/active/reflective)',
                    'engagement_level (0-2: low/medium/high)'
                ]
            },
            'action_space': {
                'total_actions': len(action_list),
                'action_ids': action_list,
                'action_mapping': action_mapping,
                'action_format': 'integer ID (0-14) representing action types'
            },
            'hyperparameters': hyperparams,
            'training_info': training_info
        }
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive Q-table summary
        
        Returns:
            Dict with Q-table statistics
        """
        if not self.agent:
            return {'error': 'No agent loaded'}
        
        q_table = self.agent.q_table
        
        # Collect all Q-values
        all_q_values = []
        states_with_nonzero_q = 0
        
        for state_actions in q_table.values():
            q_vals = list(state_actions.values())
            all_q_values.extend(q_vals)
            if any(abs(q) > 0.0001 for q in q_vals):
                states_with_nonzero_q += 1
        
        # Q-value distribution
        zero_count = sum(1 for q in all_q_values if abs(q) < 0.0001)
        positive_count = sum(1 for q in all_q_values if q > 0.0001)
        negative_count = sum(1 for q in all_q_values if q < -0.0001)
        
        # State space analysis (6D)
        dimension_stats = []
        if q_table:
            sample_state = next(iter(q_table.keys()))
            state_dim = len(sample_state)
            
            dimension_names = [
                'cluster_id',
                'module_idx', 
                'progress_bin',
                'score_bin',
                'learning_phase',
                'engagement_level'
            ]
            
            for dim in range(state_dim):
                values = [state[dim] for state in q_table.keys()]
                dimension_stats.append({
                    'dimension': dim,
                    'name': dimension_names[dim] if dim < len(dimension_names) else f'dim_{dim}',
                    'unique_values': len(set(values)),
                    'min': float(min(values)),
                    'max': float(max(values)),
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values))
                })
        
        return {
            'model_info': {
                'n_actions': self.agent.n_actions,
                'learning_rate': self.agent.learning_rate,
                'discount_factor': self.agent.discount_factor,
                'epsilon': self.agent.epsilon
            },
            'training_stats': {
                'episodes_trained': self.agent.stats.get('episodes_trained', 0),
                'total_updates': self.agent.stats.get('total_updates', 0),
                'q_table_size': self.agent.stats.get('q_table_size', len(q_table))
            },
            'qtable_stats': {
                'total_states': len(q_table),
                'states_with_nonzero_q': states_with_nonzero_q,
                'state_dimension': len(sample_state) if q_table else 0,
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
    
    def get_states_with_positive_q(self, top_n: int = 50, min_q_value: float = 0.0001) -> List[Dict]:
        """
        Get states with positive Q-values
        
        Args:
            top_n: Number of top states to return
            min_q_value: Minimum Q-value threshold
        
        Returns:
            List of states with their features and Q-info
        """
        if not self.agent:
            return []
        
        q_table = self.agent.q_table
        states_with_q = []
        
        for state_tuple, actions in q_table.items():
            if not actions:
                continue
            
            max_q = max(actions.values())
            
            if max_q > min_q_value:
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
        
        # Convert to flat features
        result = []
        for i, state_info in enumerate(states_with_q[:top_n]):
            features = self._state_tuple_to_features(state_info['state_tuple'])
            
            result.append({
                'rank': i + 1,
                'features': features,
                'q_info': {
                    'max_q_value': state_info['max_q_value'],
                    'best_action_id': state_info['best_action_id'],
                    'best_action_name': self._get_action_name(state_info['best_action_id']),
                    'num_actions': state_info['num_actions'],
                    'avg_q_value': state_info['avg_q_value']
                }
            })
        
        return result
    
    def get_diverse_samples(self, n_samples: int = 20) -> List[Dict]:
        """
        Get diverse state samples from different Q-value ranges
        
        Args:
            n_samples: Number of samples to return
        
        Returns:
            List of diverse state samples
        """
        if not self.agent:
            return []
        
        q_table = self.agent.q_table
        
        # Find states with positive Q-values
        positive_q_states = []
        for state_tuple, actions in q_table.items():
            if not actions:
                continue
            max_q = max(actions.values())
            if max_q > 0.0001:
                positive_q_states.append((state_tuple, max_q))
        
        if not positive_q_states:
            return []
        
        # Sort by Q-value
        positive_q_states.sort(key=lambda x: x[1], reverse=True)
        
        diverse_samples = []
        total = len(positive_q_states)
        
        # Sample from different quartiles
        quartile_indices = [
            0,  # Best
            total // 4,  # 75th percentile
            total // 2,  # Median
            3 * total // 4  # 25th percentile
        ]
        
        percentile_labels = ['top', '75th', '50th', '25th']
        
        for idx, label in zip(quartile_indices, percentile_labels):
            if idx < total:
                state_tuple, max_q = positive_q_states[idx]
                features = self._state_tuple_to_features(state_tuple)
                diverse_samples.append({
                    'features': features,
                    'max_q_value': float(max_q),
                    'percentile': label
                })
        
        # Add random samples
        import random
        remaining_indices = [i for i in range(total) if i not in quartile_indices]
        n_random = min(n_samples - len(diverse_samples), len(remaining_indices))
        
        if n_random > 0:
            random_indices = random.sample(remaining_indices, n_random)
            for idx in random_indices:
                state_tuple, max_q = positive_q_states[idx]
                features = self._state_tuple_to_features(state_tuple)
                diverse_samples.append({
                    'features': features,
                    'max_q_value': float(max_q),
                    'percentile': 'random'
                })
        
        return diverse_samples
    
    def _state_tuple_to_features(self, state_tuple: Tuple) -> Dict:
        """
        Convert state tuple to flat feature dict
        
        V2 State (6 dimensions):
        0: cluster_id (0-4)
        1: module_idx (0-35)
        2: progress_bin (0.25, 0.5, 0.75, 1.0)
        3: score_bin (0.25, 0.5, 0.75, 1.0)
        4: action_id (0-5)
        5: is_stuck (0 or 1)
        
        V1 State (12 dimensions) - deprecated:
        0: knowledge_level, 1: engagement_level, 2: struggle_indicator, ...
        """
        if len(state_tuple) == 6:
            # V2 format
            cluster_id = int(state_tuple[0])
            module_idx = int(state_tuple[1])
            progress_bin = float(state_tuple[2])
            score_bin = float(state_tuple[3])
            action_id = int(state_tuple[4])
            is_stuck = int(state_tuple[5])
            
            # Map to human-readable format
            cluster_names = {
                0: "Học sinh cần hỗ trợ tương tác",
                1: "Học sinh Tự giác và Theo dõi Tiến độ",
                2: "Học sinh Chủ động Hoàn thành Nhiệm vụ",
                3: "Học sinh theo dõi hiệu suất và thành tích",
                4: "Học sinh Nghiên cứu Chủ động"
            }
            
            action_names = {
                0: "watch_video",
                1: "do_quiz",
                2: "mod_forum",
                3: "review_quiz",
                4: "read_resource",
                5: "do_assignment"
            }
            
            return {
                "cluster_id": cluster_id,
                "cluster_name": cluster_names.get(cluster_id, f"Cluster {cluster_id}"),
                "module_index": module_idx,
                "progress_bin": progress_bin,
                "progress_percent": int(progress_bin * 100),
                "score_bin": score_bin,
                "score_percent": int(score_bin * 100),
                "recent_action_id": action_id,
                "recent_action": action_names.get(action_id, f"action_{action_id}"),
                "is_stuck": bool(is_stuck),
                "stuck_label": "STUCK" if is_stuck else "OK"
            }
        
        elif len(state_tuple) == 12:
            # V1 format (deprecated)
            return {
                "knowledge_level": float(state_tuple[0]),
                "engagement_level": float(state_tuple[1]),
                "struggle_indicator": float(state_tuple[2]),
                "submission_activity": float(state_tuple[3]),
                "review_activity": float(state_tuple[4]),
                "resource_usage": float(state_tuple[5]),
                "assessment_engagement": float(state_tuple[6]),
                "collaborative_activity": float(state_tuple[7]),
                "overall_progress": float(state_tuple[8]),
                "module_completion_rate": float(state_tuple[9]),
                "activity_diversity": float(state_tuple[10]),
                "completion_consistency": float(state_tuple[11])
            }
        
        else:
            # Unknown format
            return {
                "error": f"Unknown state format with {len(state_tuple)} dimensions",
                "state_tuple": list(state_tuple)
            }
    
    def get_statistics(self) -> Dict:
        """
        Get basic statistics (lightweight version of summary)
        
        Returns:
            Dict with basic stats
        """
        if not self.agent:
            return {'error': 'No agent loaded'}
        
        q_table = self.agent.q_table
        training_stats = self.agent.training_stats
        
        # Count non-zero states
        states_with_q = sum(
            1 for actions in q_table.values()
            if any(abs(q) > 0.0001 for q in actions.values())
        )
        
        return {
            'total_states': len(q_table),
            'states_with_positive_q': states_with_q,
            'episodes_trained': training_stats.get('episodes', 0),
            'total_updates': training_stats.get('total_updates', 0),
            'avg_reward': float(training_stats.get('avg_reward', 0.0))
        }
