#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Configuration File
============================
Tất cả config cho toàn bộ chương trình tập trung tại đây
"""

import os
from pathlib import Path

# ===================================================================
# BASE PATHS
# ===================================================================

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent
HERE = PROJECT_ROOT  # Alias for backward compatibility

# ===================================================================
# MODEL & DATA PATHS
# ===================================================================

# Multi-course support: Use templates for dynamic paths
MODEL_PATH_TEMPLATE = PROJECT_ROOT / 'models' / 'qtable_{course_id}.pkl'
COURSE_PATH_TEMPLATE = PROJECT_ROOT / 'data' / 'local' / 'course_structure_{course_id}.json'
COURSE_PATH_FALLBACK = PROJECT_ROOT / 'data' / 'course_structure.json'

# Helper function to get model path for a course
def get_model_path(course_id: int) -> Path:
    """Get model path for a specific course"""
    return PROJECT_ROOT / 'models' / f'qtable_{course_id}.pkl'

# Helper function to get course structure path for a course
def get_course_path(course_id: int) -> Path:
    """Get course structure path for a specific course (with fallback)"""
    course_path = PROJECT_ROOT / 'data' / 'local' / f'course_structure_{course_id}.json'
    if course_path.exists():
        return course_path
    return COURSE_PATH_FALLBACK

# Backward compatibility: Default paths (for course_id=5 or legacy code)
DEFAULT_COURSE_ID = int(os.getenv("DEFAULT_COURSE_ID", "5"))  # Default course for backward compatibility
MODEL_PATH = get_model_path(DEFAULT_COURSE_ID)
COURSE_PATH = get_course_path(DEFAULT_COURSE_ID)
CLUSTER_PROFILES_PATH = PROJECT_ROOT / 'data' / 'cluster_profiles.json'
DATA_PATH = PROJECT_ROOT / 'data'
REWARD_CONFIG_PATH = PROJECT_ROOT / 'config' / 'reward_config.json'

# ===================================================================
# MOODLE API CONFIGURATION
# ===================================================================

MOODLE_URL = os.getenv("MOODLE_URL", "http://localhost:8100")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "4b46e553766600e4d15b284aec0434cb")
# NOTE: MOODLE_COURSE_ID removed - course_id should come from requests/logs

# ===================================================================
# MONGODB CONFIGURATION
# ===================================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/courseservice?retryWrites=true&w=majority&appName=Cluster0"
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "recommendservice")
COLLECTION_USER_STATES = "user_states"
COLLECTION_STATE_HISTORY = "state_history"
COLLECTION_RECOMMENDATIONS = "recommendations"
COLLECTION_LOGS = "logs"
COLLECTION_LOG_EVENTS = "log_events"  # Alias for COLLECTION_LOGS

# ===================================================================
# Q-LEARNING HYPERPARAMETERS
# ===================================================================

LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.1"))
DISCOUNT_FACTOR = float(os.getenv("DISCOUNT_FACTOR", "0.95"))
EPSILON = float(os.getenv("EPSILON", "0.1"))

# ===================================================================
# STATE DISCRETIZATION
# ===================================================================

BINNING_STRATEGY = os.getenv("BINNING_STRATEGY", "quartile")
STATE_DECIMALS = int(os.getenv("STATE_DECIMALS", "1"))
QUARTILE_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]
TERTILE_BINS = [0.0, 0.33, 0.67, 1.0]
CUSTOM_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]

# ===================================================================
# PERFORMANCE METRICS
# ===================================================================

TARGET_COVERAGE_PERCENT = float(os.getenv("TARGET_COVERAGE_PERCENT", "0.5"))
EXPECTED_TOTAL_STATES = 4**12
EXPECTED_QTABLE_SIZE = 50000

# ===================================================================
# TRAINING CONFIGURATION
# ===================================================================

DEFAULT_EPOCHS = int(os.getenv("DEFAULT_EPOCHS", "10"))
DEFAULT_STUDENTS = int(os.getenv("DEFAULT_STUDENTS", "100"))
DEFAULT_ACTIONS_PER_STUDENT = int(os.getenv("DEFAULT_ACTIONS_PER_STUDENT", "30"))

# ===================================================================
# LLM CONFIGURATION (for Cluster Profiling)
# ===================================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "AIzaSyAPkT1V0fUCq1dqPaWk4qLHcD1GSFyXawU"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ===================================================================
# API CONFIGURATION
# ===================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# ===================================================================
# WEBHOOK CONFIGURATION
# ===================================================================

WEBHOOK_MIN_LOGS_FOR_UPDATE = int(os.getenv("WEBHOOK_MIN_LOGS_FOR_UPDATE", "2"))
WEBHOOK_MAX_BUFFER_SIZE = int(os.getenv("WEBHOOK_MAX_BUFFER_SIZE", "50"))
WEBHOOK_TIME_WINDOW_SECONDS = int(os.getenv("WEBHOOK_TIME_WINDOW_SECONDS", "300"))
WEBHOOK_ENABLE_QTABLE_UPDATES = os.getenv("WEBHOOK_ENABLE_QTABLE_UPDATES", "true").lower() == "true"

# ===================================================================
# BACKWARD COMPATIBILITY
# ===================================================================

# Alias for old imports
COURSE_STRUCTURE_PATH = COURSE_PATH
