"""
Models package
Contains data models for course structure, student profile, and outcomes.
"""

from .course_structure import CourseStructure, Module, Activity
from .student_profile import StudentProfile, LearningHistory
from .outcome import LearningOutcome

__all__ = [
    'CourseStructure',
    'Module',
    'Activity',
    'StudentProfile',
    'LearningHistory',
    'LearningOutcome',
]
