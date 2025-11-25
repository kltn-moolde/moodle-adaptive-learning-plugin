#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test StateUpdateManager - Demo cách sử dụng với logs
======================================================
"""

from core.log_processing.state_manager import StateUpdateManager
from core.rl.state_builder import StateBuilderV2
from core.rl.action_space import ActionSpace
from core.rl.reward_calculator import RewardCalculatorV2
from services.model.loader import ModelLoader
from pathlib import Path

def test_state_update_manager():
    """Test StateUpdateManager với sample logs"""
    print("=" * 80)
    print("Testing StateUpdateManager")
    print("=" * 80)
    
    # Initialize components
    base_path = Path(__file__).parent
    
    # Load model components
    model_loader = ModelLoader(
        model_path=base_path / 'models' / 'qtable.pkl',
        course_path=base_path / 'data' / 'course_structure.json',
        cluster_profiles_path=base_path / 'data' / 'cluster_profiles.json'
    )
    model_loader.load_all(verbose=False)
    
    # Initialize reward calculator
    reward_calc = RewardCalculatorV2(
        cluster_profiles_path=str(base_path / 'data' / 'cluster_profiles.json'),
        po_lo_path=str(base_path / 'data' / 'Po_Lo.json'),
        midterm_weights_path=str(base_path / 'data' / 'midterm_lo_weights.json')
    )
    
    # Initialize StateUpdateManager
    manager = StateUpdateManager(
        state_builder=model_loader.state_builder,
        action_space=model_loader.action_space,
        reward_calculator=reward_calc,
        min_logs_for_update=2,  # Test với 2 logs minimum
        max_buffer_size=20,
        time_window_seconds=60,  # 1 phút
        enable_qtable_updates=True,
        agent=model_loader.agent
    )
    
    # Sample logs (simulating real Moodle logs)
    print("\n" + "=" * 80)
    print("Test Case 1: Add logs sequentially")
    print("=" * 80)
    
    sample_logs = [
        {
            'userid': 101,
            'courseid': 5,
            'contextinstanceid': 78,
            'eventname': '\\mod_page\\event\\course_module_viewed',
            'timecreated': 1700000000,
            'component': 'mod_page',
            'action': 'viewed'
        },
        {
            'userid': 101,
            'courseid': 5,
            'contextinstanceid': 78,
            'eventname': '\\mod_quiz\\event\\attempt_started',
            'timecreated': 1700000100,
            'component': 'mod_quiz',
            'action': 'started'
        },
        {
            'userid': 101,
            'courseid': 5,
            'contextinstanceid': 78,
            'eventname': '\\mod_quiz\\event\\attempt_submitted',
            'timecreated': 1700000300,
            'grade': 85,
            'component': 'mod_quiz',
            'action': 'submitted'
        }
    ]
    
    # Add logs one by one
    for i, log in enumerate(sample_logs, 1):
        print(f"\n📥 Adding log {i}/{len(sample_logs)}:")
        print(f"   Event: {log.get('eventname', 'N/A')}")
        print(f"   Time: {log.get('timecreated', 'N/A')}")
        
        result = manager.add_log(log)
        
        if result:
            print(f"\n✅ State updated! Generated recommendation:")
            print(f"   User: {result['user_id']}")
            print(f"   Lesson: {result['lesson_id']}")
            print(f"   State: {result['state']}")
            print(f"   Time context: {result.get('time_context', 'N/A')}")
            print(f"   Q-table updated: {result.get('qtable_updated', False)}")
            
            if result.get('qtable_update_info'):
                qinfo = result['qtable_update_info']
                print(f"   Q-update: action={qinfo.get('action_type')}, reward={qinfo.get('reward', 0):.2f}")
        else:
            print(f"   ⏳ Log buffered (waiting for more logs or conditions)")
    
    # Get statistics
    print("\n" + "=" * 80)
    print("Manager Statistics:")
    print("=" * 80)
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test Case 2: Multiple users
    print("\n" + "=" * 80)
    print("Test Case 2: Multiple users, different lessons")
    print("=" * 80)
    
    multi_user_logs = [
        {
            'userid': 102,
            'courseid': 5,
            'contextinstanceid': 61,  # Different lesson
            'eventname': '\\mod_page\\event\\course_module_viewed',
            'timecreated': 1700001000,
            'component': 'mod_page',
            'action': 'viewed'
        },
        {
            'userid': 103,
            'courseid': 5,
            'contextinstanceid': 66,  # Another lesson
            'eventname': '\\mod_quiz\\event\\attempt_started',
            'timecreated': 1700001100,
            'component': 'mod_quiz',
            'action': 'started'
        }
    ]
    
    for log in multi_user_logs:
        result = manager.add_log(log)
        if result:
            print(f"✅ State updated for user {result['user_id']}, lesson {result['lesson_id']}")
    
    # Final statistics
    print("\n" + "=" * 80)
    print("Final Statistics:")
    print("=" * 80)
    final_stats = manager.get_statistics()
    for key, value in final_stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✓ StateUpdateManager test completed!")
    print("=" * 80)


if __name__ == '__main__':
    test_state_update_manager()

