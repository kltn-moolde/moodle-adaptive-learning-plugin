# q_learning.py
import pandas as pd
import json
import os
import random
import requests
import time
from config import Config
import config


def load_data():
    config.section_ids = [] 
    try:
        # 1. Gọi API lấy course structure
        url = f"{Config.ADDRESS_COURSE_SERVICE_BASE}/api/moodle/courses/{Config.COURSE_ID}/contents/structure"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()  # vì Flask route trả về JSON

        # 2. Trích xuất sectionIds
        for section in data:
            if "lessons" in section:
                for lesson in section["lessons"]:
                    config.section_ids.append(lesson["sectionIdNew"])

        # 3. Load user_clusters.csv
        config.user_clusters_df = pd.read_csv(Config.USER_CLUSTERS_CSV)

    except requests.RequestException as e:
        print(f"❌ Error calling API: {e}")
        exit()
    except FileNotFoundError as e:
        print(f"❌ Error loading data: {e}")
        exit()

# --- Q-table management ---
def initialize_q_table(filename=Config.DEFAULT_QTABLE_PATH):
    initial_q_table = {}
    levels = ['easy', 'medium', 'hard']
    for section_id in config.section_ids:
        for level in levels:
            for complete_rate in Config.COMPLETE_RATE_BINS:
                for score_bin in Config.SCORE_AVG_BINS:
                    state = (section_id, level, complete_rate, score_bin)
                    initial_q_table[state] = {action: 0.0 for action in Config.ACTIONS}
    save_q_table_to_csv(initial_q_table, filename)
    return initial_q_table

    
def save_q_table_to_csv(q_table_to_save, filename=Config.DEFAULT_QTABLE_PATH):
    # Đọc file CSV hiện có (nếu có) để giữ nguyên dữ liệu cũ
    if os.path.exists(filename):
        try:
            df_existing = pd.read_csv(filename)
            print(f"[DEBUG] Loaded existing CSV with {len(df_existing)} rows")
        except Exception as e:
            print(f"⚠️ Error loading existing CSV: {e}. Creating new one.")
            df_existing = pd.DataFrame()
    else:
        df_existing = pd.DataFrame()
        print(f"[DEBUG] Creating new Q-table CSV file")

    # Tạo danh sách các row cần cập nhật từ q_table_to_save
    updated_rows = []
    for state, actions_dict in q_table_to_save.items():
        for action, q_value in actions_dict.items():
            row = {
                'sectionid': state[0], 
                'level': state[1],
                'complete_rate': state[2], 
                'score_bin': state[3],
                'action': action, 
                'q_value': q_value
            }
            updated_rows.append(row)

    df_new = pd.DataFrame(updated_rows)

    # Nếu file cũ tồn tại, merge dữ liệu để giữ nguyên các giá trị không thay đổi
    if not df_existing.empty and len(df_new) > 0:
        # Tạo key để merge
        merge_cols = ['sectionid', 'level', 'complete_rate', 'score_bin', 'action']
        
        # Merge: giữ nguyên tất cả rows cũ, chỉ update q_value của những rows mới
        df_final = df_existing.merge(
            df_new[merge_cols + ['q_value']], 
            on=merge_cols, 
            how='left', 
            suffixes=('', '_new')
        )
        
        # Cập nhật q_value cho những row có dữ liệu mới
        df_final['q_value'] = df_final['q_value_new'].fillna(df_final['q_value'])
        df_final = df_final.drop(columns=['q_value_new'])
        
        # Thêm những row hoàn toàn mới (không có trong file cũ)
        new_rows_only = df_new.merge(
            df_existing[merge_cols], 
            on=merge_cols, 
            how='left', 
            indicator=True
        )
        new_rows_only = new_rows_only[new_rows_only['_merge'] == 'left_only'][merge_cols + ['q_value']]
        
        if not new_rows_only.empty:
            df_final = pd.concat([df_final, new_rows_only], ignore_index=True)
            
    else:
        df_final = df_new

    # 🔍 Debug in Q-value khác 0
    if not df_final.empty:
        non_zero = df_final[df_final["q_value"] != 0]
        print(f"[DEBUG] Saving Q-table → {os.path.abspath(filename)}")
        print(f"[DEBUG] Total rows: {len(df_final)}, Non-zero entries: {len(non_zero)}")
        if len(non_zero) > 0:
            print(f"[DEBUG] Sample non-zero entries:\n{non_zero.head(5)}")

    df_final.to_csv(filename, index=False)    

