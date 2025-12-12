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
        
        # Create mock LO mastery based on cluster and score for realistic recommendations
        cluster_id = int(state[0])
        score_bin = float(state[3]) if len(state) > 3 else 0.5
        
        # Map cluster to average mastery level
        cluster_mastery = {0: 0.45, 1: 0.60, 2: 0.60, 4: 0.75, 5: 0.60}
        base_mastery = cluster_mastery.get(cluster_id, 0.50)
        
        # Adjust by score_bin
        adjusted_mastery = base_mastery * (0.8 + 0.4 * score_bin)  # 0.8-1.2 multiplier
        
        # Create mock LO mastery with some weak LOs for demonstration
        mock_lo_mastery = {
            f'LO1.{i}': min(0.95, max(0.30, adjusted_mastery + (i-2)*0.05))
            for i in range(1, 4)
        }
        mock_lo_mastery.update({
            f'LO2.{i}': min(0.95, max(0.30, adjusted_mastery + (i-2)*0.08))
            for i in range(1, 5)
        })
        
        # Debug: Print mock LO mastery
        print(f"🔍 DEBUG [qtable.py]: Created mock_lo_mastery for state {state[:2]}")
        print(f"   cluster_id={cluster_id}, score_bin={score_bin:.2f}, base_mastery={base_mastery:.2f}")
        for lo_id, mastery in sorted(mock_lo_mastery.items()):
            status = "WEAK" if mastery < 0.6 else "OK"
            print(f"   {lo_id}: {mastery:.3f} [{status}]")
        
        # Get top 3 recommendations for this state with mock LO mastery
        recommendations = recommendation_service.get_recommendations(
            state=state,
            cluster_id=cluster_id,
            top_k=3,
            exclude_action_ids=None,
            lo_mastery=mock_lo_mastery,
            module_idx=int(state[1]) if len(state) > 1 else 0,
            lesson_id=int(state[1]) if len(state) > 1 else 0
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

