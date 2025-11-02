#!/usr/bin/env python3
"""
Example: Using the new structured API input format
"""

import requests
import json

API_URL = "http://localhost:8080/api/recommend"


def example_structured_input():
    """
    Example với Structured Format (RECOMMENDED)
    
    Format này match với state_description trong output
    """
    request = {
        "student_id": 12345,
        "features": {
            "performance": {
                "knowledge_level": 0.6,      # Hiểu bài: 60%
                "engagement_level": 0.8,     # Tham gia: 80%
                "struggle_indicator": 0.2    # Khó khăn: 20%
            },
            "activity_patterns": {
                "submission_activity": 0.4,       # Nộp bài: 40%
                "review_activity": 0.7,           # Xem lại: 70%
                "resource_usage": 0.8,            # Dùng tài nguyên: 80%
                "assessment_engagement": 0.6,     # Làm kiểm tra: 60%
                "collaborative_activity": 0.3     # Tương tác: 30%
            },
            "completion_metrics": {
                "overall_progress": 0.7,          # Tiến độ: 70%
                "module_completion_rate": 0.8,    # Hoàn thành: 80%
                "activity_diversity": 0.5,        # Đa dạng: 50%
                "completion_consistency": 0.6     # Nhất quán: 60%
            }
        },
        "top_k": 5
    }
    
    print("=" * 80)
    print("EXAMPLE: STRUCTURED INPUT FORMAT")
    print("=" * 80)
    print("\n📤 REQUEST:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(API_URL, json=request)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ RESPONSE:")
            print(f"Student ID: {result['student_id']}")
            print(f"Cluster: {result['cluster_name']} (ID: {result['cluster_id']})")
            
            print("\n📊 STATE DESCRIPTION:")
            for category, metrics in result['state_description'].items():
                print(f"\n  {category.upper()}:")
                for key, value in metrics.items():
                    print(f"    • {key}: {value:.2f}")
            
            print("\n🎯 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"\n  {i}. {rec['name']}")
                print(f"     Type: {rec['type']} | Difficulty: {rec['difficulty']}")
                print(f"     Q-value: {rec['q_value']:.4f}")
            
            print("\n" + "=" * 80)
            
        else:
            print(f"\n❌ ERROR {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Please start the API server first:")
        print("  uvicorn api_service:app --reload --port 8080")


def example_flat_input_backward_compatible():
    """
    Example với Flat Format (BACKWARD COMPATIBLE)
    
    Format cũ vẫn hoạt động
    """
    request = {
        "student_id": 12346,
        "features": {
            # Performance
            "knowledge_level": 0.6,
            "engagement_level": 0.8,
            "struggle_indicator": 0.2,
            # Activity patterns
            "submission_activity": 0.4,
            "review_activity": 0.7,
            "resource_usage": 0.8,
            "assessment_engagement": 0.6,
            "collaborative_activity": 0.3,
            # Completion metrics
            "overall_progress": 0.7,
            "module_completion_rate": 0.8,
            "activity_diversity": 0.5,
            "completion_consistency": 0.6
        },
        "top_k": 5
    }
    
    print("\n\n" + "=" * 80)
    print("EXAMPLE: FLAT INPUT FORMAT (BACKWARD COMPATIBLE)")
    print("=" * 80)
    print("\n📤 REQUEST:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(API_URL, json=request)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ RESPONSE: (Same format as structured)")
            print(f"Student ID: {result['student_id']}")
            print(f"Cluster: {result['cluster_name']}")
            print(f"State Vector: {result['state_vector']}")
            
        else:
            print(f"\n❌ ERROR {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")


def example_scenarios():
    """Các scenarios thực tế"""
    
    scenarios = [
        {
            "name": "Học sinh giỏi nhưng ít tương tác",
            "student_id": 1001,
            "features": {
                "performance": {
                    "knowledge_level": 0.9,
                    "engagement_level": 0.7,
                    "struggle_indicator": 0.1
                },
                "activity_patterns": {
                    "submission_activity": 0.8,
                    "review_activity": 0.6,
                    "resource_usage": 0.7,
                    "assessment_engagement": 0.9,
                    "collaborative_activity": 0.1  # ⚠️ Thấp
                },
                "completion_metrics": {
                    "overall_progress": 0.9,
                    "module_completion_rate": 0.9,
                    "activity_diversity": 0.6,
                    "completion_consistency": 0.8
                }
            }
        },
        {
            "name": "Học sinh cần hỗ trợ",
            "student_id": 1002,
            "features": {
                "performance": {
                    "knowledge_level": 0.3,
                    "engagement_level": 0.2,
                    "struggle_indicator": 0.7  # ⚠️ Cao
                },
                "activity_patterns": {
                    "submission_activity": 0.2,
                    "review_activity": 0.3,
                    "resource_usage": 0.4,
                    "assessment_engagement": 0.2,
                    "collaborative_activity": 0.1
                },
                "completion_metrics": {
                    "overall_progress": 0.3,
                    "module_completion_rate": 0.2,
                    "activity_diversity": 0.3,
                    "completion_consistency": 0.4
                }
            }
        },
        {
            "name": "Học sinh trung bình cân bằng",
            "student_id": 1003,
            "features": {
                "performance": {
                    "knowledge_level": 0.6,
                    "engagement_level": 0.6,
                    "struggle_indicator": 0.3
                },
                "activity_patterns": {
                    "submission_activity": 0.5,
                    "review_activity": 0.6,
                    "resource_usage": 0.6,
                    "assessment_engagement": 0.5,
                    "collaborative_activity": 0.4
                },
                "completion_metrics": {
                    "overall_progress": 0.6,
                    "module_completion_rate": 0.6,
                    "activity_diversity": 0.5,
                    "completion_consistency": 0.6
                }
            }
        }
    ]
    
    print("\n\n" + "=" * 80)
    print("EXAMPLE SCENARIOS")
    print("=" * 80)
    
    for scenario in scenarios:
        print(f"\n\n{'='*60}")
        print(f"📌 Scenario: {scenario['name']}")
        print(f"{'='*60}")
        
        request = {
            "student_id": scenario['student_id'],
            "features": scenario['features'],
            "top_k": 3
        }
        
        try:
            response = requests.post(API_URL, json=request)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n🎓 Cluster: {result['cluster_name']}")
                
                # Highlight key metrics
                perf = result['state_description']['performance']
                print(f"\n📊 Key Metrics:")
                print(f"  • Knowledge: {perf['knowledge_level']:.2f}")
                print(f"  • Engagement: {perf['engagement_level']:.2f}")
                print(f"  • Struggle: {perf['struggle_indicator']:.2f}")
                
                print(f"\n🎯 Recommendations:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"  {i}. {rec['name']} ({rec['type']} - {rec['difficulty']})")
                    
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: Cannot connect to API")
            break


if __name__ == '__main__':
    print("\n🚀 API Examples - Structured Input Format\n")
    
    # Example 1: Structured format
    example_structured_input()
    
    # Example 2: Flat format (backward compatible)
    example_flat_input_backward_compatible()
    
    # Example 3: Real scenarios
    example_scenarios()
    
    print("\n\n✅ All examples completed!")
