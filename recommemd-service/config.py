import threading

# --- Q-learning hyperparameters ---
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 0.2

# --- Moodle API ---
MOODLE_URL = 'http://localhost:8100/webservice/rest/server.php'
TOKEN = '7e6e5e687f484ae22d9b686e712c1060'

# --- Actions ---
ACTIONS = [
    'read_new_resource', 'review_old_resource',
    'attempt_new_quiz', 'redo_failed_quiz',
    'skip_to_next_module', 'do_quiz_harder',
    'do_quiz_easier', 'do_quiz_same'
]

# --- Discretization bins ---
SCORE_AVG_BINS = [0, 2, 4, 6, 8]
COMPLETE_RATE_BINS = [0.0, 0.3, 0.6]

# --- File paths & global variables ---
LOG_FILE_PATH = "/Users/nguyenhuuloc/Documents/MyComputer/moodledata/local_userlog_data/user_log_summary.csv"
USER_CLUSTERS_CSV = "./synthetic_user_features_clustered.csv"
COURSE_HIERARCHY_JSON = 'json_course_moodle_hierarchy_clean.json'

q_table = {}
q_table_lock = threading.Lock()
last_state_action = {}
section_ids = []
user_clusters_df = None