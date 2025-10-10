#!/usr/bin/env python3
"""
Test script cho Learning Path Explanation API
"""

import requests
import json

def test_explanation_api():
    """Test API learning path explanation"""
    
    # Test data
    test_data = {
        "user_id": "4",
        "course_id": "5",
        "learning_path": {
            "suggested_action": "do_quiz_same",
            "q_value": 0.75,
            "source_state": {
                "section_id": 2,
                "lesson_name": "Basic Concepts",
                "quiz_level": "medium",
                "complete_rate_bin": 0.6,
                "score_bin": 3
            }
        }
    }
    
    print("🧪 Testing Learning Path Explanation API...")
    print("=" * 50)
    
    try:
        # Test health check
        print("\n1. Testing health check...")
        response = requests.get("http://localhost:5001/api/learning-path/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
        
        # Test explanation generation
        print("\n2. Testing explanation generation...")
        response = requests.post(
            "http://localhost:5001/api/learning-path/explain",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Explanation generated successfully")
            print(f"From cache: {result.get('from_cache', False)}")
            
            explanation = result.get('data', {})
            print("\n📝 Explanation content:")
            print(f"Reason: {explanation.get('reason', 'N/A')}")
            print(f"Current Status: {explanation.get('current_status', 'N/A')}")
            print(f"Benefit: {explanation.get('benefit', 'N/A')}")
            print(f"Motivation: {explanation.get('motivation', 'N/A')}")
            print(f"Next Steps: {explanation.get('next_steps', [])}")
        else:
            print(f"❌ Explanation generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return
        
        # Test getting same explanation again (should be from cache)
        print("\n3. Testing cache retrieval...")
        response = requests.post(
            "http://localhost:5001/api/learning-path/explain",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('from_cache'):
                print("✅ Cache working correctly")
            else:
                print("⚠️ Cache might not be working")
        else:
            print(f"❌ Cache test failed: {response.status_code}")
        
        # Test get user explanations
        print("\n4. Testing user explanations retrieval...")
        response = requests.get("http://localhost:5001/api/learning-path/explanations/4/5")
        
        if response.status_code == 200:
            result = response.json()
            explanations = result.get('data', [])
            print(f"✅ Retrieved {len(explanations)} explanations for user")
        else:
            print(f"❌ User explanations failed: {response.status_code}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_explanation_api()