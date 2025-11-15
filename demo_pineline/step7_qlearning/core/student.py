#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Model - Đơn giản hóa cho Q-Learning Training
====================================================
Mô phỏng học sinh học tuyến tính, realistic
"""

import numpy as np
from typing import Dict, Tuple, List
from collections import defaultdict


class Student:
    """
    Student model đơn giản cho Q-Learning
    
    Features:
    - 6D state space (cluster, module, progress, score, phase, engagement)
    - LO mastery tracking
    - Linear progression through modules
    - Cluster-specific learning behavior
    """
    
    def __init__(
        self,
        student_id: int,
        cluster: str,  # 'weak', 'medium', 'strong'
        n_modules: int = 6
    ):
        """
        Initialize student
        
        Args:
            student_id: Student ID
            cluster: 'weak', 'medium', 'strong'
            n_modules: Number of modules in course
        """
        self.id = student_id
        self.cluster = cluster
        self.n_modules = n_modules
        
        # State variables
        self.cluster_id = {'weak': 0, 'medium': 2, 'strong': 4}[cluster]
        self.module_idx = 0  # Current module (0-5)
        self.progress = 0.0  # Module progress (0-1)
        self.score = 0.5  # Average score (0-1)
        
        # Learning behavior (cluster-specific)
        self.learning_params = self._init_learning_params()
        
        # LO mastery (15 LOs)
        self.lo_mastery = defaultdict(lambda: 0.4)  # Start at 40%
        
        # Learning history
        self.action_history = []  # Recent actions for phase/engagement
        self.activity_history = []  # Track activity IDs to avoid repetition
        self.score_history = []  # Score history
        self.total_actions = 0
        
        # Session state
        self.is_finished = False
    
    def _init_learning_params(self) -> Dict:
        """Initialize cluster-specific learning parameters"""
        if self.cluster == 'weak':
            return {
                'learning_rate': 0.15,  # Slow learning
                'success_rate': 0.55,   # 55% success on activities
                'progress_speed': 0.12, # Slow progress per action
                'score_variance': 0.15  # More variance in scores
            }
        elif self.cluster == 'medium':
            return {
                'learning_rate': 0.20,
                'success_rate': 0.70,
                'progress_speed': 0.15,
                'score_variance': 0.10
            }
        else:  # strong
            return {
                'learning_rate': 0.25,
                'success_rate': 0.85,
                'progress_speed': 0.18,
                'score_variance': 0.08
            }
    
    def get_state(self) -> Tuple[int, int, float, float, int, int]:
        """
        Get current 6D state
        
        Returns:
            (cluster_id, module_idx, progress_bin, score_bin, 
             learning_phase, engagement_level)
        """
        # Bin progress and score
        progress_bin = self._bin_value(self.progress)
        score_bin = self._bin_value(self.score)
        
        # Calculate learning phase (0=pre, 1=active, 2=reflective)
        learning_phase = self._get_learning_phase()
        
        # Calculate engagement (0=low, 1=medium, 2=high)
        engagement_level = self._get_engagement_level()
        
        return (
            self.cluster_id,
            self.module_idx,
            progress_bin,
            score_bin,
            learning_phase,
            engagement_level
        )
    
    def _bin_value(self, value: float) -> float:
        """Bin value into quartiles: 0.25, 0.5, 0.75, 1.0"""
        if value <= 0.25:
            return 0.25
        elif value <= 0.5:
            return 0.5
        elif value <= 0.75:
            return 0.75
        else:
            return 1.0
    
    def _get_learning_phase(self) -> int:
        """Determine learning phase from recent actions and progress"""
        if not self.action_history:
            return 0 if self.progress < 0.3 else 1
        
        recent = self.action_history[-5:]  # Last 5 actions
        
        # Count action types
        passive = sum(1 for a in recent if a in ['view_content', 'view_assignment'])
        active = sum(1 for a in recent if a in ['attempt_quiz', 'submit_assignment'])
        reflective = sum(1 for a in recent if a in ['review_quiz', 'post_forum'])
        
        # Determine phase
        if active >= 2:
            return 1  # Active learning
        elif reflective >= 2 and self.progress > 0.6:
            return 2  # Reflective
        else:
            return 0  # Pre-learning
    
    def _get_engagement_level(self) -> int:
        """Calculate engagement from recent activity"""
        if len(self.action_history) < 3:
            return 0
        
        recent = self.action_history[-10:]
        
        # Weight by action quality
        weights = {
            'view_content': 1,
            'view_assignment': 2,
            'attempt_quiz': 4,
            'submit_quiz': 5,
            'review_quiz': 3,
            'submit_assignment': 5,
            'post_forum': 3
        }
        
        score = sum(weights.get(a, 1) for a in recent)
        
        # Map to 3 levels
        if score >= 20:
            return 2  # High
        elif score >= 10:
            return 1  # Medium
        else:
            return 0  # Low
    
    def do_action(
        self,
        action: Tuple[str, str],  # (action_type, time_context)
        activity_id: int,
        lo_mappings: Dict[int, List[str]]
    ) -> Dict:
        """
        Perform an action and update state
        
        Args:
            action: (action_type, time_context) from ActionSpace
            activity_id: Activity ID
            lo_mappings: Dict of {activity_id: [lo_ids]}
            
        Returns:
            Dict with outcome and old_mastery
        """
        action_type, time_context = action
        
        # Store old mastery
        old_mastery = dict(self.lo_mastery)
        
        # Simulate action outcome
        outcome = self._simulate_outcome(action_type, time_context)
        
        # Update state based on outcome
        self._update_state(action_type, outcome)
        
        # Update LO mastery if activity maps to LOs
        if activity_id in lo_mappings:
            self._update_lo_mastery(
                lo_ids=lo_mappings[activity_id],
                outcome=outcome
            )
        
        # Record action
        self.action_history.append(action_type)
        self.activity_history.append(activity_id)  # Track activity ID
        self.total_actions += 1
        
        # Check if module completed
        if self.progress >= 1.0:
            self._advance_module()
        
        return {
            'outcome': outcome,
            'old_mastery': old_mastery
        }
    
    def _simulate_outcome(self, action_type: str, time_context: str) -> Dict:
        """Simulate realistic action outcome"""
        params = self.learning_params
        
        # Success probability
        success = np.random.random() < params['success_rate']
        
        # Score for assessment actions
        if action_type in ['attempt_quiz', 'submit_quiz', 'submit_assignment']:
            if success:
                # Good score with variance
                base_score = 0.7 if self.cluster == 'weak' else 0.8 if self.cluster == 'medium' else 0.9
                score = base_score + np.random.uniform(-params['score_variance'], params['score_variance'])
                score = np.clip(score, 0.0, 1.0)
            else:
                # Failed attempt
                score = np.random.uniform(0.2, 0.5)
            
            completed = action_type in ['submit_quiz', 'submit_assignment']
        else:
            # Non-assessment actions: no score
            score = None
            completed = False
        
        return {
            'success': success,
            'score': score,
            'completed': completed,
            'time': np.random.uniform(5, 30)  # Time in minutes
        }
    
    def _update_state(self, action_type: str, outcome: Dict):
        """Update student state after action"""
        params = self.learning_params
        
        # Update progress
        if action_type in ['view_content', 'view_assignment']:
            progress_gain = params['progress_speed'] * 0.8
        elif action_type in ['attempt_quiz', 'submit_quiz', 'submit_assignment']:
            if outcome['success']:
                progress_gain = params['progress_speed'] * 1.2
            else:
                progress_gain = params['progress_speed'] * 0.5
        elif action_type in ['review_quiz', 'post_forum']:
            progress_gain = params['progress_speed'] * 0.6
        else:
            progress_gain = params['progress_speed']
        
        self.progress = min(1.0, self.progress + progress_gain)
        
        # Update score if available
        if outcome['score'] is not None:
            self.score_history.append(outcome['score'])
            # Rolling average (last 5 scores)
            recent_scores = self.score_history[-5:]
            self.score = np.mean(recent_scores)
    
    def _update_lo_mastery(self, lo_ids: List[str], outcome: Dict):
        """Update LO mastery using exponential moving average"""
        params = self.learning_params
        alpha = params['learning_rate']
        
        # Target mastery from outcome
        if outcome['score'] is not None:
            target = outcome['score']
        elif outcome['success']:
            target = 0.75
        else:
            target = 0.45
        
        # Update each LO
        for lo_id in lo_ids:
            old_mastery = self.lo_mastery[lo_id]
            # EMA: new = old + α * (target - old)
            new_mastery = old_mastery + alpha * (target - old_mastery)
            self.lo_mastery[lo_id] = np.clip(new_mastery, 0.0, 1.0)
    
    def _advance_module(self):
        """Advance to next module"""
        self.module_idx += 1
        self.progress = 0.0
        
        if self.module_idx >= self.n_modules:
            self.is_finished = True
            self.module_idx = self.n_modules - 1  # Stay at last module
    
    def reset(self):
        """Reset student to initial state"""
        self.module_idx = 0
        self.progress = 0.0
        self.score = 0.5
        self.lo_mastery = defaultdict(lambda: 0.4)
        self.action_history = []
        self.activity_history = []  # Reset activity history
        self.score_history = []
        self.total_actions = 0
        self.is_finished = False
    
    def get_statistics(self) -> Dict:
        """Get student statistics"""
        return {
            'id': self.id,
            'cluster': self.cluster,
            'module_idx': self.module_idx,
            'progress': self.progress,
            'score': self.score,
            'total_actions': self.total_actions,
            'avg_lo_mastery': np.mean(list(self.lo_mastery.values())),
            'is_finished': self.is_finished
        }
