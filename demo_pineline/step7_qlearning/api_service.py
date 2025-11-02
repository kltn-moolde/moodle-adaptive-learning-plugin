#!/usr/bin/env python3
"""Clean FastAPI service exposing only requested endpoints under /api

Endpoints:
 - GET  /api/health      : basic health and model status
 - GET  /api/model-info  : model metadata (n_states, n_actions, training stats)
 - POST /api/recommend   : request top-K recommendations (accepts features or state)

Run: from `step7_qlearning` folder:
  uvicorn api_service:app --reload --port 8080
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import random
import json

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

from core.action_space import ActionSpace
from core.state_builder import MoodleStateBuilder
from core.qlearning_agent import QLearningAgent
from services.qtable_service import QTableService
from services.llm_cluster_profiler import LLMClusterProfiler


MODEL_PATH = HERE / 'models' / 'qlearning_model.pkl'
COURSE_PATH = HERE / 'data' / 'course_structure.json'
CLUSTER_PROFILES_PATH = HERE / 'data' / 'cluster_profiles.json'

app = FastAPI(title='Adaptive Learning API', version='1.0')

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*",  # Allow all origins (for development)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Nested feature structure matching state dimensions
class PerformanceFeatures(BaseModel):
    knowledge_level: float = 0.5
    engagement_level: float = 0.5
    struggle_indicator: float = 0.0


class ActivityPatterns(BaseModel):
    submission_activity: float = 0.0
    review_activity: float = 0.5
    resource_usage: float = 0.5
    assessment_engagement: float = 0.5
    collaborative_activity: float = 0.0


class CompletionMetrics(BaseModel):
    overall_progress: float = 0.5
    module_completion_rate: float = 0.5
    activity_diversity: float = 0.25
    completion_consistency: float = 0.5


class StructuredFeatures(BaseModel):
    performance: PerformanceFeatures
    activity_patterns: ActivityPatterns
    completion_metrics: CompletionMetrics


class RecommendRequest(BaseModel):
    student_id: Optional[int] = None  # ID của sinh viên (để tracking)
    features: Optional[Dict[str, Any]] = None  # Accepts both nested and flat format
    state: Optional[List[float]] = None
    top_k: int = 3
    exclude_action_ids: Optional[List[int]] = None


class RecommendResponse(BaseModel):
    success: bool
    student_id: Optional[int]
    cluster_id: Optional[int]  # predicted cluster
    cluster_name: Optional[str]  # cluster name from profile
    state_vector: List[float]
    state_description: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    model_info: Dict[str, Any]


def load_cluster_profiles() -> Dict[str, Any]:
    """Load cluster profiles from JSON"""
    if not CLUSTER_PROFILES_PATH.exists():
        print(f'Warning: cluster_profiles.json not found at {CLUSTER_PROFILES_PATH}')
        return {}
    
    with open(CLUSTER_PROFILES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_closest_cluster(features: Dict[str, float], cluster_profiles: Dict[str, Any]) -> tuple[int, str]:
    """
    Find closest cluster by comparing student features to cluster feature_means
    using Euclidean distance
    
    Args:
        features: Student feature dict
        cluster_profiles: Loaded cluster profiles
        
    Returns:
        (cluster_id, cluster_name) tuple
    """
    if not cluster_profiles or 'cluster_stats' not in cluster_profiles:
        return (0, 'unknown')  # fallback
    
    cluster_stats = cluster_profiles['cluster_stats']
    
    # Get feature keys that exist in both student and cluster profiles
    # Use first cluster as reference for available features
    if not cluster_stats:
        return (0, 'unknown')
    
    first_cluster_key = list(cluster_stats.keys())[0]
    first_cluster = cluster_stats[first_cluster_key]
    feature_means = first_cluster.get('feature_means', {})
    common_features = [k for k in feature_means.keys() if k in features]
    
    if not common_features:
        # Fallback: if no common features, use cluster 0
        return (0, 'unknown')
    
    min_distance = float('inf')
    closest_cluster_id = 0
    closest_cluster_name = 'unknown'
    
    for cluster_key, cluster_data in cluster_stats.items():
        cluster_id = cluster_data.get('cluster_id', int(cluster_key))
        cluster_means = cluster_data.get('feature_means', {})
        
        # Get AI profile name if available
        ai_profile = cluster_data.get('ai_profile', {})
        cluster_name = ai_profile.get('profile_name', f'Cluster {cluster_id}')
        
        # Calculate Euclidean distance for common features
        distance = 0.0
        for feature_key in common_features:
            student_val = features.get(feature_key, 0.0)
            cluster_val = cluster_means.get(feature_key, 0.0)
            distance += (student_val - cluster_val) ** 2
        
        distance = np.sqrt(distance)
        
        if distance < min_distance:
            min_distance = distance
            closest_cluster_id = cluster_id
            closest_cluster_name = cluster_name
    
    return (closest_cluster_id, closest_cluster_name)


# Initialize components (print startup info)
print('Starting Adaptive Learning API — loading components...')

if not COURSE_PATH.exists():
    print(f'Warning: course_structure.json not found at {COURSE_PATH}')
    action_space = None
else:
    action_space = ActionSpace(str(COURSE_PATH))
    print(f'Loaded action space: {action_space.get_action_count()} actions')

agent: Optional[QLearningAgent] = None
if MODEL_PATH.exists():
    try:
        # instantiate agent with action count
        agent = QLearningAgent(n_actions=(action_space.get_action_count() if action_space else 0))
        agent.load(str(MODEL_PATH))
        print(f'Loaded model from {MODEL_PATH} (states: {len(agent.q_table)})')
    except Exception as e:
        print(f'Warning: failed to load model: {e}')
        agent = None
else:
    print(f'No trained model found at {MODEL_PATH} — recommendations will fallback to random')

state_builder = MoodleStateBuilder()
print('State builder ready (state dim =', state_builder.get_state_dimension(), ')')

# Initialize Q-table service
qtable_service = QTableService(agent=agent)
print('Q-table service initialized')

# Load cluster profiles for cluster prediction
cluster_profiles = load_cluster_profiles()
if cluster_profiles:
    n_clusters = len(cluster_profiles.get('cluster_stats', {}))
    print(f'Loaded cluster profiles: {n_clusters} clusters')
else:
    print('Warning: cluster profiles not loaded — cluster prediction disabled')

# Initialize LLM Cluster Profiler (optional - only if API key available)
llm_profiler: Optional[LLMClusterProfiler] = None
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
    
    # Check if API key available (env var or config)
    has_gemini_key = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY') or config_gemini_key)
    has_openai_key = bool(os.getenv('OPENAI_API_KEY') or config_openai_key)
    
    if has_gemini_key or has_openai_key:
        llm_profiler = LLMClusterProfiler(
            cluster_profiles_path=str(CLUSTER_PROFILES_PATH),
            llm_provider=llm_provider
        )
        print(f'✓ LLM Cluster Profiler initialized (provider: {llm_provider})')
    else:
        print('⚠ LLM API key not found - LLM profiling disabled')
        print('  Set GOOGLE_API_KEY/GEMINI_API_KEY or OPENAI_API_KEY environment variable')
        print('  Or add to config.py: GEMINI_API_KEY or OPENAI_API_KEY')
except Exception as e:
    print(f'⚠ Failed to initialize LLM Profiler: {e}')


@app.get('/api/health')
def health() -> Dict[str, Any]:
    return {
        'status': 'ok',
        'model_loaded': agent is not None,
        'n_actions': action_space.get_action_count() if action_space else 0,
        'n_states_in_qtable': len(agent.q_table) if agent else 0,
    }


@app.get('/api/model-info')
def model_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        'model_loaded': agent is not None,
        'n_actions': action_space.get_action_count() if action_space else 0,
        'state_dim': state_builder.get_state_dimension(),
    }
    if agent:
        stats = agent.get_statistics()
        info.update({
            'n_states_in_qtable': stats.get('q_table_size', 0),
            'total_updates': stats.get('total_updates', 0),
            'episodes': stats.get('episodes', 0),
            'avg_reward': stats.get('avg_reward', 0.0),
        })
    return info


def _build_state_from_request(req: RecommendRequest) -> np.ndarray:
    if req.state is not None:
        arr = np.array(req.state, dtype=np.float32)
        if arr.size != state_builder.get_state_dimension():
            raise HTTPException(status_code=400, detail=f'state must be length {state_builder.get_state_dimension()}')
        return arr

    if req.features is not None:
        # ✅ Use API-friendly method for feature mapping
        return state_builder.build_state_from_api_features(req.features)

    raise HTTPException(status_code=400, detail='Provide either state or features')


@app.post('/api/recommend', response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if action_space is None:
        raise HTTPException(status_code=503, detail='Action space not available')

    state = _build_state_from_request(req)
    
    # Predict cluster based on state characteristics
    cluster_id: Optional[int] = None
    cluster_name: Optional[str] = None
    
    if req.features:
        # Simple rule-based cluster prediction from state
        knowledge = state[0]  # knowledge_level
        engagement = state[1]  # engagement_score
        
        if knowledge >= 0.75 and engagement >= 0.75:
            cluster_id = 4
            cluster_name = "Học sinh Nghiên cứu Chủ động"
        elif knowledge >= 0.75:
            cluster_id = 2
            cluster_name = "Học sinh Chủ động Hoàn thành Nhiệm vụ"
        elif knowledge >= 0.5 and engagement >= 0.5:
            cluster_id = 1
            cluster_name = "Học sinh Tự giác và Theo dõi Tiến độ"
        elif engagement >= 0.5:
            cluster_id = 5
            cluster_name = "Học sinh theo dõi hiệu suất và thành tích"
        else:
            cluster_id = 0
            cluster_name = "Học sinh cần hỗ trợ tương tác"
        
        print(f'[DEBUG] Predicted cluster: {cluster_id} ({cluster_name})')

    available_actions = [a.id for a in action_space.get_actions()]
    if req.exclude_action_ids:
        available_actions = [a for a in available_actions if a not in req.exclude_action_ids]
    if not available_actions:
        raise HTTPException(status_code=400, detail='No available actions')

    if agent:
        recs = agent.recommend_action(state, available_actions, top_k=min(req.top_k, len(available_actions)), fallback_random=True)
    else:
        sample = random.sample(available_actions, min(req.top_k, len(available_actions)))
        recs = [(aid, 0.0) for aid in sample]

    recommendations = []
    for aid, qv in recs:
        a = action_space.get_action_by_id(aid)
        if a:
            recommendations.append({
                'action_id': aid,
                'name': a.name,
                'type': a.type,
                'purpose': a.purpose,
                'difficulty': a.difficulty,
                'q_value': float(qv)
            })
        else:
            recommendations.append({'action_id': aid, 'q_value': float(qv)})

    model_info = {'model_loaded': agent is not None}
    if agent:
        model_info.update({
            'n_states_in_qtable': len(agent.q_table),
            'total_updates': agent.training_stats.get('total_updates', 0),
            'episodes': agent.training_stats.get('episodes', 0),
        })

    return RecommendResponse(
        success=True,
        student_id=req.student_id,  # Lấy từ request thay vì None
        cluster_id=cluster_id,
        cluster_name=cluster_name,
        state_vector=state.tolist(),
        state_description=state_builder.get_state_description(state),
        recommendations=recommendations,
        model_info=model_info
    )


# ============================================================================
# Q-TABLE INFORMATION ENDPOINTS
# ============================================================================

@app.get('/api/qtable/info')
def qtable_info() -> Dict[str, Any]:
    """
    Get Q-table metadata and structure information
    
    Returns:
        - qtable_metadata: Size, sparsity, memory usage
        - state_space: Dimension, features, discretization
        - action_space: Total actions, action IDs
        - hyperparameters: Learning rate, epsilon, etc.
        - training_info: Episodes, updates, rewards
    """
    if not agent:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    return qtable_service.get_qtable_info()


@app.get('/api/qtable/summary')
def qtable_summary() -> Dict[str, Any]:
    """
    Get comprehensive Q-table summary with statistics
    
    Returns:
        - model_info: Learning parameters
        - training_stats: Training history
        - qtable_stats: Q-table statistics
        - dimension_stats: State space analysis
    """
    if not agent:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    return qtable_service.get_summary()


@app.get('/api/qtable/states/positive')
def qtable_positive_states(
    top_n: int = 50,
    min_q_value: float = 0.0001
) -> Dict[str, Any]:
    """
    Get states with positive Q-values
    
    Args:
        top_n: Number of top states to return (default: 50)
        min_q_value: Minimum Q-value threshold (default: 0.0001)
    
    Returns:
        List of states with:
        - rank: Position in sorted list
        - features: Flat feature dict (ready for API testing)
        - q_info: Q-value information
    """
    if not agent:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    states = qtable_service.get_states_with_positive_q(top_n=top_n, min_q_value=min_q_value)
    
    return {
        'success': True,
        'total_states': len(states),
        'top_n': top_n,
        'min_q_value': min_q_value,
        'states': states
    }


@app.get('/api/qtable/states/diverse')
def qtable_diverse_states(n_samples: int = 20) -> Dict[str, Any]:
    """
    Get diverse state samples from different Q-value ranges
    
    Args:
        n_samples: Number of samples to return (default: 20)
    
    Returns:
        List of diverse states with:
        - features: Flat feature dict
        - max_q_value: Maximum Q-value
        - percentile: Which percentile this state comes from
    """
    if not agent:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    samples = qtable_service.get_diverse_samples(n_samples=n_samples)
    
    return {
        'success': True,
        'total_samples': len(samples),
        'samples': samples
    }


@app.get('/api/qtable/stats')
def qtable_basic_stats() -> Dict[str, Any]:
    """
    Get basic Q-table statistics (lightweight)
    
    Returns:
        Basic stats including total states, states with Q>0, training info
    """
    if not agent:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    return qtable_service.get_statistics()


# ============================================================================
# LLM CLUSTER PROFILING ENDPOINTS
# ============================================================================

@app.get('/api/clusters/list')
def list_clusters() -> Dict[str, Any]:
    """
    List all available student clusters
    
    Returns:
        List of clusters with basic statistics
    """
    if not cluster_profiles:
        raise HTTPException(status_code=503, detail='Cluster profiles not loaded')
    
    cluster_stats = cluster_profiles.get('cluster_stats', {})
    
    clusters = []
    for cluster_key in sorted(cluster_stats.keys(), key=lambda x: int(x)):
        data = cluster_stats[cluster_key]
        clusters.append({
            'cluster_id': int(cluster_key),
            'n_students': data.get('n_students', 0),
            'percentage': data.get('percentage', 0),
            'profile_name': data.get('ai_profile', {}).get('profile_name', f'Cluster {cluster_key}')
        })
    
    return {
        'success': True,
        'total_clusters': len(clusters),
        'total_students': cluster_profiles.get('total_students', 0),
        'clusters': clusters
    }


@app.get('/api/clusters/{cluster_id}')
def get_cluster_info(cluster_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific cluster
    
    Args:
        cluster_id: Cluster ID (0, 1, 2, ...)
    
    Returns:
        Cluster statistics and existing profile (if available)
    """
    if not cluster_profiles:
        raise HTTPException(status_code=503, detail='Cluster profiles not loaded')
    
    cluster_stats = cluster_profiles.get('cluster_stats', {})
    cluster_key = str(cluster_id)
    
    if cluster_key not in cluster_stats:
        raise HTTPException(status_code=404, detail=f'Cluster {cluster_id} not found')
    
    data = cluster_stats[cluster_key]
    
    return {
        'success': True,
        'cluster_id': cluster_id,
        'statistics': {
            'n_students': data.get('n_students', 0),
            'percentage': data.get('percentage', 0),
            'feature_means': data.get('feature_means', {}),
            'top_features': data.get('top_distinguishing_features', [])[:5]
        },
        'existing_profile': data.get('ai_profile', None)
    }