def load_q_table_from_csv(filename=Config.DEFAULT_QTABLE_PATH):
    if not os.path.exists(filename):
        return {}
    q_table_loaded = {}
    try:
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            state = (row['sectionid'], row['level'], row['complete_rate'], row['score_bin'])
            action = row['action']
            q_value = row['q_value']
            if state not in q_table_loaded:
                q_table_loaded[state] = {a: 0.0 for a in Config.ACTIONS}
            q_table_loaded[state][action] = q_value
    except Exception as e:
        print(f"❌ Error loading Q-table: {e}")
        return {}
    return q_table_loaded


# --- Discretization ---

def discretize_score(score):
    if score is None:
        print("⚠️ discretize_score: score=None → return 0")
        return 0

    print(f"\n🔍 DEBUG discretize_score: input score={score}")
    for b in reversed(Config.SCORE_AVG_BINS):
        print(f"  - check bin={b}: score >= {b}? {'YES' if score >= b else 'NO'}")
        if score >= b:
            print(f"  ✅ match bin={b} → return {b}")
            return b

    print("❌ no bin matched → return 0")
    return 0

def discretize_complete_rate(rate):
    if rate is None:
        return Config.COMPLETE_RATE_BINS[0]  # mặc định lấy mức thấp nhất
    for b in reversed(Config.COMPLETE_RATE_BINS):
        if rate >= b:
            return b
    return Config.COMPLETE_RATE_BINS[0]

