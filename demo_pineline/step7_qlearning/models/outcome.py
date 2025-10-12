#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Outcome Models
=======================
Định nghĩa kết quả học tập sau khi hoàn thành activity
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class LearningOutcome:
    """
    Kết quả học tập sau khi làm 1 activity
    
    Attributes:
        activity_id: ID của activity
        completed: Hoàn thành hay không
        grade: Điểm số (0-1), None nếu không có grade
        time_spent_minutes: Thời gian đã dùng
        attempts: Số lần thử
        passed: Có pass không (grade >= passing_grade)
    """
    activity_id: str
    completed: bool
    grade: Optional[float] = None
    time_spent_minutes: float = 0.0
    attempts: int = 1
    passed: bool = False
    
    def __post_init__(self):
        """Validate data"""
        if self.grade is not None and not (0 <= self.grade <= 1):
            raise ValueError(f"Grade must be in [0, 1], got {self.grade}")
        if self.time_spent_minutes < 0:
            raise ValueError(f"Time spent must be non-negative, got {self.time_spent_minutes}")
        if self.attempts < 0:
            raise ValueError(f"Attempts must be non-negative, got {self.attempts}")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'activity_id': self.activity_id,
            'completed': self.completed,
            'grade': self.grade,
            'time_spent_minutes': self.time_spent_minutes,
            'attempts': self.attempts,
            'passed': self.passed,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LearningOutcome':
        """Create from dictionary"""
        return cls(**data)
    
    def __repr__(self) -> str:
        grade_str = f"{self.grade:.2f}" if self.grade is not None else "N/A"
        return (
            f"LearningOutcome(activity='{self.activity_id}', "
            f"completed={self.completed}, grade={grade_str}, "
            f"passed={self.passed})"
        )
