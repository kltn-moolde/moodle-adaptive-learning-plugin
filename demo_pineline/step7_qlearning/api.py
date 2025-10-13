#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Recommendation API
==============================
REST API service for adaptive learning recommendations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional
import logging

# Add parent path
sys.path.append(str(Path(__file__).parent))

from core import QLearningAgentV2


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global agent instance (loaded at startup)
agent: Optional[QLearningAgentV2] = None


def convert_to_native_types(obj):
    """
    Convert numpy types to native Python types for JSON serialization
    
    Args:
        obj: Object to convert (can be dict, list, numpy types, etc.)
        
    Returns:
        Object with all numpy types converted to native Python types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_native_types(item) for item in obj)
    else:
        return obj


def load_agent(course_json_path: str, model_path: str, n_bins: int = 3):
    """
    Load trained Q-Learning agent
    
    Args:
        course_json_path: Path to course structure JSON
        model_path: Path to trained model (.pkl)
        n_bins: Number of bins for state discretization
    """
    global agent
    
    try:
        logger.info(f"Loading agent from {model_path}...")
        
        # Create agent
        agent = QLearningAgentV2.create_from_course(
            course_json_path,
            n_bins=n_bins
        )
        
        # Load trained weights
        agent.load(model_path)
        
        logger.info(f"✓ Agent loaded successfully")
        logger.info(f"  Q-table size: {len(agent.Q)}")
        logger.info(f"  Action space: {agent.action_space.get_action_space_size()} actions")
        
    except Exception as e:
        logger.error(f"Failed to load agent: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    GET /health
    
    Response:
        200: Service is healthy
        503: Service unavailable
    """
    if agent is None:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Agent not loaded'
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'message': 'Q-Learning API is running',
        'q_table_size': len(agent.Q),
        'action_space_size': agent.action_space.get_action_space_size()
    }), 200


