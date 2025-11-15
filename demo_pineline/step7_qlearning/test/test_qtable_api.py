#!/usr/bin/env python3
"""
Test Q-table API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def test_top_positive_states(top_n=3):
    """Test API để lấy top states với Q-value cao nhất"""
    print("="*80)
    print(f"🔍 Testing: GET /api/qtable/states/positive?top_n={top_n}")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/qtable/states/positive?top_n={top_n}")
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    
    print(f"\n📊 Total positive states: {data['total_positive_states']}")
    print(f"📋 Returned: {data['returned']}")
    
    for i, state_info in enumerate(data['top_states'], 1):
        print(f"\n{'='*80}")
        print(f"🎯 State #{i} - Max Q-value: {state_info['max_q_value']:.2f}")
        print(f"{'='*80}")
        
        print(f"\n📌 State Vector: {state_info['state']}")
        
        desc = state_info['state_description']
        print(f"\n📊 State Description:")
        print(f"   • Cluster: {desc['cluster_name']} (ID: {desc['cluster_id']})")
        print(f"   • Module: {desc['module_name']}")
        print(f"   • Progress: {desc['progress_label']} | Score: {desc['score_label']}")
        print(f"   • Recent action: {desc['recent_action']}")
        print(f"   • Status: {desc['stuck_label']}")
        
        print(f"\n🎓 Top 3 Recommendations:")
        for j, rec in enumerate(state_info['top_recommendations'], 1):
            print(f"   {j}. [{rec['activity_type']:10}] {rec['module_name'][:50]:50} | Q={rec['q_value']:.2f}")


def test_recommend_with_top_state():
    """Test recommendation với state có Q-value cao nhất"""
    print("\n" + "="*80)
    print("🎯 Testing: POST /api/recommend với top state")
    print("="*80)
    
    # Get top state
    response = requests.get(f"{BASE_URL}/api/qtable/states/positive?top_n=1")
    data = response.json()
    
    if not data['top_states']:
        print("❌ No top states found")
        return
    
    top_state = data['top_states'][0]
    print(f"\n📌 Using top state with Q-value: {top_state['max_q_value']:.2f}")
    print(f"   State: {top_state['state']}")
    
    # Test recommendation
    payload = {
        "student_id": 99999,
        "state": top_state['state'],
        "top_k": 5,
        "exclude_action_ids": []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recommend",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 Cluster: {result['cluster_name']}")
    
    print(f"\n🎓 Top {len(result['recommendations'])} Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"   {i}. [{rec['activity_type']:10}] {rec['module_name'][:50]:50}")
        print(f"      Purpose: {rec['purpose']:15} | Difficulty: {rec['difficulty']:6} | Q-value: {rec['q_value']:.2f}")


if __name__ == '__main__':
    # Test 1: Get top 3 states
    test_top_positive_states(top_n=3)
    
    # Test 2: Recommend với top state
    test_recommend_with_top_state()
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)
