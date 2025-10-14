#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train Q-Learning Agent với Real Moodle Data
============================================
Training script sử dụng features_scaled_report.json
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Add parent path
sys.path.append(str(Path(__file__).parent.parent))

from core import MoodleStateBuilder, ActionSpace, QLearningAgentV2


def load_student_data(data_path: str) -> List[Dict]:
    """Load student data từ features_scaled_report.json"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} students")
    return data


def extract_student_features(student_data: Dict) -> Dict:
    """
    Extract features cần thiết cho MoodleStateBuilder
    
    Chuyển đổi từ features_scaled_report format sang format mà
    MoodleStateBuilder.build_state() mong đợi
    """
    # Map các features cần thiết
    features = {
        'userid': student_data['userid'],
        'mean_module_grade': student_data.get('mean_module_grade', 0.5),
        'total_events': student_data.get('total_events', 0.5),
        'course_module': student_data.get('course_module', 0.5),
        'viewed': student_data.get('viewed', 0.5),
        'attempt': student_data.get('attempt', 0.5),
        'feedback_viewed': student_data.get('feedback_viewed', 0.5),
        'submitted': student_data.get('submitted', 0.5),
        'reviewed': student_data.get('reviewed', 0.5),
        'course_module_viewed': student_data.get('course_module_viewed', 0.5),
        'module_count': student_data.get('module_count', 0.5),
        'course_module_completion': student_data.get('course_module_completion', 0.5),
        'created': student_data.get('created', 0.5),
        'updated': student_data.get('updated', 0.5),
        'downloaded': student_data.get('downloaded', 0.5),
    }
    
    return features


def simulate_learning_trajectory(
    agent: QLearningAgentV2,
    student_features: Dict,
    max_steps: int = 5,
    explore: bool = True
) -> Tuple[List[Dict], float]:
    """
    Simulate learning trajectory của 1 student
    
    Returns:
        - trajectory: List of (state, action, reward, next_state)
        - total_reward: Tổng reward
    """
    trajectory = []
    total_reward = 0.0
    
    # Initial state
    state = agent.state_builder.build_state(student_features)
    completed_actions = []
    
    for step in range(max_steps):
        # Get available actions (chưa complete)
        available = agent.action_space.filter_actions(completed_actions)
        
        if not available:
            break
        
        # Choose action
        action = agent.choose_action(state, available, explore=explore)
        
        if action is None:
            break
        
        # Simulate reward based on action-state match
        reward = simulate_reward(action, state, student_features)
        
        # Update student state (simulate learning effect)
        student_features['mean_module_grade'] = min(
            student_features['mean_module_grade'] + reward * 0.05,
            1.0
        )
        student_features['course_module_completion'] = min(
            student_features['course_module_completion'] + 0.1,
            1.0
        )
        
        # Next state
        next_state = agent.state_builder.build_state(student_features)
        completed_actions.append(action.action_id)
        
        # Store trajectory
        trajectory.append({
            'state': state.copy(),
            'action': action,
            'reward': reward,
            'next_state': next_state.copy()
        })
        
        total_reward += reward
        state = next_state
    
    return trajectory, total_reward


def simulate_reward(action, state: np.ndarray, student_features: Dict) -> float:
    """
    Simulate reward function
    
    Reward cao khi:
    - Action difficulty phù hợp với student knowledge level
    - Action type phù hợp với student needs
    """
    knowledge_level = state[0]  # mean_module_grade
    engagement = state[1]
    struggle = state[2]
    
    # Base reward từ difficulty matching
    difficulty = action.difficulty or 'medium'
    if difficulty == 'easy':
        difficulty_value = 0.3
    elif difficulty == 'medium':
        difficulty_value = 0.6
    else:  # hard
        difficulty_value = 0.9
    
    # Matching score
    match_quality = 1.0 - abs(difficulty_value - knowledge_level)
    
    # Bonus for engagement
    if action.action_type == 'watch_video' and engagement < 0.5:
        match_quality += 0.1  # Video giúp tăng engagement
    
    if action.action_type == 'take_quiz' and struggle > 0.3:
        match_quality += 0.1  # Quiz giúp identify gaps
    
    # Add noise
    noise = np.random.normal(0, 0.05)
    reward = np.clip(match_quality + noise, 0.0, 1.0)
    
    return reward


def train_agent(
    agent: QLearningAgentV2,
    students_data: List[Dict],
    n_epochs: int = 5,
    max_steps_per_student: int = 5
) -> Dict:
    """
    Train agent với multiple epochs
    
    Returns:
        Training statistics
    """
    print("\n" + "="*70)
    print("TRAINING Q-LEARNING AGENT")
    print("="*70)
    
    stats = {
        'epoch_rewards': [],
        'epoch_q_table_sizes': [],
        'epoch_updates': []
    }
    
    for epoch in range(n_epochs):
        print(f"\n{'='*70}")
        print(f"Epoch {epoch+1}/{n_epochs}")
        print(f"{'='*70}")
        
        epoch_reward = 0.0
        epoch_updates = 0
        
        # Shuffle students
        np.random.shuffle(students_data)
        
        # Train với mỗi student
        for i, student_data in enumerate(students_data):
            # Extract features
            student_features = extract_student_features(student_data)
            
            # Simulate trajectory
            trajectory, total_reward = simulate_learning_trajectory(
                agent, 
                student_features,
                max_steps=max_steps_per_student,
                explore=True
            )
            
            # Update Q-table với trajectory
            for step_data in trajectory:
                state = step_data['state']
                action = step_data['action']
                reward = step_data['reward']
                next_state = step_data['next_state']
                
                # Get next available actions
                completed = [action.action_id]
                next_available = agent.action_space.filter_actions(completed)
                
                # Q-Learning update
                agent.update(state, action.action_id, reward, next_state, next_available)
                epoch_updates += 1
            
            epoch_reward += total_reward
            
            # Progress log
            if (i + 1) % 20 == 0:
                avg_reward = epoch_reward / (i + 1)
                print(f"  Students: {i+1}/{len(students_data)}, "
                      f"Avg reward: {avg_reward:.3f}, "
                      f"Q-table: {len(agent.Q)}")
        
        # Epoch statistics
        avg_epoch_reward = epoch_reward / len(students_data)
        stats['epoch_rewards'].append(avg_epoch_reward)
        stats['epoch_q_table_sizes'].append(len(agent.Q))
        stats['epoch_updates'].append(epoch_updates)
        
        print(f"\n  Epoch {epoch+1} Summary:")
        print(f"    Avg reward: {avg_epoch_reward:.3f}")
        print(f"    Q-table size: {len(agent.Q)}")
        print(f"    Updates: {epoch_updates}")
    
    return stats


def evaluate_agent(agent: QLearningAgentV2, test_students: List[Dict]) -> Dict:
    """
    Evaluate agent trên test set
    
    Returns:
        Evaluation metrics
    """
    print("\n" + "="*70)
    print("EVALUATING AGENT")
    print("="*70)
    
    total_reward = 0.0
    student_types = defaultdict(list)
    
    for student_data in test_students:
        student_features = extract_student_features(student_data)
        
        # Classify student
        knowledge = student_features['mean_module_grade']
        if knowledge >= 0.7:
            student_type = 'high'
        elif knowledge >= 0.4:
            student_type = 'medium'
        else:
            student_type = 'low'
        
        # Evaluate trajectory (no exploration)
        trajectory, reward = simulate_learning_trajectory(
            agent,
            student_features,
            max_steps=5,
            explore=False  # Exploitation only
        )
        
        total_reward += reward
        student_types[student_type].append(reward)
    
    # Statistics
    avg_reward = total_reward / len(test_students)
    
    print(f"\n  Test set size: {len(test_students)}")
    print(f"  Average reward: {avg_reward:.3f}")
    print(f"\n  By student type:")
    for stype, rewards in student_types.items():
        print(f"    {stype.capitalize()}: "
              f"n={len(rewards)}, "
              f"avg={np.mean(rewards):.3f}, "
              f"std={np.std(rewards):.3f}")
    
    return {
        'avg_reward': avg_reward,
        'by_type': {k: {'mean': np.mean(v), 'std': np.std(v)} 
                    for k, v in student_types.items()}
    }


def show_sample_recommendations(agent: QLearningAgentV2, students_data: List[Dict]):
    """Show recommendations cho sample students"""
    print("\n" + "="*70)
    print("SAMPLE RECOMMENDATIONS")
    print("="*70)
    
    # Pick 3 students: high, medium, low
    samples = {
        'high': None,
        'medium': None,
        'low': None
    }
    
    for student_data in students_data:
        features = extract_student_features(student_data)
        knowledge = features['mean_module_grade']
        
        if knowledge >= 0.7 and samples['high'] is None:
            samples['high'] = features
        elif 0.4 <= knowledge < 0.7 and samples['medium'] is None:
            samples['medium'] = features
        elif knowledge < 0.4 and samples['low'] is None:
            samples['low'] = features
        
        if all(v is not None for v in samples.values()):
            break
    
    # Show recommendations
    for stype, features in samples.items():
        if features is None:
            continue
        
        print(f"\n{'='*70}")
        print(f"{stype.upper()} Student (ID: {features['userid']})")
        print(f"{'='*70}")
        
        state = agent.state_builder.build_state(features)
        print(f"State: knowledge={state[0]:.2f}, "
              f"engagement={state[1]:.2f}, "
              f"struggle={state[2]:.2f}")
        
        available = agent.action_space.get_all_actions()
        recommendations = agent.recommend(state, available, top_k=5)
        
        print(f"\nTop-5 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec['resource_name']}")
            print(f"     Type: {rec['action_type']}")
            print(f"     Difficulty: {rec.get('difficulty', 'N/A')}")
            print(f"     Q-value: {rec['q_value']:.4f}")


def main():
    """Main training pipeline"""
    print("\n" + "="*70)
    print("🎓 Q-LEARNING TRAINING WITH REAL MOODLE DATA")
    print("="*70)
    
    # Paths
    data_dir = Path(__file__).parent.parent / 'data'
    student_data_path = data_dir / 'features_scaled_report.json'
    course_json_path = data_dir / 'course_structure.json'
    model_save_path = Path(__file__).parent / 'trained_agent_real_data.pkl'
    
    try:
        # 1. Load data
        print("\n1. Loading data...")
        students_data = load_student_data(str(student_data_path))
        
        # Split train/test (80/20)
        n_train = int(len(students_data) * 0.8)
        train_data = students_data[:n_train]
        test_data = students_data[n_train:]
        
        print(f"   Train: {len(train_data)} students")
        print(f"   Test: {len(test_data)} students")
        
        # 2. Create agent
        print("\n2. Creating Q-Learning agent...")
        agent = QLearningAgentV2.create_from_course(
            str(course_json_path),
            learning_rate=0.1,
            discount_factor=0.9,
            epsilon=0.3  # Higher exploration
        )
        
        print(f"   ✓ {agent}")
        print(f"   ✓ State dimension: {agent.state_builder.get_state_dimension()}")
        print(f"   ✓ Action space: {agent.action_space.get_action_space_size()} actions")
        
        # 3. Pre-initialize Q-table với training states
        print("\n3. Pre-initializing Q-table...")
        train_states = []
        for student_data in train_data:
            features = extract_student_features(student_data)
            state = agent.state_builder.build_state(features)
            train_states.append(state)
        
        agent.initialize_q_table(train_states)
        
        # 4. Train
        train_stats = train_agent(
            agent,
            train_data,
            n_epochs=5,
            max_steps_per_student=5
        )
        
        # 5. Evaluate
        eval_stats = evaluate_agent(agent, test_data)
        
        # 6. Sample recommendations
        show_sample_recommendations(agent, test_data)
        
        # 7. Save model
        print("\n" + "="*70)
        print("SAVING MODEL")
        print("="*70)
        agent.save(str(model_save_path))
        
        # 8. Summary
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETED!")
        print("="*70)
        
        print(f"\n📊 Training Statistics:")
        print(f"   Final Q-table size: {len(agent.Q)}")
        print(f"   Total updates: {sum(train_stats['epoch_updates'])}")
        print(f"   Final avg reward: {train_stats['epoch_rewards'][-1]:.3f}")
        
        print(f"\n📊 Evaluation:")
        print(f"   Test reward: {eval_stats['avg_reward']:.3f}")
        
        print(f"\n💾 Model saved to:")
        print(f"   {model_save_path}")
        
        print("\n💡 Next steps:")
        print("   1. Deploy model to production")
        print("   2. A/B test với rule-based system")
        print("   3. Collect feedback & retrain")
        print("   4. Monitor performance metrics")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
