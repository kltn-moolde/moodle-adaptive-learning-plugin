"""
Recommendation Service
Handles recommendation logic using Q-learning agent
"""
from typing import Dict, List, Optional, Tuple, Any, Set
import random

from core.rl.agent import QLearningAgentV2
from core.rl.action_space import ActionSpace
from core.rl.state_builder import StateBuilderV2
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
        
        # Initialize activity recommender for LO-based activity selection
        if activity_recommender:
            self.activity_recommender = activity_recommender
        else:
            # Try to initialize with default paths
            from pathlib import Path
            # Fix: Get project root (step7_qlearning/) instead of services/
            project_root = Path(__file__).parent.parent.parent
            po_lo_path = project_root / 'data' / 'Po_Lo.json'
            course_structure_path_default = project_root / 'data' / 'course_structure.json'
            
            print(f"🔍 DEBUG: Initializing ActivityRecommender")
            print(f"   - project_root: {project_root}")
            print(f"   - po_lo_path: {po_lo_path}")
            print(f"   - po_lo_path.exists(): {po_lo_path.exists()}")
            print(f"   - course_structure_path: {course_structure_path or course_structure_path_default}")
            
            if po_lo_path.exists():
                try:
                    self.activity_recommender = ActivityRecommender(
                        po_lo_path=str(po_lo_path),
                        course_structure_path=course_structure_path or str(course_structure_path_default)
                    )
                    print(f"   ✓ ActivityRecommender initialized successfully")
                except Exception as e:
                    print(f"   ❌ Failed to initialize ActivityRecommender: {e}")
                    import traceback
                    traceback.print_exc()
                    self.activity_recommender = None
            else:
                print(f"   ❌ Po_Lo.json not found at {po_lo_path}")
                self.activity_recommender = None
    
    def get_recommendations(
        self,
        state: Tuple,
        cluster_id: int,
        top_k: int = 3,
        exclude_action_ids: Optional[List[int]] = None,
        lo_mastery: Optional[Dict[str, float]] = None,
        module_idx: Optional[int] = None,
        course_id: Optional[int] = None,
        lesson_id: Optional[int] = None,
        past_lesson_ids: Optional[Set[int]] = None,
        future_lesson_ids: Optional[Set[int]] = None
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
        print(f"\n   🔍 DEBUG: RecommendationService.get_recommendations()")
        print(f"      Input: state={state}, cluster_id={cluster_id}, top_k={top_k}")
        print(f"      exclude_action_ids={exclude_action_ids}, lo_mastery={lo_mastery is not None}, module_idx={module_idx}")
        
        if not self.agent or not self.action_space:
            print(f"      ⚠️  Agent or action_space is None, returning random recommendations")
            return self._get_random_recommendations(top_k, exclude_action_ids)
        
        # Get all action indices
        all_action_indices = list(range(self.action_space.get_action_count()))
        print(f"      ✓ Total actions in action_space: {len(all_action_indices)}")
        
        # Exclude specified actions
        available_indices = all_action_indices
        if exclude_action_ids:
            available_indices = [i for i in all_action_indices if i not in exclude_action_ids]
            print(f"      ✓ Excluded {len(exclude_action_ids)} actions, {len(available_indices)} available")
        
        # Get recommendations from agent (Q-table uses action indices directly)
        print(f"      → Calling agent.recommend_action()...")
        try:
            recommendations = self.agent.recommend_action(
                state=state,
                available_actions=available_indices,
                top_k=top_k,
                fallback_random=True
            )
            print(f"      ← Got {len(recommendations) if recommendations else 0} recommendations from agent")
            if recommendations:
                for i, (action_idx, q_value) in enumerate(recommendations[:3], 1):
                    print(f"         {i}. action_idx={action_idx}, q_value={q_value:.3f}")
        except Exception as e:
            print(f"      ❌ Agent recommendation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_random_recommendations(top_k, exclude_action_ids)
        
        # Format recommendations with action details
        # Note: recommendations contain (action_index, q_value)
        print(f"      → Formatting recommendations with activity details...")
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
                
                print(f"         Processing action {action_index}: {action.action_type} ({action.time_context}), q_value={q_value:.3f}")
                
                # Add activity recommendation if ActivityRecommender available
                if self.activity_recommender:
                    try:
                        # Get lesson_id - ưu tiên từ parameter, fallback từ module_idx
                        if lesson_id is None:
                            # Try to map module_idx to lesson_id (nếu có mapping)
                            if module_idx is not None and hasattr(self.state_builder, 'idx_to_lesson_id'):
                                lesson_id = self.state_builder.idx_to_lesson_id.get(module_idx)
                        
                        # Fallback: use module_idx as lesson_id nếu không có mapping
                        if lesson_id is None:
                            lesson_id = module_idx if module_idx is not None else (int(state[1]) if len(state) > 1 else 0)
                        
                        # Get course_id - ưu tiên từ parameter
                        if course_id is None:
                            course_id = 5  # Default course_id
                        
                        print(f"            → Calling activity_recommender.recommend_activity()...")
                        print(f"               - action: {action.to_tuple()}")
                        print(f"               - course_id: {course_id}")
                        print(f"               - lesson_id: {lesson_id}")
                        print(f"               - past_lesson_ids: {past_lesson_ids}")
                        print(f"               - future_lesson_ids: {future_lesson_ids}")
                        print(f"               - lo_mastery provided: {lo_mastery is not None}")
                        print(f"               - cluster_id: {cluster_id}")
                        
                        # Get activity recommendation (will use fallback if lo_mastery is None)
                        activity_rec = self.activity_recommender.recommend_activity(
                            action=action.to_tuple(),
                            course_id=course_id,
                            lesson_id=lesson_id,
                            past_lesson_ids=past_lesson_ids,
                            future_lesson_ids=future_lesson_ids,
                            lo_mastery=lo_mastery,  # Can be None, will use fallback
                            previous_activities=[],
                            top_k=4,  # Get top-4 to include 3 alternatives
                            cluster_id=cluster_id
                        )
                        
                        print(f"            ← Activity recommendation: {activity_rec}")
                        
                        # Add activity details and explanation
                        rec_dict['activity_id'] = activity_rec.get('activity_id')
                        rec_dict['activity_name'] = activity_rec.get('activity_name', 'N/A')
                        rec_dict['target_los'] = activity_rec.get('weak_los', [])
                        rec_dict['explanation'] = activity_rec.get('reason', 'No explanation available')
                        rec_dict['alternatives'] = activity_rec.get('alternatives', [])
                        
                    except Exception as e:
                        print(f"            ❌ Activity recommendation failed: {e}")
                        import traceback
                        traceback.print_exc()
                        rec_dict['activity_id'] = None
                        rec_dict['activity_name'] = 'N/A'
                        rec_dict['explanation'] = f'Activity recommendation unavailable: {str(e)}'
                else:
                    print(f"            ⚠️  activity_recommender is None")
                    rec_dict['activity_id'] = None
                    rec_dict['activity_name'] = 'N/A'
                    rec_dict['explanation'] = 'Activity recommender not available'
                
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
    
    def validate_features(
        self,
        features: Dict[str, Any],
        strict: bool = True
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate features input
        
        Args:
            features: Student feature dict
            strict: If True, raise errors for invalid values. If False, return warnings.
            
        Returns:
            (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Valid action type map
        VALID_ACTION_TYPES = {0, 1, 2, 3, 4, 5}
        VALID_CLUSTER_IDS = {0, 1, 2, 3, 4}
        
        # Check required fields
        required_fields = ['current_module_id', 'module_progress', 'avg_score']
        for field in required_fields:
            if field not in features:
                errors.append(f"Missing required field: '{field}'")
        
        # Validate cluster_id if provided
        if 'cluster_id' in features:
            cluster_id = features['cluster_id']
            if not isinstance(cluster_id, int):
                errors.append(f"cluster_id must be integer, got {type(cluster_id).__name__}")
            elif cluster_id not in VALID_CLUSTER_IDS:
                msg = f"cluster_id must be in range 0-4, got {cluster_id}"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
        
        # Validate current_module_id
        if 'current_module_id' in features:
            current_module_id = features['current_module_id']
            if not isinstance(current_module_id, int):
                errors.append(f"current_module_id must be integer, got {type(current_module_id).__name__}")
            elif self.state_builder and current_module_id not in self.state_builder.module_id_to_idx:
                valid_ids = list(self.state_builder.module_id_to_idx.keys())[:5]  # Show first 5
                msg = f"current_module_id {current_module_id} not found in course structure. Valid IDs: {valid_ids}..."
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
        
        # Validate module_progress
        if 'module_progress' in features:
            module_progress = features['module_progress']
            if not isinstance(module_progress, (int, float)):
                errors.append(f"module_progress must be number, got {type(module_progress).__name__}")
            elif not (0.0 <= module_progress <= 1.0):
                msg = f"module_progress must be in range [0.0, 1.0], got {module_progress}"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
        
        # Validate avg_score
        if 'avg_score' in features:
            avg_score = features['avg_score']
            if not isinstance(avg_score, (int, float)):
                errors.append(f"avg_score must be number, got {type(avg_score).__name__}")
            elif not (0.0 <= avg_score <= 1.0):
                msg = f"avg_score must be in range [0.0, 1.0], got {avg_score}"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
        
        # Validate recent_action_type
        if 'recent_action_type' in features:
            recent_action_type = features['recent_action_type']
            if not isinstance(recent_action_type, int):
                errors.append(f"recent_action_type must be integer, got {type(recent_action_type).__name__}")
            elif recent_action_type not in VALID_ACTION_TYPES:
                msg = f"recent_action_type must be in range 0-5, got {recent_action_type}. Valid values: 0=view_content, 1=submit_quiz, 2=post_forum, 3=review_quiz, 4=read_resource, 5=submit_assignment"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
        
        # Warn about unused fields
        valid_fields = {'cluster_id', 'current_module_id', 'module_progress', 'avg_score', 
                       'recent_action_type', 'quiz_attempts', 'quiz_failures', 'time_on_module'}
        unused_fields = set(features.keys()) - valid_fields
        if unused_fields:
            warnings.append(f"Unused fields (will be ignored): {', '.join(sorted(unused_fields))}")
        
        is_valid = len(errors) == 0
        error_message = '; '.join(errors) if errors else None
        
        return is_valid, error_message, warnings
    
    def build_state_from_features(
        self,
        features: Dict[str, Any],
        cluster_id: int,
        validate: bool = True,
        strict_validation: bool = True
    ) -> Optional[Tuple]:
        """
        Build state tuple from features using StateBuilderV2
        
        Args:
            features: Student feature dict with keys:
                - cluster_id (optional, overrides parameter): int in range 0-4
                - current_module_id (required): int, valid module ID from course structure
                - module_progress (required): float in range [0.0, 1.0]
                - avg_score (required): float in range [0.0, 1.0]
                - recent_action_type (optional, default=0): int in range 0-5
                - quiz_attempts (optional): int, not used in state building
                - quiz_failures (optional): int, not used in state building
                - time_on_module (optional): float, not used in state building
            cluster_id: Predicted cluster ID (used if not in features)
            validate: If True, validate features before building state
            strict_validation: If True, raise errors for invalid values. If False, use defaults.
            
        Returns:
            State tuple or None if state_builder not available or validation fails
            
        Raises:
            ValueError: If validation fails and strict_validation=True
        """
        if not self.state_builder:
            return None
        
        # Validate features
        if validate:
            is_valid, error_message, warnings = self.validate_features(features, strict=strict_validation)
            
            if warnings:
                for warning in warnings:
                    print(f"Warning: {warning}")
            
            if not is_valid:
                if strict_validation:
                    raise ValueError(f"Invalid features: {error_message}")
                else:
                    print(f"Warning: Invalid features (using defaults): {error_message}")
        
        try:
            # Extract features with defaults
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
            
            # Validate recent_action_type and use default if invalid
            if recent_action_type not in action_type_map:
                if strict_validation:
                    raise ValueError(f"recent_action_type must be in range 0-5, got {recent_action_type}")
                else:
                    print(f"Warning: recent_action_type {recent_action_type} not in valid range [0-5], using default 0")
                    recent_action_type = 0
            
            recent_actions = [action_type_map[recent_action_type]]
            
            # Build state (6D)
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
            state: State tuple (6D)
            
        Returns:
            Dict with state component descriptions
        """
        cluster_names = {0: 'Weak', 1: 'Medium', 2: 'Medium', 3: 'Strong', 4: 'Strong'}
        
        if len(state) == 6:
            # 6D format: (cluster, module, progress, score, phase, engagement)
            cluster_id = int(state[0])
            module_idx = int(state[1])
            progress_bin = float(state[2])
            score_bin = float(state[3])
            learning_phase = int(state[4])
            engagement_level = int(state[5])
            
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
                'state_format': '6D'
            }
        else:
            return {'error': f'Invalid state dimension: {len(state)}, expected 6'}
