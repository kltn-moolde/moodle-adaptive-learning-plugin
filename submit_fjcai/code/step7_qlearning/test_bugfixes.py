#!/usr/bin/env python3
"""
Test script to verify bug fixes
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

print("=" * 70)
print("Testing Bug Fixes")
print("=" * 70)

# Test 1: ActivityRecommender initialization
print("\n1. Testing ActivityRecommender initialization...")
try:
    from core.activity_recommender import ActivityRecommender
    
    recommender = ActivityRecommender(
        po_lo_path=str(HERE / 'data' / 'Po_Lo_5.json'),
        course_structure_path=str(HERE / 'data' / 'course_structure.json'),
        course_id=5
    )
    print("   ✓ ActivityRecommender initialized successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Similar state matching
print("\n2. Testing similar state matching in agent...")
try:
    from core.rl.agent import QLearningAgentV2
    import pickle
    
    # Load trained model
    model_path = HERE / 'models' / 'qtable_5.pkl'
    if model_path.exists():
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
        
        # Recreate agent
        agent = QLearningAgentV2(n_actions=15)
        
        # Restore Q-table
        q_table_restored = {}
        for state_str, actions in data['q_table'].items():
            state_tuple = eval(state_str)
            q_table_restored[state_tuple] = actions
        agent.q_table = q_table_restored
        
        print(f"   ✓ Loaded Q-table with {len(agent.q_table)} states")
        
        # Test with unseen state
        unseen_state = (2, 1, 0.25, 0.25, 0, 0)
        print(f"   Testing unseen state: {unseen_state}")
        print(f"   State in Q-table: {unseen_state in agent.q_table}")
        
        # Try to find similar state
        similar = agent._find_similar_state(unseen_state)
        if similar:
            print(f"   ✓ Found similar state: {similar}")
            print(f"   Distance: {agent._state_distance(unseen_state, similar):.2f}")
        else:
            print("   ✗ No similar state found")
        
        # Test recommendation
        recommendations = agent.recommend_action(
            state=unseen_state,
            available_actions=list(range(15)),
            top_k=3,
            use_similar_state=True
        )
        print(f"   ✓ Got {len(recommendations)} recommendations:")
        for i, (action, q_val) in enumerate(recommendations, 1):
            print(f"      {i}. Action {action}: Q={q_val:.2f}")
            
    else:
        print(f"   ⚠️  Model file not found: {model_path}")
        
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Full integration test
print("\n3. Testing full recommendation pipeline...")
try:
    from services.business.recommendation import RecommendationService
    from services.model.loader import ModelLoader
    
    # Load model
    loader = ModelLoader(
        course_id=5,
        model_path=HERE / 'models' / 'qtable_5.pkl',
        course_path=HERE / 'data' / 'course_structure.json',
        cluster_profiles_path=HERE / 'data' / 'cluster_profiles.json'
    )
    loader.load_all(verbose=False)
    
    # Create recommendation service with activity recommender
    rec_service = RecommendationService(
        agent=loader.agent,
        action_space=loader.action_space,
        state_builder=loader.state_builder,
        course_structure_path=str(HERE / 'data' / 'course_structure.json'),
        activity_recommender=recommender  # Use recommender from Test 1
    )
    
    # Test with unseen state
    test_state = (2, 1, 0.25, 0.25, 0, 0)
    recommendations = rec_service.get_recommendations(
        state=test_state,
        cluster_id=2,
        top_k=3,
        module_idx=1,
        course_id=5,
        lesson_id=39
    )
    
    print(f"   ✓ Got {len(recommendations)} recommendations")
    if rec_service.activity_recommender:
        print("   ✓ ActivityRecommender is available")
    else:
        print("   ✗ ActivityRecommender is None")
        
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"      {i}. {rec.get('action_type')}: Q={rec.get('q_value', 0):.2f}")
        
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Testing Complete")
print("=" * 70)
