#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Routes
=========
API routes for AI-powered question generation
"""

from flask import Blueprint, request, jsonify
from services.ai_generator import AIQuestionGenerator
from services.question_generator import QuestionGenerator
from config import Config
from utils.logger import setup_logger
from utils.exceptions import AIGenerationError, ValidationError

logger = setup_logger('ai_routes')

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/generate', methods=['POST'])
def generate_questions():
    """
    Generate questions using AI
    
    Request body:
    {
        "topic": "Python Programming",
        "num_questions": 3,
        "difficulty": "medium",
        "language": "vi",
        "save_to_db": true
    }
    
    Response:
    {
        "message": "Generated 3 questions",
        "questions": [...],
        "saved_ids": ["id1", "id2"] (if save_to_db=true)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'topic' not in data:
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data['topic']
        num_questions = min(int(data.get('num_questions', 3)), 5)  # Max 5 for free tier
        difficulty = data.get('difficulty', 'medium')
        language = data.get('language', 'vi')
        save_to_db = data.get('save_to_db', False)
        
        # Validate difficulty
        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Invalid difficulty. Use: easy, medium, or hard'}), 400
        
        # Validate language
        if language not in ['vi', 'en']:
            return jsonify({'error': 'Invalid language. Use: vi or en'}), 400
        
        logger.info(f"Generating {num_questions} questions about '{topic}'")
        
        # Initialize AI generator
        ai_gen = AIQuestionGenerator(Config.GEMINI_API_KEY)
        
        # Generate questions
        questions_data = ai_gen.generate_questions(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            language=language
        )
        
        response = {
            'message': f'Generated {len(questions_data)} questions successfully',
            'questions': questions_data
        }
        
        # Save to database if requested
        if save_to_db:
            saved_questions = QuestionGenerator.create_questions_batch(questions_data)
            response['saved_ids'] = [q.question_id for q in saved_questions]
            response['message'] += f', saved {len(saved_questions)} to database'
        
        return jsonify(response), 201
        
    except AIGenerationError as e:
        logger.error(f"AI generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@ai_bp.route('/generate-batch', methods=['POST'])
def generate_batch():
    """
    Generate large batch of questions (splits into multiple AI calls)
    
    Request body:
    {
        "topic": "Python Programming",
        "total_questions": 10,
        "difficulty": "medium",
        "language": "vi",
        "save_to_db": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data['topic']
        total_questions = min(int(data.get('total_questions', 10)), 20)  # Max 20
        difficulty = data.get('difficulty', 'medium')
        language = data.get('language', 'vi')
        save_to_db = data.get('save_to_db', False)
        
        logger.info(f"Generating batch of {total_questions} questions about '{topic}'")
        
        # Initialize AI generator
        ai_gen = AIQuestionGenerator(Config.GEMINI_API_KEY)
        
        # Generate batch
        questions_data = ai_gen.generate_batch(
            topic=topic,
            total_questions=total_questions,
            difficulty=difficulty,
            language=language
        )
        
        response = {
            'message': f'Generated {len(questions_data)} questions successfully',
            'questions': questions_data
        }
        
        # Save to database if requested
        if save_to_db:
            saved_questions = QuestionGenerator.create_questions_batch(questions_data)
            response['saved_ids'] = [q.question_id for q in saved_questions]
            response['message'] += f', saved {len(saved_questions)} to database'
        
        return jsonify(response), 201
        
    except AIGenerationError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
