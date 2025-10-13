#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Profile Models
======================
Định nghĩa profile sinh viên và lịch sử học tập
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class LearningHistory:
    """
    Lịch sử học tập của sinh viên cho 1 activity
    
    Attributes:
        activity_id: ID của activity
        completed: Đã hoàn thành chưa
        grade: Điểm số (0-1), None nếu chưa có
        attempts: Số lần thử
        time_spent_minutes: Thời gian đã dùng (phút)
        first_attempt_timestamp: Timestamp lần đầu tiên
        completion_timestamp: Timestamp hoàn thành
    """
    activity_id: str
    completed: bool = False
    grade: Optional[float] = None
    attempts: int = 0
    time_spent_minutes: float = 0.0
    first_attempt_timestamp: Optional[int] = None
    completion_timestamp: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'activity_id': self.activity_id,
            'completed': self.completed,
            'grade': self.grade,
            'attempts': self.attempts,
            'time_spent_minutes': self.time_spent_minutes,
            'first_attempt_timestamp': self.first_attempt_timestamp,
            'completion_timestamp': self.completion_timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LearningHistory':
        """Create from dictionary"""
        return cls(**data)


class StudentProfile:
    """
    Profile của sinh viên
    
    Chứa thông tin về:
    - Lịch sử học tập (completed activities, grades)
    - Derived features (engagement, consistency, ...)
    - Cluster assignment (nếu có)
    """
    
    def __init__(self, 
                 student_id: str,
                 course_id: str,
                 learning_history: Optional[List[LearningHistory]] = None,
                 cluster_id: Optional[str] = None):
        """
        Initialize student profile
        
        Args:
            student_id: ID sinh viên
            course_id: ID khóa học
            learning_history: Lịch sử học tập
            cluster_id: Cluster của sinh viên (nếu có)
        """
        self.student_id = student_id
        self.course_id = course_id
        self.cluster_id = cluster_id
        
        # Learning history dictionary: activity_id -> LearningHistory
        self._history: Dict[str, LearningHistory] = {}
        if learning_history:
            for history in learning_history:
                self._history[history.activity_id] = history
    
    def add_activity_history(self, history: LearningHistory):
        """Thêm lịch sử cho 1 activity"""
        self._history[history.activity_id] = history
    
    def get_activity_history(self, activity_id: str) -> Optional[LearningHistory]:
        """Lấy lịch sử của 1 activity"""
        return self._history.get(activity_id)
    
    def get_completed_activities(self) -> Set[str]:
        """Lấy set các activity đã hoàn thành"""
        return {
            activity_id for activity_id, history in self._history.items()
            if history.completed
        }
    
    def get_grades(self) -> Dict[str, float]:
        """Lấy dictionary activity_id -> grade"""
        return {
            activity_id: history.grade
            for activity_id, history in self._history.items()
            if history.grade is not None
        }
    
    def get_average_grade(self) -> float:
        """Tính điểm trung bình"""
        grades = list(self.get_grades().values())
        return np.mean(grades) if grades else 0.0
    
    def get_completion_rate(self, total_activities: int) -> float:
        """
        Tính tỷ lệ hoàn thành
        
        Args:
            total_activities: Tổng số activities trong khóa học
        
        Returns:
            Completion rate (0-1)
        """
        if total_activities == 0:
            return 0.0
        return len(self.get_completed_activities()) / total_activities
    
    def get_engagement_score(self) -> float:
        """
        Tính engagement score dựa trên activity history
        
        Returns:
            Score (0-1)
        """
        if not self._history:
            return 0.0
        
        # Factors:
        # - Số activities đã thử
        # - Số attempts trung bình
        # - Time spent
        
        total_activities = len(self._history)
        completed_activities = len(self.get_completed_activities())
        
        # Completion ratio
        completion_ratio = completed_activities / total_activities
        
        # Average attempts (higher = more engaged but struggling)
        avg_attempts = np.mean([h.attempts for h in self._history.values()])
        attempt_score = min(avg_attempts / 3.0, 1.0)  # Normalize to [0, 1]
        
        # Engagement = weighted combination
        engagement = 0.7 * completion_ratio + 0.3 * attempt_score
        
        return np.clip(engagement, 0.0, 1.0)
    
    def get_consistency_score(self) -> float:
        """
        Tính consistency score (độ đều đặn học tập)
        
        Returns:
            Score (0-1), 1 = very consistent
        """
        timestamps = [
            h.first_attempt_timestamp
            for h in self._history.values()
            if h.first_attempt_timestamp is not None
        ]
        
        if len(timestamps) < 2:
            return 0.5  # Not enough data
        
        # Calculate time gaps
        timestamps = sorted(timestamps)
        time_gaps = np.diff(timestamps)
        
        # Consistency = 1 / (1 + coefficient_of_variation)
        mean_gap = np.mean(time_gaps)
        std_gap = np.std(time_gaps)
        
        if mean_gap == 0:
            return 0.5
        
        cv = std_gap / mean_gap
        consistency = 1.0 / (1.0 + cv)
        
        return np.clip(consistency, 0.0, 1.0)
    
    def get_activity_type_success_rates(self) -> Dict[str, float]:
        """
        Tính tỷ lệ thành công theo loại activity
        (Cần CourseStructure để biết activity types)
        
        Returns:
            Dictionary: activity_type -> success_rate
        """
        # This requires course structure context
        # Simplified version: just return pass rates
        pass_count = sum(
            1 for h in self._history.values()
            if h.grade is not None and h.grade >= 0.6
        )
        total_graded = sum(
            1 for h in self._history.values()
            if h.grade is not None
        )
        
        if total_graded == 0:
            return {}
        
        return {'overall': pass_count / total_graded}
    
    def get_time_since_last_activity(self, current_timestamp: int) -> float:
        """
        Tính thời gian từ activity gần nhất (days)
        
        Args:
            current_timestamp: Unix timestamp hiện tại
        
        Returns:
            Days since last activity
        """
        last_timestamps = [
            h.completion_timestamp or h.first_attempt_timestamp
            for h in self._history.values()
            if h.completion_timestamp or h.first_attempt_timestamp
        ]
        
        if not last_timestamps:
            return float('inf')
        
        last_timestamp = max(last_timestamps)
        days = (current_timestamp - last_timestamp) / 86400  # seconds to days
        
        return max(0.0, days)
    
    def get_feature_vector(self, course_structure, current_timestamp: Optional[int] = None) -> np.ndarray:
        """
        Tạo feature vector cho student (dùng cho state)
        
        Args:
            course_structure: CourseStructure object
            current_timestamp: Timestamp hiện tại
        
        Returns:
            Feature vector (numpy array)
        """
        total_activities = len(course_structure.activities)
        
        features = [
            self.get_average_grade(),
            self.get_completion_rate(total_activities),
            self.get_engagement_score(),
            self.get_consistency_score(),
            len(self.get_completed_activities()) / max(total_activities, 1),
        ]
        
        # Add time since last activity (if available)
        if current_timestamp:
            days_since = self.get_time_since_last_activity(current_timestamp)
            features.append(min(days_since / 7.0, 1.0))  # Normalize to weeks, cap at 1
        
        return np.array(features, dtype=np.float32)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'student_id': self.student_id,
            'course_id': self.course_id,
            'cluster_id': self.cluster_id,
            'learning_history': [h.to_dict() for h in self._history.values()],
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StudentProfile':
        """Create from dictionary"""
        learning_history = [
            LearningHistory.from_dict(h) for h in data.get('learning_history', [])
        ]
        
        return cls(
            student_id=data['student_id'],
            course_id=data['course_id'],
            learning_history=learning_history,
            cluster_id=data.get('cluster_id')
        )
    
    def __repr__(self) -> str:
        return (
            f"StudentProfile(student_id='{self.student_id}', "
            f"completed={len(self.get_completed_activities())}, "
            f"avg_grade={self.get_average_grade():.2f})"
        )
