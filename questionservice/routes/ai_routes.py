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
from services.moodle_service import MoodleAPIClient
from services.xml_converter import XMLConverter
from models.question import Question
from config import Config
from utils.logger import setup_logger
from utils.exceptions import (
    AIGenerationError, 
    ValidationError,
    MoodleAPIError,
    MoodleConnectionError,
    MoodleImportError
)

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
        num_questions = min(int(data.get('num_questions', 3)), 15)  # Max 15 for testing
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
        total_questions = min(int(data.get('total_questions', 10)), 100)  # Max 100 for testing
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


@ai_bp.route('/generate-and-import', methods=['POST'])
def generate_and_import():
    """
    Generate questions using AI and automatically import to Moodle
    
    Request body:
    {
        "topic": "Toán học phương trình bậc 2",
        "num_questions": 3,
        "difficulty": "hard",
        "language": "vi",
        "save_to_db": false,
        "import_to_moodle": true,
        "moodle_category": "Toán học"  // optional, defaults to topic
    }
    
    Response:
    {
        "message": "Generated and imported 3 questions successfully",
        "questions": [...],
        "moodle_category_id": 123,
        "moodle_question_ids": [456, 457, 458],
        "saved_ids": ["id1", "id2"] (if save_to_db=true)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'topic' not in data:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Check if Moodle import is requested
        import_to_moodle = data.get('import_to_moodle', False)
        if not import_to_moodle:
            return jsonify({'error': 'import_to_moodle must be true for this endpoint'}), 400
        
        # Validate Moodle configuration
        if not Config.MOODLE_URL or not Config.MOODLE_TOKEN:
            return jsonify({
                'error': 'Moodle configuration missing. Please set MOODLE_URL and MOODLE_TOKEN'
            }), 500
        
        topic = data['topic']
        num_questions = min(int(data.get('num_questions', 3)), 15)  # Max 15 for testing
        difficulty = data.get('difficulty', 'medium')
        language = data.get('language', 'vi')
        save_to_db = data.get('save_to_db', False)
        course_id = int(data.get('course_id', Config.MOODLE_DEFAULT_COURSE_ID))
        
        # Validate difficulty
        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Invalid difficulty. Use: easy, medium, or hard'}), 400
        
        # Validate language
        if language not in ['vi', 'en']:
            return jsonify({'error': 'Invalid language. Use: vi or en'}), 400
        
        logger.info(f"Generating {num_questions} questions about '{topic}' and importing to Moodle")
        
        # GIAI ĐOẠN 1: Generate questions using AI
        ai_gen = AIQuestionGenerator(Config.GEMINI_API_KEY)
        questions_data = ai_gen.generate_questions(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            language=language
        )
        
        # Kết quả GIAI ĐOẠN 1
        import json
        logger.info("=" * 70)
        logger.info("GIAI ĐOẠN 1 - KẾT QUẢ: JSON từ AI")
        logger.info("=" * 70)
        logger.info(json.dumps(questions_data, ensure_ascii=False, indent=2))
        logger.info("=" * 70)
        
        # GIAI ĐOẠN 2: Convert JSON to XML
        questions = [Question.from_dict(q) for q in questions_data]
        xml_content = XMLConverter.create_moodle_xml(questions, "moodle_import.xml")
        
        # Kết quả GIAI ĐOẠN 2
        xml_string = xml_content.decode('utf-8')
        logger.info("=" * 70)
        logger.info("GIAI ĐOẠN 2 - KẾT QUẢ: XML Content")
        logger.info("=" * 70)
        logger.info(xml_string)
        logger.info("=" * 70)
        
        # GIAI ĐOẠN 3: Import to Moodle
        moodle_client = MoodleAPIClient(Config.MOODLE_URL, Config.MOODLE_TOKEN)
        import_result = moodle_client.import_questions_xml_simple(xml_content, course_id)
        
        # Kết quả GIAI ĐOẠN 3
        logger.info("=" * 70)
        logger.info("GIAI ĐOẠN 3 - KẾT QUẢ: Response từ Moodle")
        logger.info("=" * 70)
        logger.info(json.dumps(import_result, ensure_ascii=False, indent=2))
        logger.info("=" * 70)
        
        # Build view URL từ instanceid
        view_url = None
        instance_id = import_result.get('instanceid')
        if instance_id:
            # view_url = f"{Config.MOODLE_URL}/question/edit.php?cmid={instance_id}"
            view_url = f"http://139.99.103.223:9090/question/edit.php?cmid={instance_id}"
        
        # Step 7: Optionally save to database
        saved_ids = []
        if save_to_db:
            try:
                saved_questions = QuestionGenerator.create_questions_batch(questions_data)
                saved_ids = [q.question_id for q in saved_questions]
                logger.info(f"✓ Saved {len(saved_ids)} questions to database")
            except Exception as e:
                logger.warning(f"Failed to save to database: {str(e)}")
                # Don't fail the whole request if DB save fails
        
        # Build response
        response = {
            'message': f'Generated and imported {len(questions_data)} questions successfully',
            'questions': questions_data,
            'moodle_course_id': course_id,
            'moodle_import_result': import_result,
            'view_questions_url': view_url
        }
        
        if saved_ids:
            response['saved_ids'] = saved_ids
            response['message'] += f', saved {len(saved_ids)} to database'
        
        return jsonify(response), 201
        
    except AIGenerationError as e:
        logger.error(f"AI generation error: {str(e)}")
        return jsonify({'error': f'AI generation failed: {str(e)}'}), 500
    except (MoodleAPIError, MoodleConnectionError, MoodleImportError) as e:
        logger.error(f"Moodle error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