@app.route('/api/v1/recommend', methods=['POST'])
def recommend():
    """
    Get learning recommendations for a student
    
    POST /api/v1/recommend
    
    Request Body:
        {
            "student_features": {
                "userid": 123,
                "mean_module_grade": 0.75,
                "total_events": 0.65,
                "course_module": 0.70,
                "viewed": 0.80,
                "attempt": 0.40,
                "feedback_viewed": 0.60,
                "submitted": 0.75,
                "reviewed": 0.50,
                "course_module_viewed": 0.80,
                "module_count": 0.70,
                "course_module_completion": 0.65,
                "created": 0.30,
                "updated": 0.40,
                "downloaded": 0.50
            },
            "completed_resources": [52, 60, 102],  # Optional
            "top_k": 5,  # Optional, default=5
            "use_heuristic_fallback": true  # Optional, default=true
        }
    
    Response:
        200: Recommendations returned
        400: Invalid request
        500: Internal error
    """
    if agent is None:
        return jsonify({
            'error': 'Agent not loaded',
            'message': 'Service not ready'
        }), 503
    
    try:
        # Parse request
        data = request.get_json()
        
        if not data or 'student_features' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Missing student_features'
            }), 400
        
        student_features = data['student_features']
        completed_resources = data.get('completed_resources', [])
        top_k = data.get('top_k', 5)
        use_heuristic_fallback = data.get('use_heuristic_fallback', True)
        
        # Validate student features
        required_features = [
            'userid', 'mean_module_grade', 'total_events', 'course_module',
            'viewed', 'attempt', 'feedback_viewed', 'submitted', 'reviewed',
            'course_module_viewed', 'module_count', 'course_module_completion',
            'created', 'updated', 'downloaded'
        ]
        
        missing_features = [f for f in required_features if f not in student_features]
        if missing_features:
            return jsonify({
                'error': 'Invalid request',
                'message': f'Missing features: {missing_features}'
            }), 400
        
        # Build state
        state = agent.state_builder.build_state(student_features)
        
        # Get available actions (filter completed)
        all_actions = agent.action_space.get_all_actions()
        completed_ids = [str(rid) for rid in completed_resources]
        available_actions = [
            a for a in all_actions 
            if a.action_id not in completed_ids
        ]
        
        if not available_actions:
            return jsonify({
                'recommendations': [],
                'message': 'All resources completed',
                'student_state': {
                    'knowledge': float(state[0]),
                    'engagement': float(state[1]),
                    'struggle': float(state[2])
                }
            }), 200
        
        # Get recommendations
        recommendations = agent.recommend(
            state,
            available_actions,
            top_k=top_k,
            use_heuristic_fallback=use_heuristic_fallback
        )
        
        # Calculate statistics
        method_counts = {'q_learning': 0, 'heuristic': 0}
        for rec in recommendations:
            method = rec.get('recommendation_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Format response
        response = {
            'recommendations': convert_to_native_types(recommendations),
            'student_state': {
                'knowledge': float(state[0]),
                'engagement': float(state[1]),
                'struggle': float(state[2]),
                'discrete_state': convert_to_native_types(agent.discretizer.discretize(state))
            },
            'metadata': {
                'total_recommendations': len(recommendations),
                'method_breakdown': method_counts,
                'heuristic_ratio': float(method_counts['heuristic'] / len(recommendations) if recommendations else 0),
                'available_resources': len(available_actions),
                'completed_resources': len(completed_resources)
            }
        }
        
        logger.info(f"Recommendation for user {student_features['userid']}: "
                   f"{len(recommendations)} items "
                   f"(Q-Learning: {method_counts['q_learning']}, "
                   f"Heuristic: {method_counts['heuristic']})")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/v1/student/state', methods=['POST'])
def get_student_state():
    """
    Get student state vector
    
    POST /api/v1/student/state
    
    Request Body:
        {
            "student_features": { ... }
        }
    
    Response:
        {
            "state": [0.75, 0.65, 0.14, ...],
            "discrete_state": [2, 1, 0, ...],
            "interpretation": {
                "knowledge": "high",
                "engagement": "medium",
                "struggle": "low"
            }
        }
    """
    if agent is None:
        return jsonify({'error': 'Agent not loaded'}), 503
    
    try:
        data = request.get_json()
        student_features = data.get('student_features')
        
        if not student_features:
            return jsonify({'error': 'Missing student_features'}), 400
        
        # Build state
        state = agent.state_builder.build_state(student_features)
        discrete_state = agent.discretizer.discretize(state)
        
        # Interpret state
        knowledge = state[0]
        engagement = state[1]
        struggle = state[2]
        
        interpretation = {
            'knowledge': 'high' if knowledge >= 0.7 else ('medium' if knowledge >= 0.4 else 'low'),
            'engagement': 'high' if engagement >= 0.7 else ('medium' if engagement >= 0.4 else 'low'),
            'struggle': 'high' if struggle >= 0.3 else ('medium' if struggle >= 0.15 else 'low')
        }
        
        return jsonify({
            'state': convert_to_native_types(state.tolist()),
            'discrete_state': convert_to_native_types(list(discrete_state)),
            'interpretation': interpretation,
            'feature_names': [
                'knowledge', 'engagement', 'struggle', 'submission',
                'review', 'resource_usage', 'assessment', 'collaborative',
                'progress', 'completion', 'diversity', 'consistency'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_student_state: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/actions', methods=['GET'])
def get_actions():
    """
    Get all available actions (resources) in course
    
    GET /api/v1/actions?type=quiz&difficulty=medium
    
    Query Parameters:
        - type: Filter by action type (optional)
        - difficulty: Filter by difficulty (optional)
    
    Response:
        {
            "actions": [...],
            "total": 35,
            "filtered": 10
        }
    """
    if agent is None:
        return jsonify({'error': 'Agent not loaded'}), 503
    
    try:
        # Get all actions
        all_actions = agent.action_space.get_all_actions()
        
        # Apply filters
        action_type = request.args.get('type')
        difficulty = request.args.get('difficulty')
        
        filtered_actions = all_actions
        
        if action_type:
            filtered_actions = [
                a for a in filtered_actions 
                if action_type.lower() in a.action_type.lower()
            ]
        
        if difficulty:
            filtered_actions = [
                a for a in filtered_actions 
                if a.difficulty and a.difficulty.lower() == difficulty.lower()
            ]
        
        # Convert to dict
        actions_list = [a.to_dict() for a in filtered_actions]
        
        return jsonify({
            'actions': convert_to_native_types(actions_list),
            'total': len(all_actions),
            'filtered': len(filtered_actions),
            'filters': {
                'type': action_type,
                'difficulty': difficulty
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_actions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    
    GET /api/v1/stats
    
    Response:
        {
            "q_table_size": 463,
            "training_updates": 300,
            "action_space_size": 35,
            "state_dimension": 12,
            "discretization_bins": 3,
            ...
        }
    """
    if agent is None:
        return jsonify({'error': 'Agent not loaded'}), 503
    
    try:
        stats = agent.get_statistics()
        
        # Add more details
        stats['state_dimension'] = agent.state_builder.get_state_dimension()
        stats['discretization_bins'] = agent.discretizer.n_bins
        stats['possible_states'] = agent.discretizer.get_state_space_size()
        stats['hyperparameters'] = {
            'learning_rate': agent.alpha,
            'discount_factor': agent.gamma,
            'epsilon': agent.epsilon
        }
        
        return jsonify(convert_to_native_types(stats)), 200
        
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Q-Learning Recommendation API')
    parser.add_argument('--course', type=str, 
                       default='data/course_structure.json',
                       help='Path to course structure JSON')
    parser.add_argument('--model', type=str,
                       default='examples/trained_agent_real_data.pkl',
                       help='Path to trained model')
    parser.add_argument('--bins', type=int, default=3,
                       help='Number of discretization bins')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to bind to')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Load agent
    logger.info("="*70)
    logger.info("Q-LEARNING RECOMMENDATION API")
    logger.info("="*70)
    
    load_agent(args.course, args.model, args.bins)
    
    # Start server
    logger.info(f"\n🚀 Starting API server on {args.host}:{args.port}")
    logger.info(f"   Course: {args.course}")
    logger.info(f"   Model: {args.model}")
    logger.info(f"   Debug: {args.debug}")
    logger.info("\n📋 Available endpoints:")
    logger.info("   GET  /health")
    logger.info("   POST /api/v1/recommend")
    logger.info("   POST /api/v1/student/state")
    logger.info("   GET  /api/v1/actions")
    logger.info("   GET  /api/v1/stats")
    logger.info("\n" + "="*70 + "\n")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()
