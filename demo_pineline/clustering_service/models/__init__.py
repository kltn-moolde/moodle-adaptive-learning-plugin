"""
MongoDB Models
==============
Database models for clustering service
"""

from .course_clusters import CourseClusterModel
from .user_cluster_history import UserClusterHistoryModel

__all__ = ['CourseClusterModel', 'UserClusterHistoryModel']
