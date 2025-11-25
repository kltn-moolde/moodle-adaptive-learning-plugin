#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Log Enrichment - Demonstrate course-level event enrichment
================================================================
Test how course_viewed event is expanded into module-specific events
"""

import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.log_processing.state_builder import LogToStateBuilder
from services.clients.moodle_client import MoodleAPIClient


def test_course_level_event_enrichment():
    """
    Test enrichment of course_viewed event
    
    Flow:
    1. Receive course_viewed event (no module_id)
    2. Detect it's course-level event
    3. Call Moodle API to get progress/scores for all modules
    4. Expand into N module-specific events
    5. Process each event to build states
    """
    print("=" * 70)
    print("Test: Course-Level Event Enrichment")
    print("=" * 70)
    
    # Sample course_viewed event from Moodle
    course_viewed_event = {
        'userid': 5,
        'courseid': 5,
        'eventname': '\\core\\event\\course_viewed',
        'component': 'core',
        'action': 'viewed',
        'target': 'course',
        'objectid': None,
        'crud': 'r',
        'edulevel': 2,
        'contextinstanceid': 5,  # This is course_id, not module_id
        'timecreated': 1763795984,
        'grade': None,
        'success': None
    }
    
    print("\n1. Input: Course-level event")
    print("-" * 70)
    print(json.dumps(course_viewed_event, indent=2))
    
    # Initialize Moodle API client
    print("\n2. Initializing Moodle API client...")
    moodle_client = MoodleAPIClient(
        moodle_url="http://localhost:8100",
        ws_token="2eacf99c3a8d4915f27c5dec58f62ef7",
        course_id=5
    )
    
    # Initialize LogToStateBuilder with moodle_client
    print("\n3. Initializing LogToStateBuilder with enrichment...")
    preprocessor = LogToStateBuilder(
        course_structure_path="data/course_structure.json",
        recent_window=10,
        excluded_clusters=[3],
        moodle_client=moodle_client
    )
    
    print(f"\n   Available modules: {len(preprocessor.modules)}")
    for i, module in enumerate(preprocessor.modules[:3], 1):
        print(f"   {i}. Module {module['id']}: {module['name']}")
    if len(preprocessor.modules) > 3:
        print(f"   ... and {len(preprocessor.modules) - 3} more modules")
    
    # Parse logs (this will trigger enrichment)
    print("\n4. Processing event (will trigger enrichment)...")
    print("-" * 70)
    events = preprocessor.parse_raw_logs([course_viewed_event])
    
    print(f"\n5. Result: {len(events)} enriched events")
    print("-" * 70)
    
    if events:
        print(f"\n   Sample enriched events:")
        for i, event in enumerate(events[:3], 1):
            print(f"\n   Event {i}:")
            print(f"   - User ID: {event.user_id}")
            print(f"   - Module ID: {event.module_id}")
            print(f"   - Action: {event.action_type}")
            print(f"   - Progress: {event.progress}")
            print(f"   - Score: {event.score}")
            print(f"   - Time spent: {event.time_spent}s")
        
        if len(events) > 3:
            print(f"\n   ... and {len(events) - 3} more events")
    else:
        print("   ⚠️  No events generated (API might be unavailable)")
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Input: 1 course-level event")
    print(f"✓ Output: {len(events)} module-specific events")
    print(f"✓ Enrichment: {'SUCCESS' if events else 'FAILED (check Moodle API)'}")
    
    # Show statistics
    print(f"\nStatistics:")
    print(f"  - Total events processed: {preprocessor.stats['total_events_processed']}")
    print(f"  - Enriched events: {preprocessor.stats['enriched_events']}")
    print(f"  - Events by user: {dict(preprocessor.stats['events_by_user'])}")
    print(f"  - Events by module: {len(preprocessor.stats['events_by_module'])} modules")
    
    print("\n" + "=" * 70)


def test_module_specific_event():
    """
    Test normal module-specific event (should pass through without enrichment)
    """
    print("\n" + "=" * 70)
    print("Test: Module-Specific Event (No Enrichment)")
    print("=" * 70)
    
    # Sample module-specific event
    module_event = {
        'userid': 5,
        'courseid': 5,
        'eventname': '\\mod_quiz\\event\\attempt_started',
        'component': 'mod_quiz',
        'action': 'started',
        'target': 'attempt',
        'objectid': 123,
        'cmid': 54,  # Specific module ID
        'contextinstanceid': 54,
        'timecreated': 1763795984,
        'grade': None,
        'success': None
    }
    
    print("\n1. Input: Module-specific event")
    print("-" * 70)
    print(json.dumps(module_event, indent=2))
    
    # Initialize LogToStateBuilder without moodle_client
    print("\n2. Initializing LogToStateBuilder without API...")
    preprocessor = LogToStateBuilder(
        course_structure_path="data/course_structure.json",
        recent_window=10,
        excluded_clusters=[3],
        moodle_client=None  # No enrichment
    )
    
    # Parse logs
    print("\n3. Processing event (should pass through)...")
    events = preprocessor.parse_raw_logs([module_event])
    
    print(f"\n4. Result: {len(events)} event(s)")
    print("-" * 70)
    
    if events:
        event = events[0]
        print(f"   ✓ User ID: {event.user_id}")
        print(f"   ✓ Module ID: {event.module_id}")
        print(f"   ✓ Action: {event.action_type}")
        print(f"   ✓ No enrichment needed")
    
    print("\n" + "=" * 70)


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LOG ENRICHMENT TEST SUITE")
    print("=" * 70)
    
    # Test 1: Course-level event with enrichment
    try:
        test_course_level_event_enrichment()
    except Exception as e:
        print(f"\n❌ Test 1 failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Module-specific event without enrichment
    try:
        test_module_specific_event()
    except Exception as e:
        print(f"\n❌ Test 2 failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✓ All tests completed")
    print("=" * 70)
    
    print("\n📋 Key Insights:")
    print("   1. course_viewed events have NO module_id")
    print("   2. These are detected and enriched via Moodle API")
    print("   3. Each course_viewed → N module-specific events")
    print("   4. Each enriched event contains: progress, score, time_spent")
    print("   5. Module-specific events pass through without enrichment")
    
    print("\n💡 Solution Summary:")
    print("   - LogEvent.from_dict() detects course-level events → returns None")
    print("   - LogToStateBuilder.enrich_course_level_log() calls Moodle API")
    print("   - API returns progress/scores for ALL modules")
    print("   - Generates N synthetic events (one per module)")
    print("   - StateBuilder can now build states for all modules")


if __name__ == '__main__':
    main()