# --- Moodle API ---
def call_moodle_api(function, extra_params):
    params = {
        'wstoken': Config.TOKEN_PLUGIN_PHP_MOODLE,
        'moodlewsrestformat': 'json',
        'wsfunction': function
    }
    params.update(extra_params)

    headers = {
        "Host": Config.ADDRESS_MOODLE,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            Config.MOODLE_API_BASE,
            data=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Moodle API '{function}': {e}")
        return {}

def safe_get(data, key, default=None):
    if isinstance(data, dict):
        return data.get(key, default)
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data[0].get(key, default)
    return default


def get_user_cluster(user_id):
    if config.user_clusters_df is None:
        return None
    row = config.user_clusters_df[config.user_clusters_df['userid'] == user_id]
    return row.iloc[0]['cluster'] if not row.empty else None

# # --- State & reward ---
# def get_state_from_moodle(userid, courseid, sectionid, objecttype, objectid):
#     avg_score_data = call_moodle_api('local_userlog_get_user_section_avg_grade', {
#         'userid': userid, 'courseid': courseid, 'sectionid': sectionid
#     })
#     avg_score = safe_get(avg_score_data, 'avg_section_grade', 0)

#     quiz_level = 'medium'
#     if objecttype == "quiz":
#         quiz_level_data = call_moodle_api('local_userlog_get_quiz_tags', {'quizid': objectid})
#         quiz_level = safe_get(quiz_level_data, 'tag_name', 'medium')

#     total_resources = safe_get(call_moodle_api('local_userlog_get_total_resources_by_section', {
#         'sectionid': sectionid, 'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
#     }), 'total_resources', 0)
#     viewed_resources = safe_get(call_moodle_api('local_userlog_get_viewed_resources_distinct_by_section', {
#         'userid': userid, 'courseid': courseid, 'sectionid': sectionid,
#         'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
#     }), 'viewed_resources', 0)
#     complete_rate = viewed_resources / total_resources if total_resources>0 else 0.0

#     passed_lastest_quiz = safe_get(call_moodle_api('local_userlog_get_latest_quiz_pass_status_by_section',{
#         'sectionid': sectionid, 'userid': userid
#     }),'is_passed',0)==1

#     state = (sectionid, quiz_level, discretize_complete_rate(complete_rate), discretize_score(avg_score))
#     return state, passed_lastest_quiz


# --- State & reward ---
def get_state_from_moodle(userid, courseid, sectionid, objecttype, objectid):
    print(f"\n🔍 DEBUG: get_state_from_moodle(userid={userid}, courseid={courseid}, sectionid={sectionid}, objecttype={objecttype}, objectid={objectid})")

    # --- Lấy điểm trung bình section ---
    avg_score_data = call_moodle_api('local_userlog_get_user_section_avg_grade', {
        'userid': userid, 'courseid': courseid, 'sectionid': sectionid
    })
    print(f"📊 API avg_score_data: {avg_score_data}")
    avg_score = safe_get(avg_score_data, 'avg_section_grade', 0)
    print(f"➡️ avg_score: {avg_score}")

    # --- Quiz level ---
    quiz_level = 'medium'
    if objecttype == "quiz":
        quiz_level_data = call_moodle_api('local_userlog_get_quiz_tags', {'quizid': objectid})
        print(f"📊 API quiz_level_data: {quiz_level_data}")
        quiz_level = safe_get(quiz_level_data, 'tag_name', 'medium')
    print(f"➡️ quiz_level: {quiz_level}")

    # --- Tài nguyên ---
    total_resources_data = call_moodle_api('local_userlog_get_total_resources_by_section', {
        'sectionid': sectionid, 'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
    })
    print(f"📊 API total_resources_data: {total_resources_data}")
    total_resources = safe_get(total_resources_data, 'total_resources', 0)

    viewed_resources_data = call_moodle_api('local_userlog_get_viewed_resources_distinct_by_section', {
        'userid': userid, 'courseid': courseid, 'sectionid': sectionid,
        'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
    })
    print(f"📊 API viewed_resources_data: {viewed_resources_data}")
    viewed_resources = safe_get(viewed_resources_data, 'viewed_resources', 0)

    complete_rate = viewed_resources / total_resources if total_resources > 0 else 0.0
    print(f"➡️ complete_rate: {complete_rate:.2f} ({viewed_resources}/{total_resources})")

    # --- Quiz pass status ---
    latest_quiz_status = call_moodle_api('local_userlog_get_latest_quiz_pass_status_by_section', {
        'sectionid': sectionid, 'userid': userid
    })
    print(f"📊 API latest_quiz_status: {latest_quiz_status}")
    passed_lastest_quiz = safe_get(latest_quiz_status, 'is_passed', 0) == 1
    print(f"➡️ passed_lastest_quiz: {passed_lastest_quiz}")

    # --- State ---
    state = (
        sectionid,
        quiz_level,
        discretize_complete_rate(complete_rate),
        discretize_score(avg_score)
    )
    print(f"✅ Final state: {state}")

    return state, passed_lastest_quiz


def get_q_value(state, action):
    # đảm bảo state luôn là tuple hashable
    state = tuple(state)  
    if state not in config.q_table:
        config.q_table[state] = {a: 0.0 for a in Config.ACTIONS}
    return config.q_table[state][action]

    
def update_q_value(state, action, reward, next_state):
    state = tuple(state)
    next_state = tuple(next_state)

    # nếu state chưa có thì giữ nguyên q_table, chỉ thêm mới
    if state not in config.q_table:
        config.q_table[state] = {a: 0.0 for a in Config.ACTIONS}

    if next_state not in config.q_table:
        config.q_table[next_state] = {a: 0.0 for a in Config.ACTIONS}

    old_value = config.q_table[state][action]
    next_max = max(config.q_table[next_state].values())

    new_value = (1 - Config.LEARNING_RATE) * old_value + \
                Config.LEARNING_RATE * (reward + Config.DISCOUNT_FACTOR * next_max)

    config.q_table[state][action] = new_value    
    

def get_reward(action, old_score, new_score, old_complete, new_complete, cluster=None, quiz_level='medium', passed_hard_quiz=1):
    score_improvement = new_score - old_score
    complete_bonus = (new_complete - old_complete) * 10
    action_bonus = 0
    cluster_bonus = 0

    print("\n[DEBUG] ==== get_reward START ====")
    print(f"Action: {action}")
    print(f"Old score: {old_score}, New score: {new_score}, Score improvement: {score_improvement}")
    print(f"Old complete: {old_complete}, New complete: {new_complete}, Complete bonus: {complete_bonus}")
    print(f"Cluster: {cluster}, Quiz level: {quiz_level}, Passed hard quiz: {passed_hard_quiz}")

    # --- Logic mới ---
    if action == 'read_new_resource':
        if new_complete >= 1.0:
            action_bonus = -2
        else:
            action_bonus = 1
    elif action == 'review_old_resource':
        if new_score < 5:
            action_bonus = 3
        else:
            action_bonus = 0.5
    elif action == 'redo_failed_quiz':
        if not passed_hard_quiz:
            action_bonus = 4
        else:
            action_bonus = 1
    elif action == 'do_quiz_easier':
        if new_score < 4:
            action_bonus = 5
        else:
            action_bonus = 0.5
    elif action == 'do_quiz_harder':
        if new_score >= 8:
            action_bonus = 4
        else:
            action_bonus = -1

    print(f"Action bonus: {action_bonus}")

    # --- Cluster-based personalization ---
    if cluster == 0:  # Yếu
        if action in ['review_old_resource', 'redo_failed_quiz', 'do_quiz_easier']:
            cluster_bonus = 2
    elif cluster == 1:  # Khá/giỏi
        if action in ['do_quiz_harder', 'skip_to_next_module']:
            cluster_bonus = 2

    print(f"Cluster bonus: {cluster_bonus}")

    total_reward = score_improvement + complete_bonus + action_bonus + cluster_bonus
    print(f"Total reward: {total_reward}")
    print("[DEBUG] ==== get_reward END ====\n")

    return total_reward


def suggest_next_action(current_state, userid):
    """
    Selects the next action using an Epsilon-Greedy policy.
    """
    filtered_actions = Config.ACTIONS.copy()
    complete_bin_resource = current_state[2]
    score_bin = current_state[3]
    section_id = current_state[0]
    complete_bin_section = safe_get(call_moodle_api('local_userlog_get_section_completion', {
        'userid': userid, 'sectionid': section_id
    }), 'completion_rate', 0)

    

    print(f"Complete_bin={complete_bin_resource}, Score_bin={score_bin}, Complete_bin_section={complete_bin_section}")

    # --- Lọc action không hợp lý ---
    if complete_bin_resource >= 0.6:
        if 'read_new_resource' in filtered_actions:
            filtered_actions.remove('read_new_resource')

    if score_bin >= 8:
        if 'do_quiz_easier' in filtered_actions:
            filtered_actions.remove('do_quiz_easier')
            
     # --- Điều kiện thêm skip_to_next_module ---
    if complete_bin_section >= 95 and score_bin >= 8:
        if 'skip_to_next_module' in filtered_actions:
            return 'skip_to_next_module', get_q_value(current_state, 'skip_to_next_module')


    # --- Exploration or Exploitation ---
    if current_state not in config.q_table or random.uniform(0, 1) < Config.EXPLORATION_RATE:
        action = random.choice(filtered_actions)
        q_value = get_q_value(current_state, action)
        return action, q_value
    else:
        q_values = {a: config.q_table[current_state][a] for a in filtered_actions}
        best_action = max(q_values, key=q_values.get)
        return best_action, q_values[best_action]
