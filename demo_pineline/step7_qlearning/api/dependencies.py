"""
Service dependencies initialization
All services are initialized here and can be imported by routes
Supports multi-course with ModelManager
"""
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from services.model.qtable_service import QTableService
from services.model.manager import ModelManager
from services.business.cluster import ClusterService
from services.business.recommendation import RecommendationService
from pipeline.log_processing_pipeline import LogProcessingPipeline
from services.repository.state_repository import StateRepository
from core.log_processing.state_manager import StateUpdateManager
from core.rl.reward_calculator import RewardCalculatorV2
from services.clients.moodle_client import MoodleAPIClient
from services.business.po_lo import POLOService
from services.business.midterm_weights import MidtermWeightsService

from .config import (
    CLUSTER_PROFILES_PATH,
    MOODLE_URL,
    MOODLE_TOKEN,
    DEFAULT_COURSE_ID,
    get_course_path
)

# ===================================================================
# Multi-course Model Manager
# ===================================================================

# Initialize ModelManager (lazy loading, supports multiple courses)
model_manager = ModelManager(default_course_id=DEFAULT_COURSE_ID)

# Backward compatibility: Get default model loader
def get_default_model_loader():
    """Get default model loader for backward compatibility"""
    return model_manager.get_loader(DEFAULT_COURSE_ID, verbose=False)

model_loader = get_default_model_loader()

# ===================================================================
# Helper functions to get services for a specific course
# ===================================================================

def get_services_for_course(course_id: int):
    """
    Get all services for a specific course
    
    Returns:
        dict with keys: loader, qtable_service, cluster_service, recommendation_service
    """
    loader = model_manager.get_loader(course_id, verbose=False)
    course_path = get_course_path(course_id)
    
    return {
        'loader': loader,
        'qtable_service': QTableService(agent=loader.agent, action_space=loader.action_space),
        'cluster_service': ClusterService(cluster_profiles=loader.cluster_profiles),
        'recommendation_service': RecommendationService(
            agent=loader.agent,
            action_space=loader.action_space,
            state_builder=loader.state_builder,
            course_structure_path=str(course_path)
        )
    }

# Initialize default services (for backward compatibility)
qtable_service = QTableService(agent=model_loader.agent, action_space=model_loader.action_space)
cluster_service = ClusterService(cluster_profiles=model_loader.cluster_profiles)
recommendation_service = RecommendationService(
    agent=model_loader.agent,
    action_space=model_loader.action_space,
    state_builder=model_loader.state_builder,
    course_structure_path=str(get_course_path(DEFAULT_COURSE_ID))
)

# ===================================================================
# Shared Services (not course-specific)
# ===================================================================

state_repository = StateRepository()

# Initialize PO/LO and Midterm Weights Services
po_lo_service = POLOService(data_dir=str(HERE / 'data'))
midterm_weights_service = MidtermWeightsService(data_dir=str(HERE / 'data'))

# Initialize MoodleAPIClient (course_id will be set per request)
moodle_client = MoodleAPIClient(
    moodle_url=MOODLE_URL,
    ws_token=MOODLE_TOKEN,
    course_id=None  # Will be set dynamically per request
)

# ===================================================================
# Helper function to get StateUpdateManager for a course
# ===================================================================

def get_state_update_manager_for_course(course_id: int) -> StateUpdateManager:
    """
    Get StateUpdateManager for a specific course
    
    Args:
        course_id: Course ID
        
    Returns:
        StateUpdateManager instance configured for the course
    """
    services = get_services_for_course(course_id)
    loader = services['loader']
    course_path = get_course_path(course_id)
    
    # Create reward calculator for this course
    reward_calculator = RewardCalculatorV2(
        cluster_profiles_path=str(CLUSTER_PROFILES_PATH),
        po_lo_path=str(HERE / 'data' / 'Po_Lo.json'),
        midterm_weights_path=str(HERE / 'data' / 'midterm_lo_weights.json'),
        course_id=course_id
    )
    
    # Create Moodle client for this course
    course_moodle_client = MoodleAPIClient(
        moodle_url=MOODLE_URL,
        ws_token=MOODLE_TOKEN,
        course_id=course_id
    )
    
    return StateUpdateManager(
        state_builder=loader.state_builder,
        action_space=loader.action_space,
        reward_calculator=reward_calculator,
        min_logs_for_update=2,
        max_buffer_size=50,
        time_window_seconds=300,
        enable_qtable_updates=True,
        agent=loader.agent,
        moodle_client=course_moodle_client
    )

# Backward compatibility: Default StateUpdateManager (for default course)
state_update_manager = get_state_update_manager_for_course(DEFAULT_COURSE_ID)

print("✓ Multi-course services initialized")
print(f"✓ Default course: {DEFAULT_COURSE_ID}")
print("="*70 + "\n")

