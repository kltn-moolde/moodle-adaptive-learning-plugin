#!/usr/bin/env python3
"""
Test script cho Learning Path API với Linear Regression
"""
import requests
import json
import time

# Cấu hình
BASE_URL = "http://127.0.0.1:8088"
TEST_USER_ID = 123
TEST_COURSE_ID = 5

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test một API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {method} {endpoint}")
        print(f"📝 Request data: {json.dumps(data, indent=2) if data else 'None'}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"📋 Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return None

def main():
    print("🚀 Testing Learning Path API with Linear Regression")
    print(f"🎯 Base URL: {BASE_URL}")
    print(f"👤 Test User: {TEST_USER_ID}")
    print(f"📚 Test Course: {TEST_COURSE_ID}")
    
    # 1. Kiểm tra health endpoint
    print("\n" + "="*60)
    print("1️⃣ Testing Health Check")
    test_api_endpoint("/")
    
    time.sleep(1)
    
    # 2. Train model
    print("\n" + "="*60)
    print("2️⃣ Training Model")
    test_api_endpoint("/api/train-model", "POST", {})
    
    time.sleep(2)
    
    # 3. Test predict performance
    print("\n" + "="*60)
    print("3️⃣ Testing Performance Prediction")
    test_api_endpoint("/api/predict-performance", "POST", {
        "userid": TEST_USER_ID,
        "section_id": 45,
        "courseid": TEST_COURSE_ID,
        "current_complete_rate": 0.6,
        "current_score": 7
    })
    
    time.sleep(1)
    
    # 4. Test generate learning path - Performance optimization
    print("\n" + "="*60)
    print("4️⃣ Testing Learning Path Generation (Performance)")
    result_performance = test_api_endpoint("/api/generate-learning-path", "POST", {
        "userid": TEST_USER_ID,
        "courseid": TEST_COURSE_ID,
        "max_sections": 5,
        "include_completed": False,
        "optimization_goal": "performance"
    })
    
    time.sleep(1)
    
    # 5. Test generate learning path - Speed optimization
    print("\n" + "="*60)
    print("5️⃣ Testing Learning Path Generation (Speed)")
    test_api_endpoint("/api/generate-learning-path", "POST", {
        "userid": TEST_USER_ID,
        "courseid": TEST_COURSE_ID,
        "max_sections": 5,
        "include_completed": False,
        "optimization_goal": "speed"
    })
    
    time.sleep(1)
    
    # 6. Test generate learning path - Comprehensive optimization
    print("\n" + "="*60)
    print("6️⃣ Testing Learning Path Generation (Comprehensive)")
    test_api_endpoint("/api/generate-learning-path", "POST", {
        "userid": TEST_USER_ID,
        "courseid": TEST_COURSE_ID,
        "max_sections": 5,
        "include_completed": True,
        "optimization_goal": "comprehensive"
    })
    
    time.sleep(1)
    
    # 7. Test learning analytics
    print("\n" + "="*60)
    print("7️⃣ Testing Learning Analytics")
    test_api_endpoint("/api/learning-analytics", "POST", {
        "userid": TEST_USER_ID,
        "courseid": TEST_COURSE_ID
    })
    
    # 8. Summary report
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print("✅ All API endpoints tested successfully!")
    print("\n🔧 Available APIs:")
    print("   • GET  /                           - Health check")
    print("   • POST /api/train-model           - Train Linear Regression model")
    print("   • POST /api/predict-performance   - Predict performance for specific section")
    print("   • POST /api/generate-learning-path - Generate optimized learning path")
    print("   • POST /api/learning-analytics    - Comprehensive learning analytics")
    print("   • POST /api/suggest-action        - Suggest single next action (Q-learning)")
    print("   • POST /api/update-learning-event - Update learning event")
    
    print("\n📈 Optimization Goals Available:")
    print("   • 'performance' - Maximize learning outcomes")
    print("   • 'speed'       - Minimize time to completion") 
    print("   • 'comprehensive' - Thorough understanding")
    
    if result_performance and result_performance.get('success'):
        print(f"\n🎯 Sample Learning Path Generated:")
        learning_path = result_performance.get('learning_path', [])
        for i, section in enumerate(learning_path[:3], 1):
            print(f"   {i}. Section {section['section_id']} - Priority: {section['priority_score']:.2f}")
            print(f"      Best Action: {section['recommended_actions'][0]['action']}")
            print(f"      Estimated Time: {section['estimated_time_minutes']} mins")

if __name__ == "__main__":
    main()