#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Enhanced StateBuilderV2 with improved state representation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rl.state_builder import StateBuilderV2
import time

# Initialize
print("=" * 80)
print("ENHANCED STATE BUILDER V2 - TEST")
print("=" * 80)

builder = StateBuilderV2(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json',
    excluded_clusters=[3],  # Exclude teacher cluster
    recent_window=10
)

print("\n" + "=" * 80)
print("STATE SPACE INFORMATION")
print("=" * 80)
info = builder.get_state_info()
for key, value in info.items():
    if key == 'dimension_details':
        print(f"\n{key}:")
        for dim, detail in value.items():
            print(f"  - {dim}: {detail}")
    else:
        print(f"{key}: {value}")

# Test Case 1: Strong student - High engagement, Active learning
print("\n" + "=" * 80)
print("TEST 1: Strong Student - High Engagement, Active Learning")
print("=" * 80)
state1 = builder.build_state(
    cluster_id=4,  # Strong cluster
    current_module_id=builder.modules[2]['id'],  # Bài 3
    module_progress=0.6,
    avg_score=0.85,
    recent_actions=["attempt_quiz", "submit_quiz", "attempt_quiz", "submit_quiz", 
                   "review_quiz", "post_forum"],
    quiz_attempts=3,
    quiz_failures=0,  # No failures
    time_on_module=1800.0,  # 30 min
    median_time=2400.0,  # Median 40 min
    recent_scores=[0.8, 0.85, 0.9],
    consecutive_failures=0,
    time_on_task=1500.0,  # Good time investment
    action_timestamps=[time.time() - i*300 for i in range(6)],  # Spread over 30 min
    repeated_views_same_content=1
)
print(f"State: {state1}")
print(f"String: {builder.state_to_string(state1)}")

# Test Case 2: Struggling student - Low engagement (frustration disabled)
print("\n" + "=" * 80)
print("TEST 2: Struggling Student - Low Engagement (Frustration Disabled)")
print("=" * 80)
state2 = builder.build_state(
    cluster_id=1,  # Weak-medium cluster
    current_module_id=builder.modules[1]['id'],  # Bài 2
    module_progress=0.35,
    avg_score=0.55,
    recent_actions=["view_content", "attempt_quiz", "view_content", "attempt_quiz",
                   "view_content", "attempt_quiz"],
    quiz_attempts=5,
    quiz_failures=3,  # 60% failure rate
    time_on_module=5400.0,  # 90 min (long)
    median_time=2400.0,  # Median 40 min
    recent_scores=[0.5, 0.6, 0.55],
    consecutive_failures=2,
    time_on_task=3600.0,
    action_timestamps=[time.time() - i*600 for i in range(6)],  # Spread over 1 hour
    repeated_views_same_content=3  # Reviewing same content
)
print(f"State: {state2}")
print(f"String: {builder.state_to_string(state2)}")

# Test Case 3: Stuck student - Low engagement (frustration disabled)
print("\n" + "=" * 80)
print("TEST 3: Stuck Student - Low Engagement (Frustration Disabled)")
print("=" * 80)
state3 = builder.build_state(
    cluster_id=0,  # Weakest cluster
    current_module_id=builder.modules[0]['id'],  # Bài 1
    module_progress=0.2,
    avg_score=0.35,
    recent_actions=["view_content", "view_content", "attempt_quiz", "view_content",
                   "attempt_quiz", "view_content", "view_content"],
    quiz_attempts=6,
    quiz_failures=5,  # 83% failure rate
    time_on_module=7200.0,  # 2 hours (very long)
    median_time=2000.0,  # Median 33 min
    recent_scores=[0.3, 0.35, 0.4, 0.3],
    consecutive_failures=3,
    time_on_task=1200.0,  # Low time despite many actions (rushed attempts)
    action_timestamps=[time.time() - i*120 for i in range(7)],  # Crammed in 14 min
    repeated_views_same_content=6  # Stuck, reviewing repeatedly
)
print(f"State: {state3}")
print(f"String: {builder.state_to_string(state3)}")

