"""
Model Loader Service
Handles loading and initialization of all model components
"""
from pathlib import Path
from typing import Optional
import json

from core.action_space import ActionSpace
from core.state_builder_v2 import StateBuilderV2
from core.qlearning_agent_v2 import QLearningAgentV2
from services.qtable_service import QTableService
from services.llm_cluster_profiler import LLMClusterProfiler


class ModelLoader:
    """Service for loading and managing model components"""
    
    def __init__(
        self,
        model_path: Path,
        course_path: Path,
        cluster_profiles_path: Path
    ):
        self.model_path = model_path
        self.course_path = course_path
        self.cluster_profiles_path = cluster_profiles_path
        
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
            print('Starting Adaptive Learning API — loading components...')
        
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
                self.llm_profiler = LLMClusterProfiler(
                    cluster_profiles_path=str(self.cluster_profiles_path),
                    llm_provider=llm_provider
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
                'n_actions': 0,
                'n_states_in_qtable': 0
            }
        
        stats = self.agent.get_statistics()
        return {
            'model_loaded': True,
            'model_version': 'V2',
            'n_actions': self.agent.n_actions,
            'state_dimensions': 6,
            'state_structure': '(cluster_id, module_idx, progress_bin, score_bin, learning_phase, engagement_level)',
            'n_states_in_qtable': len(self.agent.q_table),
            'episodes': stats.get('episodes_trained', 0),
            'avg_reward': 0.0,  # Not tracked in new format
            'coverage': f"{(len(self.agent.q_table) / 4320 * 100):.2f}%"  # 5*6*4*4*3*3 = 4,320 states
        }
