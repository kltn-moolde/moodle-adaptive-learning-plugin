"""
Service dependencies initialization
All services are initialized here and can be imported by routes
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from services.qtable_service import QTableService
from services.model_loader import ModelLoader
from services.cluster_service import ClusterService
from services.recommendation_service import RecommendationService
from pipeline.log_processing_pipeline import LogProcessingPipeline
from services.state_repository import StateRepository
from core.state_update_manager import StateUpdateManager
from core.reward_calculator_v2 import RewardCalculatorV2
from services.moodle_api_client import MoodleAPIClient
from services.po_lo_service import POLOService
from services.midterm_weights_service import MidtermWeightsService

from .config import (
    MODEL_PATH,
    COURSE_PATH,
    CLUSTER_PROFILES_PATH,
    MOODLE_URL,
    MOODLE_TOKEN,
    MOODLE_COURSE_ID
)

# Model loader service
model_loader = ModelLoader(
    model_path=MODEL_PATH,
    course_path=COURSE_PATH,
    cluster_profiles_path=CLUSTER_PROFILES_PATH
)

# Load all components
model_loader.load_all(verbose=True)
qtable_service = QTableService(agent=model_loader.agent, action_space=model_loader.action_space)

# Initialize other services
cluster_service = ClusterService(cluster_profiles=model_loader.cluster_profiles)
recommendation_service = RecommendationService(
    agent=model_loader.agent,
    action_space=model_loader.action_space,
    state_builder=model_loader.state_builder,
    course_structure_path=str(COURSE_PATH)
)

# Initialize webhook pipeline and state repository
print("\n" + "="*70)
print("Initializing Webhook Components...")
print("="*70)

pipeline = LogProcessingPipeline(
    cluster_profiles_path=str(CLUSTER_PROFILES_PATH),
    course_structure_path=str(COURSE_PATH),
    moodle_url=MOODLE_URL,
    moodle_token=MOODLE_TOKEN,
    course_id=MOODLE_COURSE_ID,
    enable_qtable_updates=False
)

state_repository = StateRepository()

# Initialize PO/LO and Midterm Weights Services
print("\nInitializing PO/LO and Midterm Weights Services...")
po_lo_service = POLOService(data_dir=str(HERE / 'data'))
midterm_weights_service = MidtermWeightsService(data_dir=str(HERE / 'data'))

# Initialize MoodleAPIClient for API enrichment
print("\nInitializing MoodleAPIClient...")
moodle_client = MoodleAPIClient(
    moodle_url=MOODLE_URL,
    ws_token=MOODLE_TOKEN,
    course_id=MOODLE_COURSE_ID
)

# Initialize StateUpdateManager for buffered log processing
print("\nInitializing StateUpdateManager...")
reward_calculator = RewardCalculatorV2(
    cluster_profiles_path=str(CLUSTER_PROFILES_PATH),
    po_lo_path=str(HERE / 'data' / 'Po_Lo.json'),
    midterm_weights_path=str(HERE / 'data' / 'midterm_lo_weights.json'),
    course_id=MOODLE_COURSE_ID  # Pass course_id for multi-course support
)

state_update_manager = StateUpdateManager(
    state_builder=model_loader.state_builder,
    action_space=model_loader.action_space,
    reward_calculator=reward_calculator,
    min_logs_for_update=2,  # Mặc định: Tối thiểu 2 logs để cập nhật state
    max_buffer_size=50,
    time_window_seconds=300,  # 5 phút
    enable_qtable_updates=True,
    agent=model_loader.agent,
    moodle_client=moodle_client  # Truyền MoodleAPIClient để enrich với API
)

print("✓ Webhook components ready")
print("✓ StateUpdateManager initialized")
print("="*70 + "\n")

