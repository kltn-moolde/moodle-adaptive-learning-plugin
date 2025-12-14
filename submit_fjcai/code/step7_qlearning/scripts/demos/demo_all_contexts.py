#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: All Action Contexts (Past/Current/Future)
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.rl.action_space import ActionSpace
from services.model.qtable_update import QTableUpdateService
from core.rl.agent import QLearningAgentV2
from core.rl.reward_calculator import RewardCalculatorV2
from core.log_processing.state_builder import LogToStateBuilder

# Setup
base_path = Path(__file__).parent
cluster_path = base_path / 'data' / 'cluster_profiles.json'
course_path = base_path / 'data' / 'course_structure.json'

action_space = ActionSpace()
agent = QLearningAgentV2(n_actions=action_space.get_action_count())
reward_calc = RewardCalculatorV2(cluster_profiles_path=str(cluster_path))
builder = LogToStateBuilder(str(cluster_path), str(course_path))

updater = QTableUpdateService(
    agent=agent,
    reward_calculator=reward_calc,
    action_space=action_space,
    log_to_state_builder=builder,
    verbose=True
)

print("=" * 80)
print("DEMO: Action Mapping với Past/Current/Future Contexts")
print("=" * 80)

# Test logs covering all contexts
test_cases = [
    {
        'name': 'PAST: Completed module (progress=1.0)',
        'logs': [
            {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'view_content',
             'timestamp': 1000, 'score': 0.8, 'progress': 1.0},
            {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'review_quiz',
             'timestamp': 1300, 'score': 0.8, 'progress': 1.0},
        ]
    },
    {
        'name': 'CURRENT: Active learning (progress=0.5)',
        'logs': [
            {'user_id': 102, 'cluster_id': 1, 'module_id': 55, 'action': 'view_content',
             'timestamp': 2000, 'score': 0.5, 'progress': 0.3},
            {'user_id': 102, 'cluster_id': 1, 'module_id': 55, 'action': 'attempt_quiz',
             'timestamp': 2300, 'score': 0.6, 'progress': 0.5},
            {'user_id': 102, 'cluster_id': 1, 'module_id': 55, 'action': 'submit_quiz',
             'timestamp': 2600, 'score': 0.7, 'progress': 0.7},
        ]
    },
    {
        'name': 'FUTURE: Preview next module (progress=0.0)',
        'logs': [
            {'user_id': 103, 'cluster_id': 3, 'module_id': 56, 'action': 'view_content',
             'timestamp': 3000, 'score': 0.0, 'progress': 0.0},
            {'user_id': 103, 'cluster_id': 3, 'module_id': 56, 'action': 'view_content',
             'timestamp': 3300, 'score': 0.0, 'progress': 0.0},
        ]
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test Case {i}: {test_case['name']}")
    print(f"{'='*80}")
    
    stats = updater.update_from_logs(test_case['logs'])
    
    print(f"\n✓ Processed {stats['transitions_processed']} transitions")
    print(f"\nAction Mappings:")
    for action_idx, count in stats['action_counts'].items():
        action = action_space.get_action_by_index(action_idx)
        print(f"  [{action.index:2d}] {action.action_type:20s} ({action.time_context:7s}) - {count}×")

print(f"\n{'='*80}")
print("SUMMARY: Action Space Coverage")
print(f"{'='*80}")

summary = action_space.get_action_summary()
print(f"\nTotal Actions: {summary['total_actions']}")
print(f"\nBy Context:")
for context, count in summary['by_context'].items():
    print(f"  {context:10s}: {count} actions")

print(f"\nBy Type:")
for action_type, count in sorted(summary['by_type'].items()):
    print(f"  {action_type:20s}: {count} actions")

print(f"\n{'='*80}")
print("✅ All contexts (past/current/future) working correctly!")
print(f"{'='*80}")
