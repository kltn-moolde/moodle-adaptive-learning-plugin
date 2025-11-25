"""
Recommendation endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from ..models import RecommendRequest, RecommendResponse
from ..dependencies import (
    model_manager,
    get_services_for_course,
    state_repository
)

router = APIRouter(prefix='/api', tags=['recommendations'])


@router.post('/recommend', response_model=RecommendResponse)
def recommend_learning_path(request: RecommendRequest):
    """
    Generate learning path recommendations for a specific course
    
    Accepts either:
    1. features dict (will predict cluster and build state)
    2. state vector (will use directly)
    
    Requires course_id for multi-course support
    """
    # Get services for this course
    try:
        services = get_services_for_course(request.course_id)
        cluster_service = services['cluster_service']
        recommendation_service = services['recommendation_service']
        model_loader = services['loader']
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f'Failed to load model for course {request.course_id}: {str(e)}'
        )
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
        
        # Validate and build state from features
        try:
            state = recommendation_service.build_state_from_features(
                features=request.features,
                cluster_id=cluster_id,
                validate=True,
                strict_validation=True
            )
            
            if state is None:
                raise HTTPException(
                    status_code=400,
                    detail='Failed to build state from features'
                )
        except ValueError as e:
            # Validation error
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            # Other errors
            raise HTTPException(
                status_code=500,
                detail=f'Error building state: {str(e)}'
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


@router.get('/recommendations/{user_id}/{module_id}')
async def get_recommendations(
    user_id: int,
    module_id: int,
    course_id: int = Query(..., description="Course ID (required for multi-course support)")
):
    """Get recommendations for a user/module (called by Moodle)"""
    try:
        rec_doc = state_repository.get_recommendations(user_id, module_id, course_id=course_id)
        
        if rec_doc is None:
            return {
                'user_id': user_id,
                'module_id': module_id,
                'recommendations': [],
                'state': None,
                'message': 'No recommendations available yet',
                'timestamp': __import__('datetime').datetime.utcnow().isoformat()
            }
        
        return {
            'user_id': user_id,
            'module_id': module_id,
            'recommendations': rec_doc['recommendations'],
            'state': rec_doc.get('state', []),
            'timestamp': rec_doc.get('timestamp', __import__('datetime').datetime.utcnow().isoformat())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

