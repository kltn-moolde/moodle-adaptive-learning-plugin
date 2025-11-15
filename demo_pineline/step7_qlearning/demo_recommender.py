#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Activity Recommender - Interactive Demo
============================================
Minh họa cách ActivityRecommender hoạt động
"""

from core.activity_recommender import ActivityRecommender
from core.action_space import ActionSpace


def demo_basic():
    """Demo cơ bản về recommendation"""
    print("=" * 80)
    print("DEMO 1: RECOMMENDATION CƠ BẢN")
    print("=" * 80)
    
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path='data/course_structure.json'
    )
    
    print(f"\n✓ Loaded: {len(recommender.activity_info)} activities, {len(recommender.lo_to_activities)} LOs")
    
    # Student profile
    print("\n📚 Hồ sơ học sinh:")
    print("  - Đang học: Module 2 (Bài 4)")
    print("  - LO yếu: LO1.1 (30%), LO1.2 (45%), LO2.1 (35%)")
    
    lo_mastery = {
        'LO1.1': 0.30, 'LO1.2': 0.45, 'LO1.3': 0.60,
        'LO1.4': 0.55, 'LO1.5': 0.50,
        'LO2.1': 0.35, 'LO2.2': 0.40, 'LO2.3': 0.55,
        'LO2.4': 0.50, 'LO3.1': 0.60, 'LO3.2': 0.65,
        'LO3.3': 0.70, 'LO4.1': 0.55, 'LO4.2': 0.60,
        'LO5.1': 0.65
    }
    
    # Test different actions
    test_cases = [
        (('submit_quiz', 'current'), "Làm quiz bài hiện tại"),
        (('view_content', 'past'), "Xem lại tài liệu bài cũ"),
        (('submit_assignment', 'current'), "Nộp bài tập hiện tại"),
        (('view_content', 'future'), "Xem trước bài sau"),
    ]
    
    for action, description in test_cases:
        print(f"\n{'─' * 80}")
        print(f"🎯 Action: {action[0]} ({action[1]}) - {description}")
        print(f"{'─' * 80}")
        
        rec = recommender.recommend_activity(
            action=action,
            module_idx=2,
            lo_mastery=lo_mastery,
            previous_activities=[]
        )
        
        activity_info = recommender.activity_info.get(rec['activity_id'], {})
        
        print(f"\n✓ Gợi ý: {rec['activity_name']}")
        print(f"  📍 Activity ID: {rec['activity_id']}")
        print(f"  📂 Module: {activity_info.get('module_idx', '?')}")
        print(f"  📊 Độ khó: {rec['difficulty']}")
        print(f"  💡 Lý do: {rec['reason']}")
        
        if rec['weak_los']:
            print(f"  🎯 Cải thiện {len(rec['weak_los'])} LOs:")
            for lo_id, mastery in rec['weak_los'][:3]:
                print(f"     - {lo_id}: {mastery:.1%}")
        
        if rec['alternatives']:
            print(f"  🔄 Có {len(rec['alternatives'])} lựa chọn khác")


def demo_time_context():
    """Demo về time context filtering"""
    print("\n\n" + "=" * 80)
    print("DEMO 2: TIME CONTEXT (PAST/CURRENT/FUTURE)")
    print("=" * 80)
    
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path='data/course_structure.json'
    )
    
    # Student ở module 2, có LOs yếu ở nhiều module
    lo_mastery = {
        'LO1.1': 0.25,  # Module 0 - Very weak
        'LO1.2': 0.40,  # Module 0 - Weak
        'LO2.1': 0.30,  # Module 1 - Weak
        'LO2.3': 0.50,  # Module 2 - Current
        'LO3.1': 0.60,  # Module 3 - Future
        'LO3.2': 0.65,
        'LO4.1': 0.70,
        'LO5.1': 0.75,
    }
    
    current_module = 2
    
    print(f"\n📚 Học sinh ở MODULE {current_module}")
    print(f"🎯 LOs yếu:")
    weak_los = [(lo_id, m) for lo_id, m in lo_mastery.items() if m < 0.6]
    weak_los.sort(key=lambda x: x[1])
    for lo_id, mastery in weak_los:
        module_of_lo = int(lo_id[2]) - 1  # LO1.x -> Module 0, LO2.x -> Module 1
        time_label = "past" if module_of_lo < current_module else "current" if module_of_lo == current_module else "future"
        print(f"  - {lo_id}: {mastery:.1%} (Module {module_of_lo} - {time_label})")
    
    # Test time contexts
    print("\n" + "─" * 80)
    print("Test với action: submit_quiz")
    print("─" * 80)
    
    for time_context in ['past', 'current', 'future']:
        print(f"\n🕐 Time context: {time_context.upper()}")
        
        rec = recommender.recommend_activity(
            action=('submit_quiz', time_context),
            module_idx=current_module,
            lo_mastery=lo_mastery,
            previous_activities=[]
        )
        
        activity_info = recommender.activity_info.get(rec['activity_id'], {})
        activity_module = activity_info.get('module_idx', -1)
        
        print(f"  → {rec['activity_name']} (Activity {rec['activity_id']})")
        print(f"  → Module của activity: {activity_module}")
        
        # Verify
        if time_context == 'past':
            status = "✓" if activity_module < current_module else "✗"
            print(f"  → Kiểm tra: {status} (module {activity_module} < {current_module})")
        elif time_context == 'current':
            status = "✓" if activity_module == current_module else "✗"
            print(f"  → Kiểm tra: {status} (module {activity_module} == {current_module})")
        else:  # future
            status = "✓" if activity_module > current_module else "✗"
            print(f"  → Kiểm tra: {status} (module {activity_module} > {current_module})")
        
        print(f"  → Lý do: {rec['reason'][:80]}...")


def demo_difficulty_matching():
    """Demo về difficulty matching với LO mastery"""
    print("\n\n" + "=" * 80)
    print("DEMO 3: DIFFICULTY MATCHING")
    print("=" * 80)
    
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path='data/course_structure.json'
    )
    
    print("\n📊 Test: Cùng LO nhưng mastery khác nhau → Gợi ý độ khó khác nhau")
    
    test_mastery_levels = [
        (0.25, "Rất yếu", "Expect: easy"),
        (0.45, "Yếu", "Expect: medium"),
        (0.65, "Tốt", "Expect: medium/hard"),
    ]
    
    for mastery_level, label, expect in test_mastery_levels:
        print(f"\n{'─' * 80}")
        print(f"🎯 LO1.2 mastery: {mastery_level:.1%} ({label}) - {expect}")
        print(f"{'─' * 80}")
        
        lo_mastery = {f'LO{i//5+1}.{i%5+1}': 0.7 for i in range(15)}
        lo_mastery['LO1.2'] = mastery_level
        
        rec = recommender.recommend_activity(
            action=('submit_quiz', 'current'),
            module_idx=0,  # Module 0 có quiz bài 1
            lo_mastery=lo_mastery,
            previous_activities=[]
        )
        
        print(f"✓ Gợi ý: {rec['activity_name']}")
        print(f"  Độ khó thực tế: {rec['difficulty']}")
        print(f"  Lý do: {rec['reason']}")


def demo_lo_priority():
    """Demo về priority scoring với nhiều LOs yếu"""
    print("\n\n" + "=" * 80)
    print("DEMO 4: LO PRIORITY SCORING")
    print("=" * 80)
    
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path='data/course_structure.json'
    )
    
    print("\n📊 Test: Nhiều LOs yếu → Ưu tiên LO yếu nhất")
    
    lo_mastery = {
        'LO1.1': 0.20,  # Yếu nhất
        'LO1.2': 0.35,  # Yếu thứ 2
        'LO1.3': 0.45,  # Yếu thứ 3
        'LO2.1': 0.50,
        'LO2.2': 0.55,
        'LO2.3': 0.60,
        'LO2.4': 0.65,
    }
    
    print("\n🎯 LOs yếu (< 0.6):")
    weak = [(lo, m) for lo, m in lo_mastery.items() if m < 0.6]
    weak.sort(key=lambda x: x[1])
    for lo_id, mastery in weak:
        print(f"  {lo_id}: {mastery:.1%}")
    
    print(f"\n{'─' * 80}")
    print("Action: view_content (current)")
    print("Module: 0")
    print(f"{'─' * 80}")
    
    rec = recommender.recommend_activity(
        action=('view_content', 'current'),
        module_idx=0,
        lo_mastery=lo_mastery,
        previous_activities=[]
    )
    
    print(f"\n✓ Gợi ý: {rec['activity_name']}")
    print(f"  🎯 Targets: {len(rec['weak_los'])} LOs yếu")
    for lo_id, mastery in rec['weak_los']:
        print(f"     - {lo_id}: {mastery:.1%}")
    print(f"  💡 {rec['reason']}")
    
    if rec['alternatives']:
        print(f"\n  🔄 Alternatives:")
        for alt in rec['alternatives']:
            print(f"     - {alt['activity_name']} → {alt['targets_lo']} ({alt['lo_mastery']:.1%})")


def demo_all_actions():
    """Show all available actions"""
    print("\n\n" + "=" * 80)
    print("DEMO 5: ALL AVAILABLE ACTIONS")
    print("=" * 80)
    
    action_space = ActionSpace()
    
    print(f"\n📋 Total actions: {action_space.get_action_count()}")
    print("\nActions grouped by time context:")
    
    from collections import defaultdict
    grouped = defaultdict(list)
    
    for i in range(action_space.get_action_count()):
        action = action_space.get_action_by_index(i)
        action_tuple = action.to_tuple()
        grouped[action_tuple[1]].append(action_tuple[0])
    
    for time_context in ['past', 'current', 'future']:
        print(f"\n{'─' * 80}")
        print(f"⏰ {time_context.upper()} ({len(grouped[time_context])} actions)")
        print(f"{'─' * 80}")
        for action_type in grouped[time_context]:
            print(f"  • {action_type}")


if __name__ == '__main__':
    # Run all demos
    demo_basic()
    demo_time_context()
    demo_difficulty_matching()
    demo_lo_priority()
    demo_all_actions()
    
    print("\n\n" + "=" * 80)
    print("✓ ALL DEMOS COMPLETED")
    print("=" * 80)
    print("\nĐọc thêm: ACTIVITY_RECOMMENDER_GUIDE.md")
