#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Action Mapping với Verbose Mode
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.qlearning_agent_v2 import QLearningAgentV2
from core.reward_calculator_v2 import RewardCalculatorV2
from core.action_space import ActionSpace
from core.log_to_state_builder import LogToStateBuilder
from services.qtable_update_service import QTableUpdateService

# Paths
base_path = Path(__file__).parent
cluster_path = base_path / 'data' / 'cluster_profiles.json'
course_path = base_path / 'data' / 'course_structure.json'

# Sample logs with different contexts
test_logs = [
    # User 101: Module 54 - Current (progress 0.3)
    {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'view_content',
     'timestamp': 1700000000, 'score': 0.0, 'progress': 0.1},
    {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'attempt_quiz',
     'timestamp': 1700000300, 'score': 0.6, 'progress': 0.3},
    {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'submit_quiz',
     'timestamp': 1700000600, 'score': 0.75, 'progress': 0.5},
    
    # User 101: Module 54 - Past (progress 1.0)
    {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'review_quiz',
     'timestamp': 1700001000, 'score': 0.75, 'progress': 1.0},
    
    # User 101: Module 55 - Future (progress 0.0)
    {'user_id': 101, 'cluster_id': 2, 'module_id': 55, 'action': 'view_content',
     'timestamp': 1700001500, 'score': 0.0, 'progress': 0.0},
]

print("=" * 80)
print("TEST: Action Mapping với Time Context")
print("=" * 80)

# Initialize
action_space = ActionSpace()
agent = QLearningAgentV2(n_actions=action_space.get_action_count())
reward_calc = RewardCalculatorV2(cluster_profiles_path=str(cluster_path))
builder = LogToStateBuilder(
    cluster_profiles_path=str(cluster_path),
    course_structure_path=str(course_path)
)

# Create updater with VERBOSE=True
updater = QTableUpdateService(
    agent=agent,
    reward_calculator=reward_calc,
    action_space=action_space,
    log_to_state_builder=builder,
    verbose=True  # ← Enable detailed logging
)

print("\n" + "=" * 80)
print("Processing logs with verbose output:")
print("=" * 80)

stats = updater.update_from_logs(test_logs)

print("\n" + "=" * 80)
print("RESULTS:")
print("=" * 80)
print(f"Transitions: {stats['transitions_processed']}")
print(f"Q-updates: {stats['q_updates']}")

print("\nAction Distribution:")
for action_idx, count in stats['action_counts'].items():
    action = action_space.get_action_by_index(action_idx)
    print(f"  [{action.index:2d}] {action.action_type:20s} ({action.time_context:7s}): {count}×")

print("\n" + "=" * 80)
print("Expected Mappings:")
print("=" * 80)
print("  view_content @ progress=0.1  → view_content (current)")
print("  attempt_quiz @ progress=0.3  → attempt_quiz (current)")
print("  submit_quiz  @ progress=0.5  → submit_quiz (current)")
print("  review_quiz  @ progress=1.0  → review_quiz (past)")
print("  view_content @ progress=0.0  → view_content (future)")
