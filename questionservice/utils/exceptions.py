#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Exceptions
=================
Custom exception classes for Question Service
"""


class QuestionServiceError(Exception):
    """Base exception for Question Service"""
    pass


class ValidationError(QuestionServiceError):
    """Validation error"""
    pass


class QuestionNotFoundError(QuestionServiceError):
    """Question not found error"""
    pass


class QuestionBankNotFoundError(QuestionServiceError):
    """Question bank not found error"""
    pass


class XMLConversionError(QuestionServiceError):
    """XML conversion error"""
    pass


class DatabaseError(QuestionServiceError):
    """Database error"""
    pass


class AIGenerationError(QuestionServiceError):
    """AI generation error"""
    pass


class MoodleAPIError(QuestionServiceError):
    """Moodle API error"""
    pass


class MoodleConnectionError(QuestionServiceError):
    """Moodle connection error"""
    pass


class MoodleImportError(QuestionServiceError):
    """Moodle import error"""
    pass
