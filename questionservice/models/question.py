#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Model
==============
Data model for quiz questions
"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Answer:
    """Answer model for multiple choice questions"""
    text: str
    fraction: int  # 100 for correct, 0 for incorrect
    feedback: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Answer':
        """Create Answer from dictionary"""
        return cls(
            text=data.get('text', ''),
            fraction=data.get('fraction', 0),
            feedback=data.get('feedback', '')
        )


@dataclass
class Question:
    """Question model"""
    name: str
    question_type: str
    question_text: str
    difficulty: str  # easy, medium, hard
    answers: List[Answer] = field(default_factory=list)
    
    # Optional fields
    question_id: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Moodle specific settings
    shuffle_answers: bool = False
    single_answer: bool = True
    answer_numbering: str = "abc"  # abc, ABCD, 123, iii
    
    def __post_init__(self):
        """Post initialization"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        
        # Convert answer dicts to Answer objects if needed
        if self.answers and isinstance(self.answers[0], dict):
            self.answers = [Answer.from_dict(a) for a in self.answers]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'name': self.name,
            'question_type': self.question_type,
            'question_text': self.question_text,
            'difficulty': self.difficulty,
            'answers': [a.to_dict() for a in self.answers],
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'shuffle_answers': self.shuffle_answers,
            'single_answer': self.single_answer,
            'answer_numbering': self.answer_numbering
        }
        
        if self.question_id:
            data['_id'] = self.question_id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Question':
        """Create Question from dictionary"""
        answers = [Answer.from_dict(a) for a in data.get('answers', [])]
        
        return cls(
            question_id=str(data.get('_id', '')),
            name=data.get('name', ''),
            question_type=data.get('question_type', 'multichoice'),
            question_text=data.get('question_text', ''),
            difficulty=data.get('difficulty', 'medium'),
            answers=answers,
            category=data.get('category'),
            tags=data.get('tags', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            shuffle_answers=data.get('shuffle_answers', False),
            single_answer=data.get('single_answer', True),
            answer_numbering=data.get('answer_numbering', 'abc')
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate question data
        Returns: (is_valid, error_message)
        """
        if not self.name:
            return False, "Question name is required"
        
        if not self.question_text:
            return False, "Question text is required"
        
        if self.question_type not in ['multichoice', 'truefalse', 'shortanswer', 'essay']:
            return False, f"Invalid question type: {self.question_type}"
        
        if self.difficulty not in ['easy', 'medium', 'hard']:
            return False, f"Invalid difficulty: {self.difficulty}"
        
        # Validate answers for multiple choice
        if self.question_type == 'multichoice':
            if not self.answers:
                return False, "Multiple choice questions must have answers"
            
            if len(self.answers) < 2:
                return False, "Multiple choice questions must have at least 2 answers"
            
            # Check if there's at least one correct answer
            correct_answers = [a for a in self.answers if a.fraction == 100]
            if not correct_answers:
                return False, "Multiple choice questions must have at least one correct answer"
        
        return True, None


@dataclass
class QuestionBank:
    """Question Bank model"""
    name: str
    description: str = ""
    bank_id: Optional[str] = None
    questions: List[str] = field(default_factory=list)  # List of question IDs
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post initialization"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'name': self.name,
            'description': self.description,
            'questions': self.questions,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self.bank_id:
            data['_id'] = self.bank_id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestionBank':
        """Create QuestionBank from dictionary"""
        return cls(
            bank_id=str(data.get('_id', '')),
            name=data.get('name', ''),
            description=data.get('description', ''),
            questions=data.get('questions', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
