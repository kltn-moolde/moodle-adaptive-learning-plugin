"""
Recommendation Service
Handles recommendation logic using Q-learning agent
"""
from typing import Dict, List, Optional, Tuple, Any
import random

from core.qlearning_agent_v2 import QLearningAgentV2
from core.action_space import ActionSpace
from core.state_builder_v2 import StateBuilderV2
from core.qtable_adapter import QTableAdapter


class RecommendationService:
    """Service for generating recommendations"""
    
    def __init__(
        self,
        agent: Optional[QLearningAgentV2],
        action_space: Optional[ActionSpace],
        state_builder: Optional[StateBuilderV2],
        course_structure_path: Optional[str] = None
    ):
        self.agent = agent
        self.action_space = action_space
        self.state_builder = state_builder
        
        # Initialize adapter for Q-table compatibility
        # Check if Q-table uses module IDs (old format) or action indices (new format)
        self.use_module_ids = False
        self.adapter = None
        
        if agent and agent.q_table:
            # Check first state to determine format
            sample_state = list(agent.q_table.keys())[0] if agent.q_table else None
            if sample_state:
                sample_actions = list(agent.q_table[sample_state].keys())
                # If actions are > 20, likely module IDs (46-83), not indices (0-14)
                if sample_actions and max(sample_actions) > 20:
                    self.use_module_ids = True
                    if course_structure_path:
                        self.adapter = QTableAdapter(course_structure_path)
                    else:
                        from pathlib import Path
                        default_path = Path(__file__).parent.parent / 'data' / 'course_structure.json'
                        if default_path.exists():
                            self.adapter = QTableAdapter(str(default_path))
    
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
            features: Student feature dict with keys:
                - cluster_id (optional, overrides parameter)
                - current_module_id
                - module_progress
                - avg_score
                - recent_action_type (optional)
                - is_stuck (optional)
            cluster_id: Predicted cluster ID (used if not in features)
            
        Returns:
            State tuple or None if state_builder not available
        """
        if not self.state_builder:
            return None
        
        try:
            # Extract features
            cluster_id = features.get('cluster_id', cluster_id)
            current_module_id = features.get('current_module_id', 67)
            module_progress = features.get('module_progress', 0.5)
            avg_score = features.get('avg_score', 0.5)
            
            # Map recent_action_type to action name if needed
            recent_action_type = features.get('recent_action_type', 0)
            action_type_map = {
                0: 'view_content',
                1: 'submit_quiz',
                2: 'post_forum',
                3: 'review_quiz',
                4: 'read_resource',
                5: 'submit_assignment'
            }
            recent_actions = [action_type_map.get(recent_action_type, 'view_content')]
            
            # Build state
            state = self.state_builder.build_state(
                cluster_id=cluster_id,
                current_module_id=current_module_id,
                module_progress=module_progress,
                avg_score=avg_score,
                recent_actions=recent_actions,
                quiz_attempts=features.get('quiz_attempts', 0),
                quiz_failures=features.get('quiz_failures', 0),
                time_on_module=features.get('time_on_module', 0.0)
            )
            return state
        except Exception as e:
            print(f"Warning: State building failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_state_description(self, state: Tuple) -> Dict[str, Any]:
        """
        Get human-readable description of state
        
        Args:
            state: State tuple (7 dimensions)
            
        Returns:
            Dict with state component descriptions
        """
        if len(state) != 7:
            return {'error': f'Invalid state dimension: {len(state)}, expected 7'}
        
        cluster_names = {0: 'Weak', 1: 'Medium', 2: 'Medium', 3: 'Strong', 4: 'Strong'}
        phase_names = {0: 'pre-learning', 1: 'active', 2: 'reflective'}
        engagement_names = {0: 'low', 1: 'medium', 2: 'high'}
        
        cluster_id = int(state[0])
        module_idx = int(state[1])
        progress_bin = float(state[2])
        score_bin = float(state[3])
        learning_phase = int(state[4])
        engagement_level = int(state[5])
        frustration_level = int(state[6])
        
        return {
            'cluster_id': cluster_id,
            'cluster_name': cluster_names.get(cluster_id, 'Unknown'),
            'module_index': module_idx,
            'module_name': f'Module {module_idx}',
            'progress_bin': progress_bin,
            'progress_label': f'{int(progress_bin * 100)}%',
            'score_bin': score_bin,
            'score_label': f'{int(score_bin * 100)}%',
            'learning_phase': learning_phase,
            'learning_phase_name': phase_names.get(learning_phase, 'unknown'),
            'engagement_level': engagement_level,
            'engagement_name': engagement_names.get(engagement_level, 'unknown'),
            'frustration_level': frustration_level
        }
