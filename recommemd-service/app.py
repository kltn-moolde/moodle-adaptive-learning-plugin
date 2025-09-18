from flask import Flask, request, jsonify
import threading
from config import q_table, q_table_lock, LOG_FILE_PATH
from q_learning import (
    load_data, load_q_table_from_csv, initialize_q_table,
    q_learning_daemon, process_log_line, suggest_next_action, last_state_action, get_state_from_log_line, get_last_user_log
)

app = Flask(__name__)

@app.route('/api/suggest-action', methods=['POST'])
def suggest_action_api():
    data = request.json
    try:
        userid = int(data.get('userid'))
        courseid = int(data.get('courseid'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input data"}), 400

    # --- Lấy log cuối cùng ---
    last_line = get_last_user_log(userid, courseid)
    if last_line is None:
        return jsonify({"error": "No recent activity for this user"}), 404

    userid, courseid, current_state, passed_quiz = get_state_from_log_line(last_line)
    if current_state is None:
        return jsonify({"error": "Cannot parse last log line"}), 500

    # --- Chọn action dựa trên state gần nhất ---
    with q_table_lock:
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

if __name__ == '__main__':
    # --- Khởi tạo dữ liệu và Q-table ---
    load_data()
    q_table = load_q_table_from_csv()
    if not q_table:
        q_table = initialize_q_table()

    # --- Chạy daemon đọc log để cập nhật Q-table realtime ---
    daemon_thread = threading.Thread(target=lambda: [process_log_line(line) for line in q_learning_daemon()])
    daemon_thread.daemon = True
    daemon_thread.start()

    # --- Chạy Flask ---
    app.run(debug=True, port=8088, use_reloader=False)