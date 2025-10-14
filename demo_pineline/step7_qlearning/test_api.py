#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Q-Learning Recommendation API
===================================
Test all API endpoints
"""

import requests
import json
from typing import Dict, List


# API Configuration
BASE_URL = "http://localhost:5001"
API_V1 = f"{BASE_URL}/api/v1"


def test_health_check():
    """Test health check endpoint"""
    print("="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_get_actions():
    """Test get actions endpoint"""
    print("="*70)
    print("TEST 2: Get All Actions")
    print("="*70)
    
    response = requests.get(f"{API_V1}/actions")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Total actions: {data['total']}")
    print(f"First 3 actions:")
    for action in data['actions'][:3]:
        print(f"  - {action['name']} ({action['type']}, {action['difficulty']})")
    print()
    
    # Test with filters
    print("Filtering by type='quiz':")
    response = requests.get(f"{API_V1}/actions?type=quiz")
    data = response.json()
    print(f"  Found: {data['filtered']} quizzes")
    print()


def test_student_state():
    """Test student state endpoint"""
    print("="*70)
    print("TEST 3: Get Student State")
    print("="*70)
    
    # High achiever student
    student_features = {
        "userid": 999,
        "mean_module_grade": 0.92,
        "total_events": 0.88,
        "course_module": 0.85,
        "viewed": 0.90,
        "attempt": 0.85,
        "feedback_viewed": 0.78,
        "submitted": 0.88,
        "reviewed": 0.75,
        "course_module_viewed": 0.92,
        "module_count": 0.85,
        "course_module_completion": 0.90,
        "created": 0.12,
        "updated": 0.15,
        "downloaded": 0.65
    }
    
    response = requests.post(
        f"{API_V1}/student/state",
        json={"student_features": student_features}
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Interpretation:")
    for key, value in data['interpretation'].items():
        print(f"  {key}: {value}")
    print(f"Discrete state: {data['discrete_state'][:3]}... (first 3 dims)")
    print()


def test_recommendations_high_achiever():
    """Test recommendations for high achiever"""
    print("="*70)
    print("TEST 4: Recommendations - High Achiever")
    print("="*70)
    
    student_features = {
        "userid": 999,
        "mean_module_grade": 0.92,
        "total_events": 0.88,
        "course_module": 0.85,
        "viewed": 0.90,
        "attempt": 0.85,
        "feedback_viewed": 0.78,
        "submitted": 0.88,
        "reviewed": 0.75,
        "course_module_viewed": 0.92,
        "module_count": 0.85,
        "course_module_completion": 0.90,
        "created": 0.12,
        "updated": 0.15,
        "downloaded": 0.65
    }
    
    payload = {
        "student_features": student_features,
        "completed_resources": [52, 60],
        "top_k": 5,
        "use_heuristic_fallback": True
    }
    
    response = requests.post(
        f"{API_V1}/recommend",
        json=payload
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"\nStudent State:")
    for key, value in data['student_state'].items():
        if key != 'discrete_state':
            print(f"  {key}: {value:.3f}")
    
    print(f"\nMetadata:")
    print(f"  Total recommendations: {data['metadata']['total_recommendations']}")
    print(f"  Q-Learning: {data['metadata']['method_breakdown']['q_learning']}")
    print(f"  Heuristic: {data['metadata']['method_breakdown']['heuristic']}")
    print(f"  Heuristic ratio: {data['metadata']['heuristic_ratio']:.1%}")
    
    print(f"\nTop {len(data['recommendations'])} Recommendations:")
    for i, rec in enumerate(data['recommendations'], 1):
        method = rec['recommendation_method']
        score = rec.get('q_value', rec.get('heuristic_score', 0))
        print(f"  {i}. {rec['resource_name']}")
        print(f"     Type: {rec['action_type']}, Difficulty: {rec.get('difficulty', 'N/A')}")
        print(f"     Method: {method}, Score: {score:.3f}")
    print()


def test_recommendations_struggling():
    """Test recommendations for struggling student"""
    print("="*70)
    print("TEST 5: Recommendations - Struggling Student")
    print("="*70)
    
    student_features = {
        "userid": 888,
        "mean_module_grade": 0.32,
        "total_events": 0.28,
        "course_module": 0.35,
        "viewed": 0.40,
        "attempt": 0.25,
        "feedback_viewed": 0.20,
        "submitted": 0.30,
        "reviewed": 0.15,
        "course_module_viewed": 0.35,
        "module_count": 0.30,
        "course_module_completion": 0.25,
        "created": 0.45,  # High struggle
        "updated": 0.50,
        "downloaded": 0.20
    }
    
    payload = {
        "student_features": student_features,
        "completed_resources": [],
        "top_k": 5,
        "use_heuristic_fallback": True
    }
    
    response = requests.post(
        f"{API_V1}/recommend",
        json=payload
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"\nStudent State:")
    for key, value in data['student_state'].items():
        if key != 'discrete_state':
            print(f"  {key}: {value:.3f}")
    
    print(f"\nTop {len(data['recommendations'])} Recommendations:")
    for i, rec in enumerate(data['recommendations'], 1):
        method = rec['recommendation_method']
        score = rec.get('q_value', rec.get('heuristic_score', 0))
        print(f"  {i}. {rec['resource_name']}")
        print(f"     Type: {rec['action_type']}, Difficulty: {rec.get('difficulty', 'N/A')}")
        print(f"     Method: {method}, Score: {score:.3f}")
    print()


def test_get_stats():
    """Test stats endpoint"""
    print("="*70)
    print("TEST 6: System Statistics")
    print("="*70)
    
    response = requests.get(f"{API_V1}/stats")
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"\nQ-Table:")
    print(f"  Size: {data['q_table_size']} entries")
    print(f"  Training updates: {data['training_updates']}")
    
    print(f"\nAction Space:")
    print(f"  Total actions: {data['action_space_size']}")
    
    print(f"\nState Space:")
    print(f"  Dimensions: {data['state_dimension']}")
    print(f"  Bins: {data['discretization_bins']}")
    print(f"  Possible states: {data['possible_states']:,}")
    
    print(f"\nHyperparameters:")
    print(f"  Learning rate (α): {data['hyperparameters']['learning_rate']}")
    print(f"  Discount factor (γ): {data['hyperparameters']['discount_factor']}")
    print(f"  Epsilon (ε): {data['hyperparameters']['epsilon']}")
    print()


def test_error_handling():
    """Test error handling"""
    print("="*70)
    print("TEST 7: Error Handling")
    print("="*70)
    
    # Test 404
    print("Testing 404 Not Found:")
    response = requests.get(f"{API_V1}/nonexistent")
    print(f"  Status: {response.status_code}")
    print(f"  Message: {response.json()['message']}")
    print()
    
    # Test missing features
    print("Testing missing student_features:")
    response = requests.post(
        f"{API_V1}/recommend",
        json={"top_k": 5}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Error: {response.json()['error']}")
    print()
    
    # Test incomplete features
    print("Testing incomplete student_features:")
    response = requests.post(
        f"{API_V1}/recommend",
        json={
            "student_features": {
                "userid": 123,
                "mean_module_grade": 0.5
            }
        }
    )
    print(f"  Status: {response.status_code}")
    print(f"  Message: {response.json()['message']}")
    print()


def test_comparison():
    """Compare with and without heuristic fallback"""
    print("="*70)
    print("TEST 8: Compare With/Without Heuristic Fallback")
    print("="*70)
    
    # New student (likely unseen state)
    student_features = {
        "userid": 777,
        "mean_module_grade": 0.55,
        "total_events": 0.50,
        "course_module": 0.48,
        "viewed": 0.52,
        "attempt": 0.45,
        "feedback_viewed": 0.40,
        "submitted": 0.48,
        "reviewed": 0.35,
        "course_module_viewed": 0.50,
        "module_count": 0.45,
        "course_module_completion": 0.42,
        "created": 0.25,
        "updated": 0.28,
        "downloaded": 0.38
    }
    
    # WITH heuristic fallback
    print("\n1. WITH Heuristic Fallback (use_heuristic_fallback=True):")
    response = requests.post(
        f"{API_V1}/recommend",
        json={
            "student_features": student_features,
            "top_k": 3,
            "use_heuristic_fallback": True
        }
    )
    data = response.json()
    print(f"   Method breakdown: {data['metadata']['method_breakdown']}")
    for i, rec in enumerate(data['recommendations'][:3], 1):
        method = rec['recommendation_method']
        score = rec.get('q_value', rec.get('heuristic_score', 0))
        print(f"   {i}. {rec['resource_name']} ({method}, score={score:.3f})")
    
    # WITHOUT heuristic fallback
    print("\n2. WITHOUT Heuristic Fallback (use_heuristic_fallback=False):")
    response = requests.post(
        f"{API_V1}/recommend",
        json={
            "student_features": student_features,
            "top_k": 3,
            "use_heuristic_fallback": False
        }
    )
    data = response.json()
    print(f"   Method breakdown: {data['metadata']['method_breakdown']}")
    for i, rec in enumerate(data['recommendations'][:3], 1):
        method = rec['recommendation_method']
        score = rec.get('q_value', rec.get('heuristic_score', 0))
        print(f"   {i}. {rec['resource_name']} ({method}, score={score:.3f})")
    
    print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "Q-LEARNING API TEST SUITE" + " "*28 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    try:
        # Test endpoints
        test_health_check()
        test_get_actions()
        test_student_state()
        test_recommendations_high_achiever()
        test_recommendations_struggling()
        test_get_stats()
        test_error_handling()
        test_comparison()
        
        print("="*70)
        print("✓ ALL TESTS COMPLETED")
        print("="*70)
        print()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure the API server is running:")
        print("   python3 api.py")
        print()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print()


if __name__ == '__main__':
    main()
