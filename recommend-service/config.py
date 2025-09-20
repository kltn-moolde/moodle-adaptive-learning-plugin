import os
import threading

class Config:
    # --- Moodle API ---
    MOODLE_API_BASE = os.getenv(
        "MOODLE_API_BASE",
        "http://localhost:8100/webservice/rest/server.php"
    )
    TOKEN_PLUGIN_PHP_MOODLE = os.getenv(
        "TOKEN_PLUGIN_PHP_MOODLE",
        "7e6e5e687f484ae22d9b686e712c1060"
    )

    # --- Course Service ---
    ADDRESS_COURSE_SERVICE_BASE = os.getenv(
        "ADDRESS_COURSE_SERVICE_BASE",
        "http://127.0.0.1:5001"
    )
    COURSE_ID = int(os.getenv("COURSE_ID", 5))

    # --- User Clusters ---
    USER_CLUSTERS_CSV = os.getenv(
        "USER_CLUSTERS_CSV",
        "https://res.cloudinary.com/doycy5gbl/raw/upload/v1758335677/synthetic_user_features_clustered_p7ps1r.csv"
    )
    
    DEFAULT_QTABLE_PATH = os.getenv(
        "DEFAULT_QTABLE_PATH", 
        "/data/q_table_results.csv")

    # --- Q-learning hyperparameters ---
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", 0.1))
    DISCOUNT_FACTOR = float(os.getenv("DISCOUNT_FACTOR", 0.9))
    EXPLORATION_RATE = float(os.getenv("EXPLORATION_RATE", 0.2))

    # --- Discretization bins ---
    SCORE_AVG_BINS = [0, 2, 4, 6, 8]
    COMPLETE_RATE_BINS = [0.0, 0.3, 0.6]

    # --- Actions ---
    ACTIONS = [
        'read_new_resource', 'review_old_resource',
        'attempt_new_quiz', 'redo_failed_quiz',
        'skip_to_next_module', 'do_quiz_harder',
        'do_quiz_easier', 'do_quiz_same'
    ]


# --- Q-learning shared states ---
q_table = {}
q_table_lock = threading.Lock()
last_state_action = {}
section_ids = []
user_clusters_df = None