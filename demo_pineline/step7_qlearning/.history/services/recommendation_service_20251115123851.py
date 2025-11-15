"""
Recommendation Service
Handles recommendation logic using Q-learning agent
"""
from typing import Dict, List, Optional, Tuple, Any
import random

from core.qlearning_agent_v2 import QLearningAgentV2
from core.action_space import ActionSpace
from core.state_builder_v2 import StateBuilderV2


class RecommendationService:
    """Service for generating recommendations"""
    
    def __init__(
        self,
        agent: Optional[QLearningAgentV2],
        action_space: Optional[ActionSpace],
        state_builder: Optional[StateBuilderV2]
    ):
        self.agent = agent
        self.action_space = action_space
        self.state_builder = state_builder
    
    def get_recommendations(
        self,
        state: Tuple,
        cluster_id: int,
        top_k: int = 3,
        exclude_action_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top-K recommendations for a given state
        
        Args:
            state: State tuple (6 dimensions)
            cluster_id: Student cluster ID
            top_k: Number of recommendations to return
            exclude_action_ids: List of action IDs to exclude
            
        Returns:
            List of recommendation dicts with action info and Q-values
        """
        if not self.agent or not self.action_space:
            return self._get_random_recommendations(top_k, exclude_action_ids)
        
        # Get all action indices
        all_action_indices = list(range(self.action_space.get_action_count()))
        
        # Exclude specified actions
        available_indices = all_action_indices
        if exclude_action_ids:
            available_indices = [i for i in all_action_indices if i not in exclude_action_ids]
        
        # Get recommendations from agent (using action indices directly)
        try:
            recommendations = self.agent.recommend_action(
                state=state,
                available_actions=available_indices,  # Pass action indices
                top_k=top_k,
                fallback_random=True
            )
        except Exception as e:
            print(f"Warning: Agent recommendation failed: {e}")
            return self._get_random_recommendations(top_k, exclude_action_ids)
        
        # Format recommendations with action details
        # Note: recommendations contain (action_index, q_value)
        results = []
        for action_index, q_value in recommendations:
            action = self.action_space.get_action_by_index(action_index)
            
            if action:
                results.append({
                    'action_id': action_index,
                    'action_type': action.action_type,
                    'time_context': action.time_context,
                    'module_name': action.name,
                    'activity_type': action.action_type,  # For backward compatibility
                    'q_value': float(q_value)
                })
            else:
                results.append({
                    'action_id': action_index,
                    'action_type': 'unknown',
                    'time_context': 'unknown',
                    'module_name': f'Action {action_index}',
                    'activity_type': 'unknown',
                    'q_value': float(q_value)
                })
        
        return results
    
    def _get_random_recommendations(
        self,
        top_k: int = 3,
        exclude_action_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Fallback: random recommendations when agent is not available"""
        if not self.action_space:
            return []
        
        # Get all action IDs
        all_action_ids = list(range(self.action_space.get_action_count()))
        
        # Exclude specified actions
        available_actions = all_action_ids
        if exclude_action_ids:
            available_actions = [a for a in all_action_ids if a not in exclude_action_ids]
        
        # Random sample
        selected = random.sample(available_actions, min(top_k, len(available_actions)))
        
        results = []
        for action_id in selected:
            action = self.action_space.get_action_by_index(action_id)
            
            if action:
                results.append({
                    'action_id': action_id,
                    'action_type': action.action_type,
                    'time_context': action.time_context,
                    'module_name': action.name,
                    'activity_type': action.action_type,  # For backward compatibility
                    'q_value': 0.0  # Random recommendation, no Q-value
                })
            else:
                results.append({
                    'action_id': action_id,
                    'module_name': f'Module {action_id}',
                    'activity_type': 'unknown',
                    'difficulty': 'medium',
                    'purpose': 'other',
                    'section': 'Unknown',
                    'q_value': 0.0,
                    'note': 'Random recommendation (model not loaded)'
                })
        
        return results
    
    def build_state_from_features(
        self,
        features: Dict[str, Any],
        cluster_id: int
    ) -> Optional[Tuple]:
        """
        Build state tuple from features using StateBuilderV2
        
        Args:
            features: Student feature dict
            cluster_id: Predicted cluster ID
            
        Returns:
            State tuple or None if state_builder not available
        """
        if not self.state_builder:
            return None
        
        try:
            state = self.state_builder.build_state(
                student_features=features,
                cluster_id=cluster_id
            )
            return state
        except Exception as e:
            print(f"Warning: State building failed: {e}")
            return None
    
    def get_state_description(self, state: Tuple) -> Dict[str, Any]:
        """
        Get human-readable description of state
        
        Args:
            state: State tuple (6 dimensions)
            
        Returns:
            Dict with state component descriptions
        """
        if len(state) != 6:
            return {'error': f'Invalid state dimension: {len(state)}'}
        
        action_type_names = ['submit', 'read_resource', 'review', 'forum', 'quiz', 'other']
        cluster_names = {0: 'Weak', 1: 'Medium', 2: 'Medium', 3: 'Strong', 4: 'Strong'}
        
        cluster_id = int(state[0])
        module_idx = int(state[1])
        progress_bin = float(state[2])
        score_bin = float(state[3])
        action_type = int(state[4])
        is_stuck = bool(state[5])
        
        # Get module name if action_space available
        module_name = f'Module {module_idx}'
        if self.action_space and module_idx < self.action_space.get_action_count():
            action = self.action_space.get_action_by_index(module_idx)
            if action:
                module_name = action.name
        
        return {
            'cluster_id': cluster_id,
            'cluster_name': cluster_names.get(cluster_id, 'Unknown'),
            'module_index': module_idx,
            'module_name': module_name,
            'progress_bin': progress_bin,
            'progress_label': f'{int(progress_bin * 100)}%',
            'score_bin': score_bin,
            'score_label': f'{int(score_bin * 100)}%',
            'recent_action_id': action_type,
            'recent_action': action_type_names[action_type] if 0 <= action_type < len(action_type_names) else 'unknown',
            'is_stuck': is_stuck,
            'stuck_label': 'STUCK' if is_stuck else 'OK'
        }
