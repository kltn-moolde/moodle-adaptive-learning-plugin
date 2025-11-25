#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ContextID to Module ID Mapping
====================================
Test how contextinstanceid is mapped to module_id (subsection)
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from core.log_models import LogEvent


def test_contextid_mapping():
    """Test contextid to module_id mapping"""
    print("=" * 70)
    print("Test: ContextID → Module ID Mapping")
    print("=" * 70)
    
    # Load course structure to show examples
    with open("data/course_structure.json", 'r', encoding='utf-8') as f:
        course = json.load(f)
    
    print("\n📚 Course Structure Overview:")
    print(f"   Course ID: {course['course_id']}")
    print(f"   Total sections: {course['total_sections']}")
    
    # Find example contextids
    test_cases = []
    
    for section in course['contents']:
        section_component = section.get('component')
        section_name = section.get('name')
        
        for module in section.get('modules', []):
            contextid = module.get('contextid')
            module_id = module.get('id')
            modname = module.get('modname')
            module_name = module.get('name')
            
            # Case 1: Subsection in regular section
            if modname == 'subsection' and section_component is None:
                test_cases.append({
                    'contextid': contextid,
                    'expected_module_id': module_id,
                    'type': 'subsection_in_regular_section',
                    'section_name': section_name,
                    'module_name': module_name
                })
            
            # Case 2: Module in subsection detail
            if section_component == 'mod_subsection':
                test_cases.append({
                    'contextid': contextid,
                    'expected_module_id': section.get('itemid'),  # Parent subsection ID
                    'type': 'module_in_subsection_detail',
                    'section_name': section_name,
                    'module_name': module_name
                })
            
            # Limit test cases
            if len(test_cases) >= 10:
                break
        
        if len(test_cases) >= 10:
            break
    
    print(f"\n🧪 Testing {len(test_cases)} cases:")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['type']}")
        print(f"  Section: {test_case['section_name']}")
        print(f"  Module: {test_case['module_name']}")
        print(f"  ContextID: {test_case['contextid']}")
        print(f"  Expected Module ID: {test_case['expected_module_id']}")
        
        # Test mapping
        result = LogEvent.getModuleIdFromContextInstanceId(test_case['contextid'])
        
        if result == test_case['expected_module_id']:
            print(f"  ✅ PASS: Got {result}")
            passed += 1
        else:
            print(f"  ❌ FAIL: Got {result}, expected {test_case['expected_module_id']}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Summary: {passed} passed, {failed} failed")
    print("=" * 70)


def test_log_event_with_contextid():
    """Test LogEvent.from_dict() with contextinstanceid"""
    print("\n" + "=" * 70)
    print("Test: LogEvent.from_dict() with contextinstanceid")
    print("=" * 70)
    
    # Sample log with contextinstanceid (typical Moodle log)
    sample_logs = [
        {
            'userid': 5,
            'courseid': 2,
            'eventname': '\\mod_quiz\\event\\attempt_started',
            'contextinstanceid': 316,  # Context of "Video bài giảng bài 6"
            'timecreated': 1763795984,
        },
        {
            'userid': 5,
            'courseid': 2,
            'eventname': '\\mod_resource\\event\\course_module_viewed',
            'contextinstanceid': 317,  # Context of "SGK_CS_Bai6"
            'timecreated': 1763795984,
        },
        {
            'userid': 5,
            'courseid': 2,
            'eventname': '\\core\\event\\course_viewed',
            'contextinstanceid': 2,  # Course context
            'timecreated': 1763795984,
        }
    ]
    
    for i, log in enumerate(sample_logs, 1):
        print(f"\n--- Log {i} ---")
        print(f"Event: {log['eventname']}")
        print(f"ContextInstanceID: {log['contextinstanceid']}")
        
        event = LogEvent.from_dict(log)
        
        if event:
            print(f"✅ Created LogEvent:")
            print(f"   module_id: {event.module_id}")
            print(f"   action_type: {event.action_type}")
        else:
            print(f"⚠️  Event returned None (course-level event)")
    
    print("\n" + "=" * 70)


def show_course_structure_logic():
    """Show course structure and mapping logic"""
    print("\n" + "=" * 70)
    print("Course Structure Mapping Logic")
    print("=" * 70)
    
    with open("data/course_structure.json", 'r', encoding='utf-8') as f:
        course = json.load(f)
    
    print("\n📖 Structure:")
    print("""
    Regular Section (component: null)
    └─ Subsection Module (modname: subsection, id: 53)
        contextid: 285
        → module_id = 53 ✓
    
    Subsection Detail Section (component: mod_subsection, itemid: 12)
    ├─ Video Module (id: 84, contextid: 316)
    │   → module_id = 12 (parent subsection) ✓
    ├─ Resource Module (id: 85, contextid: 317)
    │   → module_id = 12 (parent subsection) ✓
    └─ Quiz Module (id: 86, contextid: 318)
        → module_id = 12 (parent subsection) ✓
    """)
    
    print("\n🔍 Algorithm:")
    print("""
    def getModuleIdFromContextInstanceId(contextinstanceid):
        for section in course.contents:
            for module in section.modules:
                if module.contextid == contextinstanceid:
                    
                    # Case 1: Module in subsection detail
                    if section.component == "mod_subsection":
                        return section.itemid  # Parent subsection ID
                    
                    # Case 2: Subsection itself
                    if module.modname == "subsection":
                        return module.id  # Own ID
                    
                    # Case 3: Regular module
                    return module.id
        
        return None
    """)
    
    # Show actual examples
    print("\n📋 Examples from course_structure.json:")
    
    examples = [
        {
            'desc': 'Subsection "Bài 6" in regular section',
            'section': 'Chủ đề 3',
            'component': None,
            'module': {'id': 83, 'name': 'Bài 6', 'modname': 'subsection', 'contextid': 315},
            'result': '83 (own ID)'
        },
        {
            'desc': 'Video in subsection detail',
            'section': 'Bài 6 (detail)',
            'component': 'mod_subsection',
            'itemid': 12,
            'module': {'id': 84, 'name': 'Video bài giảng', 'contextid': 316},
            'result': '12 (parent subsection ID)'
        }
    ]
    
    for ex in examples:
        print(f"\n  Example: {ex['desc']}")
        print(f"    Section: {ex['section']}")
        print(f"    Component: {ex.get('component', 'null')}")
        if 'itemid' in ex:
            print(f"    ItemID: {ex['itemid']}")
        print(f"    Module: {ex['module']}")
        print(f"    → Result: module_id = {ex['result']}")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CONTEXTID → MODULE_ID MAPPING TEST SUITE")
    print("=" * 70)
    
    try:
        # Test 1: Mapping logic
        test_contextid_mapping()
        
        # Test 2: Integration with LogEvent
        test_log_event_with_contextid()
        
        # Test 3: Show structure
        show_course_structure_logic()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✓ All tests completed")
    print("=" * 70)
    
    print("\n💡 Key Takeaways:")
    print("   1. contextinstanceid identifies a specific module/activity")
    print("   2. For subsection content → use parent subsection ID")
    print("   3. For subsection itself → use its own ID")
    print("   4. This ensures all activities in a subsection map to the same module_id")


if __name__ == '__main__':
    main()
