
# if __name__ == '__main__':
#     main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Demo: Q-Learning Recommendation System
=============================================
Demo nhanh để test hệ thống
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.course_structure import CourseStructure, Activity, Module, ActivityType
from models.student_profile import StudentProfile, LearningHistory
from models.outcome import LearningOutcome
from core.qlearning_agent import QLearningAgent


def create_simple_course():
    """Tạo course structure đơn giản"""
    
    # Modules
    modules = [
        Module(
            module_id='mod_1',
            name='Module 1: Basics',
            order=1,
            difficulty=0.3,
            estimated_hours=5
        ),
        Module(
            module_id='mod_2',
            name='Module 2: Intermediate',
            order=2,
            difficulty=0.6,
            estimated_hours=8,
            prerequisites=['mod_1']
        ),
    ]
    
    # Activities
    activities = [
        Activity(
            activity_id='act_1_1',
            name='Intro Video',
            activity_type=ActivityType.VIDEO,
            module_id='mod_1',
            order=1,
            difficulty=0.2,
            estimated_minutes=20,
            prerequisites=[]
        ),
        Activity(
            activity_id='act_1_2',
            name='Basic Quiz',
            activity_type=ActivityType.QUIZ,
            module_id='mod_1',
            order=2,
            difficulty=0.3,
            estimated_minutes=30,
            prerequisites=['act_1_1']
        ),
        Activity(
            activity_id='act_1_3',
            name='Practice Assignment',
            activity_type=ActivityType.ASSIGNMENT,
            module_id='mod_1',
            order=3,
            difficulty=0.4,
            estimated_minutes=60,
            prerequisites=['act_1_2']
        ),
        Activity(
            activity_id='act_2_1',
            name='Advanced Video',
            activity_type=ActivityType.VIDEO,
            module_id='mod_2',
            order=4,
            difficulty=0.5,
            estimated_minutes=30,
            prerequisites=['act_1_3']
        ),
        Activity(
            activity_id='act_2_2',
            name='Advanced Quiz',
            activity_type=ActivityType.QUIZ,
            module_id='mod_2',
            order=5,
            difficulty=0.7,
            estimated_minutes=45,
            prerequisites=['act_2_1']
        ),
    ]
    
    return CourseStructure(
        course_id='demo_course',
        course_name='Demo Course',
        modules=modules,
        activities=activities
    )


def create_sample_student(course: CourseStructure):
    """Tạo sample student profile"""
    
    profile = StudentProfile(
        student_id='student_001',
        course_id=course.course_id,
        cluster_id='cluster_0'
    )
    
    # Add some learning history
    profile.add_activity_history(LearningHistory(
        activity_id='act_1_1',
        completed=True,
        grade=None,  # Video không có grade
        attempts=1,
        time_spent_minutes=18,
        completion_timestamp=1697500000
    ))
    
    profile.add_activity_history(LearningHistory(
        activity_id='act_1_2',
        completed=True,
        grade=0.85,
        attempts=1,
        time_spent_minutes=25,
        completion_timestamp=1697501000
    ))
    
    return profile


def demo_training():
    """Demo training process"""
    print("="*70)
    print("DEMO: Q-LEARNING TRAINING")
    print("="*70)
    
    # 1. Create course
    print("\n1. Creating course structure...")
    course = create_simple_course()
    print(f"   ✓ Course: {course.course_name}")
    print(f"   ✓ Modules: {len(course.modules)}")
    print(f"   ✓ Activities: {len(course.activities)}")
    
    # 2. Create agent
    print("\n2. Creating Q-Learning agent...")
    agent = QLearningAgent(
        course_structure=course,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.1
    )
    print(f"   ✓ Agent created: {agent}")
    print(f"   ✓ State dimension: {agent.state_builder.get_state_dimension()}")
    
    # 3. Simulate training episodes
    print("\n3. Simulating training episodes...")
    
    for episode in range(5):
        # Create student
        student = create_sample_student(course)
        
        # Simulate learning trajectory
        for step in range(3):
            # Choose action
            action = agent.choose_action(student)
            
            if not action:
                break
            
            print(f"\n   Episode {episode+1}, Step {step+1}:")
            print(f"   → Action: {action} ({course.activities[action].name})")
            
            # ✅ FIX: Clip grade to [0, 1]
            base_grade = 0.65 + 0.08 * episode + 0.02 * step
            simulated_grade = np.clip(base_grade + np.random.normal(0, 0.05), 0.0, 1.0)
            
            # Simulate outcome
            outcome = LearningOutcome(
                activity_id=action,
                completed=True,
                grade=simulated_grade,  # ✅ Now always in [0, 1]
                time_spent_minutes=int(20 + np.random.uniform(10, 30)),
                attempts=1,
                passed=simulated_grade >= 0.6
            )
            
            # Update student
            student.add_activity_history(LearningHistory(
                activity_id=action,
                completed=True,
                grade=outcome.grade,
                attempts=1,
                time_spent_minutes=outcome.time_spent_minutes
            ))
            
            # Q-Learning update
            q_value, reward = agent.update(
                student_profile=create_sample_student(course),  # Before
                action_id=action,
                outcome=outcome,
                next_student_profile=student  # After
            )
            
            print(f"   ← Grade: {outcome.grade:.3f}, Reward: {reward:.3f}, Q-value: {q_value:.3f}")
    
    # 4. Statistics
    print("\n4. Training statistics:")
    stats = agent.get_statistics()
    print(f"   Q-table size: {stats['q_table_size']}")
    print(f"   Training updates: {stats['training_updates']}")
    if 'reward_stats' in stats:
        print(f"   Avg reward: {stats['reward_stats']['mean']:.3f}")
        print(f"   Reward std: {stats['reward_stats']['std']:.3f}")
        print(f"   Reward range: [{stats['reward_stats']['min']:.3f}, {stats['reward_stats']['max']:.3f}]")
    
    return agent, course