# Test Case 4: Reflective learner - Post-practice review
print("\n" + "=" * 80)
print("TEST 4: Reflective Learner - Post-Practice Review")
print("=" * 80)
state4 = builder.build_state(
    cluster_id=5,  # Strong cluster
    current_module_id=builder.modules[4]['id'],  # Bài 5
    module_progress=0.85,
    avg_score=0.78,
    recent_actions=["review_quiz", "post_forum", "view_forum", "review_quiz",
                   "view_content", "post_forum"],
    quiz_attempts=2,
    quiz_failures=0,
    time_on_module=2200.0,  # Close to median
    median_time=2400.0,
    recent_scores=[0.75, 0.8],
    consecutive_failures=0,
    time_on_task=2000.0,
    action_timestamps=[time.time() - i*400 for i in range(6)],  # 40 min spread
    repeated_views_same_content=2  # Normal review
)
print(f"State: {state4}")
print(f"String: {builder.state_to_string(state4)}")

# Test Case 5: Pre-learning explorer - Just starting
print("\n" + "=" * 80)
print("TEST 5: Pre-Learning Explorer - Just Starting")
print("=" * 80)
state5 = builder.build_state(
    cluster_id=2,  # Medium cluster
    current_module_id=builder.modules[3]['id'],  # Bài 4
    module_progress=0.15,
    avg_score=0.7,  # Good from previous modules
    recent_actions=["view_content", "download_resource", "view_assignment", 
                   "view_content", "view_content"],
    quiz_attempts=0,  # Not attempted yet
    quiz_failures=0,
    time_on_module=1200.0,  # 20 min
    median_time=2400.0,
    recent_scores=[0.7],
    consecutive_failures=0,
    time_on_task=1100.0,
    action_timestamps=[time.time() - i*240 for i in range(5)],  # 20 min spread
    repeated_views_same_content=0
)
print(f"State: {state5}")
print(f"String: {builder.state_to_string(state5)}")

# Test Case 6: Inconsistent engagement - Low consistency
print("\n" + "=" * 80)
print("TEST 6: Inconsistent Engagement - Cramming Before Deadline")
print("=" * 80)
state6 = builder.build_state(
    cluster_id=2,
    current_module_id=builder.modules[5]['id'],  # Bài 6
    module_progress=0.4,
    avg_score=0.65,
    recent_actions=["view_content", "attempt_quiz", "submit_quiz", "attempt_quiz",
                   "view_content", "submit_quiz", "review_quiz"],
    quiz_attempts=3,
    quiz_failures=1,
    time_on_module=900.0,  # Only 15 min (rushed)
    median_time=2400.0,
    recent_scores=[0.6, 0.65, 0.7],
    consecutive_failures=0,
    time_on_task=800.0,  # Low time for many actions
    action_timestamps=[time.time() - i*10 for i in range(7)],  # All in 70 seconds! (cramming)
    repeated_views_same_content=0
)
print(f"State: {state6}")
print(f"String: {builder.state_to_string(state6)}")

print("\n" + "=" * 80)
print("SUMMARY OF ENHANCEMENTS (OPTIMIZED VERSION)")
print("=" * 80)
print("""
✅ Learning Phase: Now considers recent actions, not just progress
   - Pre-learning: view_content, download_resource, view_assignment
   - Active-learning: attempt_quiz, submit_quiz, submit_assignment
   - Reflective-learning: review_quiz, post_forum, view_forum

✅ Engagement Level: Multi-factor calculation (OPTIMIZED: 3 levels)
   - Weighted action quality (quiz=5, forum=3, view=1)
   - Time on task bonus (adequate time investment)
   - Consistency bonus (actions spread over time, not crammed)
   - Thresholds: [0, 8, 16] → Low (0-7) / Medium (8-15) / High (16+)

⚠️ Frustration Level: TEMPORARILY DISABLED (always 0)
   - Implementation preserved in code comments for future use
   - Disabled to reduce state space from 17,280 to 4,320 states (75% reduction)
   - Can be re-enabled when Q-table converges

✅ Cluster Mapping: Flexible, supports multiple excluded clusters

✅ State Space: 5 × 6 × 4 × 4 × 3 × 3 × 1 = 4,320 states
   - Optimized from 17,280 states (engagement 4→3 levels, frustration disabled)
   - Trade-off: Reduced granularity for better Q-Learning tractability
""")

print("✅ All enhanced tests completed (optimized version)!")