@app.post('/api/clusters/{cluster_id}/profile')
def generate_cluster_profile(cluster_id: int) -> Dict[str, Any]:
    """
    Generate LLM-powered profile for a specific cluster
    
    Args:
        cluster_id: Cluster ID
    
    Returns:
        Generated profile with name, description, strengths, weaknesses, recommendations
    
    Requires:
        - LLM API key (GOOGLE_API_KEY or OPENAI_API_KEY)
    """
    if not llm_profiler:
        raise HTTPException(
            status_code=503,
            detail='LLM Profiler not available. Set GOOGLE_API_KEY or OPENAI_API_KEY environment variable.'
        )
    
    try:
        profile = llm_profiler.generate_cluster_description(cluster_id)
        
        return {
            'success': True,
            'cluster_id': cluster_id,
            'profile': profile,
            'llm_provider': llm_profiler.llm_provider
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to generate profile: {str(e)}')


@app.post('/api/clusters/profile-all')
def generate_all_cluster_profiles() -> Dict[str, Any]:
    """
    Generate LLM-powered profiles for ALL clusters
    
    Returns:
        Profiles for all clusters
    
    Requires:
        - LLM API key (GOOGLE_API_KEY or OPENAI_API_KEY)
    
    Note: This may take some time depending on number of clusters
    """
    if not llm_profiler:
        raise HTTPException(
            status_code=503,
            detail='LLM Profiler not available. Set GOOGLE_API_KEY or OPENAI_API_KEY environment variable.'
        )
    
    try:
        profiles = llm_profiler.generate_all_clusters()
        
        # Format response
        formatted_profiles = []
        for cluster_key in sorted(profiles.keys(), key=lambda x: int(x)):
            data = profiles[cluster_key]
            formatted_profiles.append({
                'cluster_id': data['cluster_id'],
                'n_students': data['statistics'].get('n_students', 0),
                'percentage': data['statistics'].get('percentage', 0),
                'profile': data['ai_profile']
            })
        
        return {
            'success': True,
            'total_clusters': len(formatted_profiles),
            'llm_provider': llm_profiler.llm_provider,
            'clusters': formatted_profiles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to generate profiles: {str(e)}')


@app.get('/api/clusters/export/report')
def export_cluster_report() -> Dict[str, Any]:
    """
    Export full cluster profiling report (with LLM if available)
    
    Returns:
        File path to generated reports
    
    Note: Generates both JSON and TXT reports
    """
    if not llm_profiler:
        raise HTTPException(
            status_code=503,
            detail='LLM Profiler not available. Set GOOGLE_API_KEY or OPENAI_API_KEY environment variable.'
        )
    
    try:
        output_dir = HERE / 'outputs' / 'cluster_profiling_llm'
        output_file = output_dir / 'cluster_profiles_llm.json'
        
        llm_profiler.save_profiles(str(output_file))
        
        return {
            'success': True,
            'output_dir': str(output_dir),
            'json_file': str(output_file),
            'txt_file': str(output_dir / 'cluster_profiles_llm_report.txt'),
            'message': 'Reports generated successfully'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to export report: {str(e)}')


if __name__ == '__main__':
    print('Run: uvicorn api_service:app --reload --port 8080')

