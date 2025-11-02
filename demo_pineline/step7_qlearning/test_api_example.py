#!/usr/bin/env python3
"""
Test API examples - Minh họa cách gọi API và hiểu input/output
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8080"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Kiểm tra health của service"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_model_info():
    """Lấy thông tin model"""
    print_section("TEST 2: Model Info")
    
    response = requests.get(f"{BASE_URL}/api/model-info")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_recommend_with_features():
    """Test gợi ý với features (case thực tế)"""
    print_section("TEST 3: Recommend với Features (Sinh viên #12345)")
    
    # Sinh viên #12345 có profile:
    # - Kiến thức trung bình (60%)
    # - Tham gia thấp (46.7%)
    # - Xem lại nhiều nhưng ít làm bài kiểm tra
    request_data = {
        "student_id": 12345,  # 👈 ĐÃ FIX: giờ có student_id
        "features": {
            "mean_module_grade": 0.6,
            "total_events": 0.9,
            "viewed": 0.5,
            "attempt": 0.2,
            "feedback_viewed": 0.8,
            "module_count": 0.3,
            "course_module_completion": 0.8
        },
        "top_k": 5
    }
    
    print("📥 INPUT:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/recommend", json=request_data)
    print(f"\n📤 OUTPUT (Status: {response.status_code}):")
    result = response.json()
    
    # Print formatted output
    print(f"\n✅ Success: {result['success']}")
    print(f"👤 Student ID: {result['student_id']}")
    print(f"📊 Cluster: {result['cluster_id']} - {result['cluster_name']}")
    
    print("\n📈 State Description:")
    desc = result['state_description']
    
    print("   Performance:")
    for key, val in desc['performance'].items():
        print(f"      - {key}: {val:.3f}")
    
    print("   Activity Patterns:")
    for key, val in desc['activity_patterns'].items():
        print(f"      - {key}: {val:.3f}")
    
    print("   Completion Metrics:")
    for key, val in desc['completion_metrics'].items():
        print(f"      - {key}: {val:.3f}")
    
    print(f"\n🎯 Top {len(result['recommendations'])} Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"   {i}. [{rec['type']}] {rec['name']}")
        print(f"      - Purpose: {rec['purpose']}, Difficulty: {rec['difficulty']}")
        print(f"      - Q-value: {rec['q_value']:.4f}, ID: {rec['action_id']}")
    
    print(f"\n🤖 Model Info:")
    for key, val in result['model_info'].items():
        print(f"   - {key}: {val}")

def test_recommend_with_state():
    """Test gợi ý với state vector trực tiếp"""
    print_section("TEST 4: Recommend với State Vector")
    
    # Trường hợp đã có state vector sẵn (từ preprocessing khác)
    request_data = {
        "student_id": 67890,
        "state": [0.75, 0.8, 0.6, 0.5, 0.9, 0.4, 0.85, 0.0, 0.5, 0.7, 0.3, 0.8],
        "top_k": 3
    }
    
    print("📥 INPUT (với state vector):")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/recommend", json=request_data)
    result = response.json()
    
    print(f"\n📤 OUTPUT:")
    print(f"✅ Success: {result['success']}")
    print(f"👤 Student ID: {result['student_id']}")
    print(f"📊 Cluster: {result['cluster_id']} - {result['cluster_name']}")
    print(f"🎯 Recommendations: {len(result['recommendations'])} items")

def test_recommend_with_exclusions():
    """Test gợi ý với loại trừ một số activities"""
    print_section("TEST 5: Recommend với Exclusions")
    
    # Sinh viên đã làm xong một số bài, loại trừ khỏi gợi ý
    request_data = {
        "student_id": 11111,
        "features": {
            "mean_module_grade": 0.85,
            "total_events": 0.95,
            "viewed": 0.8,
            "attempt": 0.7,
            "feedback_viewed": 0.9,
            "module_count": 0.6,
            "course_module_completion": 0.9
        },
        "top_k": 3,
        "exclude_action_ids": [64, 70, 58]  # Đã làm xong 3 bài này
    }
    
    print("📥 INPUT (loại trừ activities [64, 70, 58]):")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/recommend", json=request_data)
    result = response.json()
    
    print(f"\n📤 Recommendations (không có ID 64, 70, 58):")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"   {i}. ID={rec['action_id']}: {rec['name']}")

def compare_students():
    """So sánh 3 loại sinh viên khác nhau"""
    print_section("TEST 6: So Sánh 3 Loại Sinh Viên")
    
    students = {
        "Sinh viên yếu": {
            "student_id": 1001,
            "features": {
                "mean_module_grade": 0.3,
                "total_events": 0.4,
                "viewed": 0.2,
                "attempt": 0.1,
                "feedback_viewed": 0.3,
                "module_count": 0.2,
                "course_module_completion": 0.2
            },
            "top_k": 3
        },
        "Sinh viên trung bình": {
            "student_id": 2002,
            "features": {
                "mean_module_grade": 0.6,
                "total_events": 0.7,
                "viewed": 0.5,
                "attempt": 0.4,
                "feedback_viewed": 0.6,
                "module_count": 0.5,
                "course_module_completion": 0.6
            },
            "top_k": 3
        },
        "Sinh viên giỏi": {
            "student_id": 3003,
            "features": {
                "mean_module_grade": 0.95,
                "total_events": 0.98,
                "viewed": 0.9,
                "attempt": 0.85,
                "feedback_viewed": 0.95,
                "module_count": 0.8,
                "course_module_completion": 0.95
            },
            "top_k": 3
        }
    }
    
    for student_type, data in students.items():
        print(f"\n--- {student_type} (ID: {data['student_id']}) ---")
        
        response = requests.post(f"{BASE_URL}/api/recommend", json=data)
        result = response.json()
        
        print(f"Cluster: {result['cluster_name']}")
        desc = result['state_description']
        print(f"Knowledge Level: {desc['performance']['knowledge_level']:.2f}")
        print(f"Engagement Level: {desc['performance']['engagement_level']:.2f}")
        print(f"Overall Progress: {desc['completion_metrics']['overall_progress']:.2f}")
        
        print("Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec['name']} ({rec['difficulty']})")

def main():
    print("\n🚀 ADAPTIVE LEARNING API TEST SUITE")
    print("="*70)
    
    try:
        # Test 1-2: Basic checks
        test_health()
        test_model_info()
        
        # Test 3-5: Recommendation scenarios
        test_recommend_with_features()
        test_recommend_with_state()
        test_recommend_with_exclusions()
        
        # Test 6: Compare students
        compare_students()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("👉 Make sure the server is running:")
        print("   cd demo_pineline/step7_qlearning")
        print("   uvicorn api_service:app --reload --port 8080")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
