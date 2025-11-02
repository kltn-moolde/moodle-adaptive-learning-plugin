#!/usr/bin/env python3
"""
Test API với diverse features (bao gồm submitted và comment)
"""
import requests
import json

API_URL = "http://localhost:8080/api/recommend"

# Test case 1: Student với submitted và comment activities
test_case_1 = {
    "student_id": 12345,
    "features": {
        "mean_module_grade": 0.6,
        "total_events": 0.9,
        "viewed": 0.5,
        "attempt": 0.2,
        "feedback_viewed": 0.8,
        "module_count": 0.3,
        "course_module_completion": 0.8,
        
        # ✅ THÊM DIVERSE FEATURES
        "submitted": 0.4,                    # Submission activity
        "assessable_submitted": 0.3,         # Related submission
        "comment": 0.2,                      # Collaborative activity
        "\\mod_forum\\event\\course_module_viewed": 0.1  # Forum activity
    },
    "top_k": 5
}

# Test case 2: High-performing student với nhiều activities
test_case_2 = {
    "student_id": 67890,
    "features": {
        "mean_module_grade": 0.9,
        "total_events": 1.0,
        "viewed": 0.8,
        "attempt": 0.6,
        "feedback_viewed": 0.9,
        "module_count": 0.8,
        "course_module_completion": 0.9,
        
        "submitted": 0.7,
        "assessable_submitted": 0.6,
        "comment": 0.5,
        "\\mod_forum\\event\\course_module_viewed": 0.4
    },
    "top_k": 5
}

# Test case 3: Low-performing student với ít activities
test_case_3 = {
    "student_id": 11111,
    "features": {
        "mean_module_grade": 0.3,
        "total_events": 0.4,
        "viewed": 0.3,
        "attempt": 0.1,
        "feedback_viewed": 0.2,
        "module_count": 0.2,
        "course_module_completion": 0.3,
        
        "submitted": 0.1,
        "assessable_submitted": 0.05,
        "comment": 0.0,
        "\\mod_forum\\event\\course_module_viewed": 0.0
    },
    "top_k": 5
}

print("="*70)
print("TEST API WITH DIVERSE FEATURES")
print("="*70)
print()

test_cases = [
    ("High Engagement", test_case_1),
    ("Top Performer", test_case_2),
    ("Struggling Student", test_case_3)
]

for name, test_data in test_cases:
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(API_URL, json=test_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ SUCCESS (student_id: {result.get('student_id')})")
            print(f"\n📊 State Vector:")
            state_vec = result.get('state_vector', [])
            dim_names = [
                'knowledge', 'engagement', 'struggle',
                'submission', 'review', 'resource', 'assessment', 'collaborative',
                'progress', 'completion', 'diversity', 'consistency'
            ]
            for i, (name, val) in enumerate(zip(dim_names, state_vec)):
                status = "🎯" if i in [3, 7] else "  "  # Highlight submission & collaborative
                print(f"  [{i:2d}] {name:<15} {val:.3f} {status}")
            
            print(f"\n🎯 Top {len(result.get('recommendations', []))} Recommendations:")
            for i, rec in enumerate(result.get('recommendations', []), 1):
                q_val = rec.get('q_value', 0.0)
                status = "✅" if q_val > 0 else "❌"
                print(f"  {i}. {rec.get('name', 'N/A'):<40} q={q_val:6.2f} {status}")
            
            # Check if any q_values > 0
            q_values = [r.get('q_value', 0.0) for r in result.get('recommendations', [])]
            if any(q > 0 for q in q_values):
                print(f"\n  🎉 SUCCESS: Found states in Q-table!")
                print(f"     Non-zero Q-values: {sum(1 for q in q_values if q > 0)}/{len(q_values)}")
            else:
                print(f"\n  ⚠️  WARNING: All Q-values = 0 (state not in Q-table)")
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API")
        print("   Make sure API is running: python3 api_service.py")
        break
    except Exception as e:
        print(f"❌ ERROR: {e}")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print()
print("✅ Model retrained với diverse data:")
print("   - Q-table: 69,836 states (tăng 97%)")
print("   - submission_activity: 10 unique values")
print("   - collaborative_activity: 9 unique values")
print()
print("💡 Nếu vẫn q_values=0, cần:")
print("   1. Add more diverse training data")
print("   2. Implement nearest neighbor fallback")
print("   3. Giảm state_decimals (1 → 0)")
print()
