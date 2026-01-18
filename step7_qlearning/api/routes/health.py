"""
Health check and model info endpoints
"""
from fastapi import APIRouter
from ..dependencies import model_loader

router = APIRouter(prefix='/api', tags=['health'])


@router.get('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'model_loaded': model_loader.agent is not None,
        'n_actions': model_loader.agent.n_actions if model_loader.agent else 0,
        'n_states_in_qtable': len(model_loader.agent.q_table) if model_loader.agent else 0
    }


@router.get('/model-info')
def get_model_info():
    """Get detailed model information"""
    return model_loader.get_model_info()

