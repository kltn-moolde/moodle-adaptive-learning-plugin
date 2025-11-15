#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Training - Đơn giản và hiệu quả
=========================================
Train Q-table để gợi ý activities tối ưu cho học sinh
"""

import numpy as np
import json
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict

from core.student import Student
from core.qlearning_agent_v2 import QLearningAgentV2
from core.action_space import ActionSpace
from core.reward_calculator_v2 import RewardCalculatorV2
from core.activity_recommender import ActivityRecommender
from core.learning_path_simulator import LearningPathSimulator
from core.lo_mastery_tracker import LOMasteryTracker
from core.state_transition_logger import StateTransitionLogger


def train_qlearning(
    n_episodes: int = 100,
    n_students_per_cluster: int = 5,
    steps_per_episode: int = 30,
    save_path: str = 'models/qtable.pkl',
    verbose: bool = True,
    enable_detailed_logging: bool = False,
    log_interval: int = 10,
    log_output_path: Optional[str] = None
):
    """
    Train Q-Learning agent với tích hợp detailed logging
    
    Args:
        n_episodes: Number of training episodes
        n_students_per_cluster: Number of students per cluster
        steps_per_episode: Max steps per student per episode
        save_path: Path to save trained Q-table
        verbose: Print training progress
        enable_detailed_logging: Enable detailed state transition logging
        log_interval: Log every N episodes (only if enable_detailed_logging=True)
        log_output_path: Path to save detailed logs (default: data/simulated/training_logs_episode_{episode}.json)
    """
    if verbose:
        print("=" * 80)
        print("Q-LEARNING TRAINING")
        print("=" * 80)
    
    # Initialize components
    action_space = ActionSpace()
    n_actions = action_space.get_action_count()
    
    reward_calc = RewardCalculatorV2(
        cluster_profiles_path='data/cluster_profiles.json',
        po_lo_path='data/Po_Lo.json',
        midterm_weights_path='data/midterm_lo_weights.json'
    )
    
    # Activity recommender (intelligent activity selection)
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path='data/course_structure.json'
    )
    
    # Initialize detailed logging components (if enabled)
    lo_tracker = None
    logger = None
    if enable_detailed_logging:
        lo_tracker = LOMasteryTracker(
            midterm_weights_path='data/midterm_lo_weights.json',
            po_lo_path='data/Po_Lo.json'
        )
        logger = StateTransitionLogger(verbose=False)  # Don't print during training
    
    agent = QLearningAgentV2(
        n_actions=n_actions,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01,
        cluster_adaptive=True
    )
    
    # Load LO mappings
    with open('data/Po_Lo.json', 'r', encoding='utf-8') as f:
        po_lo_data = json.load(f)
    
    lo_mappings = defaultdict(list)
    for lo in po_lo_data['learning_outcomes']:
        for activity_id in lo.get('activity_ids', []):
            lo_mappings[activity_id].append(lo['id'])
    
    # Create students
    students = []
    student_id = 1
    for cluster in ['weak', 'medium', 'strong']:
        for _ in range(n_students_per_cluster):
            students.append(Student(student_id, cluster))
            student_id += 1
    
    if verbose:
        print(f"\n✓ Initialized:")
        print(f"  - Action space: {n_actions} actions")
        print(f"  - Students: {len(students)} ({n_students_per_cluster} per cluster)")
        print(f"  - LO mappings: {len(lo_mappings)} activities → {len(po_lo_data['learning_outcomes'])} LOs")
    
    # Training loop
    episode_rewards = []
    
    for episode in range(n_episodes):
        episode_reward = 0.0
        episode_steps = 0
        
        # Reset all students
        for student in students:
            student.reset()
            # Initialize/reset LO tracker for this student (if detailed logging enabled)
            if enable_detailed_logging and lo_tracker:
                lo_tracker.initialize_student(student.id)
        
        # Train on each student
        for student in students:
            student_reward = 0.0
            prev_state = None
            prev_action_type = None
            
            for step in range(steps_per_episode):
                if student.is_finished:
                    break
                
                # Get current state
                state = student.get_state()
                
                # Choose action (using select_action from QLearningAgentV2)
                import random
                best_action_idx = agent.get_best_action(state)
                epsilon_check = random.random()
                action_idx = agent.select_action(state)
                is_exploration = (epsilon_check < agent.epsilon) and \
                    (agent.epsilon > 0) and \
                    (action_idx != best_action_idx)
                
                action = action_space.get_action_by_index(action_idx)
                if action is None:
                    action = action_space.get_action_by_index(0)
                action_tuple = action.to_tuple()
                
                # Get Q-values
                q_value = agent.get_q_value(state, action_idx)
                
                # Get weak LOs for filtering (if detailed logging)
                weak_los = None
                if enable_detailed_logging and lo_tracker:
                    weak_los = lo_tracker.get_weak_los(student.id, threshold=0.6)
                
                # Get activity recommendation (intelligent selection based on weak LOs)
                recommendation = recommender.recommend_activity(
                    action=action_tuple,
                    module_idx=student.module_idx,
                    lo_mastery=lo_tracker.get_mastery(student.id) if lo_tracker else student.lo_mastery,
                    previous_activities=getattr(student, 'activity_history', [])
                )
                activity_id = recommendation['activity_id']
                activity_name = recommendation['activity_name']
                
                # Execute action
                result = student.do_action(action_tuple, activity_id, lo_mappings)
                old_mastery = result['old_mastery']
                outcome = result['outcome']
                
                # Update LO mastery in tracker (if detailed logging)
                lo_deltas = {}
                if enable_detailed_logging and lo_tracker:
                    if activity_id in lo_mappings:
                        for lo_id in lo_mappings[activity_id]:
                            new_mastery = student.lo_mastery.get(lo_id, 0.4)
                            lo_tracker.update_mastery(
                                student_id=student.id,
                                lo_id=lo_id,
                                new_mastery=new_mastery,
                                activity_id=activity_id,
                                timestamp=step
                            )
                            old_val = old_mastery.get(lo_id, 0.4)
                            lo_deltas[lo_id] = new_mastery - old_val
                
                # Calculate reward (with or without breakdown)
                if enable_detailed_logging:
                    reward, reward_breakdown = reward_calc.calculate_reward_with_breakdown(
                        state=state,
                        action={'type': action_tuple[0], 'difficulty': 'medium'},
                        outcome=outcome,
                        previous_state=prev_state,
                        previous_action_type=prev_action_type,
                        student_id=student.id,
                        activity_id=activity_id
                    )
                else:
                    reward = reward_calc.calculate_reward(
                        state=state,
                        action={'type': action_tuple[0], 'difficulty': 'medium'},
                        outcome=outcome,
                        previous_state=prev_state,
                        previous_action_type=prev_action_type,
                        student_id=student.id,
                        activity_id=activity_id
                    )
                    reward_breakdown = {}
                
                # Get next state
                next_state = student.get_state()
                max_next_q = agent.get_max_q_value(next_state)
                
                # Get midterm prediction (if detailed logging)
                midterm_prediction = None
                if enable_detailed_logging and lo_tracker:
                    midterm_prediction = lo_tracker.predict_midterm_score(student.id)
                
                # Log transition (if detailed logging enabled and at log interval)
                if enable_detailed_logging and logger and (episode + 1) % log_interval == 0:
                    logger.log_transition(
                        step=step + 1,
                        student_id=student.id,
                        cluster_id=student.cluster_id,
                        state=state,
                        action_idx=action_idx,
                        action_type=action_tuple[0],
                        activity_id=activity_id,
                        activity_name=activity_name,
                        reward=reward,
                        reward_breakdown=reward_breakdown,
                        next_state=next_state,
                        q_value=q_value,
                        max_q_value=max_next_q,
                        is_exploration=is_exploration,
                        weak_los=weak_los,
                        lo_deltas=lo_deltas,
                        midterm_prediction=midterm_prediction,
                        timestamp=step + 1
                    )
                
                # Update Q-table
                agent.update(
                    state=state,
                    action=action_idx,
                    reward=reward,
                    next_state=next_state,
                    is_terminal=student.is_finished
                )
                
                student_reward += reward
                episode_steps += 1
                
                # Update previous state/action for next iteration
                prev_state = state
                prev_action_type = action_tuple[0]
            
            episode_reward += student_reward
        
        # Decay epsilon (QLearningAgentV2 tự động decay trong update)
        
        # Track statistics
        avg_reward = episode_reward / len(students)
        episode_rewards.append(avg_reward)
        
        # Save detailed logs (if enabled and at log interval)
        if enable_detailed_logging and logger and (episode + 1) % log_interval == 0:
            if log_output_path:
                output_file = log_output_path.format(episode=episode + 1)
            else:
                output_file = f'data/simulated/training_logs_episode_{episode + 1}.json'
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            logger.export_to_json(output_file)
            logger.reset()  # Reset for next interval
            
            if verbose:
                print(f"  ✓ Detailed logs saved to {output_file}")
        
        # Print progress
        if verbose and (episode + 1) % 10 == 0:
            recent_avg = np.mean(episode_rewards[-10:])
            stats = agent.get_statistics()
            print(f"\nEpisode {episode + 1}/{n_episodes}")
            print(f"  Avg reward: {recent_avg:.2f}")
            print(f"  Epsilon: {stats['current_epsilon']:.3f}")
            print(f"  Q-table states: {stats['q_table_size']}")
            print(f"  Total updates: {stats['total_updates']}")
            
            # Print LO mastery summary (if detailed logging)
            if enable_detailed_logging and lo_tracker:
                # Get average LO mastery across all students
                all_masteries = []
                for student in students:
                    mastery = lo_tracker.get_mastery(student.id)
                    all_masteries.extend(mastery.values())
                
                if all_masteries:
                    avg_mastery = np.mean(all_masteries)
                    print(f"  Avg LO mastery: {avg_mastery:.3f}")
    
    # Final statistics
    if verbose:
        print("\n" + "=" * 80)
        print("TRAINING COMPLETED")
        print("=" * 80)
        
        stats = agent.get_statistics()
        print(f"\nAgent Statistics:")
        print(f"  Total updates: {stats['total_updates']}")
        print(f"  Episodes: {stats['episodes_trained']}")
        print(f"  Final epsilon: {stats['current_epsilon']:.3f}")
        print(f"  Q-table size: {stats['q_table_size']} states")
        print(f"  Avg actions per state: {stats['avg_actions_per_state']:.1f}")
        
        print(f"\nReward Statistics:")
        print(f"  Final avg reward: {np.mean(episode_rewards[-10:]):.2f}")
        print(f"  Best avg reward: {max(episode_rewards):.2f}")
        print(f"  Improvement: {episode_rewards[-1] - episode_rewards[0]:.2f}")
    
    # Save Q-table
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    agent.save(save_path)
    
    if verbose:
        print(f"\n✓ Training complete! Q-table saved to {save_path}")
    
    return agent, episode_rewards


def test_trained_agent(
    qtable_path: str = 'models/qtable.pkl',
    n_test_students: int = 3
):
    """
    Test trained Q-Learning agent
    
    Args:
        qtable_path: Path to trained Q-table
        n_test_students: Number of test students per cluster
    """
    print("\n" + "=" * 80)
    print("TESTING TRAINED AGENT")
    print("=" * 80)
    
    # Load components
    action_space = ActionSpace()
    agent = QLearningAgentV2(n_actions=action_space.get_action_count())
    agent.load(qtable_path)
    
    reward_calc = RewardCalculatorV2(
        cluster_profiles_path='data/cluster_profiles.json'
    )
    
    # Activity recommender
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path='data/course_structure.json'
    )
    
    # Load LO mappings
    with open('data/Po_Lo.json', 'r', encoding='utf-8') as f:
        po_lo_data = json.load(f)
    
    lo_mappings = defaultdict(list)
    for lo in po_lo_data['learning_outcomes']:
        for activity_id in lo.get('activity_ids', []):
            lo_mappings[activity_id].append(lo['id'])
    
    # Create test students
    test_students = []
    student_id = 9000
    for cluster in ['weak', 'medium', 'strong']:
        for i in range(n_test_students):
            test_students.append(Student(student_id, cluster))
            student_id += 1
    
    print(f"\n✓ Testing with {len(test_students)} students ({n_test_students} per cluster)")
    
    # Test each student
    for student in test_students:
        print(f"\n{'─' * 60}")
        print(f"Student {student.id} ({student.cluster.upper()})")
        print(f"{'─' * 60}")
        
        total_reward = 0.0
        
        for step in range(20):  # 20 steps per student
            if student.is_finished:
                break
            
            # Get state and best action (greedy, epsilon=0)
            state = student.get_state()
            old_epsilon = agent.epsilon
            agent.epsilon = 0.0  # Greedy for testing
            action_idx = agent.select_action(state)
            agent.epsilon = old_epsilon
            action = action_space.get_action_by_index(action_idx).to_tuple()
            
            # Get activity recommendation with detailed explanation
            recommendation = recommender.recommend_activity(
                action=action,
                module_idx=student.module_idx,
                lo_mastery=student.lo_mastery,
                previous_activities=getattr(student, 'activity_history', [])
            )
            activity_id = recommendation['activity_id']
            activity_name = recommendation['activity_name']
            reason = recommendation['reason']
            
            # Execute
            result = student.do_action(action, activity_id, lo_mappings)
            outcome = result['outcome']
            
            # Calculate reward
            reward = reward_calc.calculate_reward(
                state=state,
                action={'type': action[0], 'difficulty': 'medium'},
                outcome=outcome,
                student_id=student.id,
                activity_id=activity_id
            )
            
            total_reward += reward
            
            # Print detailed step info
            print(f"  Step {step+1}: {action[0]:20s} → {activity_name[:40]}")
            print(f"           💡 {reason}")
            print(f"           📊 Reward={reward:.2f} | Progress={student.progress:.2f} | Score={student.score:.2f}")
        
        # Print weak LO summary
        weak_lo_summary = recommender.get_weak_lo_summary(student.lo_mastery)
        print(f"\n  {weak_lo_summary}")
        
        # Final statistics
        stats = student.get_statistics()
        print(f"\n  Final Statistics:")
        print(f"    Total reward: {total_reward:.2f}")
        print(f"    Module: {stats['module_idx'] + 1}/6")
        print(f"    Progress: {stats['progress']:.2f}")
        print(f"    Score: {stats['score']:.2f}")
        print(f"    Avg LO mastery: {stats['avg_lo_mastery']:.2f}")
        print(f"    Total actions: {stats['total_actions']}")
    
    print("\n" + "=" * 80)
    print("✓ Testing completed!")
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Q-Learning agent với optional detailed logging')
    parser.add_argument('--episodes', type=int, default=100, help='Number of training episodes')
    parser.add_argument('--students', type=int, default=5, help='Students per cluster')
    parser.add_argument('--steps', type=int, default=30, help='Steps per episode')
    parser.add_argument('--output', type=str, default='models/qtable.pkl', help='Output Q-table path')
    parser.add_argument('--detailed-logging', action='store_true', help='Enable detailed state transition logging')
    parser.add_argument('--log-interval', type=int, default=10, help='Log every N episodes')
    parser.add_argument('--log-output', type=str, default=None, help='Log output path pattern (use {episode} placeholder)')
    parser.add_argument('--quiet', action='store_true', help='Disable verbose output')
    
    args = parser.parse_args()
    
    # Train
    agent, rewards = train_qlearning(
        n_episodes=args.episodes,
        n_students_per_cluster=args.students,
        steps_per_episode=args.steps,
        save_path=args.output,
        verbose=not args.quiet,
        enable_detailed_logging=args.detailed_logging,
        log_interval=args.log_interval,
        log_output_path=args.log_output
    )
    
    # Test
    test_trained_agent(
        qtable_path='models/qtable.pkl',
        n_test_students=2
    )
    
    # Visualize (optional - uncomment to enable)
    print("\n" + "=" * 80)
    print("🎨 VISUALIZATION")
    print("=" * 80)
    print("\nTo visualize training results, run:")
    print("  python3 visualize_training.py")
    print("\nOr uncomment the following lines to auto-visualize:")
    print("  # from visualize_training import TrainingVisualizer")
    print("  # viz = TrainingVisualizer(qtable_path='models/qtable.pkl')")
    print("  # viz.visualize_student_learning('weak', n_steps=50)")
    print("  # viz.compare_clusters(n_students_per_cluster=5)")
    print("  # viz.visualize_midterm_predictions(n_students_per_cluster=10)")
    print("=" * 80)
