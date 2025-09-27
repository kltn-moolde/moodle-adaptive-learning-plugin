import json
import threading
import os
from config import Config

DEFAULT_STATE_PATH = Config.DEFAULT_STATE_PATH
lock = threading.Lock()

def load_last_state_action():
    if not os.path.exists(DEFAULT_STATE_PATH):
        return {}
    try:
        with open(DEFAULT_STATE_PATH, "r") as f:
            raw = json.load(f)
            return {k: (tuple(v[0]), v[1]) for k, v in raw.items()}
    except Exception:
        return {}

def save_last_state_action(last_state_action):
    with lock:
        with open(DEFAULT_STATE_PATH, "w") as f:
            json.dump(last_state_action, f)
            