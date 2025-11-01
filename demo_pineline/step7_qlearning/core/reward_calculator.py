#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reward Calculator
=================
Tính reward động dựa trên cluster profiles và action outcomes
"""

import json
import numpy as np
from typing import Dict, Optional
from .action_space import LearningAction


class RewardCalculator:
    """
    Reward Calculator cho Q-Learning
    
    Reward được tính dựa trên:
    1. Cluster profile (học viên thuộc nhóm nào)
    2. Action type và outcome
    3. Student performance metrics
    
    Reward Strategy tự động phân loại cluster theo performance metrics:
    - Cluster yếu: mean_module_grade thấp → Reward cao khi hoàn thành bài
    - Cluster trung bình: mean_module_grade trung bình → Reward cân bằng
    - Cluster mạnh: mean_module_grade cao → Reward khi học nhanh + score cao
    """
    
    def __init__(self, cluster_profiles_path: str):
        """
        Initialize reward calculator
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json
        """
        self.cluster_profiles_path = cluster_profiles_path
        self.cluster_profiles = {}
        self.n_clusters = 0
        self.cluster_performance_levels = {}  # Map cluster_id -> 'weak'/'medium'/'strong'
        
        self._load_profiles()
        self._classify_clusters()
    
    def _load_profiles(self):
        """Load cluster profiles"""
        with open(self.cluster_profiles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.n_clusters = data.get('n_clusters', 6)
        self.cluster_profiles = data.get('cluster_stats', {})
    
    def _classify_clusters(self):
        """
        Tự động phân loại clusters thành weak/medium/strong
        dựa trên mean_module_grade trong feature_means
        """
        # Extract mean_module_grade for all clusters
        grade_data = []
        for cluster_id in range(self.n_clusters):
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
        
        print("\n=== AUTO-CLASSIFY CLUSTERS ===")
        for i, (cluster_id, grade, name) in enumerate(grade_data):
            if i < weak_threshold:
                level = 'weak'
            elif i < strong_threshold:
                level = 'medium'
            else:
                level = 'strong'
            
            self.cluster_performance_levels[cluster_id] = level
            
            print(f"Cluster {cluster_id}: grade={grade:.3f} → {level:8s} | {name}")
    
    def get_cluster_level(self, cluster_id: int) -> str:
        """
        Get performance level of a cluster
        
        Args:
            cluster_id: ID của cluster
        
        Returns:
            'weak', 'medium', or 'strong'
        """
        return self.cluster_performance_levels.get(cluster_id, 'medium')
    
    def calculate_reward(
        self,
        cluster_id: int,
        action: LearningAction,
        outcome: Dict,
        state: np.ndarray
    ) -> float:
        """
        Tính reward cho một action
        
        Args:
            cluster_id: ID của cluster (0-5)
            action: Learning action được thực hiện
            outcome: Kết quả của action (completed, score, time_spent, etc.)
            state: Current state của student
        
        Returns:
            Reward value (float)
        """
        # Base reward
        reward = 0.0
        
        # Get cluster profile
        profile = self.cluster_profiles.get(str(cluster_id), {})
        
        # Extract outcome metrics
        completed = outcome.get('completed', False)
        score = outcome.get('score', 0.0)  # 0-1
        time_spent = outcome.get('time_spent', 0)  # minutes
        attempts = outcome.get('attempts', 1)
        
        # Extract state metrics
        knowledge_level = state[0] if len(state) > 0 else 0.5
        engagement_level = state[1] if len(state) > 1 else 0.5
        
        # === REWARD CALCULATION ===
        
        # 1. Completion reward
        if completed:
            reward += 1.0
        
        # 2. Score-based reward
        if action.purpose == 'assessment':
            reward += score * 2.0  # Double weight for assessments
        else:
            reward += score
        
        # 3. Cluster-specific bonuses
        reward += self._cluster_bonus(
            cluster_id, action, score, knowledge_level, time_spent, attempts
        )
        
        # 4. Difficulty bonus
        reward += self._difficulty_bonus(action, score, knowledge_level)
        
        # 5. Engagement bonus
        if engagement_level > 0.7:
            reward += 0.3
        
        # 6. Penalty for too many attempts
        if attempts > 3:
            reward -= 0.2 * (attempts - 3)
        
        # 7. Time efficiency bonus (complete nhanh)
        if time_spent > 0 and time_spent < 30:  # < 30 phút
            reward += 0.2
        
        # Clip reward to reasonable range
        reward = np.clip(reward, -2.0, 5.0)
        
        return reward
    
    def _cluster_bonus(
        self,
        cluster_id: int,
        action: LearningAction,
        score: float,
        knowledge_level: float,
        time_spent: int,
        attempts: int
    ) -> float:
        """
        Cluster-specific reward bonus (TỰ ĐỘNG phân loại)
        
        Strategy dựa trên performance level:
        - Weak: Reward cao khi hoàn thành quiz/assign
        - Medium: Reward cân bằng
        - Strong: Reward khi học nhanh, score cao
        """
        bonus = 0.0
        
        # Get cluster level from auto-classification
        level = self.get_cluster_level(cluster_id)
        
        # Weak clusters
        if level == 'weak':
            # High reward for completing assessments
            if action.purpose == 'assessment' and score > 0.5:
                bonus += 0.8
            
            # Reward for reviewing content
            if action.type in ['resource', 'page', 'hvp']:
                bonus += 0.3
        
        # Medium clusters
        elif level == 'medium':
            # Balanced rewards
            if action.purpose == 'assessment' and score > 0.7:
                bonus += 0.5
            
            if knowledge_level > 0.6:
                bonus += 0.2
        
        # Strong clusters
        elif level == 'strong':
            # Reward for high scores
            if score > 0.8:
                bonus += 0.6
            
            # Reward for speed (few attempts)
            if attempts == 1 and score > 0.7:
                bonus += 0.5
            
            # Reward for completing hard activities
            if action.difficulty == 'hard' and score > 0.7:
                bonus += 0.7
        
        return bonus
    
    def _difficulty_bonus(
        self,
        action: LearningAction,
        score: float,
        knowledge_level: float
    ) -> float:
        """
        Bonus dựa trên độ khó và knowledge level
        
        Logic:
        - Easy activities: Small bonus
        - Medium activities: Moderate bonus
        - Hard activities: High bonus if completed well
        """
        bonus = 0.0
        
        if action.difficulty == 'easy':
            bonus = 0.1 * score
        elif action.difficulty == 'medium':
            bonus = 0.3 * score
        elif action.difficulty == 'hard':
            # Higher bonus for hard activities
            bonus = 0.5 * score
            
            # Extra bonus if knowledge level is low (struggle student completing hard)
            if knowledge_level < 0.5 and score > 0.6:
                bonus += 0.4
        
        return bonus
    
    def get_cluster_count(self) -> int:
        """Get number of clusters"""
        return self.n_clusters


# Example usage
if __name__ == '__main__':
    import os
    from .action_space import ActionSpace, LearningAction
    
    # Test reward calculator
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    profiles_path = os.path.join(data_dir, 'cluster_profiles.json')
    
    calculator = RewardCalculator(profiles_path)
    
    print("=" * 70)
    print("REWARD CALCULATOR TEST")
    print("=" * 70)
    
    # Sample action
    action = LearningAction(
        id=48,
        name="Bài kiểm tra cuối kỳ",
        type='quiz',
        section='General',
        purpose='assessment',
        difficulty='hard'
    )
    
    # Sample state (12 dims from state_builder)
    state = np.array([0.4, 0.6, 0.5, 0.3, 0.4, 0.5, 0.7, 0.2, 0.5, 0.6, 0.4, 0.7])
    
    # Test different clusters
    print("\nReward for different clusters:")
    print("-" * 70)
    
    for cluster_id in range(6):
        # Test different outcomes
        outcomes = [
            {'completed': True, 'score': 0.9, 'time_spent': 20, 'attempts': 1},
            {'completed': True, 'score': 0.5, 'time_spent': 45, 'attempts': 3},
            {'completed': False, 'score': 0.3, 'time_spent': 60, 'attempts': 5}
        ]
        
        print(f"\nCluster {cluster_id}:")
        for i, outcome in enumerate(outcomes):
            reward = calculator.calculate_reward(cluster_id, action, outcome, state)
            print(f"  Outcome {i+1}: score={outcome['score']:.1f}, "
                  f"attempts={outcome['attempts']} → Reward={reward:.2f}")
