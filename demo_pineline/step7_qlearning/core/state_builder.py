#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract State Builder
======================
Xây dựng state representation từ student profile và activity context
"""

import numpy as np
from typing import Optional, Dict, List
from abc import ABC, abstractmethod

from models.course_structure import CourseStructure, Activity, ActivityType
from models.student_profile import StudentProfile


class AbstractStateBuilder(ABC):
    """
    Abstract base class cho State Builder
    
    State = Vector mô tả:
    - Student profile (knowledge, engagement, ...)
    - Current position in course
    - Target activity context (nếu có)
    
    ⚠️ KEY DESIGN: State KHÔNG chứa activity IDs cụ thể
    → Dùng abstract features → Generalize across courses
    """
    
    def __init__(self, course_structure: CourseStructure):
        """
        Args:
            course_structure: CourseStructure object
        """
        self.course_structure = course_structure
    
    @abstractmethod
    def build_state(self, 
                    student_profile: StudentProfile,
                    target_activity_id: Optional[str] = None,
                    current_timestamp: Optional[int] = None) -> np.ndarray:
        """
        Xây dựng state vector
        
        Args:
            student_profile: StudentProfile object
            target_activity_id: ID của activity đang xem xét (for context)
            current_timestamp: Timestamp hiện tại
        
        Returns:
            State vector (numpy array)
        """
        pass
    
    @abstractmethod
    def get_state_dimension(self) -> int:
        """
        Lấy số chiều của state vector
        
        Returns:
            Dimension
        """
        pass


class DefaultStateBuilder(AbstractStateBuilder):
    """
    Default implementation của State Builder
    
    State components:
    1. Student profile features (5-6 features)
    2. Activity context features (8-10 features)
    3. Optional: Cluster features (nếu có)
    """
    
    def __init__(self, course_structure: CourseStructure, use_cluster: bool = False):
        """
        Args:
            course_structure: CourseStructure object
            use_cluster: Có dùng cluster info không
        """
        super().__init__(course_structure)
        self.use_cluster = use_cluster
        
        # Cache activity type encoding
        self._activity_types = [t.value for t in ActivityType]
    
    def build_state(self,
                    student_profile: StudentProfile,
                    target_activity_id: Optional[str] = None,
                    current_timestamp: Optional[int] = None) -> np.ndarray:
        """
        Build state vector
        
        State structure:
        [student_features | activity_features | optional_cluster]
        """
        # 1. Student profile features
        student_features = self._extract_student_features(
            student_profile, current_timestamp
        )
        
        # 2. Activity context features
        if target_activity_id:
            activity_features = self._extract_activity_features(
                target_activity_id, student_profile
            )
        else:
            # No target activity → pad with zeros
            activity_features = np.zeros(self._get_activity_feature_dim())
        
        # 3. Combine
        state = np.concatenate([student_features, activity_features])
        
        # 4. Optional: Add cluster one-hot
        if self.use_cluster and student_profile.cluster_id:
            cluster_features = self._extract_cluster_features(student_profile)
            state = np.concatenate([state, cluster_features])
        
        return state.astype(np.float32)
    
    def _extract_student_features(self, 
                                  student_profile: StudentProfile,
                                  current_timestamp: Optional[int]) -> np.ndarray:
        """
        Extract student profile features
        
        Features:
        - avg_grade
        - completion_rate
        - engagement_score
        - consistency_score
        - progress (normalized completed count)
        - time_since_last_activity (optional)
        """
        total_activities = len(self.course_structure.activities)
        
        features = [
            student_profile.get_average_grade(),
            student_profile.get_completion_rate(total_activities),
            student_profile.get_engagement_score(),
            student_profile.get_consistency_score(),
            len(student_profile.get_completed_activities()) / max(total_activities, 1),
        ]
        
        # Add time since last activity
        if current_timestamp:
            days_since = student_profile.get_time_since_last_activity(current_timestamp)
            features.append(min(days_since / 7.0, 1.0))  # Normalize to weeks
        else:
            features.append(0.0)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_activity_features(self,
                                   activity_id: str,
                                   student_profile: StudentProfile) -> np.ndarray:
        """
        Extract activity context features
        
        Features:
        - difficulty
        - estimated_time (normalized)
        - prerequisite_met (binary)
        - n_prerequisites (normalized)
        - is_optional (binary)
        - activity_type (one-hot encoded)
        - module_position (normalized)
        - activity_depth (normalized)
        - similar_activity_success_rate
        """
        activity = self.course_structure.activities[activity_id]
        completed = student_profile.get_completed_activities()
        
        # Basic features
        difficulty = activity.difficulty
        estimated_time = min(activity.estimated_minutes / 120.0, 1.0)  # Normalize, cap at 2h
        
        # Prerequisites
        prereqs = set(activity.prerequisites)
        prerequisite_met = 1.0 if prereqs.issubset(completed) else 0.0
        n_prerequisites = min(len(prereqs) / 5.0, 1.0)  # Normalize, cap at 5
        
        # Optional
        is_optional = 1.0 if activity.is_optional else 0.0
        
        # Activity type (one-hot)
        activity_type_vector = self._encode_activity_type(activity.activity_type)
        
        # Position in course
        module = self.course_structure.modules[activity.module_id]
        total_modules = len(self.course_structure.modules)
        module_position = module.order / max(total_modules, 1)
        
        # Activity depth in prerequisite graph
        depth = self.course_structure.get_activity_depth(activity_id)
        max_depth = max(
            self.course_structure.get_activity_depth(aid)
            for aid in self.course_structure.activities.keys()
        )
        activity_depth = depth / max(max_depth, 1) if max_depth > 0 else 0.0
        
        # Success rate with similar activities
        similar_success = self._get_similar_activity_success_rate(
            activity, student_profile
        )
        
        # Combine
        features = [
            difficulty,
            estimated_time,
            prerequisite_met,
            n_prerequisites,
            is_optional,
        ]
        features.extend(activity_type_vector)
        features.extend([
            module_position,
            activity_depth,
            similar_success,
        ])
        
        return np.array(features, dtype=np.float32)
    
    def _encode_activity_type(self, activity_type: ActivityType) -> List[float]:
        """One-hot encode activity type"""
        encoding = [0.0] * len(self._activity_types)
        try:
            idx = self._activity_types.index(activity_type.value)
            encoding[idx] = 1.0
        except ValueError:
            pass  # Unknown type → all zeros
        return encoding
    
    def _get_similar_activity_success_rate(self,
                                          activity: Activity,
                                          student_profile: StudentProfile) -> float:
        """
        Tính success rate với các activities cùng type
        
        Args:
            activity: Target activity
            student_profile: Student profile
        
        Returns:
            Success rate (0-1)
        """
        grades = student_profile.get_grades()
        
        # Find activities with same type that student has completed
        similar_grades = []
        for act_id, grade in grades.items():
            if act_id in self.course_structure.activities:
                act = self.course_structure.activities[act_id]
                if act.activity_type == activity.activity_type:
                    similar_grades.append(grade)
        
        if not similar_grades:
            return 0.5  # No data → neutral
        
        return np.mean(similar_grades)
    
    def _extract_cluster_features(self, student_profile: StudentProfile) -> np.ndarray:
        """
        Extract cluster features (one-hot)
        
        Assumes cluster_id in format 'cluster_0', 'cluster_1', etc.
        """
        # Simple: Assume 2 clusters
        if student_profile.cluster_id == 'cluster_0':
            return np.array([1.0, 0.0], dtype=np.float32)
        elif student_profile.cluster_id == 'cluster_1':
            return np.array([0.0, 1.0], dtype=np.float32)
        else:
            return np.array([0.0, 0.0], dtype=np.float32)  # Unknown
    
    def _get_activity_feature_dim(self) -> int:
        """Calculate activity feature dimension"""
        # 5 basic + len(activity_types) one-hot + 3 positional
        return 5 + len(self._activity_types) + 3
    
    def get_state_dimension(self) -> int:
        """Get total state dimension"""
        student_dim = 6  # 5 basic + 1 time_since
        activity_dim = self._get_activity_feature_dim()
        cluster_dim = 2 if self.use_cluster else 0
        
        return student_dim + activity_dim + cluster_dim
    
    def hash_state(self, state: np.ndarray, decimals: int = 2) -> tuple:
        """
        Hash state vector thành tuple (để dùng làm key cho Q-table)
        
        Args:
            state: State vector
            decimals: Số chữ số thập phân để round
        
        Returns:
            Tuple (hashable)
        """
        return tuple(np.round(state, decimals=decimals))
