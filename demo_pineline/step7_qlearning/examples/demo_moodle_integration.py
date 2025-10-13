#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Q-Learning với Moodle State & Action Space
=================================================
Test thiết kế mới: State từ behavioral logs, Action từ course structure
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add parent path
sys.path.append(str(Path(__file__).parent.parent))

from core.moodle_state_builder import MoodleStateBuilder
from core.action_space import ActionSpace, Action


def demo_state_extraction():
    """Demo 1: Trích xuất state từ Moodle logs"""
    print("\n" + "="*70)
    print("DEMO 1: STATE EXTRACTION FROM MOODLE LOGS")
    print("="*70)
    
    # Sample student data (giống features_scaled_report.json)
    sample_student = {
        'userid': 8609,
        'mean_module_grade': 0.75,
        'total_events': 0.6,
        'course_module': 0.5,
        'viewed': 0.7,
        'attempt': 0.8,
        'feedback_viewed': 0.3,
        'submitted': 0.6,
        'reviewed': 0.4,
        'course_module_viewed': 0.5,
        'module_count': 0.5,
        'course_module_completion': 0.6,
        'created': 0.2,
        'updated': 0.1,
        'downloaded': 0.3
    }
    
    # Build state
    state_builder = MoodleStateBuilder()
    state = state_builder.build_state(sample_student)
    
    print(f"\n1. Student: {sample_student['userid']}")
    print(f"   State dimension: {state_builder.get_state_dimension()}")
    print(f"   State vector: {state}")
    
    # Show detailed description
    print("\n2. State breakdown:")
    description = state_builder.get_state_description(state)
    for category, values in description.items():
        print(f"\n   {category.upper()}:")
        for key, val in values.items():
            print(f"     {key}: {val:.3f}")
    
    # Hash state
    state_hash = state_builder.hash_state(state)
    print(f"\n3. State hash (for Q-table key): {state_hash}")
    
    return state_builder, state


