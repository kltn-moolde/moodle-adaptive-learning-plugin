#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Webhook Service
====================
Test script để kiểm tra webhook service
"""

import requests
import json
from datetime import datetime

# Webhook URL - CẬP NHẬT: port 8080 (cùng API service)
WEBHOOK_URL = "http://localhost:8080/webhook/moodle-events"
RECOMMENDATIONS_URL = "http://localhost:8080/api/recommendations"
HEALTH_URL = "http://localhost:8080/health"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("1. Testing Health Check")
    print("="*70)
    
    try:
        response = requests.get(HEALTH_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_webhook_post():
    """Test webhook POST endpoint"""
    print("\n" + "="*70)
    print("2. Testing Webhook POST")
    print("="*70)
    
    # Sample Moodle event
    sample_event = {
        "logs": [
            {
                "userid": 101,
                "courseid": 2,
                "eventname": "\\mod_quiz\\event\\attempt_submitted",
                "component": "mod_quiz",
                "action": "submitted",
                "target": "attempt",
                "objectid": 46,
                "crud": "c",
                "edulevel": 2,
                "contextinstanceid": 54,
                "timecreated": int(datetime.now().timestamp()),
                "grade": 8.5,
                "success": 1
            }
        ],
        "event_id": "test_event_123",
        "timestamp": int(datetime.now().timestamp())
    }
    
    try:
        print(f"Sending event: {json.dumps(sample_event, indent=2)}")
        response = requests.post(
            WEBHOOK_URL,
            json=sample_event,
            headers={"Content-Type": "application/json"}
        )
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_recommendations():
    """Test GET recommendations endpoint"""
    print("\n" + "="*70)
    print("3. Testing GET Recommendations")
    print("="*70)
    
    user_id = 101
    module_id = 54
    
    try:
        # Wait a bit for background processing
        print("Waiting 3 seconds for background processing...")
        import time
        time.sleep(3)
        
        url = f"{RECOMMENDATIONS_URL}/{user_id}/{module_id}"
        print(f"Requesting: {url}")
        
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_multiple_events():
    """Test webhook with multiple events"""
    print("\n" + "="*70)
    print("4. Testing Multiple Events")
    print("="*70)
    
    # Multiple events
    payload = {
        "logs": [
            {
                "userid": 102,
                "courseid": 2,
                "eventname": "\\mod_quiz\\event\\attempt_started",
                "component": "mod_quiz",
                "action": "started",
                "target": "attempt",
                "objectid": 46,
                "crud": "c",
                "edulevel": 2,
                "contextinstanceid": 54,
                "timecreated": int(datetime.now().timestamp()),
                "grade": None,
                "success": None
            },
            {
                "userid": 102,
                "courseid": 2,
                "eventname": "\\core\\event\\course_module_viewed",
                "component": "core",
                "action": "viewed",
                "target": "course_module",
                "objectid": 55,
                "crud": "r",
                "edulevel": 2,
                "contextinstanceid": 54,
                "timecreated": int(datetime.now().timestamp()),
                "grade": None,
                "success": None
            }
        ],
        "event_id": "test_batch_456"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 WEBHOOK SERVICE TEST SUITE")
    print("="*70)
    print("Make sure API service is running (with webhook):")
    print("  python api_service.py")
    print("  Port: 8080 (same as API service)")
    print("="*70)
    
    results = {}
    
    # Test 1: Health check
    results['health'] = test_health_check()
    
    # Test 2: Webhook POST
    results['webhook_post'] = test_webhook_post()
    
    # Test 3: Get recommendations
    results['get_recommendations'] = test_get_recommendations()
    
    # Test 4: Multiple events
    results['multiple_events'] = test_multiple_events()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n{passed}/{total} tests passed")
    
    print("\n" + "="*70)
    print("💡 NEXT STEPS:")
    print("="*70)
    print("1. Deploy webhook service to production server")
    print("2. Update observer.php URL to production webhook")
    print("3. Upload observer.php to Moodle plugin")
    print("4. Test with real Moodle events")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
