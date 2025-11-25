"""
Q-table related endpoints
"""
from fastapi import APIRouter, HTTPException
from ..dependencies import qtable_service, model_loader, recommendation_service

router = APIRouter(prefix='/api/qtable', tags=['qtable'])


@router.get('/info')
def get_qtable_info():
    """
    Get Q-table metadata and structure information
    
    Returns:
        Dict with total states, actions, state dimensions, sparsity, etc.
    """
    if not qtable_service.agent:
        raise HTTPException(status_code=503, detail="Q-learning agent not loaded")
    
    info = qtable_service.get_qtable_info()
    return info


@router.get('/summary')
def get_qtable_summary():
    """
    Get comprehensive Q-table summary including Q-value distribution
    and state dimension statistics
    
    Returns:
        Dict with summary of Q-table
    """
    if not qtable_service.agent:
        raise HTTPException(status_code=503, detail="Q-learning agent not loaded")
    
    summary = qtable_service.get_summary()
    return summary


@router.get('/states/positive')
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

