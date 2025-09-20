# q_learning.py
import pandas as pd
import json
import os
import random
import requests
import time
from config import *

section_ids = []
user_clusters_df = None

def load_data():
    global section_ids, user_clusters_df
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
                    section_ids.append(lesson["sectionIdNew"])

        # 3. Load user_clusters.csv
        user_clusters_df = pd.read_csv(Config.USER_CLUSTERS_CSV)

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
    for section_id in section_ids:
        for level in levels:
            for complete_rate in Config.COMPLETE_RATE_BINS:
                for score_bin in Config.SCORE_AVG_BINS:
                    state = (section_id, level, complete_rate, score_bin)
                    initial_q_table[state] = {action: 0.0 for action in Config.ACTIONS}
    save_q_table_to_csv(initial_q_table, filename)
    return initial_q_table

def save_q_table_to_csv(q_table_to_save, filename=Config.DEFAULT_QTABLE_PATH):
    q_table_data = []
    for state, actions_dict in q_table_to_save.items():
        for action, q_value in actions_dict.items():
            row = {
                'sectionid': state[0], 'level': state[1],
                'complete_rate': state[2], 'score_bin': state[3],
                'action': action, 'q_value': q_value
            }
            q_table_data.append(row)
    pd.DataFrame(q_table_data).to_csv(filename, index=False)

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
    for b in reversed(Config.SCORE_AVG_BINS):
        if score >= b: return b
    return Config.SCORE_AVG_BINS[0]

def discretize_complete_rate(rate):
    for b in reversed(Config.COMPLETE_RATE_BINS):
        if rate >= b: return b
    return Config.COMPLETE_RATE_BINS[0]

# --- Moodle API ---
def call_moodle_api(function, extra_params):
    params = {'wstoken': Config.TOKEN_PLUGIN_PHP_MOODLE, 'moodlewsrestformat': 'json', 'wsfunction': function}
    params.update(extra_params)
    try:
        response = requests.post(Config.MOODLE_API_BASE, data=params, timeout=10)
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
    global user_clusters_df
    if user_clusters_df is None:
        return None
    row = user_clusters_df[user_clusters_df['userid']==user_id]
    return row.iloc[0]['cluster'] if not row.empty else None

# --- State & reward ---
def get_state_from_moodle(userid, courseid, sectionid, objecttype, objectid):
    avg_score_data = call_moodle_api('local_userlog_get_user_section_avg_grade', {
        'userid': userid, 'courseid': courseid, 'sectionid': sectionid
    })
    avg_score = safe_get(avg_score_data, 'avg_section_grade', 0)

    quiz_level = 'medium'
    if objecttype == "quiz":
        quiz_level_data = call_moodle_api('local_userlog_get_quiz_tags', {'quizid': objectid})
        quiz_level = safe_get(quiz_level_data, 'tag_name', 'medium')

    total_resources = safe_get(call_moodle_api('local_userlog_get_total_resources_by_section', {
        'sectionid': sectionid, 'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
    }), 'total_resources', 0)
    viewed_resources = safe_get(call_moodle_api('local_userlog_get_viewed_resources_distinct_by_section', {
        'userid': userid, 'courseid': courseid, 'sectionid': sectionid,
        'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
    }), 'viewed_resources', 0)
    complete_rate = viewed_resources / total_resources if total_resources>0 else 0.0

    passed_lastest_quiz = safe_get(call_moodle_api('local_userlog_get_latest_quiz_pass_status_by_section',{
        'sectionid': sectionid, 'userid': userid
    }),'is_passed',0)==1

    state = (sectionid, quiz_level, discretize_complete_rate(complete_rate), discretize_score(avg_score))
    return state, passed_lastest_quiz

def get_q_value(state, action):
    global q_table
    if state not in q_table:
        q_table[state] = {a:0.0 for a in Config.ACTIONS}
    return q_table[state][action]

def update_q_table(state, action, reward, next_state):
    global q_table
    current_q = get_q_value(state, action)
    max_future_q = max(q_table[next_state].values()) if next_state in q_table else 0.0
    q_table[state][action] = current_q + Config.LEARNING_RATE * (reward + Config.DISCOUNT_FACTOR * max_future_q - current_q)

def get_reward(action, old_score, new_score, old_complete, new_complete, cluster=None, quiz_level='medium', passed_hard_quiz=1):
    score_improvement = new_score - old_score
    complete_bonus = (new_complete - old_complete) * 10
    action_bonus = 0
    cluster_bonus = 0
    
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


    # --- Cluster-based personalization ---
    if cluster == 0:  # Yếu
        if action in ['review_old_resource', 'redo_failed_quiz', 'do_quiz_easier']:
            cluster_bonus = 2
    elif cluster == 1:  # Khá/giỏi
        if action in ['do_quiz_harder', 'skip_to_next_module']:
            cluster_bonus = 2


    total_reward = score_improvement + complete_bonus + action_bonus + cluster_bonus
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
    if current_state not in q_table or random.uniform(0, 1) < Config.EXPLORATION_RATE:
        action = random.choice(filtered_actions)
        q_value = get_q_value(current_state, action)
        return action, q_value
    else:
        q_values = {a: q_table[current_state][a] for a in filtered_actions}
        best_action = max(q_values, key=q_values.get)
        return best_action, q_values[best_action]
