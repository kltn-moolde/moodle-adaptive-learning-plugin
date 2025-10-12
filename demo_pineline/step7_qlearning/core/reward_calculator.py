#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reward Calculator
=================
Tính reward dựa trên learning outcome
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Optional

from models.course_structure import CourseStructure, Activity
from models.student_profile import StudentProfile
from models.outcome import LearningOutcome


class RewardCalculator(ABC):
    """
    Abstract base class cho Reward Calculator
    """
    
    def __init__(self, course_structure: CourseStructure):
        """
        Args:
            course_structure: CourseStructure object
        """
        self.course_structure = course_structure
    
    @abstractmethod
    def calculate_reward(self,
                        student_profile: StudentProfile,
                        action_id: str,
                        outcome: LearningOutcome) -> float:
        """
        Tính reward
        
        Args:
            student_profile: Student profile TRƯỚC khi làm activity
            action_id: Activity ID đã recommend
            outcome: Learning outcome
        
        Returns:
            Reward (float)
        """
        pass


class DefaultRewardCalculator(RewardCalculator):
    """
    Default implementation của Reward Calculator
    
    Reward components:
    1. Completion reward (+0.5 if completed)
    2. Grade reward (dựa trên grade và difficulty)
    3. Difficulty appropriateness (phù hợp với student level)
    4. Time efficiency
    5. Attempt penalty (nhiều attempts → struggling)
    """
    
    def __init__(self,
                 course_structure: CourseStructure,
                 cluster_benchmarks: Optional[Dict] = None):
        """
        Args:
            course_structure: CourseStructure object
            cluster_benchmarks: Cluster statistics (từ cluster_full_statistics.json)
                               Dùng để so sánh với cluster tốt
        """
        super().__init__(course_structure)
        self.cluster_benchmarks = cluster_benchmarks or {}
    
    def calculate_reward(self,
                        student_profile: StudentProfile,
                        action_id: str,
                        outcome: LearningOutcome) -> float:
        """
        Calculate reward
        
        Reward range: [-1, 1]
        """
        reward = 0.0
        
        activity = self.course_structure.activities[action_id]
        
        # 1. Completion reward
        if outcome.completed:
            reward += 0.5
        else:
            reward -= 0.5  # Heavy penalty for not completing
        
        # 2. Grade reward
        if outcome.grade is not None:
            reward += self._calculate_grade_reward(outcome.grade, activity)
        
        # 3. Difficulty appropriateness
        reward += self._calculate_difficulty_reward(
            activity, student_profile, outcome
        )
        
        # 4. Time efficiency
        reward += self._calculate_time_reward(activity, outcome)
        
        # 5. Attempt penalty
        reward += self._calculate_attempt_reward(outcome)
        
        # 6. Progress toward cluster_0 (if benchmarks available)
        if self.cluster_benchmarks:
            reward += self._calculate_cluster_reward(outcome, student_profile)
        
        # Clip to [-1, 1]
        return np.clip(reward, -1.0, 1.0)
    
    def _calculate_grade_reward(self, grade: float, activity: Activity) -> float:
        """
        Grade reward (max +0.3)
        
        - Excellent (>= 0.8): +0.3
        - Good (>= 0.6): +0.1
        - Pass (>= passing_grade): +0.05
        - Fail: -0.2
        """
        if grade >= 0.8:
            return 0.3
        elif grade >= 0.6:
            return 0.1
        elif grade >= activity.passing_grade:
            return 0.05
        else:
            return -0.2
    
    def _calculate_difficulty_reward(self,
                                    activity: Activity,
                                    student_profile: StudentProfile,
                                    outcome: LearningOutcome) -> float:
        """
        Difficulty appropriateness reward (max +0.2)
        
        Reward for recommending activity với độ khó phù hợp
        """
        student_level = student_profile.get_average_grade()
        difficulty_gap = abs(activity.difficulty - student_level)
        
        if difficulty_gap < 0.1:
            return 0.2  # Perfect match
        elif difficulty_gap < 0.2:
            return 0.1  # Good match
        elif difficulty_gap < 0.3:
            return 0.0  # OK
        else:
            # Too easy or too hard
            if activity.difficulty < student_level - 0.3:
                return -0.05  # Too easy (waste of time)
            else:
                return -0.1  # Too hard (likely to fail)
    
    def _calculate_time_reward(self, activity: Activity, outcome: LearningOutcome) -> float:
        """
        Time efficiency reward (max +0.1)
        
        Reward if time spent is reasonable
        """
        if outcome.time_spent_minutes <= 0:
            return 0.0
        
        estimated = activity.estimated_minutes
        actual = outcome.time_spent_minutes
        
        ratio = actual / estimated
        
        if 0.8 <= ratio <= 1.2:
            return 0.1  # Efficient
        elif 0.5 <= ratio <= 1.5:
            return 0.05  # OK
        elif ratio > 2.0:
            return -0.1  # Took too long (maybe too hard)
        else:
            return 0.0
    
    def _calculate_attempt_reward(self, outcome: LearningOutcome) -> float:
        """
        Attempt penalty (max -0.1)
        
        Nhiều attempts → struggling → penalty
        """
        if outcome.attempts <= 1:
            return 0.0
        elif outcome.attempts <= 2:
            return -0.05
        else:
            return -0.1
    
    def _calculate_cluster_reward(self,
                                  outcome: LearningOutcome,
                                  student_profile: StudentProfile) -> float:
        """
        Reward for progressing toward "good" cluster (cluster_0)
        
        So sánh grade với cluster_0 benchmark
        """
        if outcome.grade is None:
            return 0.0
        
        # Get cluster_0 benchmark (if available)
        cluster_0_stats = self.cluster_benchmarks.get('cluster_0', {})
        mean_grade = cluster_0_stats.get('feature_statistics', {}).get(
            'mean_module_grade', {}
        ).get('mean', 0.7)
        
        # Compare
        if outcome.grade >= mean_grade:
            return 0.1  # At or above cluster_0 level
        elif outcome.grade >= mean_grade * 0.8:
            return 0.05  # Close to cluster_0
        else:
            return -0.05  # Below cluster_0
