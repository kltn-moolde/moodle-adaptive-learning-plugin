#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test - Test pipeline với sample data (không cần Moodle API)
"""

from pathlib import Path
from core.log_processing.state_builder import LogToStateBuilder

# Sample logs (giả lập từ Moodle)
sample_logs = [
    {
        'user_id': 101,
        'cluster_id': 2,  # Medium learner
        'module_id': 54,
        'action': 'view_content',
        'timestamp': 1700000000,
        'progress': 0.3
    },
    {
        'user_id': 101,
        'cluster_id': 2,
        'module_id': 54,
        'action': 'attempt_quiz',
        'timestamp': 1700000300,
        'score': 0.75,
        'progress': 0.5
    },
    {
        'user_id': 101,
        'cluster_id': 2,
        'module_id': 54,
        'action': 'submit_quiz',
        'timestamp': 1700000600,
        'score': 0.80,
        'progress': 0.6
    }
]

print("=" * 70)
print("QUICK TEST: Build 6D States từ Sample Logs")
print("=" * 70)

# Paths
base_path = Path(__file__).parent
cluster_path = base_path / 'data' / 'cluster_profiles.json'
course_path = base_path / 'data' / 'course_structure.json'

if not cluster_path.exists():
    print(f"\n❌ Không tìm thấy: {cluster_path}")
    print("   Cần file này để chạy!")
    exit(1)

if not course_path.exists():
    print(f"\n❌ Không tìm thấy: {course_path}")
    print("   Cần file này để chạy!")
    exit(1)

# Initialize builder
print("\n1. Initialize LogToStateBuilder...")
builder = LogToStateBuilder(
    cluster_profiles_path=str(cluster_path),
    course_structure_path=str(course_path)
)

# Build states
print("\n2. Build states từ sample logs...")
states = builder.build_states_from_logs(sample_logs)

print(f"\n   ✅ Built {len(states)} states")

# Show results
print("\n3. Kết quả:")
for (user_id, module_id), state in states.items():
    print(f"\n   📊 User {user_id}, Module {module_id}:")
    print(f"      State tuple: {state}")
    print(f"      {builder.state_builder.state_to_string(state)}")
    
    # Get explanation
    explanation = builder.get_state_explanation(state, verbose=True)
    print(f"\n      💡 Giải thích:")
    for line in explanation['interpretation'].split('\n'):
        if line.strip():
            print(f"         {line}")

print("\n" + "=" * 70)
print("✅ Test thành công!")
print("\n📝 Ý nghĩa:")
print("   - State này có thể dùng trực tiếp cho Q-Learning")
print("   - Không cần Moodle API")
print("   - Chỉ cần logs dưới dạng dict/JSON")
print("=" * 70)
