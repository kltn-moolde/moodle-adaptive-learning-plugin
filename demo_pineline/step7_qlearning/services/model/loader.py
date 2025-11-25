"""
Model Loader Service
Handles loading and initialization of all model components
Supports multi-course with course_id parameter
"""
from pathlib import Path
from typing import Optional, Union
import json
import sys

# Import config for paths
try:
    import config
    PROJECT_ROOT = config.PROJECT_ROOT
except ImportError:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from core.rl.action_space import ActionSpace
from core.rl.state_builder import StateBuilderV2
from core.rl.agent import QLearningAgentV2
from services.model.qtable_service import QTableService
from services.business.llm_profiler import LLMClusterProfiler


class ModelLoader:
    """Service for loading and managing model components for a specific course"""
    
    def __init__(
        self,
        course_id: int,
        model_path: Optional[Union[Path, str]] = None,
        course_path: Optional[Union[Path, str]] = None,
        cluster_profiles_path: Optional[Union[Path, str]] = None
    ):
        """
        Initialize model loader for a specific course
        
        Args:
            course_id: Course ID (required for multi-course support)
            model_path: Optional path to model file. If None, uses: models/qtable_{course_id}.pkl
            course_path: Optional path to course structure. If None, uses: data/local/course_structure_{course_id}.json
            cluster_profiles_path: Optional path to cluster profiles. If None, uses: data/cluster_profiles.json
        """
        self.course_id = course_id
        
        # Auto-generate paths if not provided
        if model_path is None:
            model_path = PROJECT_ROOT / 'models' / f'qtable_{course_id}.pkl'
        if course_path is None:
            # Try course-specific first, then fallback to default
            course_path = PROJECT_ROOT / 'data' / 'local' / f'course_structure_{course_id}.json'
            if not course_path.exists():
                course_path = PROJECT_ROOT / 'data' / 'course_structure.json'
        if cluster_profiles_path is None:
            cluster_profiles_path = PROJECT_ROOT / 'data' / 'cluster_profiles.json'
        
        self.model_path = Path(model_path)
        self.course_path = Path(course_path)
        self.cluster_profiles_path = Path(cluster_profiles_path)
        
        # Components
        self.action_space: Optional[ActionSpace] = None
        self.state_builder: Optional[StateBuilderV2] = None
        self.agent: Optional[QLearningAgentV2] = None
        self.qtable_service: Optional[QTableService] = None
        self.cluster_profiles: dict = {}
        self.llm_profiler: Optional[LLMClusterProfiler] = None
        
    def load_all(self, verbose: bool = True):
        """Load all components"""
        if verbose:
            print(f'Starting Adaptive Learning API — loading components for course {self.course_id}...')
        
        # Load action space
        self._load_action_space(verbose)
        
        # Load state builder
        self._load_state_builder(verbose)
        
        # Load agent
        self._load_agent(verbose)
        
        # Initialize services
        self._initialize_services(verbose)
        
        # Load cluster profiles
        self._load_cluster_profiles(verbose)
        
        # Initialize LLM profiler
        self._initialize_llm_profiler(verbose)
        
        if verbose:
            print('✓ All components loaded successfully')
    
    def _load_action_space(self, verbose: bool = True):
        """Load action space from course structure"""
        if not self.course_path.exists():
            if verbose:
                print(f'Warning: course_structure.json not found at {self.course_path}')
            self.action_space = None
            return
        
        self.action_space = ActionSpace(str(self.course_path))
        if verbose:
            print(f'Loaded action space: {self.action_space.get_action_count()} actions')
    
    def _load_state_builder(self, verbose: bool = True):
        """Load state builder V2"""
        if not self.cluster_profiles_path.exists() or not self.course_path.exists():
            if verbose:
                print(f'Warning: Required files not found')
            self.state_builder = None
            return
        
        self.state_builder = StateBuilderV2(
            cluster_profiles_path=str(self.cluster_profiles_path),
            course_structure_path=str(self.course_path)
        )
        if verbose:
            print(f'✓ State builder V2 ready (6 dimensions)')
    
    def _load_agent(self, verbose: bool = True):
        """Load Q-learning agent"""
        if not self.model_path.exists() or not self.action_space:
            if verbose:
                print(f'No trained model found at {self.model_path} — recommendations will fallback to random')
            self.agent = None
            return
        
        try:
            # Create agent and use its load() method (handles string → tuple conversion)
            self.agent = QLearningAgentV2(n_actions=self.action_space.get_action_count())
            self.agent.load(str(self.model_path))
            if verbose:
                print(f'✓ Loaded model from {self.model_path} ({len(self.agent.q_table)} states)')
        except Exception as e:
            if verbose:
                print(f'Warning: failed to load model: {e}')
            self.agent = None
    
    def _initialize_services(self, verbose: bool = True):
        """Initialize Q-table service"""
        self.qtable_service = QTableService(agent=self.agent)
        if verbose:
            print('Q-table service initialized')
    
    def _load_cluster_profiles(self, verbose: bool = True):
        """Load cluster profiles from JSON"""
        if not self.cluster_profiles_path.exists():
            if verbose:
                print(f'Warning: cluster_profiles.json not found at {self.cluster_profiles_path}')
            self.cluster_profiles = {}
            return
        
        with open(self.cluster_profiles_path, 'r', encoding='utf-8') as f:
            self.cluster_profiles = json.load(f)
        
        if self.cluster_profiles and verbose:
            n_clusters = len(self.cluster_profiles.get('cluster_stats', {}))
            print(f'Loaded cluster profiles: {n_clusters} clusters')
    
    def _initialize_llm_profiler(self, verbose: bool = True):
        """Initialize LLM Cluster Profiler (optional)"""
        try:
            import os
            # Try to load config
            try:
                import config
                llm_provider = getattr(config, 'LLM_PROVIDER', 'gemini')
                config_gemini_key = getattr(config, 'GEMINI_API_KEY', '')
                config_openai_key = getattr(config, 'OPENAI_API_KEY', '')
            except:
                llm_provider = 'gemini'
                config_gemini_key = ''
                config_openai_key = ''
            
            # Check if API key available
            has_gemini_key = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY') or config_gemini_key)
            has_openai_key = bool(os.getenv('OPENAI_API_KEY') or config_openai_key)
            
            if has_gemini_key or has_openai_key:
                # Pass API key to LLMProfiler
                api_key = None
                if llm_provider == 'gemini':
                    api_key = config_gemini_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                elif llm_provider == 'openai':
                    api_key = config_openai_key or os.getenv('OPENAI_API_KEY')
                
                self.llm_profiler = LLMClusterProfiler(
                    cluster_profiles_path=str(self.cluster_profiles_path),
                    llm_provider=llm_provider,
                    api_key=api_key
                )
                if verbose:
                    print(f'✓ LLM Cluster Profiler initialized (provider: {llm_provider})')
            else:
                self.llm_profiler = None
                if verbose:
                    print('ℹ LLM Cluster Profiler disabled (no API key found)')
        except Exception as e:
            self.llm_profiler = None
            if verbose:
                print(f'Warning: LLM Cluster Profiler initialization failed: {e}')
    
    def get_model_info(self) -> dict:
        """Get model information"""
        if not self.agent:
            return {
                'model_loaded': False,
                'course_id': self.course_id,
                'n_actions': 0,
                'n_states_in_qtable': 0
            }
        
        stats = self.agent.get_statistics()
        return {
            'model_loaded': True,
            'course_id': self.course_id,
            'model_version': 'V2',
            'n_actions': self.agent.n_actions,
            'state_dimensions': 6,
            'state_structure': '(cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level)',
            'n_states_in_qtable': len(self.agent.q_table),
            'episodes': stats.get('episodes_trained', 0),
            'avg_reward': 0.0,  # Not tracked in new format
            'coverage': f"{(len(self.agent.q_table) / 4320 * 100):.2f}%"  # 5*6*4*4*3*3 = 4,320 states
        }
