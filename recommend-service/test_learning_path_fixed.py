#!/usr/bin/env python3
"""
Test script để kiểm tra API Learning Path đã được sửa lỗi
"""

import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8088"

def test_generate_learning_path():
    """Test API generate learning path với các tham số khác nhau"""
    print("🔄 Testing Generate Learning Path API...")
    
    test_cases = [
        {
            "name": "Basic Performance Optimization",
            "payload": {
                "userid": 5,
                "courseid": 5,
                "max_sections": 5,
                "include_completed": False,
                "optimization_goal": "performance"
            }
        },
        {
            "name": "Speed Optimization", 
            "payload": {
                "userid": 10,
                "courseid": 5,
                "max_sections": 3,
                "include_completed": True,
                "optimization_goal": "speed"
            }
        },
        {
            "name": "Comprehensive Learning",
            "payload": {
                "userid": 15,
                "courseid": 5,
                "max_sections": 8,
                "include_completed": False,
                "optimization_goal": "comprehensive"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        try:
            response = requests.post(f"{API_BASE}/api/generate-learning-path", 
                                   json=test_case['payload'], timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API Success!")
                print(f"📊 Generated {data.get('total_sections', 0)} sections")
                print(f"⏱️  Total time: {data.get('estimated_total_time_minutes', 0)} minutes")
                print(f"📈 Avg performance score: {data.get('average_performance_score', 0)}")
                print(f"🎯 Optimization goal: {data.get('optimization_goal', 'N/A')}")
                
                # Kiểm tra learning path structure
                learning_path = data.get('learning_path', [])
                if learning_path:
                    print(f"🔍 First section: {learning_path[0]['section_name']}")
                    print(f"   Priority score: {learning_path[0]['priority_score']}")
                    print(f"   Next action: {learning_path[0]['recommended_actions'][0]['action']}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def test_predict_performance():
    """Test API predict performance"""
    print("\n\n🔄 Testing Predict Performance API...")
    
    test_payload = {
        "userid": 5,
        "section_id": 20,
        "current_complete_rate": 0.7,
        "current_score": 6.5
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/predict-performance", 
                               json=test_payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predict Performance API Success!")
            print(f"🎯 Predicted performance: {data.get('predicted_performance', 'N/A')}")
            print(f"📊 Performance level: {data.get('performance_level', {}).get('level', 'N/A')}")
            print(f"👤 User cluster: {data.get('user_cluster', 'N/A')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing predict performance: {e}")

def test_learning_analytics():
    """Test API learning analytics"""  
    print("\n\n🔄 Testing Learning Analytics API...")
    
    test_payload = {
        "userid": 5,
        "courseid": 5
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/learning-analytics",
                               json=test_payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Learning Analytics API Success!")
            analytics = data.get('analytics', {})
            
            overall = analytics.get('overall_progress', {})
            print(f"📈 Completion: {overall.get('completion_percentage', 0)}%")
            print(f"📊 Average score: {overall.get('average_score', 0)}")
            
            profile = analytics.get('user_profile', {})  
            print(f"👤 Learning style: {profile.get('learning_style', 'N/A')}")
            
            predictions = analytics.get('performance_predictions', [])
            if predictions:
                print(f"🔮 Top prediction: Section {predictions[0].get('section_id')} - {predictions[0].get('predicted_performance')}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing learning analytics: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Learning Path API Tests")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ Service is running!")
        else:
            print("❌ Service not responding properly")
            return
    except:
        print("❌ Cannot connect to service. Make sure it's running on port 8088")
        return
    
    # Run tests
    test_generate_learning_path()
    test_predict_performance() 
    test_learning_analytics()
    
    print("\n" + "=" * 50)
    print(f"🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()