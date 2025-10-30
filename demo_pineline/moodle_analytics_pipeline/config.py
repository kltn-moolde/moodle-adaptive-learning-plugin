#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Configuration
=====================
Centralized configuration for all pipeline parameters
"""

# ============================================================================
# INPUT DATA PATHS
# ============================================================================
INPUT_GRADES_PATH = '../data/udk_moodle_grades_course_670.filtered.csv'
INPUT_LOGS_PATH = '../data/udk_moodle_log_course_670.filtered.csv'

# ============================================================================
# OUTPUT DIRECTORIES
# ============================================================================
BASE_OUTPUT_DIR = 'outputs'
FEATURES_OUTPUT_DIR = 'outputs/features'
CLUSTERING_OUTPUT_DIR = 'outputs/clustering'
SIMULATION_OUTPUT_DIR = 'outputs/simulation'
COMPARISON_OUTPUT_DIR = 'outputs/comparison'

# ============================================================================
# FEATURE EXTRACTION SETTINGS
# ============================================================================
# Normalization method
NORMALIZATION_METHOD = 'minmax'  # Options: 'minmax', 'standard', 'robust'

# Feature selection
MIN_FEATURE_VARIANCE = 0.0  # Minimum variance threshold (0 = keep all)
MAX_FEATURES = None  # Maximum number of features (None = use all)

# ============================================================================
# CLUSTERING SETTINGS
# ============================================================================
# Number of clusters (None = auto-detect)
N_CLUSTERS = None

# Auto-detection settings
MIN_CLUSTERS = 2
MAX_CLUSTERS = 10
USE_ELBOW_METHOD = True
USE_SILHOUETTE_SCORE = True
USE_DAVIES_BOULDIN = True

# KMeans parameters
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10
KMEANS_MAX_ITER = 300

# ============================================================================
# SIMULATION SETTINGS
# ============================================================================
# Number of students to simulate
N_SIMULATED_STUDENTS = 100

# Noise level for simulation (0.0 = no noise, 1.0 = high noise)
SIMULATION_NOISE_LEVEL = 0.1

# Simulation random state
SIMULATION_RANDOM_STATE = 42

# Cluster distribution (None = use real distribution)
CLUSTER_DISTRIBUTION = None  # Example: [0.3, 0.3, 0.4] for 3 clusters

# ============================================================================
# COMPARISON & VISUALIZATION SETTINGS
# ============================================================================
# Number of features to compare
MAX_FEATURES_TO_COMPARE = 15

# Statistical test thresholds
KS_TEST_ALPHA = 0.05  # Significance level for KS test
CHI2_TEST_ALPHA = 0.05  # Significance level for Chi-square test

# Visualization settings
FIGURE_DPI = 300
FIGURE_FORMAT = 'png'  # Options: 'png', 'pdf', 'svg'

# Color schemes
REAL_COLOR = 'steelblue'
SIMULATED_COLOR = 'coral'
CLUSTER_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# ============================================================================
# LOGGING SETTINGS
# ============================================================================
LOG_LEVEL = 'INFO'  # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_FILE = 'pipeline.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
# Parallel processing
N_JOBS = -1  # Number of CPU cores to use (-1 = all cores)

# Memory management
MEMORY_EFFICIENT_MODE = False  # Use chunking for large datasets

# ============================================================================
# VALIDATION SETTINGS
# ============================================================================
# Enable/disable validation steps
VALIDATE_INPUT_DATA = True
VALIDATE_FEATURE_QUALITY = True
VALIDATE_CLUSTER_QUALITY = True
VALIDATE_SIMULATION_QUALITY = True

# Data validation thresholds
MIN_STUDENTS = 10
MIN_FEATURES = 3
MAX_MISSING_RATIO = 0.3  # Maximum ratio of missing values

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
# PCA settings for visualization
PCA_N_COMPONENTS = 2
PCA_RANDOM_STATE = 42

# Feature importance
CALCULATE_FEATURE_IMPORTANCE = True

# Export formats
EXPORT_JSON = True
EXPORT_CSV = True
EXPORT_PLOTS = True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config_dict():
    """Return all configuration as dictionary"""
    return {
        'input': {
            'grades_path': INPUT_GRADES_PATH,
            'logs_path': INPUT_LOGS_PATH
        },
        'output': {
            'base_dir': BASE_OUTPUT_DIR,
            'features_dir': FEATURES_OUTPUT_DIR,
            'clustering_dir': CLUSTERING_OUTPUT_DIR,
            'simulation_dir': SIMULATION_OUTPUT_DIR,
            'comparison_dir': COMPARISON_OUTPUT_DIR
        },
        'feature_extraction': {
            'normalization': NORMALIZATION_METHOD,
            'min_variance': MIN_FEATURE_VARIANCE,
            'max_features': MAX_FEATURES
        },
        'clustering': {
            'n_clusters': N_CLUSTERS,
            'min_clusters': MIN_CLUSTERS,
            'max_clusters': MAX_CLUSTERS,
            'random_state': KMEANS_RANDOM_STATE,
            'n_init': KMEANS_N_INIT,
            'max_iter': KMEANS_MAX_ITER
        },
        'simulation': {
            'n_students': N_SIMULATED_STUDENTS,
            'noise_level': SIMULATION_NOISE_LEVEL,
            'random_state': SIMULATION_RANDOM_STATE,
            'cluster_distribution': CLUSTER_DISTRIBUTION
        },
        'comparison': {
            'max_features': MAX_FEATURES_TO_COMPARE,
            'ks_alpha': KS_TEST_ALPHA,
            'chi2_alpha': CHI2_TEST_ALPHA
        },
        'visualization': {
            'dpi': FIGURE_DPI,
            'format': FIGURE_FORMAT,
            'real_color': REAL_COLOR,
            'simulated_color': SIMULATED_COLOR
        },
        'logging': {
            'level': LOG_LEVEL,
            'file': LOG_FILE,
            'format': LOG_FORMAT
        }
    }


def print_config():
    """Print current configuration"""
    import json
    config = get_config_dict()
    print(json.dumps(config, indent=2))


if __name__ == '__main__':
    print("Current Pipeline Configuration:")
    print("="*80)
    print_config()
