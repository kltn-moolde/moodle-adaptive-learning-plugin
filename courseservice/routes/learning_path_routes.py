from flask import Blueprint, request, jsonify
import logging
from services.gemini_service import gemini_service
from database import mongo
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

learning_path_bp = Blueprint('learning_path', __name__)

def generate_explanation_id(user_id: str, course_id: str, learning_path_data: dict) -> str:
    """Generate unique ID for explanation based on input data"""
    key_data = f"{user_id}_{course_id}_{learning_path_data.get('suggested_action')}_{learning_path_data.get('source_state', {}).get('section_id')}"
    return hashlib.md5(key_data.encode()).hexdigest()

@learning_path_bp.route('/learning-path/explain', methods=['POST'])
def explain_learning_path():
    """
    API để giải thích tại sao AI gợi ý learning path này cho học sinh
    
    POST /learning-path/explain
    Body: {
        "user_id": "4",
        "course_id": "5",
        "learning_path": {
            "suggested_action": "do_quiz_same",
            "q_value": 0.75,
            "source_state": {
                "section_id": 2,
                "lesson_name": "Basic Concepts",
                "quiz_level": "medium", 
                "complete_rate_bin": 0.6,
                "score_bin": 3
            }
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_id = data.get('user_id')
        course_id = data.get('course_id') 
        learning_path = data.get('learning_path', {})
        
        if not user_id or not course_id or not learning_path:
            return jsonify({'error': 'user_id, course_id and learning_path are required'}), 400
        
        # Generate unique explanation ID
        explanation_id = generate_explanation_id(user_id, course_id, learning_path)
        
        # Check if explanation already exists in MongoDB
        existing = mongo.db.learning_path_explanations.find_one({'explanation_id': explanation_id})
        
        if existing:
            logger.info(f"Found existing explanation for {explanation_id}")
            return jsonify({
                'success': True,
                'data': existing['explanation'],
                'from_cache': True
            }), 200
        
        # Generate new explanation using Gemini AI
        logger.info(f"Generating new explanation for user {user_id}, course {course_id}")
        
        # Create simple prompt for Gemini
        prompt = create_learning_path_explanation_prompt(learning_path)
        
        # Call Gemini AI
        explanation = call_gemini_for_explanation(prompt)
        
        if explanation:
            # Save to MongoDB
            save_data = {
                'explanation_id': explanation_id,
                'user_id': user_id,
                'course_id': course_id,
                'learning_path': learning_path,
                'explanation': explanation,
                'created_at': datetime.now(),
                'source': 'gemini_ai'
            }
            
            mongo.db.learning_path_explanations.insert_one(save_data)
            logger.info(f"Saved explanation to MongoDB with ID: {explanation_id}")
            
            return jsonify({
                'success': True,
                'data': explanation,
                'from_cache': False
            }), 200
        else:
            # Return fallback explanation
            fallback_explanation = get_fallback_explanation(learning_path)
            return jsonify({
                'success': True,
                'data': fallback_explanation,
                'from_cache': False,
                'note': 'AI service unavailable, using fallback explanation'
            }), 200
            
    except Exception as e:
        logger.error(f"Error in explain_learning_path: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def create_learning_path_explanation_prompt(learning_path: dict) -> str:
    """Tạo prompt đơn giản cho Gemini"""
    source_state = learning_path.get('source_state', {})
    
    prompt = f"""
Bạn là AI mentor thân thiện. Hãy giải thích cho học sinh tại sao hệ thống gợi ý learning path này.

THÔNG TIN HỌC SINH:
- Bài học hiện tại: {source_state.get('lesson_name', 'N/A')}
- Mức độ quiz: {source_state.get('quiz_level', 'N/A')}  
- Điểm số: {source_state.get('score_bin', 'N/A')}/10
- Tỷ lệ hoàn thành: {source_state.get('complete_rate_bin', 0)*100:.0f}%
- Section: {source_state.get('section_id', 'N/A')}

HÀNH ĐỘNG ĐỀ XUẤT: {learning_path.get('suggested_action', 'N/A')}
Q-VALUE: {learning_path.get('q_value', 'N/A')}

Trả về JSON format:
{{
  "reason": "Lý do chính tại sao gợi ý này (50-100 từ)",
  "current_status": "Phân tích trạng thái học tập hiện tại (30-50 từ)",
  "benefit": "Lợi ích của việc làm theo gợi ý (30-50 từ)", 
  "motivation": "Lời động viên (20-30 từ)",
  "next_steps": ["Bước 1", "Bước 2", "Bước 3"]
}}

Viết bằng tiếng Việt, giọng điệu thân thiện.
"""
    return prompt

def call_gemini_for_explanation(prompt: str) -> dict:
    """Gọi Gemini API để lấy explanation"""
    try:
        return gemini_service.generate_explanation(prompt)
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        return None

def get_fallback_explanation(learning_path: dict) -> dict:
    """Fallback explanation khi Gemini không available"""
    source_state = learning_path.get('source_state', {})
    suggested_action = learning_path.get('suggested_action', 'continue')
    score_bin = source_state.get('score_bin', 5)
    
    if score_bin <= 3:
        reason = "AI nhận thấy bạn cần củng cố thêm kiến thức cơ bản để có nền tảng vững chắc."
        benefit = "Việc luyện tập thêm sẽ giúp bạn tự tin hơn với các bài học tiếp theo."
    elif score_bin >= 8:
        reason = "Kết quả học tập của bạn rất tốt, AI đề xuất tiếp tục thử thách với nội dung nâng cao."
        benefit = "Việc tiếp tục học sẽ giúp bạn phát triển tối đa năng lực."
    else:
        reason = "Dựa trên tiến độ hiện tại, AI gợi ý bạn duy trì nhịp độ học tập ổn định."
        benefit = "Việc học đều đặn sẽ giúp bạn đạt kết quả tốt nhất."
    
    return {
        "reason": reason,
        "current_status": f"Bạn đang ở mức điểm {score_bin}/10 với tỷ lệ hoàn thành {source_state.get('complete_rate_bin', 0)*100:.0f}%.",
        "benefit": benefit,
        "motivation": "Hãy tiếp tục nỗ lực! Bạn đang trên đường thành công.",
        "next_steps": [
            f"Thực hiện: {suggested_action.replace('_', ' ')}",
            "Hoàn thành các bài tập được gợi ý", 
            "Kiểm tra tiến độ sau 1-2 ngày"
        ]
    }

@learning_path_bp.route('/learning-path/explanations/<user_id>/<course_id>', methods=['GET'])
def get_user_explanations(user_id, course_id):
    """Lấy tất cả explanations của user trong course"""
    try:
        explanations = list(mongo.db.learning_path_explanations.find(
            {'user_id': user_id, 'course_id': course_id},
            {'_id': 0}
        ).sort('created_at', -1).limit(10))
        
        return jsonify({
            'success': True,
            'data': explanations
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user explanations: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@learning_path_bp.route('/learning-path/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'success': True,
        'message': 'Learning path explanation service is healthy'
    }), 200