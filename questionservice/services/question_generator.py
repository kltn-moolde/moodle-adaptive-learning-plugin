#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Generator Service
===========================
Service for generating and managing questions
"""

from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId

from database import mongo
from models.question import Question, QuestionBank
from utils.logger import setup_logger
from utils.exceptions import QuestionNotFoundError, ValidationError

logger = setup_logger('question_generator')


class QuestionGenerator:
    """Service for generating and managing questions"""
    
    @staticmethod
    def create_question(question_data: Dict) -> Question:
        """
        Create a new question
        
        Args:
            question_data: Question data dictionary
            
        Returns:
            Created Question object
        """
        try:
            # Create Question object
            question = Question.from_dict(question_data)
            
            # Validate
            is_valid, error_msg = question.validate()
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Save to database
            question.created_at = datetime.utcnow()
            question.updated_at = datetime.utcnow()
            
            result = mongo.db.questions.insert_one(question.to_dict())
            question.question_id = str(result.inserted_id)
            
            logger.info(f"✓ Created question: {question.question_id}")
            return question
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"✗ Failed to create question: {str(e)}")
            raise
    
    @staticmethod
    def create_questions_batch(questions_data: List[Dict]) -> List[Question]:
        """
        Create multiple questions at once
        
        Args:
            questions_data: List of question data dictionaries
            
        Returns:
            List of created Question objects
        """
        created_questions = []
        errors = []
        
        for idx, q_data in enumerate(questions_data):
            try:
                question = QuestionGenerator.create_question(q_data)
                created_questions.append(question)
            except Exception as e:
                errors.append(f"Question {idx + 1}: {str(e)}")
                logger.warning(f"Failed to create question {idx + 1}: {str(e)}")
        
        if errors:
            logger.warning(f"Created {len(created_questions)}/{len(questions_data)} questions with errors")
        else:
            logger.info(f"✓ Successfully created {len(created_questions)} questions")
        
        return created_questions
    
    @staticmethod
    def get_question(question_id: str) -> Question:
        """
        Get question by ID
        
        Args:
            question_id: Question ID
            
        Returns:
            Question object
        """
        try:
            question_data = mongo.db.questions.find_one({'_id': ObjectId(question_id)})
            
            if not question_data:
                raise QuestionNotFoundError(f"Question not found: {question_id}")
            
            return Question.from_dict(question_data)
            
        except QuestionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"✗ Failed to get question {question_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_questions(
        filters: Optional[Dict] = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = 'created_at',
        sort_order: int = -1
    ) -> tuple[List[Question], int]:
        """
        Get questions with filters and pagination
        
        Args:
            filters: MongoDB filter dict
            page: Page number (1-indexed)
            limit: Items per page
            sort_by: Field to sort by
            sort_order: 1 for ascending, -1 for descending
            
        Returns:
            (questions, total_count)
        """
        try:
            if filters is None:
                filters = {}
            
            # Get total count
            total = mongo.db.questions.count_documents(filters)
            
            # Get paginated results
            skip = (page - 1) * limit
            cursor = mongo.db.questions.find(filters).sort(sort_by, sort_order).skip(skip).limit(limit)
            
            questions = [Question.from_dict(q) for q in cursor]
            
            logger.info(f"✓ Retrieved {len(questions)} questions (page {page}, total {total})")
            return questions, total
            
        except Exception as e:
            logger.error(f"✗ Failed to get questions: {str(e)}")
            raise
    
    @staticmethod
    def update_question(question_id: str, update_data: Dict) -> Question:
        """
        Update question
        
        Args:
            question_id: Question ID
            update_data: Data to update
            
        Returns:
            Updated Question object
        """
        try:
            # Get existing question
            question = QuestionGenerator.get_question(question_id)
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(question, key) and key not in ['question_id', 'created_at']:
                    setattr(question, key, value)
            
            question.updated_at = datetime.utcnow()
            
            # Validate
            is_valid, error_msg = question.validate()
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Save to database
            mongo.db.questions.update_one(
                {'_id': ObjectId(question_id)},
                {'$set': question.to_dict()}
            )
            
            logger.info(f"✓ Updated question: {question_id}")
            return question
            
        except (QuestionNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"✗ Failed to update question {question_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_question(question_id: str) -> bool:
        """
        Delete question
        
        Args:
            question_id: Question ID
            
        Returns:
            True if deleted successfully
        """
        try:
            result = mongo.db.questions.delete_one({'_id': ObjectId(question_id)})
            
            if result.deleted_count == 0:
                raise QuestionNotFoundError(f"Question not found: {question_id}")
            
            logger.info(f"✓ Deleted question: {question_id}")
            return True
            
        except QuestionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"✗ Failed to delete question {question_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_questions_by_ids(question_ids: List[str]) -> List[Question]:
        """
        Get multiple questions by IDs
        
        Args:
            question_ids: List of question IDs
            
        Returns:
            List of Question objects
        """
        try:
            object_ids = [ObjectId(qid) for qid in question_ids]
            cursor = mongo.db.questions.find({'_id': {'$in': object_ids}})
            
            questions = [Question.from_dict(q) for q in cursor]
            
            logger.info(f"✓ Retrieved {len(questions)} questions by IDs")
            return questions
            
        except Exception as e:
            logger.error(f"✗ Failed to get questions by IDs: {str(e)}")
            raise
