"""
Configuration constants for API service
DEPRECATED: Import from root config.py instead
"""
# Import from root config for backward compatibility
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    MODEL_PATH,
    COURSE_PATH,
    CLUSTER_PROFILES_PATH,
    MOODLE_URL,
    MOODLE_TOKEN,
    DEFAULT_COURSE_ID,
    HERE,
    PROJECT_ROOT,
    get_model_path,
    get_course_path
)

