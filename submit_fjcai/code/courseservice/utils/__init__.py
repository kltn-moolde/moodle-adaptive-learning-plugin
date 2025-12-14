#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils Module
============
Shared utilities for Course Service
"""

from .logger import setup_logger, log_request, log_execution_time
from .exceptions import (
    CourseServiceError,
    MoodleAPIError,
    DatabaseError,
    ValidationError,
    NotFoundError,
    ConversionError,
    ConfigurationError
)
from .moodle_converter import (
    MoodleStructureConverter,
    HierarchyNode,
    NodeType,
    convert_moodle_structure
)

__all__ = [
    # Logger
    'setup_logger',
    'log_request',
    'log_execution_time',
    
    # Exceptions
    'CourseServiceError',
    'MoodleAPIError',
    'DatabaseError',
    'ValidationError',
    'NotFoundError',
    'ConversionError',
    'ConfigurationError',
    
    # Converter
    'MoodleStructureConverter',
    'HierarchyNode',
    'NodeType',
    'convert_moodle_structure',
]
