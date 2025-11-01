#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulate Learning Data
=======================
Generate simulated learning data for Q-learning training
"""

import os
import argparse
from datetime import datetime

from core.state_builder import MoodleStateBuilder
from core.action_space import ActionSpace
from core.reward_calculator import RewardCalculator
from core.simulator import LearningSimulator


def simulate_learning_data(
    n_students: int = 100,
    n_actions_per_student: int = 30,
    output_dir: str = 'data/simulated'
):
    """
    Main function to generate simulated learning data
    
    Args:
        n_students: Number of students to simulate
        n_actions_per_student: Number of actions per student
        output_dir: Output directory for simulated data
    """
    print("=" * 70)
    print("SIMULATE LEARNING DATA")
    print("=" * 70)
    
    # Setup paths
    data_dir = 'data'
    course_structure_path = os.path.join(data_dir, 'course_structure.json')
    cluster_profiles_path = os.path.join(data_dir, 'cluster_profiles.json')
    
    # Initialize components
    print("\n[1/4] Initializing components...")
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(course_structure_path)
    reward_calculator = RewardCalculator(cluster_profiles_path)
    simulator = LearningSimulator(state_builder, action_space, reward_calculator)
    
    print(f"  ✓ Action space: {action_space.get_action_count()} actions")
    print(f"  ✓ Clusters: {reward_calculator.get_cluster_count()}")
    
    # Simulate data
    print(f"\n[2/4] Simulating {n_students} students...")
    interactions = simulator.simulate_batch(
        n_students=n_students,
        n_actions_per_student=n_actions_per_student
    )
    
    print(f"  ✓ Generated {len(interactions)} interactions")
    
    # Get statistics
    print("\n[3/4] Calculating statistics...")
    stats = simulator.get_simulation_stats(interactions)
    
    print(f"\nSimulation Statistics:")
    print(f"  Total interactions: {stats['total_interactions']}")
    print(f"  Unique students: {stats['unique_students']}")
    print(f"  Avg score: {stats['avg_score']:.2f}")
    print(f"  Completion rate: {stats['completion_rate']:.2%}")
    print(f"  Avg attempts: {stats['avg_attempts']:.2f}")
    print(f"  Avg time spent: {stats['avg_time_spent']:.1f} min")
    print(f"  Avg reward: {stats['avg_reward']:.2f}")
    
    print(f"\n  Cluster distribution:")
    for cid, count in stats['cluster_distribution'].items():
        pct = count / stats['total_interactions'] * 100
        print(f"    Cluster {cid}: {count:4d} ({pct:5.1f}%)")
    
    # Save data
    print(f"\n[4/4] Saving data...")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(
        output_dir,
        f'simulated_data_{timestamp}.json'
    )
    
    simulator.save_simulated_data(interactions, output_file)
    print(f"  ✓ Saved to: {output_file}")
    
    # Save latest
    latest_file = os.path.join(output_dir, 'latest_simulation.json')
    simulator.save_simulated_data(interactions, latest_file)
    print(f"  ✓ Saved latest: {latest_file}")
    
    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETE")
    print("=" * 70)
    
    return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate simulated learning data'
    )
    parser.add_argument(
        '--n-students',
        type=int,
        default=100,
        help='Number of students to simulate (default: 100)'
    )
    parser.add_argument(
        '--n-actions',
        type=int,
        default=30,
        help='Number of actions per student (default: 30)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/simulated',
        help='Output directory (default: data/simulated)'
    )
    
    args = parser.parse_args()
    
    simulate_learning_data(
        n_students=args.n_students,
        n_actions_per_student=args.n_actions,
        output_dir=args.output_dir
    )
