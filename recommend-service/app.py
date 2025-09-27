from flask import Flask, request, jsonify
import os

from state_manager import load_last_state_action, save_last_state_action
from config import Config, q_table, q_table_lock
import config

from q_learning import (
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

        return jsonify({
            "user_id": userid,
            "course_id": courseid,
            "suggested_action": action,
            "q_value": q_value,
            "source_state": {
                "section_id": current_state[0],
                "quiz_level": current_state[1],
                "complete_rate_bin": current_state[2],
                "score_bin": current_state[3]
            }
        })

    @app.route("/")
    def health():
        return "✅ Recommend Service is running!"

    return app


# --- Local dev chạy trực tiếp ---
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8088, use_reloader=False)