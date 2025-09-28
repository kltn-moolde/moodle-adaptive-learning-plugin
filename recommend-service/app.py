from flask import Flask, request, jsonify
import os
import pandas as pd
from datetime import datetime
import requests

from state_manager import load_last_state_action, save_last_state_action
from config import Config, q_table, q_table_lock
import config

from q_learning import (
    call_moodle_api,
    load_data,
    load_q_table_from_csv,
    initialize_q_table,
    save_q_table_to_csv,
    update_q_value,
    suggest_next_action,
    get_state_from_moodle,
    get_reward,
    get_user_cluster,
)

from learning_path_optimizer import learning_path_optimizer

last_state_action = load_last_state_action()


def create_app():
    app = Flask(__name__)


    # --- Load data + Q-table khi service khởi động ---
    load_data()
    global q_table
    if not os.path.exists(Config.DEFAULT_QTABLE_PATH):
        print(f"⚠️ Q-table file not found. Initializing new Q-table at {Config.DEFAULT_QTABLE_PATH}")
        q_table = initialize_q_table(Config.DEFAULT_QTABLE_PATH)
    else:
        q_table = load_q_table_from_csv(Config.DEFAULT_QTABLE_PATH)

    # --- ROUTES ---
    @app.route('/api/update-learning-event', methods=['POST'])
    def update_learning_event():
        global last_state_action, q_table

        data = request.json
        try:
            userid = int(data['userid'])
            courseid = int(data['courseid'])
            sectionid = int(data['sectionid'])
            objecttype = data['type']
            objectid = int(data['objectid'])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Invalid payload"}), 400

        # Lấy trạng thái mới từ Moodle
        current_state, passed_quiz = get_state_from_moodle(
            userid, courseid, sectionid, objecttype, objectid
        )

        # Cập nhật Q-table
        with q_table_lock:
            user_key = str(userid)   # gán ngay từ đầu

            if user_key in last_state_action:
                prev_state, prev_action = last_state_action[user_key]

                # Chỉ update nếu cùng section
                if prev_state[0] == current_state[0]:
                    reward = get_reward(
                        action=prev_action,
                        old_score=prev_state[3],
                        new_score=current_state[3],
                        old_complete=prev_state[2],
                        new_complete=current_state[2],
                        cluster=get_user_cluster(userid),
                        quiz_level=prev_state[1],
                        passed_hard_quiz=passed_quiz,
                    )
                    update_q_value(prev_state, prev_action, reward, current_state)
                    save_q_table_to_csv(config.q_table)

            # Chọn action tiếp theo
            action, _ = suggest_next_action(current_state, userid=userid)
            last_state_action[user_key] = (current_state, action)
            
            # 👉 Lưu xuống file JSON
            save_last_state_action(last_state_action)
        return jsonify({"status": "ok", "next_action": action})

    @app.route('/api/suggest-action', methods=['POST'])
    def suggest_action_api():
        data = request.json
        try:
            userid = int(data['userid'])
            courseid = int(data['courseid'])
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid input data"}), 400

        with q_table_lock:
            user_key = str(userid)
            if user_key not in last_state_action:
                return jsonify({"error": "No recent activity for this user"}), 404

            current_state, _ = last_state_action[user_key]
            action, q_value = suggest_next_action(current_state, userid)

        section_id = current_state[0]

        # Gọi API Moodle để lấy cấu trúc course
        course_structure = call_moodle_api(
            'local_course_get_contents_structure', 
            {'courseid': courseid}
        )
        
        # 1. Gọi API lấy course structure
        url = f"{Config.ADDRESS_COURSE_SERVICE_BASE}/api/moodle/courses/{Config.COURSE_ID}/contents/structure"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        course_structure = response.json() 

        # Tìm lesson tương ứng với section_id
        lesson_name = None
        for section in course_structure:
            lessons = section.get('lessons', [])
            for lesson in lessons:
                if lesson.get('sectionIdNew') == section_id:
                    lesson_name = lesson.get('name')
                    break
            if lesson_name:
                break

        return jsonify({
            "user_id": userid,
            "course_id": courseid,
            "suggested_action": action,
            "q_value": q_value,
            "source_state": {
                "section_id": section_id,
                "lesson_name": lesson_name,  # thêm tên bài học
                "quiz_level": current_state[1],
                "complete_rate_bin": current_state[2],
                "score_bin": current_state[3]
            }
        })

    @app.route('/api/qtable/nonzero', methods=['GET'])
    def get_nonzero_qvalues():
        # Load CSV
        df = pd.read_csv(Config.DEFAULT_QTABLE_PATH)

        # Lọc các dòng q_value != 0, giữ nguyên tất cả cột
        nonzero_df = df[df['q_value'] != 0]

        # Chuyển sang dict để jsonify
        results = nonzero_df.to_dict(orient='records')

        # Trả về JSON nguyên bản
        return jsonify(results), 200

    @app.route('/api/generate-learning-path', methods=['POST'])
    def generate_learning_path_api():
        """
        API để tạo lộ trình học hoàn chỉnh sử dụng Linear Regression
        Input:
        {
            "userid": 123,
            "courseid": 5,
            "max_sections": 10,      // optional, default 10
            "include_completed": false, // optional, default false
            "optimization_goal": "performance" // optional: "performance", "speed", "comprehensive"
        }
        """
        data = request.json
        try:
            userid = int(data['userid'])
            courseid = int(data['courseid'])
            max_sections = int(data.get('max_sections', 10))
            include_completed = data.get('include_completed', False)
            optimization_goal = data.get('optimization_goal', 'performance')
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Invalid input data. Required: userid, courseid"}), 400

        try:
            # Train model nếu chưa được train
            if not learning_path_optimizer.is_trained:
                print(f"🔄 Training model for user {userid}...")
                success = learning_path_optimizer.train_model()
                if not success:
                    return jsonify({"error": "Failed to train learning path model"}), 500

            # Generate learning path
            learning_path = learning_path_optimizer.generate_learning_path(
                userid, courseid, max_sections, include_completed, optimization_goal
            )

            if not learning_path:
                return jsonify({"error": "Could not generate learning path for this user"}), 404

            # Tính toán metadata
            user_cluster = get_user_cluster(userid)
            total_estimated_time = sum([section.get('estimated_time_minutes', 30) for section in learning_path])
            
            # An toàn tính avg_performance_score, xử lý None values
            valid_scores = [section.get('priority_score', 0.5) for section in learning_path if section.get('priority_score') is not None]
            avg_performance_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.5

            # Format response
            response = {
                "success": True,
                "user_id": userid,
                "course_id": courseid,
                "total_sections": len(learning_path),
                "estimated_total_time_minutes": total_estimated_time,
                "average_performance_score": round(avg_performance_score, 3),
                "optimization_goal": optimization_goal,
                "learning_path": learning_path,
                "generated_at": datetime.now().isoformat(),
                "model_info": {
                    "algorithm": "Linear Regression + Q-Learning Hybrid",
                    "user_cluster": user_cluster,
                    "cluster_description": {
                        0: "Beginner - Focuses on foundational concepts",
                        1: "Intermediate - Balanced approach",
                        2: "Advanced - Emphasizes challenging content"
                    }.get(user_cluster, "Unknown"),
                    "personalization_enabled": True,
                    "model_version": "1.0"
                },
                "recommendations": {
                    "study_tips": learning_path_optimizer.get_study_tips(user_cluster),
                    "next_immediate_action": learning_path[0]['recommended_actions'][0]['action'] if learning_path else None
                }
            }

            return jsonify(response)

        except Exception as e:
            print(f"❌ Error generating learning path: {e}")
            return jsonify({
                "success": False,
                "error": f"Internal error: {str(e)}",
                "user_id": userid,
                "course_id": courseid
            }), 500

    @app.route('/api/predict-performance', methods=['POST'])
    def predict_performance_api():
        """
        API để dự đoán hiệu suất học tập cho section cụ thể
        Input:
        {
            "userid": 123,
            "section_id": 45,
            "current_complete_rate": 0.5,  // optional, sẽ lấy từ Moodle nếu không có
            "current_score": 6              // optional, sẽ lấy từ Moodle nếu không có
        }
        """
        data = request.json
        try:
            userid = int(data['userid'])
            section_id = int(data['section_id'])
            
            # Lấy current state từ input hoặc từ Moodle
            if 'current_complete_rate' in data and 'current_score' in data:
                complete_rate = float(data['current_complete_rate'])
                score = float(data['current_score'])
            else:
                # Lấy từ Moodle API
                courseid = int(data.get('courseid', Config.COURSE_ID))
                current_state, _ = get_state_from_moodle(userid, courseid, section_id, "resource", 0)
                complete_rate = current_state[2]
                score = current_state[3]
                
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Invalid input data. Required: userid, section_id"}), 400

        try:
            # Đảm bảo model đã được train
            if not learning_path_optimizer.is_trained:
                success = learning_path_optimizer.train_model()
                if not success:
                    return jsonify({"error": "Failed to initialize model"}), 500

            # Dự đoán performance
            predicted_performance = learning_path_optimizer.predict_performance(
                userid, section_id, complete_rate, score
            )
            
            user_cluster = get_user_cluster(userid)
            
            return jsonify({
                "success": True,
                "user_id": userid,
                "section_id": section_id,
                "predicted_performance": round(predicted_performance, 4),
                "current_state": {
                    "complete_rate": complete_rate,
                    "score": score
                },
                "user_cluster": user_cluster,
                "performance_level": {
                    "level": "High" if predicted_performance >= 0.8 else "Medium" if predicted_performance >= 0.6 else "Low",
                    "confidence": "High" if learning_path_optimizer.is_trained else "Medium"
                },
                "predicted_at": datetime.now().isoformat()
            })

        except Exception as e:
            print(f"❌ Error predicting performance: {e}")
            return jsonify({
                "success": False,
                "error": f"Prediction error: {str(e)}"
            }), 500

    @app.route('/api/train-model', methods=['POST'])
    def train_model_api():
        """
        API để train lại model (cho admin)
        """
        try:
            success = learning_path_optimizer.train_model()
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Model trained successfully",
                    "trained_at": datetime.now().isoformat(),
                    "model_metrics": {
                        "algorithm": "Linear Regression",
                        "features_used": ["section_id", "cluster", "current_complete_rate", "current_score", "difficulty_preference"]
                    }
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to train model"
                }), 500
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error training model: {str(e)}"
            }), 500

    @app.route('/api/learning-analytics', methods=['POST'])
    def learning_analytics_api():
        """
        API để phân tích và so sánh hiệu suất học tập
        """
        data = request.json
        try:
            userid = int(data['userid'])
            courseid = int(data.get('courseid', Config.COURSE_ID))
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Invalid input data. Required: userid"}), 400

        try:
            if not learning_path_optimizer.is_trained:
                learning_path_optimizer.train_model()

            # Phân tích tổng thể
            analytics = learning_path_optimizer.analyze_user_performance(userid, courseid)
            
            return jsonify({
                "success": True,
                "user_id": userid,
                "course_id": courseid,
                "analytics": analytics,
                "generated_at": datetime.now().isoformat()
            })

        except Exception as e:
            print(f"❌ Error generating analytics: {e}")
            return jsonify({
                "success": False,
                "error": f"Analytics error: {str(e)}"
            }), 500

    @app.route("/")
    def health():
        return "✅ Recommend Service is running!"

    return app


# --- Local dev chạy trực tiếp ---
if __name__ == "__main__":
    
    app = create_app()
    app.run(debug=True, port=8088, use_reloader=False)