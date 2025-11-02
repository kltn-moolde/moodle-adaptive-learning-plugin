#!/usr/bin/env python3
"""Test API with new structured format matching state dimensions"""

import requests
import json

API_URL = "http://localhost:8080/api/recommend"


def test_structured_format():
    """Test with new nested structure matching state_description"""
    print("=" * 80)
    print("TEST 1: STRUCTURED FORMAT (NEW - RECOMMENDED)")
    print("=" * 80)
    
    request_data = {
        "student_id": 1,
        "features": {
            "performance": {
                "knowledge_level": 0.3,
                "engagement_level": 0.1,
                "struggle_indicator": 0.0
            },
            "activity_patterns": {
                "submission_activity": 0.0,
                "review_activity": 0.75,
                "resource_usage": 0.75,
                "assessment_engagement": 0.75,
                "collaborative_activity": 0.0
            },
            "completion_metrics": {
                "overall_progress": 0.75,
                "module_completion_rate": 0.1,
                "activity_diversity": 0.25,
                "completion_consistency": 0.5
            }
        },
        "top_k": 3
    }
    
    print("\n📤 REQUEST (Structured):")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(API_URL, json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ RESPONSE SUCCESS:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n📊 STATE VECTOR:", result['state_vector'])
        print("\n📋 STATE DESCRIPTION:")
        for category, values in result['state_description'].items():
            print(f"\n  {category}:")
            for key, val in values.items():
                print(f"    {key}: {val}")
    else:
        print(f"\n❌ ERROR {response.status_code}:")
        print(response.text)


def test_flat_format_backward_compatible():
    """Test with old flat format (backward compatible)"""
    print("\n\n" + "=" * 80)
    print("TEST 2: FLAT FORMAT (OLD - BACKWARD COMPATIBLE)")
    print("=" * 80)
    
    request_data = {
        "student_id": 2,
        "features": {
            # Performance
            "knowledge_level": 0.3,
            "engagement_level": 0.1,
            "struggle_indicator": 0.0,
            # Activity patterns
            "submission_activity": 0.0,
            "review_activity": 0.75,
            "resource_usage": 0.75,
            "assessment_engagement": 0.75,
            "collaborative_activity": 0.0,
            # Completion metrics
            "overall_progress": 0.75,
            "module_completion_rate": 0.1,
            "activity_diversity": 0.25,
            "completion_consistency": 0.5
        },
        "top_k": 3
    }
    
    print("\n📤 REQUEST (Flat):")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(API_URL, json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ RESPONSE SUCCESS:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n📊 STATE VECTOR:", result['state_vector'])
    else:
        print(f"\n❌ ERROR {response.status_code}:")
        print(response.text)


def test_old_legacy_format():
    """Test với format cũ hoàn toàn (legacy compatibility)"""
    print("\n\n" + "=" * 80)
    print("TEST 3: LEGACY FORMAT (VERY OLD - WITH OLD KEY NAMES)")
    print("=" * 80)
    
    request_data = {
        "student_id": 3,
        "features": {
            # Old key names
            "knowledge_level": 0.6,
            "engagement_score": 0.8,  # old name for engagement_level
            "struggle_indicator": 0.1,
            "assessment_performance": 0.7,  # maps to assessment_engagement
            "progress_rate": 0.75,  # maps to overall_progress
            "completion_rate": 0.8,  # maps to module_completion_rate
            "resource_diversity": 0.5,  # maps to activity_diversity
            "time_spent_avg": 0.6  # maps to completion_consistency
        },
        "top_k": 3
    }
    
    print("\n📤 REQUEST (Legacy):")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(API_URL, json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ RESPONSE SUCCESS:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n📊 STATE VECTOR:", result['state_vector'])
    else:
        print(f"\n❌ ERROR {response.status_code}:")
        print(response.text)


def compare_results():
    """So sánh kết quả giữa structured và flat format"""
    print("\n\n" + "=" * 80)
    print("COMPARISON: STRUCTURED vs FLAT FORMAT")
    print("=" * 80)
    
    # Same values, different format
    structured = {
        "student_id": 100,
        "features": {
            "performance": {
                "knowledge_level": 0.5,
                "engagement_level": 0.5,
                "struggle_indicator": 0.2
            },
            "activity_patterns": {
                "submission_activity": 0.3,
                "review_activity": 0.6,
                "resource_usage": 0.7,
                "assessment_engagement": 0.8,
                "collaborative_activity": 0.1
            },
            "completion_metrics": {
                "overall_progress": 0.6,
                "module_completion_rate": 0.7,
                "activity_diversity": 0.4,
                "completion_consistency": 0.5
            }
        },
        "top_k": 3
    }
    
    flat = {
        "student_id": 101,
        "features": {
            "knowledge_level": 0.5,
            "engagement_level": 0.5,
            "struggle_indicator": 0.2,
            "submission_activity": 0.3,
            "review_activity": 0.6,
            "resource_usage": 0.7,
            "assessment_engagement": 0.8,
            "collaborative_activity": 0.1,
            "overall_progress": 0.6,
            "module_completion_rate": 0.7,
            "activity_diversity": 0.4,
            "completion_consistency": 0.5
        },
        "top_k": 3
    }
    
    print("\n🔵 Structured format state vector:")
    r1 = requests.post(API_URL, json=structured)
    if r1.status_code == 200:
        vec1 = r1.json()['state_vector']
        print(vec1)
    
    print("\n🟢 Flat format state vector:")
    r2 = requests.post(API_URL, json=flat)
    if r2.status_code == 200:
        vec2 = r2.json()['state_vector']
        print(vec2)
    
    if r1.status_code == 200 and r2.status_code == 200:
        if vec1 == vec2:
            print("\n✅ VECTORS ARE IDENTICAL - Both formats work correctly!")
        else:
            print("\n⚠️ VECTORS DIFFER - Check implementation!")
            print(f"Difference: {[abs(a - b) for a, b in zip(vec1, vec2)]}")


if __name__ == '__main__':
    try:
        print("\n🚀 Starting API Tests with Structured Format\n")
        
        test_structured_format()
        test_flat_format_backward_compatible()
        test_old_legacy_format()
        compare_results()
        
        print("\n\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Please start the API server first:")
        print("  uvicorn api_service:app --reload --port 8080")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