def demo_action_space():
    """Demo 2: Xây dựng action space từ course structure"""
    print("\n" + "="*70)
    print("DEMO 2: ACTION SPACE FROM COURSE STRUCTURE")
    print("="*70)
    
    # Sample course structure (subset)
    sample_course = {
        "course_id": "5",
        "contents": [
            {
                "sectionIdOld": 34,
                "name": "Chủ đề 1: MÁY TÍNH VÀ XÃ HỘI TRI THỨC",
                "lessons": [
                    {
                        "sectionIdNew": 38,
                        "name": "Bài 1: Làm quen với Trí tuệ nhân tạo",
                        "resources": [
                            {
                                "id": 62,
                                "name": "SGK_CS_Bai1",
                                "modname": "resource"
                            },
                            {
                                "id": 63,
                                "name": "Video bài giảng bài 1",
                                "modname": "hvp"
                            },
                            {
                                "id": 61,
                                "name": "bài kiểm tra bài 1 - easy",
                                "modname": "quiz"
                            },
                            {
                                "id": 106,
                                "name": "bài kiểm tra bài 1 - medium",
                                "modname": "quiz"
                            },
                            {
                                "id": 107,
                                "name": "bài kiểm tra bài 1 - hard",
                                "modname": "quiz"
                            }
                        ]
                    },
                    {
                        "sectionIdNew": 39,
                        "name": "Bài 2: Trí tuệ nhân tạo trong khoa học và đời sống",
                        "resources": [
                            {
                                "id": 64,
                                "name": "SGK_CS_Bai2",
                                "modname": "resource"
                            },
                            {
                                "id": 65,
                                "name": "Video bài giảng bài 2",
                                "modname": "hvp"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Build action space
    action_space = ActionSpace(sample_course)
    
    print(f"\n1. Total actions: {action_space.get_action_space_size()}")
    
    print("\n2. Action type distribution:")
    distribution = action_space.get_action_type_distribution()
    for action_type, count in sorted(distribution.items()):
        print(f"   {action_type}: {count}")
    
    print("\n3. All actions:")
    for action in action_space.get_all_actions():
        print(f"   {action}")
    
    print("\n4. Filter actions (quizzes only, easy difficulty):")
    easy_quizzes = action_space.get_actions_by_difficulty('easy')
    for quiz in easy_quizzes:
        print(f"   {quiz}")
    
    return action_space


def demo_state_action_interaction():
    """Demo 3: Interaction giữa State và Action"""
    print("\n" + "="*70)
    print("DEMO 3: STATE-ACTION INTERACTION")
    print("="*70)
    
    # Build components
    state_builder = MoodleStateBuilder()
    
    sample_course = {
        "course_id": "5",
        "contents": [
            {
                "sectionIdOld": 34,
                "name": "Chủ đề 1",
                "lessons": [
                    {
                        "sectionIdNew": 38,
                        "name": "Bài 1",
                        "resources": [
                            {"id": 61, "name": "Quiz 1 - easy", "modname": "quiz"},
                            {"id": 106, "name": "Quiz 1 - medium", "modname": "quiz"},
                            {"id": 107, "name": "Quiz 1 - hard", "modname": "quiz"}
                        ]
                    }
                ]
            }
        ]
    }
    
    action_space = ActionSpace(sample_course)
    
    # 3 student profiles
    students = [
        {
            'name': 'High Achiever',
            'data': {
                'userid': 1,
                'mean_module_grade': 0.9,  # High
                'engagement': 0.8,
                'struggle': 0.1,
                'attempt': 0.2,
                'feedback_viewed': 0.9,
                'total_events': 0.8,
                'course_module': 0.8,
                'viewed': 0.8,
                'submitted': 0.9,
                'reviewed': 0.8,
                'course_module_viewed': 0.8,
                'module_count': 0.8,
                'course_module_completion': 0.9,
                'created': 0.5,
                'updated': 0.5,
                'downloaded': 0.5
            }
        },
        {
            'name': 'Average Learner',
            'data': {
                'userid': 2,
                'mean_module_grade': 0.7,
                'engagement': 0.5,
                'struggle': 0.4,
                'attempt': 0.5,
                'feedback_viewed': 0.5,
                'total_events': 0.5,
                'course_module': 0.5,
                'viewed': 0.5,
                'submitted': 0.5,
                'reviewed': 0.5,
                'course_module_viewed': 0.5,
                'module_count': 0.5,
                'course_module_completion': 0.6,
                'created': 0.3,
                'updated': 0.3,
                'downloaded': 0.3
            }
        },
        {
            'name': 'Struggling Student',
            'data': {
                'userid': 3,
                'mean_module_grade': 0.4,  # Low
                'engagement': 0.3,
                'struggle': 0.8,  # High struggle
                'attempt': 0.9,  # Many attempts
                'feedback_viewed': 0.2,  # Low feedback
                'total_events': 0.3,
                'course_module': 0.3,
                'viewed': 0.3,
                'submitted': 0.3,
                'reviewed': 0.2,
                'course_module_viewed': 0.3,
                'module_count': 0.3,
                'course_module_completion': 0.3,
                'created': 0.1,
                'updated': 0.1,
                'downloaded': 0.1
            }
        }
    ]
    
    print("\nRecommendation logic (rule-based for demo):")
    print("="*60)
    
    for student in students:
        state = state_builder.build_state(student['data'])
        knowledge_level = state[0]
        struggle_indicator = state[2]
        
        print(f"\n{student['name']}:")
        print(f"  Knowledge level: {knowledge_level:.2f}")
        print(f"  Struggle indicator: {struggle_indicator:.2f}")
        
        # Simple recommendation logic
        if struggle_indicator > 0.6:
            # Struggling → recommend easy quiz
            recommended_actions = action_space.get_actions_by_difficulty('easy')
            print(f"  → Recommendation: Start with EASY quiz")
        elif knowledge_level > 0.8:
            # High achiever → recommend hard quiz
            recommended_actions = action_space.get_actions_by_difficulty('hard')
            print(f"  → Recommendation: Challenge with HARD quiz")
        else:
            # Average → recommend medium quiz
            recommended_actions = action_space.get_actions_by_difficulty('medium')
            print(f"  → Recommendation: Try MEDIUM quiz")
        
        if recommended_actions:
            print(f"  → Action: {recommended_actions[0]}")


def main():
    """Main demo"""
    print("\n" + "="*70)
    print("🎓 Q-LEARNING ADAPTIVE LEARNING SYSTEM")
    print("   Demo: Moodle State & Action Space")
    print("="*70)
    
    try:
        # Demo 1: State extraction
        state_builder, sample_state = demo_state_extraction()
        
        # Demo 2: Action space
        action_space = demo_action_space()
        
        # Demo 3: Interaction
        demo_state_action_interaction()
        
        print("\n" + "="*70)
        print("✅ All demos completed successfully!")
        print("="*70)
        
        print("\n💡 Next steps:")
        print("   1. Integrate Q-Learning agent")
        print("   2. Train on historical Moodle data")
        print("   3. Validate recommendations")
        print("   4. Deploy for real students")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
