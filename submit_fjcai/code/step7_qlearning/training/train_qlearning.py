#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Training - Đơn giản và hiệu quả
=========================================
Train Q-table để gợi ý activities tối ưu cho học sinh
"""

import sys
import numpy as np
import json
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.simulation.student import Student
from core.rl.agent import QLearningAgentV2
from core.rl.action_space import ActionSpace
from core.rl.reward_calculator import RewardCalculatorV2
from core.activity_recommender import ActivityRecommender
from core.simulation.simulator import LearningPathSimulator
from core.lo_mastery_tracker import LOMasteryTracker
from core.simulation.logger import StateTransitionLogger
import random


def _normalize_distribution(mix: Dict[str, float]) -> Optional[Dict[str, float]]:
    """Normalize cluster distribution to sum to 1.0"""
    total = sum(mix.values())
    if total <= 0:
        return None
    return {k: v / total for k, v in mix.items()}


def _generate_students_by_mix(
    n_students: int,
    cluster_mix: Optional[Dict[str, float]] = None
) -> List[Student]:
    """Generate students following cluster ratio distribution"""
    mix = cluster_mix or {'weak': 0.2, 'medium': 0.6, 'strong': 0.2}
    mix = _normalize_distribution(mix) or {'weak': 0.2, 'medium': 0.6, 'strong': 0.2}
    
    students = []
    cumulative = []
    total = 0.0
    for cluster, weight in mix.items():
        total += weight
        cumulative.append((total, cluster))
    
    for student_id in range(1, n_students + 1):
        r = random.random()
        cluster = next(c for threshold, c in cumulative if r <= threshold)
        students.append(Student(student_id, cluster))
    
    return students


def train_qlearning(
    n_episodes: int = 100,
    n_students_per_cluster: int = 5,
    steps_per_episode: int = 30,
    course_id: int = 5,
    verbose: bool = True,
    enable_detailed_logging: bool = False,
    log_interval: int = 10,
    log_output_path: Optional[str] = None,
    total_students: Optional[int] = None,
    cluster_mix: Optional[Dict[str, float]] = None
):
    """
    Train Q-Learning agent với tích hợp detailed logging
    
    Args:
        n_episodes: Number of training episodes
        n_students_per_cluster: Number of students per cluster (used if total_students not provided)
        steps_per_episode: Max steps per student per episode
        course_id: Course ID for multi-course support (default: 5)
        verbose: Print training progress
        enable_detailed_logging: Enable detailed state transition logging
        log_interval: Log every N episodes (only if enable_detailed_logging=True)
        log_output_path: Path to save detailed logs (default: data/simulated/training_logs_episode_{episode}.json)
        total_students: Total number of students (auto-distributes by cluster_mix). Overrides n_students_per_cluster
        cluster_mix: Cluster distribution ratios {'weak': 0.2, 'medium': 0.6, 'strong': 0.2}
    
    Output:
        Model will be saved to: models/qtable_{course_id}.pkl
    """
    # Always use format: models/qtable_{course_id}.pkl
    save_path = f'models/qtable_{course_id}.pkl'
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
    import config
    course_structure_path = str(config.get_course_path(course_id))
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path=course_structure_path,
        course_id=course_id
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
    
    # Create students with cluster_mix support
    if total_students is not None:
        # Use cluster_mix to distribute students
        if cluster_mix is None:
            cluster_mix = {'weak': 0.2, 'medium': 0.6, 'strong': 0.2}
        students = _generate_students_by_mix(total_students, cluster_mix)
        if verbose:
            print(f"\n✓ Initialized:")
            print(f"  - Action space: {n_actions} actions")
            print(f"  - Students: {len(students)} total")
            print(f"  - Cluster mix (weak/medium/strong): {cluster_mix['weak']:.1%}/{cluster_mix['medium']:.1%}/{cluster_mix['strong']:.1%}")
            print(f"  - LO mappings: {len(lo_mappings)} activities → {len(po_lo_data['learning_outcomes'])} LOs")
    else:
        # Use old method: n_students_per_cluster
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
    epsilon_history = []
    q_table_size_history = []
    total_updates_history = []
    
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
                # Map module_idx to lesson_id (for training, use module_idx as lesson_id)
                lesson_id = student.module_idx  # In training, module_idx can be used as lesson_id
                recommendation = recommender.recommend_activity(
                    action=action_tuple,
                    course_id=course_id,
                    lesson_id=lesson_id,
                    past_lesson_ids=None,  # Not tracked in training simulation
                    future_lesson_ids=None,  # Not tracked in training simulation
                    lo_mastery=lo_tracker.get_mastery(student.id) if lo_tracker else student.lo_mastery,
                    previous_activities=getattr(student, 'activity_history', []),
                    cluster_id=student.cluster_id if hasattr(student, 'cluster_id') else 2
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
        
        # Decay epsilon after each episode
        agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)
        
        # Update episode statistics
        agent.stats['episodes_trained'] += 1
        agent.stats['epsilon_history'].append(agent.epsilon)
        agent.stats['q_table_size'] = len(agent.q_table)
        
        # Track statistics for plotting
        avg_reward = episode_reward / len(students)
        episode_rewards.append(avg_reward)
        epsilon_history.append(agent.epsilon)
        q_table_size_history.append(len(agent.q_table))
        
        # Calculate total updates (n_students * steps_per_episode * (episode+1))
        total_updates = (episode + 1) * len(students) * steps_per_episode
        total_updates_history.append(total_updates)
        
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
    
    # Return agent with training history data
    agent.training_history = {
        'episode_rewards': episode_rewards,
        'epsilon_history': epsilon_history,
        'q_table_size_history': q_table_size_history,
        'total_updates_history': total_updates_history
    }
    
    return agent, episode_rewards


def test_trained_agent(
    qtable_path: Optional[str] = None,
    course_id: int = 5,
    n_test_students: int = 3
):
    """
    Test trained Q-Learning agent
    
    Args:
        qtable_path: Path to Q-table file (if None, uses: models/qtable_{course_id}.pkl)
        course_id: Course ID for multi-course support (default: 5)
        n_test_students: Number of test students
    """
    # Auto-generate qtable_path if not provided
    if qtable_path is None:
        qtable_path = f'models/qtable_{course_id}.pkl'
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
        cluster_profiles_path='data/cluster_profiles.json',
        po_lo_path='data/Po_Lo.json',
        midterm_weights_path='data/midterm_lo_weights.json',
        course_id=course_id
    )
    
    # Activity recommender
    import config
    course_structure_path = str(config.get_course_path(course_id))
    recommender = ActivityRecommender(
        po_lo_path='data/Po_Lo.json',
        course_structure_path=course_structure_path,
        course_id=course_id
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
            # Map module_idx to lesson_id (for training, use module_idx as lesson_id)
            lesson_id = student.module_idx  # In training, module_idx can be used as lesson_id
            recommendation = recommender.recommend_activity(
                action=action,
                course_id=course_id,
                lesson_id=lesson_id,
                past_lesson_ids=None,  # Not tracked in training simulation
                future_lesson_ids=None,  # Not tracked in training simulation
                lo_mastery=student.lo_mastery,
                previous_activities=getattr(student, 'activity_history', []),
                cluster_id=student.cluster_id if hasattr(student, 'cluster_id') else 2
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
    parser.add_argument('--students', type=int, default=5, help='Students per cluster (used if --total-students not provided)')
    parser.add_argument('--steps', type=int, default=30, help='Steps per episode')
    parser.add_argument('--course-id', type=int, default=5, help='Course ID for multi-course support (default: 5). Output will be: models/qtable_{course_id}.pkl')
    parser.add_argument('--detailed-logging', action='store_true', help='Enable detailed state transition logging')
    parser.add_argument('--log-interval', type=int, default=10, help='Log every N episodes')
    parser.add_argument('--log-output', type=str, default=None, help='Log output path pattern (use {episode} placeholder)')
    parser.add_argument('--quiet', action='store_true', help='Disable verbose output')
    parser.add_argument('--total-students', type=int, default=None, help='Total number of students (auto-distributes by cluster-mix). Overrides --students')
    parser.add_argument(
        '--cluster-mix',
        type=float,
        nargs=3,
        default=None,
        metavar=('WEAK', 'MEDIUM', 'STRONG'),
        help='Cluster distribution ratio (default: 0.2 0.6 0.2). Only used with --total-students'
    )
    parser.add_argument('--plot', action='store_true', help='Generate convergence plots after training')
    
    args = parser.parse_args()
    
    # Build cluster_mix dict if provided
    cluster_mix = None
    if args.cluster_mix:
        cluster_mix = {
            'weak': args.cluster_mix[0],
            'medium': args.cluster_mix[1],
            'strong': args.cluster_mix[2]
        }
    
    # Train (save_path will be auto-generated as models/qtable_{course_id}.pkl)
    agent, rewards = train_qlearning(
        n_episodes=args.episodes,
        n_students_per_cluster=args.students,
        steps_per_episode=args.steps,
        course_id=args.course_id,
        verbose=not args.quiet,
        enable_detailed_logging=args.detailed_logging,
        log_interval=args.log_interval,
        log_output_path=args.log_output,
        total_students=args.total_students,
        cluster_mix=cluster_mix
    )
    
    # Test (qtable_path will be auto-generated as models/qtable_{course_id}.pkl)
    test_trained_agent(
        course_id=args.course_id,
        n_test_students=2
    )
    
    # Plot convergence analysis
    if args.plot:
        print("\n" + "="*80)
        print("📊 GENERATING CONVERGENCE PLOTS")
        print("="*80)
        
        try:
            from scripts.utils.plot_training_convergence import plot_from_training_stats
            
            # Use actual training history data
            training_history = agent.training_history if hasattr(agent, 'training_history') else {}
            
            epsilon_history = training_history.get('epsilon_history', [])
            q_table_size_history = training_history.get('q_table_size_history', [])
            total_updates_history = training_history.get('total_updates_history', [])
            
            # Generate plots
            plot_from_training_stats(
                episode_rewards=rewards,
                epsilon_history=epsilon_history,
                q_table_size_history=q_table_size_history,
                total_updates_history=total_updates_history,
                course_id=args.course_id,
                output_dir='plots/convergence'
            )
        except ImportError as e:
            print(f"  ⚠️  Could not import plotting module: {e}")
        except Exception as e:
            print(f"  ⚠️  Error generating plots: {e}")
    
    # Visualize (optional - uncomment to enable)
    print("\n" + "=" * 80)
    print("🎨 VISUALIZATION")
    print("=" * 80)
    print("\nTo visualize training results, run:")
    print(f"  python3 scripts/utils/visualize_training.py --course-id {args.course_id}")
    print("\nOr uncomment the following lines to auto-visualize:")
    print("  # from scripts.utils.visualize_training import TrainingVisualizer")
    print(f"  # viz = TrainingVisualizer(course_id={args.course_id})")
    print("  # viz.visualize_student_learning('weak', n_steps=50)")
    print("  # viz.compare_clusters(n_students_per_cluster=5)")
    print("  # viz.visualize_midterm_predictions(n_students_per_cluster=10)")
    print("=" * 80)
