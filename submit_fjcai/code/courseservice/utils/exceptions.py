#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exception Classes for Course Service
=====================================
Custom exceptions with proper error handling
"""

from typing import Optional, Dict, Any


class CourseServiceError(Exception):
    """Base exception for course service"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class MoodleAPIError(CourseServiceError):
    """Moodle API related errors"""
    pass


class DatabaseError(CourseServiceError):
    """Database operation errors"""
    pass


class ValidationError(CourseServiceError):
    """Data validation errors"""
    pass


class ConversionError(CourseServiceError):
    """Structure conversion errors"""
    pass


class NotFoundError(CourseServiceError):
    """Resource not found errors"""
    pass


class ConfigurationError(CourseServiceError):
    """Configuration errors"""
    pass
