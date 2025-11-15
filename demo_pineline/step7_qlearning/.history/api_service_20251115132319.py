#!/usr/bin/env python3
"""
Adaptive Learning API Service
Clean and modular FastAPI service with business logic separated into services

Endpoints:
 - GET  /api/health      : Health check and model status
 - GET  /api/model-info  : Model metadata and training statistics
 - POST /api/recommend   : Get top-K learning recommendations

Run: uvicorn api_service:app --reload --port 8080
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import services
from services.model_loader import ModelLoader
from services.cluster_service import ClusterService
from services.recommendation_service import RecommendationService

# =============================================================================
# Configuration
# =============================================================================

MODEL_PATH = HERE / 'models' / 'qtable_best.pkl'  # Best trained model
COURSE_PATH = HERE / 'data' / 'course_structure.json'
CLUSTER_PROFILES_PATH = HERE / 'data' / 'cluster_profiles.json'

# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(
    title='Adaptive Learning API',
    version='2.0',
    description='Q-Learning based adaptive learning path recommendation system'
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Request/Response Models
# =============================================================================

class RecommendRequest(BaseModel):
    """Request model for recommendations"""
    student_id: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    state: Optional[List[float]] = None
    top_k: int = 3
    exclude_action_ids: Optional[List[int]] = None
    lo_mastery: Optional[Dict[str, float]] = None  # LO mastery scores for activity recommendation


class RecommendResponse(BaseModel):
    """Response model for recommendations"""
    success: bool
    student_id: Optional[int]
    cluster_id: Optional[int]
    cluster_name: Optional[str]
    state_vector: List[float]
    state_description: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    model_info: Dict[str, Any]

# =============================================================================
# Initialize Services (on startup)
# =============================================================================

# Model loader service
model_loader = ModelLoader(
    model_path=MODEL_PATH,
    course_path=COURSE_PATH,
    cluster_profiles_path=CLUSTER_PROFILES_PATH
)

# Load all components
model_loader.load_all(verbose=True)

# Initialize other services
cluster_service = ClusterService(cluster_profiles=model_loader.cluster_profiles)
recommendation_service = RecommendationService(
    agent=model_loader.agent,
    action_space=model_loader.action_space,
    state_builder=model_loader.state_builder,
    course_structure_path=str(COURSE_PATH)
)

# =============================================================================
# API Endpoints
# =============================================================================

@app.get('/api/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'model_loaded': model_loader.agent is not None,
        'n_actions': model_loader.agent.n_actions if model_loader.agent else 0,
        'n_states_in_qtable': len(model_loader.agent.q_table) if model_loader.agent else 0
    }


@app.get('/api/model-info')
def get_model_info():
    """Get detailed model information"""
    return model_loader.get_model_info()


@app.post('/api/recommend', response_model=RecommendResponse)
def recommend_learning_path(request: RecommendRequest):
    """
    Generate learning path recommendations
    
    Accepts either:
    1. features dict (will predict cluster and build state)
    2. state vector (will use directly)
    """
    # Determine state
    if request.state:
        # Use provided state directly
        state = tuple(request.state)
        cluster_id = int(state[0])
        cluster_name = f'Cluster {cluster_id}'
        
    elif request.features:
        # Use cluster_id from features if provided, otherwise predict
        if 'cluster_id' in request.features:
            cluster_id = int(request.features['cluster_id'])
            # Get cluster name from cluster service
            cluster_info = cluster_service.get_cluster_info(cluster_id)
            cluster_name = cluster_info.get('cluster_name')
            
            # Fallback to default names if not found
            if not cluster_name or cluster_name == f'Cluster {cluster_id}':
                cluster_names = {
                    0: 'Weak',
                    1: 'Medium', 
                    2: 'Medium',
                    3: 'Strong',
                    4: 'Strong'
                }
                cluster_name = cluster_names.get(cluster_id, f'Cluster {cluster_id}')
        else:
            # Predict cluster from features
            cluster_id, cluster_name = cluster_service.find_closest_cluster(request.features)
            
            # Fallback if name is unknown
            if not cluster_name or cluster_name == 'unknown':
                cluster_names = {
                    0: 'Weak',
                    1: 'Medium',
                    2: 'Medium', 
                    3: 'Strong',
                    4: 'Strong'
                }
                cluster_name = cluster_names.get(cluster_id, f'Cluster {cluster_id}')
        
        # Build state from features
        state = recommendation_service.build_state_from_features(
            features=request.features,
            cluster_id=cluster_id
        )
        
        if state is None:
            raise HTTPException(
                status_code=400,
                detail='Failed to build state from features'
            )
    else:
        raise HTTPException(
            status_code=400,
            detail='Either features or state must be provided'
        )
    
    # Get LO mastery (use provided or create default)
    lo_mastery = request.lo_mastery
    if lo_mastery is None:
        # Create default LO mastery (all LOs at 0.4 = 40%)
        # Try to get LO list from ActivityRecommender if available
        if hasattr(recommendation_service, 'activity_recommender') and recommendation_service.activity_recommender:
            lo_mastery = {lo_id: 0.4 for lo_id in recommendation_service.activity_recommender.lo_to_activities.keys()}
        else:
            # Fallback: use common LO IDs
            lo_mastery = {f'LO{i//10}.{i%10}' for i in range(1, 16)}  # LO1.1 to LO2.5
            lo_mastery = {lo_id: 0.4 for lo_id in lo_mastery}
    
    # Get module_idx from state
    module_idx = int(state[1]) if len(state) > 1 else 0
    
    # Get recommendations with activity details
    recommendations = recommendation_service.get_recommendations(
        state=state,
        cluster_id=cluster_id,
        top_k=request.top_k,
        exclude_action_ids=request.exclude_action_ids,
        lo_mastery=lo_mastery,
        module_idx=module_idx
    )
    
    # Get state description
    state_description = recommendation_service.get_state_description(state)
    
    # Get model info
    model_info = {
        'model_version': 'V2',
        'n_states_in_qtable': len(model_loader.agent.q_table) if model_loader.agent else 0
    }
    
    return RecommendResponse(
        success=True,
        student_id=request.student_id,
        cluster_id=cluster_id,
        cluster_name=cluster_name,
        state_vector=list(state),
        state_description=state_description,
        recommendations=recommendations,
        model_info=model_info
    )


@app.get('/api/qtable/states/positive')
def get_top_positive_states(top_n: int = 10):
    """
    Get top N states with highest Q-values from Q-table
    
    Args:
        top_n: Number of top states to return (default: 10)
    
    Returns:
        List of states with their max Q-values and recommendations
    """
    if not model_loader.agent or not model_loader.agent.q_table:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Get all states with their max Q-values
    state_q_values = []
    for state, q_values in model_loader.agent.q_table.items():
        if isinstance(q_values, dict):
            max_q = max(q_values.values())
            avg_q = sum(q_values.values()) / len(q_values)
        else:
            # Fallback for unexpected format
            max_q = float(q_values) if hasattr(q_values, '__float__') else 0.0
            avg_q = max_q
            
        if max_q > 0:  # Only positive Q-values
            state_q_values.append({
                'state': list(state),
                'max_q_value': float(max_q),
                'avg_q_value': float(avg_q)
            })
    
    # Sort by max Q-value descending
    state_q_values.sort(key=lambda x: x['max_q_value'], reverse=True)
    
    # Get top N
    top_states = state_q_values[:top_n]
    
    # Add state descriptions and recommendations for each
    results = []
    for item in top_states:
        state = tuple(item['state'])
        
        # Get state description
        state_desc = recommendation_service.get_state_description(state)
        
        # Get top 3 recommendations for this state
        recommendations = recommendation_service.get_recommendations(
            state=state,
            cluster_id=int(state[0]),
            top_k=3,
            exclude_action_ids=None
        )
        
        results.append({
            'state': item['state'],
            'max_q_value': item['max_q_value'],
            'avg_q_value': item['avg_q_value'],
            'state_description': state_desc,
            'top_recommendations': recommendations
        })
    
    return {
        'total_positive_states': len(state_q_values),
        'returned': len(results),
        'top_states': results
    }


@app.get('/')
def root():
    """Root endpoint"""
    return {
        'service': 'Adaptive Learning API',
        'version': '2.0',
        'endpoints': {
            'health': '/api/health',
            'model_info': '/api/model-info',
            'recommend': '/api/recommend (POST)',
            'top_states': '/api/qtable/states/positive?top_n=N'
        }
    }


# =============================================================================
# Startup Message
# =============================================================================

if __name__ == '__main__':
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Adaptive Learning API Server")
    print("="*70)
    print(f"📊 Model: {MODEL_PATH}")
    print(f"🎯 Q-table states: {len(model_loader.agent.q_table) if model_loader.agent else 0}")
    print(f"🌐 Server: http://localhost:8080")
    print(f"📖 Docs: http://localhost:8080/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host='0.0.0.0', port=8080)
