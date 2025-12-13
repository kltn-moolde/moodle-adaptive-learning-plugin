#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clustering Service Configuration
==================================
Centralized configuration for automated clustering service
"""

import os
from pathlib import Path

# ===================================================================
# BASE PATHS
# ===================================================================

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_PATH = PROJECT_ROOT / 'outputs'

# ===================================================================
# MOODLE API CONFIGURATION
# ===================================================================

MOODLE_URL = os.getenv("MOODLE_URL", "http://localhost:8100")

# Custom API Token (for local_* APIs - custom endpoints)
MOODLE_CUSTOM_TOKEN = os.getenv("MOODLE_CUSTOM_TOKEN", "86e86e0301d495db032da3b855180f5f")

# Standard Moodle Web Service Token (for core_* APIs)
MOODLE_STANDARD_TOKEN = os.getenv("MOODLE_STANDARD_TOKEN", "eb4a1ea54118eb52574ac5ede106dbd3")

# API endpoint configuration
MOODLE_WEBSERVICE_ENDPOINT = f"{MOODLE_URL}/webservice/rest/server.php"

# Default limit for log fetching
MOODLE_LOG_LIMIT = int(os.getenv("MOODLE_LOG_LIMIT", "1000000"))

# ===================================================================
# MONGODB CONFIGURATION
# ===================================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/"
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "clustering_service")

# Collection names
COLLECTION_COURSE_CLUSTERS = "course_clusters"
COLLECTION_USER_CLUSTER_HISTORY = "user_cluster_history"
COLLECTION_CLUSTER_SNAPSHOTS = "cluster_snapshots"

# ===================================================================
# LLM CONFIGURATION
# ===================================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyCiX6FffxgOZi1SSOhVJGzcYkqpZadlV3Y"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ENABLE_LLM_PROFILING = os.getenv("ENABLE_LLM_PROFILING", "true").lower() == "true"

# ===================================================================
# CLUSTERING CONFIGURATION
# ===================================================================

# Feature extraction settings
MIN_VARIANCE_THRESHOLD = float(os.getenv("MIN_VARIANCE_THRESHOLD", "0.01"))
MAX_CORRELATION_THRESHOLD = float(os.getenv("MAX_CORRELATION_THRESHOLD", "0.95"))

# KMeans settings
MIN_CLUSTERS = int(os.getenv("MIN_CLUSTERS", "2"))
MAX_CLUSTERS = int(os.getenv("MAX_CLUSTERS", "10"))
KMEANS_RANDOM_STATE = int(os.getenv("KMEANS_RANDOM_STATE", "42"))
KMEANS_MAX_ITER = int(os.getenv("KMEANS_MAX_ITER", "300"))

# Minimum students required for clustering
MIN_STUDENTS_FOR_CLUSTERING = int(os.getenv("MIN_STUDENTS_FOR_CLUSTERING", "10"))

# ===================================================================
# SCHEDULER CONFIGURATION
# ===================================================================

# Cron format: minute hour day month day_of_week
CLUSTER_JOB_SCHEDULE = os.getenv("CLUSTER_JOB_SCHEDULE", "0 2 * * *")  # Daily at 2AM
CLUSTER_JOB_ENABLED = os.getenv("CLUSTER_JOB_ENABLED", "true").lower() == "true"
CLUSTER_JOB_RETRY_ATTEMPTS = int(os.getenv("CLUSTER_JOB_RETRY_ATTEMPTS", "3"))

# Retry backoff settings (in seconds)
RETRY_BACKOFF_DELAYS = [60, 300, 900]  # 1min, 5min, 15min

# Courses to run clustering on (comma-separated course IDs)
# Empty means run on all courses with enrolled students
CLUSTER_TARGET_COURSES = os.getenv("CLUSTER_TARGET_COURSES", "")  # e.g., "5,42,670"

# ===================================================================
# API CONFIGURATION
# ===================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# ===================================================================
# LOGGING CONFIGURATION
# ===================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
