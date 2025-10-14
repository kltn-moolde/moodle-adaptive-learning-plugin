#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Q-Learning Agent Training
================================
Demo training Q-Learning agent với simulated data
"""

import sys
import numpy as np
from pathlib import Path

# Add parent path
sys.path.append(str(Path(__file__).parent.parent))

from core import MoodleStateBuilder, ActionSpace, QLearningAgentV2


def create_sample_student_data(student_type: str) -> dict:
    """Tạo sample student data theo type"""
    
    if student_type == 'high':
        return {
            'userid': 1,
            'mean_module_grade': 0.9,
            'total_events': 0.8,
            'course_module': 0.8,
            'viewed': 0.9,
            'attempt': 0.2,
            'feedback_viewed': 0.9,
            'submitted': 0.9,
            'reviewed': 0.8,
            'course_module_viewed': 0.9,
            'module_count': 0.8,
            'course_module_completion': 0.9,
            'created': 0.5,
            'updated': 0.5,
            'downloaded': 0.5
        }
    elif student_type == 'medium':
        return {
            'userid': 2,
            'mean_module_grade': 0.7,
            'total_events': 0.5,
            'course_module': 0.5,
            'viewed': 0.6,
            'attempt': 0.5,
            'feedback_viewed': 0.5,
            'submitted': 0.6,
            'reviewed': 0.5,
            'course_module_viewed': 0.6,
            'module_count': 0.5,
            'course_module_completion': 0.6,
            'created': 0.3,
            'updated': 0.3,
            'downloaded': 0.3
        }
    else:  # low
        return {
            'userid': 3,
            'mean_module_grade': 0.4,
            'total_events': 0.3,
            'course_module': 0.3,
            'viewed': 0.3,
            'attempt': 0.9,
            'feedback_viewed': 0.2,
            'submitted': 0.3,
            'reviewed': 0.2,
            'course_module_viewed': 0.3,
            'module_count': 0.3,
            'course_module_completion': 0.3,
            'created': 0.1,
            'updated': 0.1,
            'downloaded': 0.1
        }


def simulate_reward(action_difficulty: str, student_grade: float) -> float:
    """
    Simulate reward function
    
    Good match → high reward
    Poor match → low reward
    """
    if action_difficulty == 'easy':
        difficulty_value = 0.3
    elif action_difficulty == 'medium':
        difficulty_value = 0.6
    else:  # hard
        difficulty_value = 0.9
    
    # Reward cao khi difficulty match với student level
    match_quality = 1.0 - abs(difficulty_value - student_grade)
    
    # Add randomness
    noise = np.random.normal(0, 0.1)
    reward = np.clip(match_quality + noise, 0.0, 1.0)
    
    return reward


def demo_training():
    """Demo training Q-Learning agent"""
    print("\n" + "="*70)
    print("DEMO: Q-LEARNING AGENT TRAINING")
    print("="*70)
    
    # 1. Create agent
    print("\n1. Creating agent...")
    course_json = Path(__file__).parent.parent / 'data' / 'course_structure.json'
    
    agent = QLearningAgentV2.create_from_course(
        str(course_json),
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.2
    )
    
    print(f"   ✓ {agent}")
    print(f"   ✓ State dimension: {agent.state_builder.get_state_dimension()}")
    print(f"   ✓ Action space: {agent.action_space.get_action_space_size()} actions")
    
    # 2. Training episodes
    print("\n2. Training episodes...")
    n_episodes = 10
    max_steps_per_episode = 3
    
    student_types = ['high', 'medium', 'low']
    
    for episode in range(n_episodes):
        # Random student type
        student_type = np.random.choice(student_types)
        student_data = create_sample_student_data(student_type)
        
        # Initial state
        state = agent.state_builder.build_state(student_data)
        knowledge_level = state[0]
        
        # Simulate learning trajectory
        completed_actions = []
        
        for step in range(max_steps_per_episode):
            # Get available actions
            available = agent.action_space.filter_actions(completed_actions)
            
            if not available:
                break
            
            # Choose action
            action = agent.choose_action(state, available, explore=True)
            
            if action is None:
                break
            
            # Simulate outcome & reward
            reward = simulate_reward(action.difficulty or 'medium', knowledge_level)
            
            # Update student (simulate grade improvement)
            student_data['mean_module_grade'] += reward * 0.1
            student_data['mean_module_grade'] = min(student_data['mean_module_grade'], 1.0)
            
            # Next state
            next_state = agent.state_builder.build_state(student_data)
            completed_actions.append(action.action_id)
            next_available = agent.action_space.filter_actions(completed_actions)
            
            # Q-Learning update
            new_q = agent.update(state, action.action_id, reward, next_state, next_available)
            
            # Log
            if episode < 3:  # Print first 3 episodes
                print(f"\n   Episode {episode+1}, Step {step+1}:")
                print(f"   → Student: {student_type} (grade={knowledge_level:.3f})")
                print(f"   → Action: {action.resource_name} ({action.difficulty or 'N/A'})")
                print(f"   ← Reward: {reward:.3f}, Q-value: {new_q:.3f}")
            
            # Update state
            state = next_state
            knowledge_level = state[0]
    
    # 3. Statistics
    print("\n3. Training statistics:")
    stats = agent.get_statistics()
    print(f"   Q-table size: {stats['q_table_size']}")
    print(f"   Training updates: {stats['training_updates']}")
    if 'reward_stats' in stats:
        print(f"   Avg reward: {stats['reward_stats']['mean']:.3f}")
        print(f"   Reward std: {stats['reward_stats']['std']:.3f}")
    
    return agent


def demo_inference(agent):
    """Demo inference - recommendations"""
    print("\n" + "="*70)
    print("DEMO: INFERENCE - RECOMMENDATIONS")
    print("="*70)
    
    # Test với 3 student profiles
    test_students = [
        ('High Achiever', create_sample_student_data('high')),
        ('Average Student', create_sample_student_data('medium')),
        ('Struggling Student', create_sample_student_data('low'))
    ]
    
    for name, student_data in test_students:
        print(f"\n{'='*70}")
        print(f"Student: {name}")
        print(f"{'='*70}")
        
        # Build state
        state = agent.state_builder.build_state(student_data)
        
        print(f"State:")
        print(f"  Knowledge level: {state[0]:.2f}")
        print(f"  Engagement: {state[1]:.2f}")
        print(f"  Struggle: {state[2]:.2f}")
        
        # Get recommendations
        available = agent.action_space.get_all_actions()
        recommendations = agent.recommend(state, available, top_k=3)
        
        print(f"\nTop-3 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec['resource_name']}")
            print(f"     Type: {rec['action_type']}")
            print(f"     Difficulty: {rec.get('difficulty', 'N/A')}")
            print(f"     Q-value: {rec['q_value']:.3f}")


def demo_save_load(agent):
    """Demo save/load agent"""
    print("\n" + "="*70)
    print("DEMO: SAVE & LOAD MODEL")
    print("="*70)
    
    # Save
    save_path = Path(__file__).parent / 'trained_agent.pkl'
    agent.save(str(save_path))
    
    # Load
    print("\nLoading model...")
    course_json = Path(__file__).parent.parent / 'data' / 'course_structure.json'
    new_agent = QLearningAgentV2.create_from_course(str(course_json))
    new_agent.load(str(save_path))
    
    print("\n✅ Model loaded successfully!")
    print(f"   {new_agent}")


def main():
    """Main demo"""
    print("\n" + "="*70)
    print("🎓 Q-LEARNING AGENT DEMO")
    print("   Training & Inference")
    print("="*70)
    
    try:
        # Train
        agent = demo_training()
        
        # Inference
        demo_inference(agent)
        
        # Save/Load
        demo_save_load(agent)
        
        print("\n" + "="*70)
        print("✅ All demos completed successfully!")
        print("="*70)
        
        print("\n💡 Next steps:")
        print("   1. Train với real student data")
        print("   2. Validate recommendations")
        print("   3. Tune hyperparameters")
        print("   4. Deploy to production")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
