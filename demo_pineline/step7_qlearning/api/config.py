"""
Configuration constants for API service
"""
from pathlib import Path

# Base directory
HERE = Path(__file__).resolve().parent.parent

# Model and data paths
MODEL_PATH = HERE / 'models' / 'qtable.pkl'  # Trained model
COURSE_PATH = HERE / 'data' / 'local' / 'course_structure_5.json'  # Course structure for course_id=5
CLUSTER_PROFILES_PATH = HERE / 'data' / 'cluster_profiles.json'

# Moodle API Configuration (for log enrichment)
MOODLE_URL = "http://localhost:8100"  # Your Moodle instance
MOODLE_TOKEN = "4b46e553766600e4d15b284aec0434cb"  # Web service token
MOODLE_COURSE_ID = 5  # Course ID

