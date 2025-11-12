#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Routes
===============
API routes for question management
"""

from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from typing import Dict

from services.question_generator import QuestionGenerator
from services.xml_converter import XMLConverter
from utils.logger import setup_logger
from utils.exceptions import (
    QuestionServiceError,
    ValidationError,
    QuestionNotFoundError
)
from utils.validators import validate_question_data, validate_questions_batch

logger = setup_logger('question_routes')

question_bp = Blueprint('questions', __name__)


@question_bp.route('/create', methods=['POST'])
def create_question():
    """
    Create a new question
    
    Request body:
    {
        "name": "Question name",
        "question_type": "multichoice",
        "question_text": "<p>Question text</p>",
        "difficulty": "easy",
        "answers": [
            {"text": "Answer 1", "fraction": 100, "feedback": "Correct!"},
            {"text": "Answer 2", "fraction": 0, "feedback": "Wrong"}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate
        is_valid, error = validate_question_data(data)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Create question
        question = QuestionGenerator.create_question(data)
        
        return jsonify({
            'message': 'Question created successfully',
            'question': {
                'id': question.question_id,
                'name': question.name,
                'type': question.question_type,
                'difficulty': question.difficulty
            }
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating question: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/create-batch', methods=['POST'])
def create_questions_batch():
    """
    Create multiple questions at once
    
    Request body:
    {
        "questions": [
            {
                "name": "Question 1",
                "question_type": "multichoice",
                ...
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'questions' not in data:
            return jsonify({'error': 'No questions provided'}), 400
        
        questions_data = data['questions']
        
        # Validate batch
        is_valid, errors = validate_questions_batch(questions_data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Create questions
        questions = QuestionGenerator.create_questions_batch(questions_data)
        
        return jsonify({
            'message': f'Created {len(questions)} questions successfully',
            'questions': [
                {
                    'id': q.question_id,
                    'name': q.name,
                    'type': q.question_type,
                    'difficulty': q.difficulty
                }
                for q in questions
            ]
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating questions batch: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/<question_id>', methods=['GET'])
def get_question(question_id: str):
    """Get question by ID"""
    try:
        question = QuestionGenerator.get_question(question_id)
        
        return jsonify({
            'question': {
                'id': question.question_id,
                'name': question.name,
                'question_type': question.question_type,
                'question_text': question.question_text,
                'difficulty': question.difficulty,
                'answers': [a.to_dict() for a in question.answers],
                'category': question.category,
                'tags': question.tags,
                'created_at': question.created_at.isoformat() if question.created_at else None,
                'updated_at': question.updated_at.isoformat() if question.updated_at else None
            }
        }), 200
        
    except QuestionNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting question: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/', methods=['GET'])
def get_questions():
    """
    Get questions with filters and pagination
    
    Query params:
        - difficulty: easy|medium|hard
        - type: multichoice|truefalse|shortanswer|essay
        - category: category name
        - page: page number (default: 1)
        - limit: items per page (default: 10)
        - sort_by: field to sort by (default: created_at)
        - sort_order: asc|desc (default: desc)
    """
    try:
        # Parse query params
        difficulty = request.args.get('difficulty')
        question_type = request.args.get('type')
        category = request.args.get('category')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = -1 if request.args.get('sort_order', 'desc') == 'desc' else 1
        
        # Build filters
        filters = {}
        if difficulty:
            filters['difficulty'] = difficulty
        if question_type:
            filters['question_type'] = question_type
        if category:
            filters['category'] = category
        
        # Get questions
        questions, total = QuestionGenerator.get_questions(
            filters=filters,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify({
            'questions': [
                {
                    'id': q.question_id,
                    'name': q.name,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'category': q.category,
                    'created_at': q.created_at.isoformat() if q.created_at else None
                }
                for q in questions
            ],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/<question_id>', methods=['PUT'])
def update_question(question_id: str):
    """Update question"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update question
        question = QuestionGenerator.update_question(question_id, data)
        
        return jsonify({
            'message': 'Question updated successfully',
            'question': {
                'id': question.question_id,
                'name': question.name,
                'updated_at': question.updated_at.isoformat() if question.updated_at else None
            }
        }), 200
        
    except QuestionNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating question: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/<question_id>', methods=['DELETE'])
def delete_question(question_id: str):
    """Delete question"""
    try:
        QuestionGenerator.delete_question(question_id)
        
        return jsonify({
            'message': 'Question deleted successfully'
        }), 200
        
    except QuestionNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting question: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/export/xml', methods=['POST'])
def export_xml():
    """
    Export questions to Moodle XML format
    
    Request body:
    {
        "question_ids": ["id1", "id2", ...],
        "filename": "quiz.xml"  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'question_ids' not in data:
            return jsonify({'error': 'No question IDs provided'}), 400
        
        question_ids = data['question_ids']
        filename = data.get('filename', 'moodle_quiz.xml')
        
        # Get questions
        questions = QuestionGenerator.get_questions_by_ids(question_ids)
        
        if not questions:
            return jsonify({'error': 'No questions found'}), 404
        
        # Generate XML
        xml_content = XMLConverter.create_moodle_xml(questions, filename)
        
        # Send as file
        return send_file(
            BytesIO(xml_content),
            mimetype='application/xml',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error exporting XML: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@question_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get question statistics"""
    try:
        from database import mongo
        
        # Total questions
        total = mongo.db.questions.count_documents({})
        
        # By difficulty
        by_difficulty = {}
        for difficulty in ['easy', 'medium', 'hard']:
            count = mongo.db.questions.count_documents({'difficulty': difficulty})
            by_difficulty[difficulty] = count
        
        # By type
        by_type = {}
        for qtype in ['multichoice', 'truefalse', 'shortanswer', 'essay']:
            count = mongo.db.questions.count_documents({'question_type': qtype})
            by_type[qtype] = count
        
        return jsonify({
            'total': total,
            'by_difficulty': by_difficulty,
            'by_type': by_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
