#!/usr/bin/env python3
"""
Verify that webhook service has the fixes applied
"""
import requests
import json
import time

print("=" * 70)
print("🔍 Verifying Webhook Service Fixes")
print("=" * 70)

# Test 1: Check if service is running
print("\n1. Checking if service is running...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Service is running")
    else:
        print(f"   ⚠️  Service responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Service not reachable: {e}")
    print("   → Make sure webhook service is running on port 8000")
    exit(1)

# Test 2: Send test event
print("\n2. Sending test event...")
test_payload = {
    "logs": [{
        "userid": 4,
        "courseid": 5,
        "eventname": "\\mod_quiz\\event\\attempt_submitted",
        "component": "mod_quiz",
        "action": "submitted",
        "target": "attempt",
        "objectid": 999,
        "crud": "c",
        "edulevel": 0,
        "contextinstanceid": 39,
        "timecreated": int(time.time())
    }]
}

try:
    response = requests.post(
        "http://localhost:8000/webhook/moodle-events",
        json=test_payload,
        timeout=10
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Event accepted: {result.get('message')}")
        print(f"   Events received: {result.get('events_received')}")
    else:
        print(f"   ⚠️  Unexpected status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Request failed: {e}")

# Test 3: Check logs for fixes
print("\n3. Checking service logs for fix indicators...")
import subprocess

try:
    # Check for Activity Recommender initialization
    result = subprocess.run(
        ['grep', 'Activity recommender ready', 'webhook_new.log'],
        cwd='/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning',
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ Activity Recommender initialized")
    else:
        print("   ❌ Activity Recommender NOT found in logs")
        print("   ⚠️  This means the OLD code is running!")
        
except Exception as e:
    print(f"   ⚠️  Could not check logs: {e}")

# Test 4: Verify agent.py has similar state matching
print("\n4. Checking agent.py for similar state matching...")
try:
    with open('/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/core/rl/agent.py', 'r') as f:
        content = f.read()
        if '_find_similar_state' in content and 'use_similar_state' in content:
            print("   ✅ Similar state matching code present in agent.py")
        else:
            print("   ❌ Similar state matching NOT found in agent.py")
except Exception as e:
    print(f"   ⚠️  Could not check agent.py: {e}")

# Test 5: Verify webhook_service.py has ActivityRecommender
print("\n5. Checking webhook_service.py for ActivityRecommender...")
try:
    with open('/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/webhook_service.py', 'r') as f:
        content = f.read()
        if 'from core.activity_recommender import ActivityRecommender' in content:
            print("   ✅ ActivityRecommender import present")
        else:
            print("   ❌ ActivityRecommender import NOT found")
            
        if 'activity_recommender = ActivityRecommender(' in content:
            print("   ✅ ActivityRecommender initialization present")
        else:
            print("   ❌ ActivityRecommender initialization NOT found")
except Exception as e:
    print(f"   ⚠️  Could not check webhook_service.py: {e}")

print("\n" + "=" * 70)
print("✅ Verification Complete")
print("=" * 70)
print("\nIf you see errors above, the running service may be using old code.")
print("Solution: Kill the old process and restart the service:")
print("  1. ps aux | grep webhook")
print("  2. kill <PID>")
print("  3. python3 webhook_service.py")