def demo_inference(agent, course):
    """Demo inference (recommendation)"""
    print("\n" + "="*70)
    print("DEMO: RECOMMENDATION")
    print("="*70)
    
    # Create new student
    print("\n1. New student profile:")
    student = create_sample_student(course)
    print(f"   Student ID: {student.student_id}")
    print(f"   Cluster: {student.cluster_id}")
    print(f"   Completed: {len(student.get_completed_activities())} activities")
    print(f"   Avg grade: {student.get_average_grade():.2f}")
    
    # ✅ FIX: Tính progress rate inline thay vì gọi method
    total_activities = len(course.activities)
    completed_count = len(student.get_completed_activities())
    progress_rate = completed_count / total_activities if total_activities > 0 else 0.0
    print(f"   Progress: {progress_rate:.1%}")
    
    # Get recommendations
    print("\n2. Top-3 Recommendations:")
    recommendations = agent.recommend(student, top_k=3)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. {rec['activity_name']}")
        print(f"      Activity ID: {rec['activity_id']}")
        print(f"      Type: {rec['activity_type']}")
        print(f"      Module: {rec['module_name']}")
        print(f"      Difficulty: {rec['difficulty']:.2f}")
        print(f"      Est. time: {rec['estimated_minutes']} min")
        print(f"      Q-value: {rec['q_value']:.4f} ⭐")
        print(f"      Prerequisites met: {'✅' if rec['prerequisites_met'] else '❌'}")

def demo_compare_students(agent, course):
    """Demo: So sánh recommendations cho các student profiles khác nhau"""
    print("\n" + "="*70)
    print("DEMO: COMPARE STUDENT PROFILES")
    print("="*70)
    
    # Tạo 3 student profiles khác nhau
    students = []
    
    # ✅ FIX: Student 1 - High achiever
    s1 = StudentProfile(
        student_id='student_high',
        course_id=course.course_id,
        cluster_id='cluster_0'
    )
    s1.add_activity_history(LearningHistory(
        activity_id='act_1_1',
        completed=True,
        grade=None,
        attempts=1,
        time_spent_minutes=15
    ))
    s1.add_activity_history(LearningHistory(
        activity_id='act_1_2',
        completed=True,
        grade=0.95,
        attempts=1,
        time_spent_minutes=20
    ))
    students.append(("High Achiever", s1))
    
    # ✅ FIX: Student 2 - Moderate learner
    s2 = StudentProfile(
        student_id='student_moderate',
        course_id=course.course_id,
        cluster_id='cluster_0'
    )
    s2.add_activity_history(LearningHistory(
        activity_id='act_1_1',
        completed=True,
        grade=None,
        attempts=1,
        time_spent_minutes=22
    ))
    s2.add_activity_history(LearningHistory(
        activity_id='act_1_2',
        completed=True,
        grade=0.70,
        attempts=2,
        time_spent_minutes=35
    ))
    students.append(("Moderate Learner", s2))
    
    # ✅ FIX: Student 3 - Struggling
    s3 = StudentProfile(
        student_id='student_struggling',
        course_id=course.course_id,
        cluster_id='cluster_1'
    )
    s3.add_activity_history(LearningHistory(
        activity_id='act_1_1',
        completed=True,
        grade=None,
        attempts=1,
        time_spent_minutes=28
    ))
    s3.add_activity_history(LearningHistory(
        activity_id='act_1_2',
        completed=True,
        grade=0.55,
        attempts=3,
        time_spent_minutes=45
    ))
    students.append(("Struggling Student", s3))
    
    for label, student in students:
        print(f"\n{'='*70}")
        print(f"Student: {label}")
        print(f"{'='*70}")
        print(f"Profile:")
        print(f"  - Avg grade: {student.get_average_grade():.2f}")
        print(f"  - Completed: {len(student.get_completed_activities())} activities")
        print(f"  - Cluster: {student.cluster_id}")
        
        print(f"\nTop-2 Recommendations:")
        recommendations = agent.recommend(student, top_k=2)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['activity_name']} (Q={rec['q_value']:.3f})")

def main():
    """Main demo"""
    print("\n🎓 Q-LEARNING ADAPTIVE LEARNING SYSTEM")
    print("   Demo: Course Recommendation\n")
    
    # Training
    agent, course = demo_training()
    
    # Inference
    demo_inference(agent, course)
    
    # Compare students
    demo_compare_students(agent, course)
    
    # Save model
    print("\n" + "="*70)
    print("SAVING MODEL")
    print("="*70)
    model_path = Path(__file__).parent / 'demo_model.pkl'
    agent.save(str(model_path))
    print(f"✅ Model saved to: {model_path}")
    
    # Save Q-table visualization
    print("\n" + "="*70)
    print("Q-TABLE STATISTICS")
    print("="*70)
    stats = agent.get_statistics()
    print(f"Total Q-values stored: {stats['q_table_size']}")
    print(f"Training updates: {stats['training_updates']}")
    
    if stats['q_table_size'] > 0:
        q_values = list(agent.Q.values())
        print(f"\nQ-value distribution:")
        print(f"  Min:  {min(q_values):.4f}")
        print(f"  Max:  {max(q_values):.4f}")
        print(f"  Mean: {np.mean(q_values):.4f}")
        print(f"  Std:  {np.std(q_values):.4f}")
    
    print("\n✅ Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Load real course structure from JSON")
    print("   2. Train on historical student data (15 students)")
    print("   3. Validate on held-out test set")
    print("   4. Deploy for real recommendations")
    print("\n📚 Files generated:")
    print(f"   - {model_path}")


if __name__ == '__main__':
    main()