#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Builder V2 - State representation with 6 dimensions
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class StateBuilderV2:
    """State Builder for Q-Learning System V2 with 6D state"""
    
    # Action weights for engagement calculation (quality of interaction)
    ACTION_WEIGHTS = {
        "view_content": 1,
        "view_assignment": 2,
        "attempt_quiz": 4,
        "submit_quiz": 5,
        "review_quiz": 3,
        "submit_assignment": 5,
        "post_forum": 3,
        "download_resource": 2,
        "view_forum": 1
    }
    
    # Action types for learning phase classification
    PRE_LEARNING_ACTIONS = {"view_content", "download_resource", "view_assignment"}
    ACTIVE_LEARNING_ACTIONS = {"attempt_quiz", "submit_quiz", "submit_assignment"}
    REFLECTIVE_LEARNING_ACTIONS = {"review_quiz", "post_forum", "view_forum"}
    
    LEARNING_PHASE = {
        0: "pre_learning",      # Exploring, watching, reading
        1: "active_learning",   # Doing, practicing, attempting
        2: "reflective_learning" # Reviewing, discussing, consolidating
    }
    
    # Engagement thresholds based on weighted score in recent window
    # Reduced to 3 levels to decrease state space
    ENGAGEMENT_THRESHOLDS = [0, 8, 16]  # Low (0-7), Medium (8-15), High (16+)
    
    # Binning thresholds
    PROGRESS_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]
    SCORE_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    def __init__(self, cluster_profiles_path: str, course_structure_path: str,
                 excluded_clusters: List[int] = None, recent_window: int = 10):
        """
        Initialize State Builder V2
        
        Args:
            cluster_profiles_path: Path to cluster profiles JSON
            course_structure_path: Path to course structure JSON
            excluded_clusters: List of cluster IDs to exclude (default: [3] - teachers)
            recent_window: Number of recent actions to consider (default: 10)
        """
        self.cluster_profiles_path = Path(cluster_profiles_path)
        self.course_structure_path = Path(course_structure_path)
        self.excluded_clusters = excluded_clusters if excluded_clusters else [3]
        self.recent_window = recent_window
        
        self._load_cluster_profiles()
        self._load_course_structure()
        self._build_cluster_mapping()
        self.n_clusters = len(self.cluster_mapping)
        
        print(f"StateBuilderV2 initialized:")
        print(f"  - Clusters: {self.n_clusters} (excluded: {self.excluded_clusters})")
        print(f"  - Modules: {self.n_modules}")
        print(f"  - State space: {self.calculate_state_space_size():,}")
        print(f"  - Recent window: {self.recent_window} actions")
        
    def calculate_state_space_size(self) -> int:
        """Calculate total state space size: clusters × modules × progress × score × phase × engagement"""
        # State space: 5 × 6 × 4 × 4 × 3 × 3 = 4,320 states
        return self.n_clusters * self.n_modules * 4 * 4 * 3 * 3
        
    def _load_cluster_profiles(self):
        """Load cluster profiles"""
        with open(self.cluster_profiles_path, 'r') as f:
            data = json.load(f)
        self.cluster_profiles = data.get('cluster_stats', {})
        self.original_n_clusters = data.get('n_clusters', 7)
        
    def _load_course_structure(self):
        """Load course structure - only top-level subsections under each topic"""
        with open(self.course_structure_path, 'r') as f:
            data = json.load(f)
        
        self.modules = []
        for section in data.get('contents', []):
            # Skip General section (section 0) - only get topic sections
            if section.get('section', 0) == 0:
                continue
            
            # Skip subsection detail sections (those with component='mod_subsection')
            if section.get('component') == 'mod_subsection':
                continue
                
            # Get only subsection modules (first-level modules under topics)
            for module in section.get('modules', []):
                if module.get('modname') == 'subsection':
                    if module.get('visible', 0) == 1 and module.get('uservisible', False):
                        self.modules.append({
                            'id': module['id'],
                            'name': module['name'],
                            'type': 'subsection',
                            'section': section['name']
                        })
        
        self.n_modules = len(self.modules)
        self.module_id_to_idx = {m['id']: idx for idx, m in enumerate(self.modules)}
        
    def _build_cluster_mapping(self):
        """Build cluster mapping - flexible to handle any excluded clusters"""
        self.cluster_mapping = {}
        self.reverse_cluster_mapping = {}  # New cluster ID -> Original cluster ID
        new_id = 0
        
        for orig_id in range(self.original_n_clusters):
            if orig_id in self.excluded_clusters:
                continue
            self.cluster_mapping[orig_id] = new_id
            self.reverse_cluster_mapping[new_id] = orig_id
            new_id += 1
    
    def map_cluster_id(self, original_cluster_id: int) -> Optional[int]:
        """Map original cluster ID to new ID"""
        return self.cluster_mapping.get(original_cluster_id, None)
    
    def get_original_cluster_id(self, mapped_cluster_id: int) -> Optional[int]:
        """Map new cluster ID back to original ID"""
        return self.reverse_cluster_mapping.get(mapped_cluster_id, None)
    
    def quartile_bin(self, value: float, bins: List[float]) -> float:
        """Bin value into quartiles"""
        value = max(0.0, min(1.0, value))
        for i in range(len(bins) - 1):
            if value <= bins[i + 1]:
                return bins[i + 1]
        return bins[-1]
    
    def calculate_learning_phase(self, module_progress: float, recent_actions: List[str]) -> int:
        """
        Determine learning phase based on both progress AND recent actions
        
        Args:
            module_progress: Progress in module (0-1)
            recent_actions: Recent action types
            
        Returns:
            0: Pre-learning (exploring, watching)
            1: Active-learning (doing, practicing)  
            2: Reflective-learning (reviewing, consolidating)
        """
        if not recent_actions:
            # Fallback to progress-based if no actions
            if module_progress < 0.3:
                return 0
            elif module_progress < 0.8:
                return 1
            else:
                return 2
        
        # Count action types in recent window
        recent = recent_actions[:self.recent_window]
        pre_count = sum(1 for a in recent if a in self.PRE_LEARNING_ACTIONS)
        active_count = sum(1 for a in recent if a in self.ACTIVE_LEARNING_ACTIONS)
        reflective_count = sum(1 for a in recent if a in self.REFLECTIVE_LEARNING_ACTIONS)
        
        # Determine dominant phase
        max_count = max(pre_count, active_count, reflective_count)
        
        # Tie-breaking: use progress as secondary indicator
        if active_count == max_count:
            return 1  # Active is most important
        elif reflective_count == max_count and module_progress >= 0.6:
            return 2  # Reflective with good progress
        elif pre_count == max_count:
            return 0  # Pre-learning
        else:
            # Default fallback
            if module_progress < 0.3:
                return 0
            elif module_progress < 0.8:
                return 1
            else:
                return 2
    
    def calculate_engagement_level(
        self, 
        recent_actions: List[str],
        time_on_task: float = 0.0,
        action_timestamps: List[float] = None
    ) -> int:
        """
        Calculate engagement level based on quality, quantity, and consistency
        
        Args:
            recent_actions: List of recent action types
            time_on_task: Total time spent (seconds) in recent window
            action_timestamps: Timestamps of actions for consistency check
            
        Returns:
            0: Low engagement (0-7 points)
            1: Medium engagement (8-15 points)
            2: High engagement (16+ points)
        """
        if not recent_actions:
            return 0
        
        # 1. Weighted score (quality of actions)
        actions_to_consider = recent_actions[:self.recent_window]
        weighted_score = sum(
            self.ACTION_WEIGHTS.get(action, 1) 
            for action in actions_to_consider
        )
        
        # 2. Time on task bonus (if provided)
        time_bonus = 0
        if time_on_task > 0:
            # Expected: ~5-10 min per action
            expected_time = len(actions_to_consider) * 5 * 60  # 5 min per action
            if time_on_task >= expected_time * 0.5:  # At least 50% expected time
                time_bonus = 2
            elif time_on_task >= expected_time * 0.3:
                time_bonus = 1
        
        # 3. Consistency bonus (if timestamps provided)
        consistency_bonus = 0
        if action_timestamps and len(action_timestamps) >= 3:
            # Check if actions are spread out (not all in one burst)
            sorted_times = sorted(action_timestamps[:self.recent_window])
            time_diffs = [sorted_times[i+1] - sorted_times[i] 
                         for i in range(len(sorted_times)-1)]
            
            # If actions spread over time (not crammed)
            if len(time_diffs) > 0:
                avg_gap = np.mean(time_diffs)
                # Consistent if gaps are reasonable (not too short, not too long)
                if 60 <= avg_gap <= 3600:  # Between 1 min and 1 hour
                    consistency_bonus = 2
                elif 30 <= avg_gap <= 7200:  # Between 30 sec and 2 hours
                    consistency_bonus = 1
        
        # 4. Total engagement score
        total_score = weighted_score + time_bonus + consistency_bonus
        
        # Map to engagement level (3 levels)
        for level in range(len(self.ENGAGEMENT_THRESHOLDS) - 1, -1, -1):
            if total_score >= self.ENGAGEMENT_THRESHOLDS[level]:
                return level
        
        return 0
    
    # =========================================================================
    # FRUSTRATION DETECTION - TEMPORARILY DISABLED
    # =========================================================================
    # Uncomment and re-enable in the future when needed
    # This reduces state space from 4,320 to manageable size
    # =========================================================================
    
    # def detect_frustration(
    #     self,
    #     quiz_attempts: int = 0,
    #     quiz_failures: int = 0,
    #     time_on_module: float = 0.0,
    #     median_time: float = 3600.0,
    #     recent_scores: List[float] = None,
    #     consecutive_failures: int = 0,
    #     repeated_views_same_content: int = 0
    # ) -> int:
    #     """
    #     Detect frustration level (0=low, 1=medium, 2=high)
    #     
    #     Args:
    #         quiz_attempts: Number of quiz attempts
    #         quiz_failures: Number of failed quiz attempts
    #         time_on_module: Time spent on module (seconds)
    #         median_time: Median time for this module (seconds)
    #         recent_scores: List of recent scores (0-1)
    #         consecutive_failures: Number of consecutive failed attempts
    #         repeated_views_same_content: Times revisited same content
    #         
    #     Returns:
    #         0: Low frustration (doing well)
    #         1: Medium frustration (some struggles)
    #         2: High frustration (stuck/overwhelmed)
    #     """
    #     frustration_score = 0
    #     
    #     # Factor 1: Quiz attempts and failures
    #     if quiz_attempts > 0:
    #         failure_rate = quiz_failures / quiz_attempts
    #         if failure_rate >= 0.7:  # 70%+ failure rate
    #             frustration_score += 3
    #         elif failure_rate >= 0.5:  # 50%+ failure rate
    #             frustration_score += 2
    #         elif failure_rate >= 0.3:  # 30%+ failure rate
    #             frustration_score += 1
    #     
    #     # Factor 2: Time on module (too long = struggling)
    #     if median_time > 0 and time_on_module > 0:
    #         time_ratio = time_on_module / median_time
    #         if time_ratio > 3.0:  # 3x+ median time
    #             frustration_score += 3
    #         elif time_ratio > 2.0:  # 2x+ median time
    #             frustration_score += 2
    #         elif time_ratio > 1.5:  # 1.5x+ median time
    #             frustration_score += 1
    #     
    #     # Factor 3: Recent scores consistently low
    #     if recent_scores and len(recent_scores) >= 2:
    #         avg_score = np.mean(recent_scores)
    #         score_std = np.std(recent_scores) if len(recent_scores) > 1 else 0
    #         
    #         if avg_score < 0.4:  # Very low scores
    #             frustration_score += 3
    #         elif avg_score < 0.5:  # Low scores
    #             frustration_score += 2
    #         elif avg_score < 0.6:  # Below average
    #             frustration_score += 1
    #         
    #         # High variance = inconsistent performance = confusion
    #         if score_std > 0.25:
    #             frustration_score += 1
    #     
    #     # Factor 4: Consecutive failures
    #     if consecutive_failures >= 3:
    #         frustration_score += 3
    #     elif consecutive_failures >= 2:
    #         frustration_score += 2
    #     elif consecutive_failures >= 1:
    #         frustration_score += 1
    #     
    #     # Factor 5: Repeated views of same content (stuck)
    #     if repeated_views_same_content >= 5:
    #         frustration_score += 2
    #     elif repeated_views_same_content >= 3:
    #         frustration_score += 1
    #     
    #     # Map frustration score to level
    #     if frustration_score >= 8:
    #         return 2  # High frustration
    #     elif frustration_score >= 4:
    #         return 1  # Medium frustration
    #     else:
    #         return 0  # Low frustration
    
    def build_state(
        self,
        cluster_id: int,
        current_module_id: int,
        module_progress: float,
        avg_score: float,
        recent_actions: List[str],
        quiz_attempts: int = 0,
        quiz_failures: int = 0,
        time_on_module: float = 0.0,
        median_time: float = 3600.0,
        recent_scores: List[float] = None,
        consecutive_failures: int = 0,
        time_on_task: float = 0.0,
        action_timestamps: List[float] = None,
        repeated_views_same_content: int = 0
    ) -> Tuple[int, int, float, float, int, int, int]:
        """
        Build 7D state representation
        
        Args:
            cluster_id: Original cluster ID (0-6)
            current_module_id: Module ID from course structure
            module_progress: Progress in module (0-1)
            avg_score: Average score across activities (0-1)
            recent_actions: List of recent action types
            quiz_attempts: Number of quiz attempts
            quiz_failures: Number of failed quiz attempts
            time_on_module: Time on module (seconds)
            median_time: Median time for module (seconds)
            recent_scores: Recent scores
            consecutive_failures: Consecutive failed attempts
            time_on_task: Total time on recent actions (seconds)
            action_timestamps: Timestamps of recent actions
            repeated_views_same_content: Times viewing same content
            
        Returns:
            7D State tuple: (cluster_id, module_idx, progress_bin, score_bin, 
                           learning_phase, engagement_level, frustration_level)
        """
        # 1. Map cluster ID (exclude teacher cluster)
        mapped_cluster = self.map_cluster_id(cluster_id)
        if mapped_cluster is None:
            raise ValueError(f"Cluster {cluster_id} is excluded")
        
        # 2. Map module ID to index
        module_idx = self.module_id_to_idx.get(current_module_id, 0)
        
        # 3. Bin module progress
        progress_bin = self.quartile_bin(module_progress, self.PROGRESS_BINS)
        
        # 4. Bin average score
        score_bin = self.quartile_bin(avg_score, self.SCORE_BINS)
        
        # 5. Calculate learning phase (behavior-based)
        learning_phase = self.calculate_learning_phase(module_progress, recent_actions)
        
        # 6. Calculate engagement level (quality + consistency)
        engagement_level = self.calculate_engagement_level(
            recent_actions, time_on_task, action_timestamps
        )
        
        # 7. Frustration level - TEMPORARILY DISABLED (always 0)
        # Future: re-enable detect_frustration() for multi-level detection
        frustration_level = 0
        
        return (
            mapped_cluster,
            module_idx,
            progress_bin,
            score_bin,
            learning_phase,
            engagement_level,
            frustration_level
        )
    
    def state_to_string(self, state: Tuple) -> str:
        """Convert state to readable string"""
        cluster_id, module_idx, progress, score, phase, engagement, frustration = state
        
        phase_names = {0: "Pre", 1: "Active", 2: "Reflective"}
        engagement_names = {0: "Low", 1: "Medium", 2: "High"}
        
        module_name = self.modules[module_idx]['name'] if module_idx < len(self.modules) else "?"
        
        return (
            f"C{cluster_id} | M{module_idx}({module_name[:30]}) | "
            f"Prog={progress:.2f} Score={score:.2f} | "
            f"Phase={phase_names.get(phase, '?')} | "
            f"Engage={engagement_names.get(engagement, '?')}"
        )
    
    def get_state_info(self) -> Dict:
        """Get information about state space"""
        return {
            'dimensions': 7,
            'dimension_details': {
                'cluster_id': f'0-{self.n_clusters-1}',
                'module_idx': f'0-{self.n_modules-1}',
                'progress_bin': '0.25/0.5/0.75/1.0',
                'score_bin': '0.25/0.5/0.75/1.0',
                'learning_phase': '0=pre/1=active/2=reflective',
                'engagement_level': '0=low/1=medium/2=high (OPTIMIZED: 3 levels)',
                'frustration_level': '0=low (DISABLED: always 0 for state space optimization)'
            },
            'n_clusters': self.n_clusters,
            'n_modules': self.n_modules,
            'excluded_clusters': self.excluded_clusters,
            'state_space_size': self.calculate_state_space_size(),
            'recent_window': self.recent_window
        }
    
    def convert_7d_to_6d(self, state_7d: Tuple) -> Tuple:
        """
        Convert 7D state to 6D format (for compatibility with old Q-table)
        
        Args:
            state_7d: 7D state (cluster, module, progress, score, phase, engagement, frustration)
            
        Returns:
            6D state (cluster, module, progress, score, phase, engagement)
        """
        if len(state_7d) != 7:
            return state_7d  # Already 6D or invalid
        
        cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level, frustration_level = state_7d
        
        # Convert learning_phase to action_id (simplified mapping)
        # phase 0 (pre) -> action 0, phase 1 (active) -> action 1, phase 2 (reflective) -> action 3
        action_id_map = {0: 0, 1: 1, 2: 3}
        action_id = action_id_map.get(learning_phase, 1)
        
        # Convert frustration_level to stuck (boolean)
        is_stuck = bool(frustration_level > 0)
        
        return (cluster_id, module_idx, progress_bin, score_bin, action_id, is_stuck)
    
    def build_state_from_dict(self, state_dict: Dict) -> Tuple:
        """
        Build state from dictionary (convenience method for backward compatibility)
        
        Args:
            state_dict: Dictionary with required and optional keys
        
        Returns:
            State tuple (7D)
        """
        return self.build_state(
            cluster_id=state_dict['cluster_id'],
            current_module_id=state_dict['current_module_id'],
            module_progress=state_dict.get('module_progress', 0.0),
            avg_score=state_dict.get('avg_score', 0.0),
            recent_actions=state_dict.get('recent_actions', []),
            quiz_attempts=state_dict.get('quiz_attempts', 0),
            quiz_failures=state_dict.get('quiz_failures', 0),
            time_on_module=state_dict.get('time_on_module', 0.0),
            median_time=state_dict.get('median_time', 3600.0),
            recent_scores=state_dict.get('recent_scores', None),
            consecutive_failures=state_dict.get('consecutive_failures', 0),
            time_on_task=state_dict.get('time_on_task', 0.0),
            action_timestamps=state_dict.get('action_timestamps', None),
            repeated_views_same_content=state_dict.get('repeated_views_same_content', 0)
        )
