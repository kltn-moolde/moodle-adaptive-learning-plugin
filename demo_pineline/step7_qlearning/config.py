#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Configuration
=========================
Configuration for Q-learning agent and state discretization
"""

# ===================================================================
# Q-LEARNING HYPERPARAMETERS
# ===================================================================

# Learning parameters
LEARNING_RATE = 0.1         # Alpha: How much to update Q-values
DISCOUNT_FACTOR = 0.95      # Gamma: Future reward importance
EPSILON = 0.1               # Exploration rate

# ===================================================================
# STATE DISCRETIZATION
# ===================================================================

# State binning strategy
# Options:
#   - 'decimals': Round to N decimal places (e.g., decimals=1 → 11 bins)
#   - 'quartile': 4 bins [0, 0.25, 0.5, 0.75, 1.0]
#   - 'tertile': 3 bins [0, 0.33, 0.67, 1.0]
#   - 'custom': Custom bins defined below

BINNING_STRATEGY = 'quartile'  # ✅ Changed from 'decimals' to 'quartile'

# For 'decimals' strategy
STATE_DECIMALS = 1  # Used if BINNING_STRATEGY = 'decimals'

# For 'quartile' strategy (4 bins)
# Low (0-0.25), Medium-Low (0.25-0.5), Medium-High (0.5-0.75), High (0.75-1.0)
QUARTILE_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]

# For 'tertile' strategy (3 bins)
# Low (0-0.33), Medium (0.33-0.67), High (0.67-1.0)
TERTILE_BINS = [0.0, 0.33, 0.67, 1.0]

# For 'custom' strategy - define your own bins
CUSTOM_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]

# ===================================================================
# PERFORMANCE METRICS
# ===================================================================

# Target coverage (for monitoring)
TARGET_COVERAGE_PERCENT = 0.5  # 0.5% coverage is good with quartile bins

# Expected stats with quartile binning
EXPECTED_TOTAL_STATES = 4**12  # 16,777,216 possible states
EXPECTED_QTABLE_SIZE = 50000   # ~50k states with 150k interactions

# ===================================================================
# PATHS
# ===================================================================

MODEL_PATH = 'models/qlearning_model.pkl'
DATA_PATH = 'data/simulated/latest_simulation.json'
COURSE_STRUCTURE_PATH = 'data/course_structure.json'
CLUSTER_PROFILES_PATH = 'data/cluster_profiles.json'

# ===================================================================
# TRAINING CONFIGURATION
# ===================================================================

DEFAULT_EPOCHS = 10
DEFAULT_STUDENTS = 100
DEFAULT_ACTIONS_PER_STUDENT = 30

# ===================================================================
# LLM CONFIGURATION (for Cluster Profiling)
# ===================================================================

# LLM Provider: 'gemini' or 'openai'
LLM_PROVIDER = 'gemini'

# API Keys (leave empty to use environment variables)
# Priority: Environment Variable > Config File
GEMINI_API_KEY = 'AIzaSyAPkT1V0fUCq1dqPaWk4qLHcD1GSFyXawU'  # Set your Gemini API key here if not using env var
OPENAI_API_KEY = ''  # Set your OpenAI API key here if not using env var

# Note: For security, it's recommended to use environment variables instead:
#   export GOOGLE_API_KEY='your-key'
#   export GEMINI_API_KEY='your-key'
#   export OPENAI_API_KEY='your-key'
