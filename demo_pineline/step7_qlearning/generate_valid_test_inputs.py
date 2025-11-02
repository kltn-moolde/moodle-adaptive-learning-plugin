#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Valid Test Inputs from Trained Q-table
================================================
Extract states from Q-table that have high Q-values and convert back to API input format
"""

import pickle
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from core.state_builder import MoodleStateBuilder


def extract_top_states_from_qtable(model_path: str, top_n: int = 10) -> List[tuple]:
    """
    Extract states with highest max Q-values from Q-table
    
    Returns:
        List of (state_hash, max_q_value, best_action_id) tuples
    """
    print(f"\n[1/3] Loading model from {model_path}...")
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    # Handle both dict and agent object formats
    if isinstance(model_data, dict):
        q_table = model_data.get('q_table', {})
        state_bins = model_data.get('state_bins', None)
    else:
        q_table = model_data.q_table
        state_bins = getattr(model_data, 'state_bins', None)
    
    print(f"  ✓ Q-table size: {len(q_table):,} states")
    print(f"  ✓ Bins: {state_bins}")
    
    # Find states with highest max Q-values
    print(f"\n[2/3] Finding top {top_n} states with highest Q-values...")
    state_scores = []
    
    for state_hash, actions in q_table.items():
        if actions:
            max_q = max(actions.values())
            best_action = max(actions.keys(), key=lambda k: actions[k])
            state_scores.append((state_hash, max_q, best_action))
    
    # Sort by Q-value descending
    state_scores.sort(key=lambda x: x[1], reverse=True)
    
    print(f"  ✓ Found {len(state_scores)} states with Q-values")
    print(f"  ✓ Top Q-value: {state_scores[0][1]:.3f}")
    print(f"  ✓ Bottom Q-value: {state_scores[-1][1]:.3f}")
    
    return state_scores[:top_n]


def convert_state_hash_to_features(state_hash: tuple, state_builder: MoodleStateBuilder) -> Dict[str, float]:
    """
    Convert discretized state hash back to feature dict
    
    Since state is 12D: [knowledge, engagement, struggle, submission, review, 
                         resource, assessment, collaborative, progress, completion, 
                         diversity, consistency]
    
    We reverse engineer approximate feature values
    """
    state_vector = np.array(state_hash)
    
    # State indices (from state_builder.py)
    # 0: knowledge_level
    # 1: engagement_score  
    # 2: struggle_indicator
    # 3: submission_activity (from quiz/assignment features)
    # 4: review_activity (from reviewing)
    # 5: resource_usage (from page/resource views)
    # 6: assessment_score (from quiz performance)
    # 7: collaborative_activity (from forum/comments)
    # 8: progress_consistency (from time patterns)
    # 9: completion_rate
    # 10: diversity_score (from variety of activities)
    # 11: time_consistency (from session patterns)
    
    # Map back to original features (approximate)
    features = {
        'knowledge_level': float(state_vector[0]),
        'engagement_score': float(state_vector[1]),
        'struggle_indicator': float(state_vector[2]),
        'progress_rate': float(state_vector[8]),  # progress_consistency
        'completion_rate': float(state_vector[9]),
        'resource_diversity': float(state_vector[10]),  # diversity_score
        'assessment_performance': float(state_vector[6]),  # assessment_score
        'time_spent_avg': float(state_vector[11]),  # time_consistency
        
        # Approximate counts from normalized values (reverse scaling)
        'submitted_activities': int(state_vector[3] * 20),  # submission_activity * 20
        'comments_count': int(state_vector[7] * 10),  # collaborative_activity * 10
    }
    
    return features


def generate_test_cases(model_path: str, output_path: str, top_n: int = 10):
    """Generate test cases from top Q-value states"""
    
    print("="*70)
    print("GENERATE VALID TEST INPUTS FROM Q-TABLE")
    print("="*70)
    
    # Extract top states
    top_states = extract_top_states_from_qtable(model_path, top_n)
    
    # Convert to API format
    print(f"\n[3/3] Converting to API test format...")
    state_builder = MoodleStateBuilder()
    
    test_cases = []
    for i, (state_hash, max_q, best_action) in enumerate(top_states, 1):
        features = convert_state_hash_to_features(state_hash, state_builder)
        
        test_case = {
            'test_id': i,
            'description': f'Test case {i} - High Q-value state (q={max_q:.3f})',
            'expected_max_q_value': float(max_q),
            'best_action_id': int(best_action),
            'state_hash': list(state_hash),
            'api_request': {
                'student_id': i,
                'features': features,
                'top_k': 3
            }
        }
        test_cases.append(test_case)
        
        print(f"  Test {i}: Q-value={max_q:.3f}, Action={best_action}, State={state_hash[:3]}...")
    
    # Save to JSON
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    
    print(f"\n  ✓ Saved {len(test_cases)} test cases to {output_file}")
    
    print("\n" + "="*70)
    print("✅ TEST CASES GENERATED SUCCESSFULLY")
    print("="*70)
    
    # Print example test case
    print("\n📝 Example test case (copy to test API):")
    print("-"*70)
    example = test_cases[0]
    print(f"Expected Q-value: {example['expected_max_q_value']:.3f}")
    print(f"Expected best action: {example['best_action_id']}")
    print("\nCurl command:")
    print(f"""
curl -X POST http://localhost:8080/api/recommend \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(example['api_request'], indent=2)}'
""")
    
    return test_cases


if __name__ == '__main__':
    MODEL_PATH = 'models/qlearning_model.pkl'
    OUTPUT_PATH = 'test_cases_from_qtable.json'
    
    test_cases = generate_test_cases(MODEL_PATH, OUTPUT_PATH, top_n=10)
    
    print("\n🚀 Next steps:")
    print("  1. Start API: uvicorn api_service:app --reload --port 8080")
    print("  2. Test with generated cases in test_cases_from_qtable.json")
    print("  3. Verify q_values > 0 in API response")
