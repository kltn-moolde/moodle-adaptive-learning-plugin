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
from core.activity_recommender import ActivityRecommender


class RecommendationService:
    """Service for generating recommendations"""
    
    def __init__(
        self,
        agent: Optional[QLearningAgentV2],
        action_space: Optional[ActionSpace],
        state_builder: Optional[StateBuilderV2],
        course_structure_path: Optional[str] = None,
        activity_recommender: Optional[ActivityRecommender] = None
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
        
        # Initialize activity recommender for LO-based activity selection
        if activity_recommender:
            self.activity_recommender = activity_recommender
        else:
            # Try to initialize with default paths
            from pathlib import Path
            po_lo_path = Path(__file__).parent.parent / 'data' / 'Po_Lo.json'
            if po_lo_path.exists():
                try:
                    self.activity_recommender = ActivityRecommender(
                        po_lo_path=str(po_lo_path),
                        course_structure_path=course_structure_path or str(Path(__file__).parent.parent / 'data' / 'course_structure.json')
                    )
                except Exception as e:
                    print(f"Warning: Failed to initialize ActivityRecommender: {e}")
                    self.activity_recommender = None
            else:
                self.activity_recommender = None
    
    def get_recommendations(
        self,
        state: Tuple,
        cluster_id: int,
        top_k: int = 3,
        exclude_action_ids: Optional[List[int]] = None,
        lo_mastery: Optional[Dict[str, float]] = None,
        module_idx: Optional[int] = None
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
        
        # Convert action indices to module IDs if Q-table uses module IDs
        if self.use_module_ids and self.adapter:
            available_actions_for_qtable = self.adapter.convert_available_actions(
                available_indices,
                to_module_ids=True
            )
        else:
            available_actions_for_qtable = available_indices
        
        # Get recommendations from agent
        try:
            recommendations = self.agent.recommend_action(
                state=state,
                available_actions=available_actions_for_qtable,  # May be module IDs or indices
                top_k=top_k,
                fallback_random=True
            )
            
            # Convert back to action indices if needed
            if self.use_module_ids and self.adapter:
                recommendations = self.adapter.convert_recommendations(
                    recommendations,
                    from_module_ids=True
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
                rec_dict = {
                    'action_id': action_index,
                    'action_type': action.action_type,
                    'time_context': action.time_context,
                    'module_name': action.name,
                    'activity_type': action.action_type,  # For backward compatibility
                    'q_value': float(q_value)
                }
                
                # Add activity recommendation if ActivityRecommender available
                if self.activity_recommender and lo_mastery is not None:
                    try:
                        # Get module_idx from state if not provided
                        if module_idx is None:
                            module_idx = int(state[1]) if len(state) > 1 else 0
                        
                        # Get activity recommendation based on LO mastery
                        activity_rec = self.activity_recommender.recommend_activity(
                            action=action.to_tuple(),
                            module_idx=module_idx,
                            lo_mastery=lo_mastery,
                            previous_activities=[],
                            top_k=1
                        )
                        
                        # Add activity details and explanation
                        rec_dict['activity_id'] = activity_rec.get('activity_id')
                        rec_dict['activity_name'] = activity_rec.get('activity_name', 'N/A')
                        rec_dict['target_los'] = activity_rec.get('weak_los', [])
                        rec_dict['explanation'] = activity_rec.get('reason', 'No explanation available')
                        rec_dict['alternatives'] = activity_rec.get('alternatives', [])
                        
                    except Exception as e:
                        print(f"Warning: Activity recommendation failed: {e}")
                        rec_dict['activity_id'] = None
                        rec_dict['activity_name'] = 'N/A'
                        rec_dict['explanation'] = f'Activity recommendation unavailable: {str(e)}'
                else:
                    rec_dict['activity_id'] = None
                    rec_dict['activity_name'] = 'N/A'
                    rec_dict['explanation'] = 'LO mastery not provided for activity recommendation'
                
                results.append(rec_dict)
            else:
                results.append({
                    'action_id': action_index,
                    'action_type': 'unknown',
                    'time_context': 'unknown',
                    'module_name': f'Action {action_index}',
                    'activity_type': 'unknown',
                    'q_value': float(q_value),
                    'activity_id': None,
                    'activity_name': 'N/A',
                    'explanation': 'Unknown action type'
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
            
            # Build state (7D)
            state_7d = self.state_builder.build_state(
                cluster_id=cluster_id,
                current_module_id=current_module_id,
                module_progress=module_progress,
                avg_score=avg_score,
                recent_actions=recent_actions,
                quiz_attempts=features.get('quiz_attempts', 0),
                quiz_failures=features.get('quiz_failures', 0),
                time_on_module=features.get('time_on_module', 0.0)
            )
            
            # Convert to 6D if Q-table uses 6D format
            if self.use_module_ids and hasattr(self.state_builder, 'convert_7d_to_6d'):
                # Q-table best model uses 6D format
                state = self.state_builder.convert_7d_to_6d(state_7d)
            else:
                state = state_7d
            
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
            state: State tuple (6D or 7D)
            
        Returns:
            Dict with state component descriptions
        """
        cluster_names = {0: 'Weak', 1: 'Medium', 2: 'Medium', 3: 'Strong', 4: 'Strong'}
        
        if len(state) == 6:
            # 6D format: (cluster, module, progress, score, action_id, stuck)
            cluster_id = int(state[0])
            module_idx = int(state[1])
            progress_bin = float(state[2])
            score_bin = float(state[3])
            action_id = int(state[4])
            is_stuck = bool(state[5])
            
            return {
                'cluster_id': cluster_id,
                'cluster_name': cluster_names.get(cluster_id, 'Unknown'),
                'module_index': module_idx,
                'module_name': f'Module {module_idx}',
                'progress_bin': progress_bin,
                'progress_label': f'{int(progress_bin * 100)}%',
                'score_bin': score_bin,
                'score_label': f'{int(score_bin * 100)}%',
                'recent_action_id': action_id,
                'is_stuck': is_stuck,
                'stuck_label': 'STUCK' if is_stuck else 'OK',
                'state_format': '6D'
            }
        elif len(state) == 7:
            # 7D format: (cluster, module, progress, score, phase, engagement, frustration)
            cluster_id = int(state[0])
            module_idx = int(state[1])
            progress_bin = float(state[2])
            score_bin = float(state[3])
            learning_phase = int(state[4])
            engagement_level = int(state[5])
            frustration_level = int(state[6])
            
            phase_names = {0: 'pre-learning', 1: 'active', 2: 'reflective'}
            engagement_names = {0: 'low', 1: 'medium', 2: 'high'}
            
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
                'frustration_level': frustration_level,
                'state_format': '7D'
            }
        else:
            return {'error': f'Invalid state dimension: {len(state)}, expected 6 or 7'}
