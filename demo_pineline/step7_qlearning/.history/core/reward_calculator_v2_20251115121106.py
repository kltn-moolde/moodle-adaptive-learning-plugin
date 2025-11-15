#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reward Calculator V2 - Refactored with LO Mastery Integration
===============================================================
Cluster-specific reward design for adaptive learning with configurable parameters

Key Improvements:
- Supports 7D state from StateBuilderV2 (cluster, module, progress, score, phase, engagement, frustration)
- Config-driven thresholds and action mappings
- Normalized rewards to prevent Q-learning instability
- Compatible with new ActionSpace (15 temporal actions)
- **NEW**: LO mastery tracking and midterm-weighted reward bonus

LO Integration Strategy:
========================
ΔLO reward = Σ(ΔLO_mastery[lo] × midterm_weight[lo] × cluster_bonus)

This encourages the agent to recommend activities that:
1. Improve weak LOs (low current mastery)
2. Are important for upcoming midterm (high midterm_weight)
3. Match cluster learning capacity (cluster_bonus multiplier)
"""

import json
from typing import Dict, Optional, Tuple, List
from pathlib import Path
import numpy as np
from collections import defaultdict


class RewardCalculatorV2:
    """
    Reward Calculator V2 với cluster-specific rewards và config-driven design
    
    State Tuple (7D from StateBuilderV2):
    =====================================
    (cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level, frustration_level)
    - cluster_id: 0-4 (mapped, excluded teacher cluster)
    - module_idx: 0-5 (6 subsection modules)
    - progress_bin: 0.25/0.5/0.75/1.0
    - score_bin: 0.25/0.5/0.75/1.0
    - learning_phase: 0=pre/1=active/2=reflective
    - engagement_level: 0=low/1=medium/2=high
    - frustration_level: 0 (temporarily disabled, always 0)
    
    Reward Strategy:
    ================
    - Weak clusters: High completion rewards, encourage any progress
    - Medium clusters: Balanced rewards, focus on score improvement
    - Strong clusters: Challenge bonuses, time efficiency rewards
    """
    
    def __init__(
        self, 
        cluster_profiles_path: str,
        reward_config_path: Optional[str] = None,
        po_lo_path: Optional[str] = None,
        midterm_weights_path: Optional[str] = None
    ):
        """
        Initialize reward calculator with LO mastery integration
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json
            reward_config_path: Path to reward_config.json (optional)
            po_lo_path: Path to Po_Lo.json (optional)
            midterm_weights_path: Path to midterm_lo_weights.json (optional)
        """
        self.cluster_profiles_path = Path(cluster_profiles_path)
        self.cluster_profiles = {}
        self.n_clusters = 0
        self.cluster_levels = {}  # cluster_id -> 'weak'/'medium'/'strong'
        
        # Load configurations
        self._load_profiles()
        self._classify_clusters()
        
        # Load reward config
        if reward_config_path is None:
            reward_config_path = Path(__file__).parent.parent / 'config' / 'reward_config.json'
        self.config = self._load_config(reward_config_path)
        
        # Build action mappings from config
        self.action_types = self.config['action_mappings']
        self.action_type_to_id = {v: k for k, v in self.action_types.items()}
        
        # Build sequence lookup
        self._build_sequence_lookup()
        
        # Load LO mappings and midterm weights
        if po_lo_path is None:
            po_lo_path = Path(__file__).parent.parent / 'data' / 'Po_Lo.json'
        if midterm_weights_path is None:
            midterm_weights_path = Path(__file__).parent.parent / 'data' / 'midterm_lo_weights.json'
        
        self._load_lo_mappings(po_lo_path)
        self._load_midterm_weights(midterm_weights_path)
        
        # LO mastery tracking (per student)
        self.lo_mastery_cache = {}  # student_id -> {lo_id: mastery_score}
        
        print(f"\n✓ RewardCalculatorV2 initialized:")
        print(f"  - Clusters: {len(self.cluster_levels)} (weak/medium/strong)")
        print(f"  - Action types: {len(self.action_types)}")
        print(f"  - Beneficial sequences: {len(self.beneficial_sequences)}")
        print(f"  - Normalization: {self.config['normalization']['enabled']}")
        print(f"  - Learning Outcomes: {len(self.lo_data)} LOs mapped to {len(self.activity_to_los)} activities")
        print(f"  - Midterm LO weights: {len(self.midterm_weights)} LOs tracked")
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load reward configuration from JSON"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_lo_mappings(self, po_lo_path: Path):
        """Load LO mappings from Po_Lo.json"""
        with open(po_lo_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.lo_data = {lo['id']: lo for lo in data['learning_outcomes']}
        
        # Build activity_id -> [LO_ids] mapping
        self.activity_to_los = defaultdict(list)
        for lo_id, lo in self.lo_data.items():
            for activity_id in lo.get('activity_ids', []):
                self.activity_to_los[activity_id].append(lo_id)
    
    def _load_midterm_weights(self, weights_path: Path):
        """Load midterm LO weights"""
        with open(weights_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.midterm_weights = data['lo_weights']
        self.midterm_quiz_id = data.get('midterm_quiz_id', 107)
    
    def _build_sequence_lookup(self):
        """Build lookup dict for beneficial action sequences"""
        self.beneficial_sequences = {}
        
        for seq in self.config['action_sequences']['sequences']:
            from_action = seq['from']
            to_action = seq['to']
            
            # Get action IDs
            from_id = self.action_types.get(from_action)
            to_id = self.action_types.get(to_action)
            
            if from_id is not None and to_id is not None:
                self.beneficial_sequences[(from_id, to_id)] = {
                    'bonus': seq['bonus'],
                    'rationale': seq['rationale']
                }
    
    def _load_profiles(self):
        """Load cluster profiles"""
        with open(self.cluster_profiles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.n_clusters = data.get('n_clusters', 7)
        self.cluster_profiles = data.get('cluster_stats', {})
    
    def _classify_clusters(self):
        """
        Tự động phân loại clusters thành weak/medium/strong
        dựa trên mean_module_grade
        """
        # Extract grades for all clusters (exclude teacher cluster 3)
        grade_data = []
        for cluster_id in range(self.n_clusters):
            if cluster_id == 3:  # Skip teacher cluster
                continue
            
            profile = self.cluster_profiles.get(str(cluster_id), {})
            mean_grade = profile.get('feature_means', {}).get('mean_module_grade', 0.5)
            profile_name = profile.get('ai_profile', {}).get('name', 'Unknown')
            grade_data.append((cluster_id, mean_grade, profile_name))
        
        # Sort by grade
        grade_data.sort(key=lambda x: x[1])
        
        # Split into 3 groups (weak, medium, strong)
        n = len(grade_data)
        weak_threshold = n // 3
        strong_threshold = 2 * n // 3
        
        print("\n=== CLUSTER CLASSIFICATION ===")
        for i, (cluster_id, grade, name) in enumerate(grade_data):
            if i < weak_threshold:
                level = 'weak'
            elif i < strong_threshold:
                level = 'medium'
            else:
                level = 'strong'
            
            self.cluster_levels[cluster_id] = level
            
            print(f"  Cluster {cluster_id}: grade={grade:.3f} → {level:8s} | {name}")
        print("=" * 50)
    
    def get_cluster_level(self, cluster_id: int) -> str:
        """
        Get performance level of a cluster
        
        Args:
            cluster_id: ID của cluster (already mapped, 0-4)
            
        Returns:
            'weak', 'medium', or 'strong'
        """
        return self.cluster_levels.get(cluster_id, 'medium')
    
    def _normalize_reward(self, reward: float) -> float:
        """
        Normalize reward to prevent extreme values
        
        Args:
            reward: Raw reward value
            
        Returns:
            Normalized reward
        """
        if not self.config['normalization']['enabled']:
            return reward
        
        method = self.config['normalization']['method']
        
        if method == 'clip':
            min_r = self.config['normalization']['min_reward']
            max_r = self.config['normalization']['max_reward']
            return np.clip(reward, min_r, max_r)
        elif method == 'tanh':
            # Tanh scaling: maps (-inf, inf) to (-1, 1)
            return np.tanh(reward / 10.0) * 10.0
        else:
            return reward
    
    def _map_action_to_type(self, action_type_str: str) -> int:
        """
        Map action type string to action type ID (config-driven)
        
        Args:
            action_type_str: Action type string (e.g., 'attempt_quiz', 'view_content')
            
        Returns:
            Action type ID from config
        """
        # Normalize action type string
        action_type_str = action_type_str.lower().strip()
        
        # Direct mapping from config
        if action_type_str in self.action_types:
            return self.action_types[action_type_str]
        
        # Fuzzy matching for common variations
        fuzzy_map = {
            'quiz': 'attempt_quiz',
            'do_quiz': 'attempt_quiz',
            'video': 'view_content',
            'watch_video': 'view_content',
            'forum': 'post_forum',
            'discussion': 'post_forum',
            'mod_forum': 'post_forum',
            'resource': 'download_resource',
            'page': 'view_content',
            'url': 'view_content',
            'assignment': 'submit_assignment',
            'assign': 'submit_assignment',
            'do_assignment': 'submit_assignment',
            'review': 'review_quiz',
            'download': 'download_resource'
        }
        
        # Try fuzzy matching
        for key, mapped_action in fuzzy_map.items():
            if key in action_type_str:
                return self.action_types.get(mapped_action, 0)
        
        # Default to view_content
        return self.action_types.get('view_content', 0)
    
    def calculate_lo_mastery_delta(
        self,
        student_id: int,
        activity_id: int,
        outcome: Dict,
        cluster_id: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate ΔLO mastery reward for an activity
        
        Args:
            student_id: Student ID for tracking mastery
            activity_id: Activity ID performed
            outcome: Activity outcome (score, success, etc.)
            cluster_id: Student's cluster ID
            
        Returns:
            Tuple of (total_lo_reward, lo_deltas)
        """
        # Get LOs associated with this activity
        related_los = self.activity_to_los.get(activity_id, [])
        
        if not related_los:
            return 0.0, {}
        
        # Initialize student mastery if not exists
        if student_id not in self.lo_mastery_cache:
            self.lo_mastery_cache[student_id] = defaultdict(lambda: 0.5)  # Start at 50%
        
        student_mastery = self.lo_mastery_cache[student_id]
        
        # Calculate mastery improvement based on outcome
        outcome_score = outcome.get('score', 0.0)
        success = outcome.get('success', True)
        
        # Mastery update formula: new = old + α × (outcome - old)
        # Learning rate α depends on cluster (weak=0.3, medium=0.2, strong=0.15)
        cluster_level = self.get_cluster_level(cluster_id)
        alpha = {'weak': 0.3, 'medium': 0.2, 'strong': 0.15}.get(cluster_level, 0.2)
        
        # Cluster-specific bonus multiplier for LO improvement
        # Weak clusters get more reward for any LO improvement
        cluster_bonus = {'weak': 1.5, 'medium': 1.2, 'strong': 1.0}.get(cluster_level, 1.0)
        
        total_reward = 0.0
        lo_deltas = {}
        
        for lo_id in related_los:
            old_mastery = student_mastery[lo_id]
            
            # Update mastery
            if outcome_score is not None:
                # Have score - use it
                if success:
                    new_mastery = old_mastery + alpha * (outcome_score - old_mastery)
                else:
                    # Failed activity: slight mastery decrease
                    new_mastery = old_mastery - alpha * 0.1
            else:
                # No score (e.g., view_content) - small positive gain
                new_mastery = old_mastery + alpha * 0.05
            
            # Clamp to [0, 1]
            new_mastery = max(0.0, min(1.0, new_mastery))
            
            # Calculate delta
            delta = new_mastery - old_mastery
            lo_deltas[lo_id] = delta
            
            # Update cache
            student_mastery[lo_id] = new_mastery
            
            # Calculate reward contribution
            # High midterm weight + low current mastery = high priority
            midterm_weight = self.midterm_weights.get(lo_id, 0.0)
            
            # Inverse mastery bonus: reward improving weak LOs more
            # If mastery is low (0.3), bonus = 1.7; if high (0.9), bonus = 1.1
            inverse_mastery_bonus = 2.0 - old_mastery
            
            lo_reward = delta * midterm_weight * cluster_bonus * inverse_mastery_bonus * 10.0
            total_reward += lo_reward
        
        return total_reward, lo_deltas
    
    def get_lo_mastery_state(self, student_id: int) -> Dict[str, float]:
        """
        Get current LO mastery state for a student
        
        Args:
            student_id: Student ID
            
        Returns:
            Dict of {lo_id: mastery_score}
        """
        if student_id not in self.lo_mastery_cache:
            return {lo_id: 0.5 for lo_id in self.lo_data.keys()}
        
        return dict(self.lo_mastery_cache[student_id])
    
    def get_weak_los_for_midterm(self, student_id: int, threshold: float = 0.6) -> List[Tuple[str, float, float]]:
        """
        Get weak LOs that are important for midterm
        
        Args:
            student_id: Student ID
            threshold: Mastery threshold below which LO is considered weak
            
        Returns:
            List of (lo_id, current_mastery, midterm_weight) sorted by priority
        """
        mastery = self.get_lo_mastery_state(student_id)
        
        weak_los = []
        for lo_id, midterm_weight in self.midterm_weights.items():
            current_mastery = mastery.get(lo_id, 0.5)
            if current_mastery < threshold:
                # Priority = weight × (1 - mastery)
                priority = midterm_weight * (1.0 - current_mastery)
                weak_los.append((lo_id, current_mastery, midterm_weight, priority))
        
        # Sort by priority (descending)
        weak_los.sort(key=lambda x: x[3], reverse=True)
        
        return [(lo_id, mastery, weight) for lo_id, mastery, weight, _ in weak_los]
    
    def calculate_reward(
        self,
        state: Tuple[int, int, float, float, int, int, int],
        action: Dict,
        outcome: Dict,
        previous_state: Optional[Tuple[int, int, float, float, int, int, int]] = None,
        previous_action_type: Optional[str] = None,
        student_id: Optional[int] = None,
        activity_id: Optional[int] = None
    ) -> float:
        """
        Calculate reward based on cluster-specific strategy + LO mastery improvement
        
        Args:
            state: Current 7D state tuple from StateBuilderV2
                   (cluster_id, module_idx, progress_bin, score_bin, 
                    learning_phase, engagement_level, frustration_level)
            action: Action taken (dict with 'type', 'difficulty', 'expected_time')
            outcome: Action outcome (dict with 'completed', 'score', 'time', 'success')
            previous_state: Previous 7D state tuple (for delta calculation)
            previous_action_type: Previous action type string (for sequence bonus)
            student_id: Student ID (for LO mastery tracking)
            activity_id: Activity ID (for LO mapping)
            
        Returns:
            Normalized reward value (float)
        """
        # Unpack 7D state
        cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level, frustration_level = state
        
        # Get cluster level
        cluster_level = self.get_cluster_level(cluster_id)
        
        # Extract previous state if available
        prev_score_bin = previous_state[3] if previous_state else score_bin
        prev_engagement = previous_state[5] if previous_state else engagement_level
        
        # Map current action to type ID
        action_type_str = action.get('type', 'view_content')
        current_action_id = self._map_action_to_type(action_type_str)
        
        # Base reward
        reward = 0.0
        
        # ===================================================================
        # Component 1: Completion Reward (cluster-adaptive)
        # ===================================================================
        if outcome.get('completed', False):
            completion_cfg = self.config['reward_components']['completion']
            reward += completion_cfg.get(cluster_level, 3.0)
        
        # ===================================================================
        # Component 2: Score Improvement (all clusters value this)
        # ===================================================================
        outcome_score = outcome.get('score')
        
        # Only calculate score delta if score is available
        if outcome_score is not None:
            score_delta = outcome_score - prev_score_bin
            
            if score_delta > 0:
                multiplier = self.config['reward_components']['score_improvement']['multiplier']
                reward += score_delta * multiplier
                
                # Milestone bonus for weak clusters
                milestone_cfg = self.config['reward_components']['score_improvement'].get('milestone_bonus', {})
                if cluster_level == 'weak' and outcome_score >= milestone_cfg.get('threshold', 0.7):
                    reward += milestone_cfg.get('weak', 2.0)
        else:
            # No score available (e.g., view_content), use small default
            score_delta = 0.0
        
        # ===================================================================
        # Component 3: High Score Bonus
        # ===================================================================
        high_score_cfg = self.config['reward_components']['high_score_bonus']
        if outcome_score is not None and outcome_score >= high_score_cfg['threshold']:
            reward += high_score_cfg.get(cluster_level, 2.0)
        
        # ===================================================================
        # Component 4: Progression Bonus (difficulty-based)
        # ===================================================================
        action_difficulty = action.get('difficulty', 'medium')
        if outcome.get('completed', False):
            prog_cfg = self.config['reward_components']['progression']
            
            if cluster_level == 'weak':
                reward += prog_cfg['weak'].get('any', 2.0)
            else:
                difficulty_rewards = prog_cfg.get(cluster_level, {})
                reward += difficulty_rewards.get(action_difficulty, 2.0)
        
        # ===================================================================
        # Component 5: Time Efficiency (strong clusters value this)
        # ===================================================================
        time_cfg = self.config['reward_components']['time_efficiency']
        if cluster_level in time_cfg.get('enabled_for', []):
            time_taken = outcome.get('time', 0)
            expected_time = action.get('expected_time', 30)
            
            if time_taken > 0 and time_taken < expected_time * time_cfg['threshold_ratio']:
                reward += time_cfg['bonus']
        
        # ===================================================================
        # Component 6: Engagement Bonus (from state)
        # ===================================================================
        engagement_cfg = self.config['reward_components']['engagement_bonus']
        engagement_names = {0: 'low', 1: 'medium', 2: 'high'}
        engagement_key = engagement_names.get(engagement_level, 'low')
        reward += engagement_cfg.get(engagement_key, 0.0)
        
        # ===================================================================
        # Component 7: Learning Phase Alignment
        # ===================================================================
        phase_cfg = self.config['reward_components']['learning_phase_bonus']
        phase_names = {0: 'pre', 1: 'active', 2: 'reflective'}
        phase_key = phase_names.get(learning_phase, 'pre')
        
        # Bonus for phase-appropriate actions
        if learning_phase == 1 and 'quiz' in action_type_str:  # Active phase + quiz
            reward += phase_cfg.get('active', 1.0)
        elif learning_phase == 2 and 'review' in action_type_str:  # Reflective + review
            reward += phase_cfg.get('reflective', 1.5)
        
        # ===================================================================
        # Component 8: Frustration Penalty (currently disabled in state)
        # ===================================================================
        frustration_cfg = self.config['penalties']['frustration']
        if frustration_cfg.get('enabled', False) and frustration_level > 0:
            # Note: frustration_level always 0 in current StateBuilderV2
            penalty = frustration_cfg['values'].get(cluster_level, -1.0)
            reward += penalty * frustration_level
        
        # ===================================================================
        # Component 9: Failure Penalty
        # ===================================================================
        if not outcome.get('success', True):
            failure_cfg = self.config['penalties']['failure']
            reward += failure_cfg.get(cluster_level, -1.0)
        
        # ===================================================================
        # Component 10: Low Engagement Penalty
        # ===================================================================
        low_engage_cfg = self.config['penalties']['low_engagement']
        if low_engage_cfg.get('enabled', True) and engagement_level == low_engage_cfg.get('threshold', 0):
            reward += low_engage_cfg.get('penalty', -0.5)
        
        # ===================================================================
        # Component 11: Action Sequence Bonus
        # ===================================================================
        if previous_action_type:
            prev_action_id = self._map_action_to_type(previous_action_type)
            sequence_key = (prev_action_id, current_action_id)
            
            if sequence_key in self.beneficial_sequences:
                seq_data = self.beneficial_sequences[sequence_key]
                base_bonus = seq_data['bonus']
                
                # Scale by cluster level
                scaling = self.config['action_sequences']['cluster_scaling']
                scaled_bonus = base_bonus * scaling.get(cluster_level, 1.0)
                reward += scaled_bonus
        
        # ===================================================================
        # Component 12: LO Mastery Improvement (NEW)
        # ===================================================================
        if student_id is not None and activity_id is not None:
            lo_reward, lo_deltas = self.calculate_lo_mastery_delta(
                student_id=student_id,
                activity_id=activity_id,
                outcome=outcome,
                cluster_id=cluster_id
            )
            reward += lo_reward
            
            # Store lo_deltas in outcome for debugging (optional)
            if lo_deltas:
                outcome['lo_deltas'] = lo_deltas
        
        # ===================================================================
        # Normalize reward to prevent extreme values
        # ===================================================================
        return self._normalize_reward(reward)
    
    def calculate_reward_with_breakdown(
        self,
        state: Tuple[int, int, float, float, int, int, int],
        action: Dict,
        outcome: Dict,
        previous_state: Optional[Tuple[int, int, float, float, int, int, int]] = None,
        previous_action_type: Optional[str] = None,
        student_id: Optional[int] = None,
        activity_id: Optional[int] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate reward with detailed breakdown
        
        Returns:
            (reward, breakdown_dict) where breakdown_dict contains component values
        """
        # Unpack 7D state
        cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level, frustration_level = state
        
        # Get cluster level
        cluster_level = self.get_cluster_level(cluster_id)
        
        # Extract previous state if available
        prev_score_bin = previous_state[3] if previous_state else score_bin
        prev_engagement = previous_state[5] if previous_state else engagement_level
        
        # Map current action to type ID
        action_type_str = action.get('type', 'view_content')
        current_action_id = self._map_action_to_type(action_type_str)
        
        # Base reward and breakdown
        reward = 0.0
        breakdown = {}
        
        # ===================================================================
        # Component 1: Completion Reward
        # ===================================================================
        if outcome.get('completed', False):
            completion_cfg = self.config['reward_components']['completion']
            completion_reward = completion_cfg.get(cluster_level, 3.0)
            reward += completion_reward
            breakdown['completion'] = completion_reward
        
        # ===================================================================
        # Component 2: Score Improvement
        # ===================================================================
        outcome_score = outcome.get('score')
        if outcome_score is not None:
            score_delta = outcome_score - prev_score_bin
            if score_delta > 0:
                multiplier = self.config['reward_components']['score_improvement']['multiplier']
                score_reward = score_delta * multiplier
                reward += score_reward
                breakdown['score_improvement'] = score_reward
                
                # Milestone bonus
                milestone_cfg = self.config['reward_components']['score_improvement'].get('milestone_bonus', {})
                if cluster_level == 'weak' and outcome_score >= milestone_cfg.get('threshold', 0.7):
                    milestone_bonus = milestone_cfg.get('weak', 2.0)
                    reward += milestone_bonus
                    breakdown['milestone_bonus'] = milestone_bonus
        
        # ===================================================================
        # Component 3: High Score Bonus
        # ===================================================================
        high_score_cfg = self.config['reward_components']['high_score_bonus']
        if outcome_score is not None and outcome_score >= high_score_cfg['threshold']:
            high_score_reward = high_score_cfg.get(cluster_level, 2.0)
            reward += high_score_reward
            breakdown['high_score_bonus'] = high_score_reward
        
        # ===================================================================
        # Component 4: Progression Bonus
        # ===================================================================
        action_difficulty = action.get('difficulty', 'medium')
        if outcome.get('completed', False):
            prog_cfg = self.config['reward_components']['progression']
            if cluster_level == 'weak':
                prog_reward = prog_cfg['weak'].get('any', 2.0)
            else:
                difficulty_rewards = prog_cfg.get(cluster_level, {})
                prog_reward = difficulty_rewards.get(action_difficulty, 2.0)
            reward += prog_reward
            breakdown['progression'] = prog_reward
        
        # ===================================================================
        # Component 5: Time Efficiency
        # ===================================================================
        time_cfg = self.config['reward_components']['time_efficiency']
        if cluster_level in time_cfg.get('enabled_for', []):
            time_taken = outcome.get('time', 0)
            expected_time = action.get('expected_time', 30)
            if time_taken > 0 and time_taken < expected_time:
                time_reward = time_cfg.get('bonus', 1.5)
                reward += time_reward
                breakdown['time_efficiency'] = time_reward
        
        # ===================================================================
        # Component 6: Learning Phase Bonus
        # ===================================================================
        phase_cfg = self.config['reward_components'].get('learning_phase_bonus', {})
        phase_names = {0: 'pre', 1: 'active', 2: 'reflective'}
        phase_key = phase_names.get(learning_phase, 'pre')
        if phase_key in phase_cfg:
            phase_reward = phase_cfg.get(phase_key, 0.0)
            reward += phase_reward
            breakdown['learning_phase'] = phase_reward
        
        # ===================================================================
        # Component 7: Engagement Bonus
        # ===================================================================
        engage_cfg = self.config['reward_components'].get('engagement_bonus', {})
        engage_levels = {0: 'low', 1: 'medium', 2: 'high'}
        engage_key = engage_levels.get(engagement_level, 'low')
        if engage_key in engage_cfg:
            engage_reward = engage_cfg.get(engage_key, 0.0)
            reward += engage_reward
            breakdown['engagement'] = engage_reward
        
        # ===================================================================
        # Component 8: Failure Penalty
        # ===================================================================
        if not outcome.get('success', True):
            failure_penalty = self.config['penalties']['failure'].get(cluster_level, -2.0)
            reward += failure_penalty
            breakdown['failure_penalty'] = failure_penalty
        
        # ===================================================================
        # Component 9: Stuck Penalty
        # ===================================================================
        if frustration_level > 0:
            stuck_penalty = self.config['penalties']['stuck'].get(cluster_level, -1.0)
            reward += stuck_penalty
            breakdown['stuck_penalty'] = stuck_penalty
        
        # ===================================================================
        # Component 10: Low Engagement Penalty
        # ===================================================================
        low_engage_cfg = self.config['penalties']['low_engagement']
        if low_engage_cfg.get('enabled', True) and engagement_level == low_engage_cfg.get('threshold', 0):
            low_engage_penalty = low_engage_cfg.get('penalty', -0.5)
            reward += low_engage_penalty
            breakdown['low_engagement_penalty'] = low_engage_penalty
        
        # ===================================================================
        # Component 11: Action Sequence Bonus
        # ===================================================================
        if previous_action_type:
            prev_action_id = self._map_action_to_type(previous_action_type)
            sequence_key = (prev_action_id, current_action_id)
            if sequence_key in self.beneficial_sequences:
                seq_data = self.beneficial_sequences[sequence_key]
                base_bonus = seq_data['bonus']
                scaling = self.config['action_sequences']['cluster_scaling']
                scaled_bonus = base_bonus * scaling.get(cluster_level, 1.0)
                reward += scaled_bonus
                breakdown['sequence_bonus'] = scaled_bonus
        
        # ===================================================================
        # Component 12: LO Mastery Improvement
        # ===================================================================
        if student_id is not None and activity_id is not None:
            lo_reward, lo_deltas = self.calculate_lo_mastery_delta(
                student_id=student_id,
                activity_id=activity_id,
                outcome=outcome,
                cluster_id=cluster_id
            )
            reward += lo_reward
            breakdown['lo_mastery_improvement'] = lo_reward
            if lo_deltas:
                outcome['lo_deltas'] = lo_deltas
        
        # Normalize
        normalized_reward = self._normalize_reward(reward)
        
        return normalized_reward, breakdown
    
    def calculate_reward_simple(
        self,
        cluster_id: int,
        completed: bool,
        score: float,
        previous_score: float,
        is_stuck: bool,
        difficulty: str = 'medium'
    ) -> float:
        """
        Simplified reward calculation (for quick testing)
        
        Args:
            cluster_id: Cluster ID (0-5)
            completed: Whether action was completed
            score: Current score (0-1)
            previous_score: Previous score (0-1)
            is_stuck: Whether student is stuck
            difficulty: Action difficulty
            
        Returns:
            Reward value
        """
        cluster_level = self.get_cluster_level(cluster_id)
        reward = 0.0
        
        # Completion
        if completed:
            if cluster_level == 'weak':
                reward += 10.0
            elif cluster_level == 'medium':
                reward += 7.0
            else:
                reward += 5.0
        
        # Score improvement
        score_delta = score - previous_score
        if score_delta > 0:
            reward += score_delta * 10.0
        
        # Stuck penalty
        if is_stuck:
            reward -= (3.0 if cluster_level == 'weak' else 2.0)
        
        # Difficulty bonus for strong clusters
        if cluster_level == 'strong' and difficulty == 'hard' and completed:
            reward += 5.0
        
        return reward
    
    def get_reward_strategy_description(self, cluster_id: int) -> Dict:
        """
        Get description of reward strategy for a cluster
        
        Args:
            cluster_id: Cluster ID (0-4)
            
        Returns:
            Dict describing reward strategy
        """
        level = self.get_cluster_level(cluster_id)
        
        strategies = {
            'weak': {
                'focus': 'Completion and Progress',
                'completion_reward': 10.0,
                'stuck_penalty': -3.0,
                'philosophy': 'High rewards for any completion. Need motivation and guidance. '
                             'Small wins build confidence. Avoid harsh penalties.',
                'recommended_actions': 'Easy to medium difficulty. Step-by-step progression.'
            },
            'medium': {
                'focus': 'Balanced Growth',
                'completion_reward': 7.0,
                'stuck_penalty': -2.0,
                'philosophy': 'Balanced rewards. Focus on appropriate difficulty. '
                             'Build skills systematically. Moderate challenge.',
                'recommended_actions': 'Medium difficulty preferred. Mix of content and assessment.'
            },
            'strong': {
                'focus': 'Challenge and Mastery',
                'completion_reward': 5.0,
                'stuck_penalty': -1.0,
                'philosophy': 'Challenge-seeking. Reward hard tasks and efficiency. '
                             'High expectations. Focus on mastery and speed.',
                'recommended_actions': 'Hard difficulty preferred. Advanced topics. Time efficiency valued.'
            }
        }
        
        return {
            'cluster_id': cluster_id,
            'level': level,
            'strategy': strategies[level]
        }
    
    def get_all_strategies(self) -> Dict:
        """Get reward strategies for all clusters"""
        return {
            cid: self.get_reward_strategy_description(cid)
            for cid in self.cluster_levels.keys()
        }
    
    def get_action_sequence_info(self) -> Dict:
        """
        Get information about beneficial action sequences
        
        Returns:
            Dict with sequence information
        """
        sequences = []
        for (prev_id, curr_id), seq_data in self.beneficial_sequences.items():
            prev_name = self.action_type_to_id.get(prev_id, 'unknown')
            curr_name = self.action_type_to_id.get(curr_id, 'unknown')
            sequences.append({
                'previous_action': prev_name,
                'current_action': curr_name,
                'bonus_reward': seq_data['bonus'],
                'rationale': seq_data['rationale']
            })
        
        return {
            'total_sequences': len(self.beneficial_sequences),
            'sequences': sequences,
            'cluster_scaling': self.config['action_sequences']['cluster_scaling']
        }
    
    def get_config_info(self) -> Dict:
        """Get summary of reward configuration"""
        return {
            'version': self.config['version'],
            'action_types': len(self.action_types),
            'beneficial_sequences': len(self.beneficial_sequences),
            'normalization': {
                'enabled': self.config['normalization']['enabled'],
                'method': self.config['normalization']['method'],
                'range': [
                    self.config['normalization']['min_reward'],
                    self.config['normalization']['max_reward']
                ]
            },
            'clusters': {
                'total': len(self.cluster_levels),
                'weak': sum(1 for l in self.cluster_levels.values() if l == 'weak'),
                'medium': sum(1 for l in self.cluster_levels.values() if l == 'medium'),
                'strong': sum(1 for l in self.cluster_levels.values() if l == 'strong')
            },
            'lo_integration': {
                'total_los': len(self.lo_data),
                'midterm_tracked_los': len(self.midterm_weights),
                'activities_mapped': len(self.activity_to_los)
            }
        }
    
    def get_recommended_activities_for_weak_los(
        self, 
        student_id: int, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Get recommended activities to improve weak LOs for midterm
        
        Args:
            student_id: Student ID
            top_k: Number of activities to recommend
            
        Returns:
            List of dicts with activity recommendations
        """
        # Get weak LOs
        weak_los = self.get_weak_los_for_midterm(student_id)
        
        if not weak_los:
            return []
        
        # Build activity priority scores
        activity_scores = defaultdict(float)
        activity_los = defaultdict(list)
        
        for lo_id, mastery, weight in weak_los:
            # Priority = weight × (1 - mastery)
            priority = weight * (1.0 - mastery)
            
            # Find activities for this LO
            lo_info = self.lo_data.get(lo_id, {})
            for activity_id in lo_info.get('activity_ids', []):
                activity_scores[activity_id] += priority
                activity_los[activity_id].append({
                    'lo_id': lo_id,
                    'mastery': mastery,
                    'weight': weight,
                    'priority': priority
                })
        
        # Sort by score
        sorted_activities = sorted(
            activity_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # Format recommendations
        recommendations = []
        for activity_id, score in sorted_activities:
            recommendations.append({
                'activity_id': activity_id,
                'priority_score': score,
                'target_los': activity_los[activity_id],
                'rationale': f"Improves {len(activity_los[activity_id])} weak LOs important for midterm"
            })
        
        return recommendations
    
    def explain_recommendation(
        self,
        activity_id: int,
        student_id: int,
        cluster_id: Optional[int] = None,
        include_alternatives: bool = False
    ) -> Dict:
        """
        Giải thích tại sao gợi ý activity này cho student
        
        Args:
            activity_id: Activity ID được gợi ý
            student_id: Student ID
            cluster_id: Cluster ID (optional, để customize explanation)
            include_alternatives: Include alternative activities (default False)
            
        Returns:
            Dict with detailed explanation
        """
        # Get LOs for this activity
        target_los = self.activity_to_los.get(activity_id, [])
        
        if not target_los:
            return {
                'activity_id': activity_id,
                'recommendation': f"Làm activity {activity_id}",
                'why': {'error': 'Activity không map với LO nào'}
            }
        
        # Get student's current mastery
        mastery_state = self.get_lo_mastery_state(student_id)
        
        # Calculate expected gains for each target LO
        lo_gains = {}
        for lo_id in target_los:
            current_mastery = mastery_state.get(lo_id, 0.5)
            midterm_weight = self.midterm_weights.get(lo_id, 0.0)
            
            # Expected gain = (potential improvement) × weight
            # Assume average outcome score = 0.75
            expected_outcome = 0.75
            cluster_level = self.get_cluster_level(cluster_id) if cluster_id is not None else 'medium'
            alpha = {'weak': 0.3, 'medium': 0.2, 'strong': 0.15}.get(cluster_level, 0.2)
            
            expected_delta = alpha * (expected_outcome - current_mastery)
            expected_gain = expected_delta * midterm_weight
            
            lo_gains[lo_id] = {
                'current_mastery': current_mastery,
                'midterm_weight': midterm_weight,
                'expected_delta': expected_delta,
                'expected_gain': expected_gain
            }
        
        # Find primary target LO (highest expected gain)
        if lo_gains:
            primary_lo = max(lo_gains.items(), key=lambda x: x[1]['expected_gain'])
            primary_lo_id, primary_lo_data = primary_lo
        else:
            return {
                'activity_id': activity_id,
                'recommendation': f"Làm activity {activity_id}",
                'why': {'error': 'Không tính được expected gain'}
            }
        
        # Get cluster strategy
        cluster_level = self.get_cluster_level(cluster_id) if cluster_id is not None else 'medium'
        cluster_strategies = {
            'weak': 'Bạn thuộc nhóm cần hỗ trợ → ưu tiên hoàn thành và xây dựng nền tảng',
            'medium': 'Bạn thuộc nhóm trung bình → tập trung vào LO quan trọng để nâng cao điểm',
            'strong': 'Bạn thuộc nhóm giỏi → thử thách bản thân với LO phức tạp và chứng minh mastery'
        }
        
        # Build explanation
        explanation = {
            'activity_id': activity_id,
            'recommendation': f"Làm activity {activity_id}",
            'why': {
                'target_LO': primary_lo_id,
                'lo_description': self.lo_data.get(primary_lo_id, {}).get('description', 'N/A'),
                'current_mastery': round(primary_lo_data['current_mastery'], 2),
                'midterm_weight': f"{primary_lo_data['midterm_weight']*100:.1f}%",
                'expected_gain': round(primary_lo_data['expected_gain'], 3),
                'cluster_strategy': cluster_strategies.get(cluster_level, 'Học đều đặn'),
                'evidence': f"LO này chiếm {primary_lo_data['midterm_weight']*100:.1f}% điểm giữa kỳ",
                'urgency': self._calculate_urgency(primary_lo_data['current_mastery'], 
                                                   primary_lo_data['midterm_weight'])
            }
        }
        
        # Add all target LOs details
        if len(target_los) > 1:
            explanation['why']['additional_los'] = [
                {
                    'lo_id': lo_id,
                    'current_mastery': round(lo_gains[lo_id]['current_mastery'], 2),
                    'midterm_weight': f"{lo_gains[lo_id]['midterm_weight']*100:.1f}%"
                }
                for lo_id in target_los if lo_id != primary_lo_id
            ]
        
        # Add alternative activities if requested
        if include_alternatives:
            alternatives = self.get_recommended_activities_for_weak_los(
                student_id=student_id, 
                top_k=5
            )
            # Filter out current activity
            alternatives = [a for a in alternatives if a['activity_id'] != activity_id][:3]
            
            explanation['alternatives'] = [
                {
                    'activity_id': alt['activity_id'],
                    'priority_score': round(alt['priority_score'], 3),
                    'rationale': alt['rationale']
                }
                for alt in alternatives
            ]
        
        return explanation
    
    def _calculate_urgency(self, current_mastery: float, midterm_weight: float) -> str:
        """
        Tính mức độ cấp thiết của việc cải thiện LO
        
        Args:
            current_mastery: Current mastery score [0-1]
            midterm_weight: Midterm weight [0-1]
            
        Returns:
            Urgency level string
        """
        # Priority = weight × (1 - mastery)
        priority = midterm_weight * (1.0 - current_mastery)
        
        if priority >= 0.15:
            return "🔴 RẤT CẤP THIẾT - LO quan trọng mà bạn còn yếu!"
        elif priority >= 0.08:
            return "🟡 CẦN CHÚ Ý - Nên cải thiện sớm trước kỳ thi"
        elif priority >= 0.04:
            return "🟢 CỦNG CỐ - Học thêm để đạt điểm tốt hơn"
        else:
            return "⚪ ỔN ĐỊNH - Duy trì và ôn tập định kỳ"


def test_reward_calculator():
    """Test RewardCalculatorV2 with 7D state support + LO mastery integration"""
    print("=" * 80)
    print("Testing RewardCalculatorV2 - Refactored (7D State + LO Mastery)")
    print("=" * 80)
    
    # Path
    base_path = Path(__file__).parent.parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    
    # Initialize
    calc = RewardCalculatorV2(cluster_profiles_path=str(cluster_path))
    
    # Test 1: Config info
    print("\n1. Configuration Info:")
    config_info = calc.get_config_info()
    print(f"   Version: {config_info['version']}")
    print(f"   Action types: {config_info['action_types']}")
    print(f"   Beneficial sequences: {config_info['beneficial_sequences']}")
    print(f"   Normalization: {config_info['normalization']['enabled']} "
          f"({config_info['normalization']['method']}, "
          f"range={config_info['normalization']['range']})")
    print(f"   Clusters: {config_info['clusters']}")
    print(f"   LO Integration: {config_info['lo_integration']}")
    
    # Test 2: LO Mastery Delta Calculation
    print("\n2. LO Mastery Delta Calculation:")
    student_id = 101
    
    # Simulate activity completion for LO1.1 (activity_ids: [54, 98])
    test_activity = 54
    test_outcome = {'completed': True, 'score': 0.85, 'success': True}
    
    print(f"   Student {student_id} completes activity {test_activity}")
    print(f"   Outcome: score={test_outcome['score']}, success={test_outcome['success']}")
    
    lo_reward, lo_deltas = calc.calculate_lo_mastery_delta(
        student_id=student_id,
        activity_id=test_activity,
        outcome=test_outcome,
        cluster_id=0  # weak cluster
    )
    
    print(f"   LO Reward: {lo_reward:.3f}")
    print(f"   LO Deltas:")
    for lo_id, delta in lo_deltas.items():
        mastery = calc.get_lo_mastery_state(student_id)[lo_id]
        print(f"      {lo_id}: Δ={delta:+.3f} → mastery={mastery:.3f}")
    
    # Test 3: Weak LOs for midterm
    print("\n3. Weak LOs for Midterm (student 101):")
    weak_los = calc.get_weak_los_for_midterm(student_id, threshold=0.6)
    print(f"   Found {len(weak_los)} weak LOs:")
    for lo_id, mastery, weight in weak_los[:5]:
        print(f"      {lo_id}: mastery={mastery:.3f}, midterm_weight={weight:.3f}")
    
    # Test 4: Recommended activities
    print("\n4. Recommended Activities to Improve Weak LOs:")
    recommendations = calc.get_recommended_activities_for_weak_los(student_id, top_k=3)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   #{i} Activity {rec['activity_id']} (priority={rec['priority_score']:.3f})")
        print(f"      {rec['rationale']}")
        print(f"      Target LOs:")
        for lo_info in rec['target_los'][:2]:
            print(f"         - {lo_info['lo_id']}: mastery={lo_info['mastery']:.3f}, weight={lo_info['weight']:.3f}")
    
    # Test 5: Sample reward calculations with LO integration
    print("\n5. Sample Reward Calculations (with LO Integration):")
    print("   Format: (cluster_id, module_idx, progress_bin, score_bin,")
    print("            learning_phase, engagement_level, frustration_level)\n")
    
    test_cases = [
        {
            'description': 'Weak learner improves LO1.1 (high midterm weight=0.15)',
            'state': (0, 0, 0.5, 0.5, 1, 1, 0),
            'action': {'type': 'attempt_quiz', 'difficulty': 'easy', 'expected_time': 30},
            'outcome': {'completed': True, 'score': 0.70, 'success': True, 'time': 25},
            'prev_state': (0, 0, 0.25, 0.5, 0, 0, 0),
            'prev_action': 'view_content',
            'student_id': 102,
            'activity_id': 56  # LO1.2 activity (midterm_weight=0.15)
        },
        {
            'description': 'Medium learner works on LO2.2 (high weight=0.25)',
            'state': (2, 2, 0.75, 0.75, 1, 2, 0),
            'action': {'type': 'attempt_quiz', 'difficulty': 'medium', 'expected_time': 30},
            'outcome': {'completed': True, 'score': 0.85, 'success': True, 'time': 28},
            'prev_state': (2, 2, 0.5, 0.75, 1, 2, 0),
            'prev_action': 'download_resource',
            'student_id': 103,
            'activity_id': 68  # LO2.2 activity (midterm_weight=0.25)
        },
        {
            'description': 'Strong learner on low-weight LO (standard reward)',
            'state': (4, 4, 0.75, 0.90, 2, 2, 0),
            'action': {'type': 'review_quiz', 'difficulty': 'hard', 'expected_time': 20},
            'outcome': {'completed': True, 'score': 0.95, 'success': True, 'time': 15},
            'prev_state': (4, 4, 0.75, 0.85, 1, 2, 0),
            'prev_action': 'attempt_quiz',
            'student_id': 104,
            'activity_id': 92  # LO1.3 activity (midterm_weight=0.05)
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test['description']}")
        print(f"      State: {test['state']}")
        print(f"      Action: {test['action']['type']} ({test['action'].get('difficulty', 'N/A')})")
        print(f"      Outcome: score={test['outcome']['score']}, completed={test['outcome']['completed']}")
        
        reward = calc.calculate_reward(
            state=test['state'],
            action=test['action'],
            outcome=test['outcome'],
            previous_state=test.get('prev_state'),
            previous_action_type=test.get('prev_action'),
            student_id=test.get('student_id'),
            activity_id=test.get('activity_id')
        )
        
        print(f"      → Total Reward: {reward:.3f}")
        
        # Show LO deltas if present
        if 'lo_deltas' in test['outcome']:
            print(f"      → LO Deltas: {test['outcome']['lo_deltas']}")
    
    # Test 6: Explain Recommendations
    print("\n6. Explain Recommendations (Giải thích tại sao gợi ý):")
    
    # Explain recommendation for activity 68 (LO2.2, high weight)
    print("\n   Example 1: Activity 68 cho student 103 (medium learner)")
    explanation = calc.explain_recommendation(
        activity_id=68,
        student_id=103,
        cluster_id=2,
        include_alternatives=True
    )
    
    print(f"   📚 {explanation['recommendation']}")
    print(f"\n   🎯 Mục tiêu chính: {explanation['why']['target_LO']}")
    print(f"      Mô tả: {explanation['why']['lo_description']}")
    print(f"      Trình độ hiện tại: {explanation['why']['current_mastery']} (mastery)")
    print(f"      Trọng số giữa kỳ: {explanation['why']['midterm_weight']}")
    print(f"      Lợi ích dự kiến: +{explanation['why']['expected_gain']} (mastery gain)")
    print(f"      {explanation['why']['urgency']}")
    print(f"\n   💡 Chiến lược: {explanation['why']['cluster_strategy']}")
    print(f"   📊 Bằng chứng: {explanation['why']['evidence']}")
    
    if 'alternatives' in explanation:
        print(f"\n   🔄 Hoặc bạn có thể làm:")
        for alt in explanation['alternatives'][:2]:
            print(f"      - Activity {alt['activity_id']}: {alt['rationale']}")
    
    # Explain for weak learner with urgent LO
    print("\n   Example 2: Activity 56 cho student 105 (weak learner, urgent LO)")
    
    # Simulate weak mastery
    calc.lo_mastery_cache[105] = defaultdict(lambda: 0.5)
    calc.lo_mastery_cache[105]['LO1.2'] = 0.35  # Very weak on important LO
    
    explanation2 = calc.explain_recommendation(
        activity_id=56,
        student_id=105,
        cluster_id=0,  # weak cluster
        include_alternatives=False
    )
    
    print(f"   📚 {explanation2['recommendation']}")
    print(f"   🎯 Target: {explanation2['why']['target_LO']}")
    print(f"      Trình độ: {explanation2['why']['current_mastery']} | Trọng số: {explanation2['why']['midterm_weight']}")
    print(f"      {explanation2['why']['urgency']}")
    print(f"   💡 {explanation2['why']['cluster_strategy']}")
    
    print("\n" + "=" * 80)
    print("✓ RewardCalculatorV2 (with LO Mastery) test completed!")
    print("=" * 80)


if __name__ == '__main__':
    test_reward_calculator()
