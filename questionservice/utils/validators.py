#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validators
==========
Validation utilities for questions
"""

from typing import Dict, List, Optional, Tuple


def validate_question_type(question_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate question type
    
    Args:
        question_type: Question type to validate
        
    Returns:
        (is_valid, error_message)
    """
    valid_types = ['multichoice', 'truefalse', 'shortanswer', 'essay']
    
    if question_type not in valid_types:
        return False, f"Invalid question type. Must be one of: {', '.join(valid_types)}"
    
    return True, None


def validate_difficulty(difficulty: str) -> Tuple[bool, Optional[str]]:
    """
    Validate difficulty level
    
    Args:
        difficulty: Difficulty level to validate
        
    Returns:
        (is_valid, error_message)
    """
    valid_difficulties = ['easy', 'medium', 'hard']
    
    if difficulty not in valid_difficulties:
        return False, f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}"
    
    return True, None


def validate_answer_fraction(fraction: int) -> Tuple[bool, Optional[str]]:
    """
    Validate answer fraction
    
    Args:
        fraction: Answer fraction to validate
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(fraction, int):
        return False, "Fraction must be an integer"
    
    if fraction not in [0, 100]:
        return False, "Fraction must be 0 or 100"
    
    return True, None


def validate_question_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate question data dictionary
    
    Args:
        data: Question data to validate
        
    Returns:
        (is_valid, error_message)
    """
    # Required fields
    required_fields = ['name', 'question_type', 'question_text', 'difficulty']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not data[field]:
            return False, f"Field '{field}' cannot be empty"
    
    # Validate question type
    is_valid, error = validate_question_type(data['question_type'])
    if not is_valid:
        return False, error
    
    # Validate difficulty
    is_valid, error = validate_difficulty(data['difficulty'])
    if not is_valid:
        return False, error
    
    # Validate answers for multiple choice
    if data['question_type'] == 'multichoice':
        if 'answers' not in data or not data['answers']:
            return False, "Multiple choice questions must have answers"
        
        if len(data['answers']) < 2:
            return False, "Multiple choice questions must have at least 2 answers"
        
        # Validate each answer
        for idx, answer in enumerate(data['answers']):
            if 'text' not in answer or not answer['text']:
                return False, f"Answer {idx + 1}: text is required"
            
            if 'fraction' not in answer:
                return False, f"Answer {idx + 1}: fraction is required"
            
            is_valid, error = validate_answer_fraction(answer['fraction'])
            if not is_valid:
                return False, f"Answer {idx + 1}: {error}"
        
        # Check for at least one correct answer
        correct_answers = [a for a in data['answers'] if a['fraction'] == 100]
        if not correct_answers:
            return False, "Multiple choice questions must have at least one correct answer"
    
    return True, None


def validate_questions_batch(questions_data: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate batch of questions
    
    Args:
        questions_data: List of question data dictionaries
        
    Returns:
        (is_valid, list_of_errors)
    """
    if not questions_data:
        return False, ["No questions provided"]
    
    if not isinstance(questions_data, list):
        return False, ["Questions data must be a list"]
    
    errors = []
    
    for idx, q_data in enumerate(questions_data):
        is_valid, error = validate_question_data(q_data)
        if not is_valid:
            errors.append(f"Question {idx + 1}: {error}")
    
    return len(errors) == 0, errors
