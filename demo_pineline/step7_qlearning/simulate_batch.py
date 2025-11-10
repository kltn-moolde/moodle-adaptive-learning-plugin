"""
Batch Simulation Script
Generates synthetic student trajectories for Q-Learning training

This script uses StudentSimulatorV2 to generate diverse student behaviors
across all clusters, producing training data for the Q-Learning agent.
"""

import argparse
from datetime import datetime
from core.simulator_v2 import StudentSimulatorV2


def main():
    """Generate batch trajectories"""
    parser = argparse.ArgumentParser(description='Generate synthetic student trajectories')
    parser.add_argument('--n-per-cluster', type=int, default=20,
                       help='Number of students per cluster (default: 20)')
    parser.add_argument('--max-steps', type=int, default=150,
                       help='Maximum steps per student (default: 150)')
    parser.add_argument('--output', type=str, default='data/simulated_trajectories.json',
                       help='Output JSON file path')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress progress output')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Batch Simulation - Generating Training Data")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Students per cluster: {args.n_per_cluster}")
    print(f"  Max steps per student: {args.max_steps}")
    print(f"  Output file: {args.output}")
    print(f"  Random seed: {args.seed}")
    print()
    
    # Initialize simulator
    simulator = StudentSimulatorV2(
        course_structure_path="data/course_structure.json",
        cluster_profiles_path="data/cluster_profiles.json",
        seed=args.seed
    )
    
    # Generate trajectories
    trajectories = simulator.simulate_batch(
        n_students_per_cluster=args.n_per_cluster,
        max_steps_per_student=args.max_steps,
        start_date=datetime(2024, 1, 1),
        verbose=not args.quiet
    )
    
    # Save trajectories
    simulator.save_trajectories(trajectories, args.output)
    
    # Summary
    print("\n" + "=" * 70)
    print("Simulation Summary")
    print("=" * 70)
    
    total_students = len(trajectories)
    total_transitions = sum(len(t) for t in trajectories.values())
    avg_length = total_transitions / total_students if total_students > 0 else 0
    
    # Calculate per-cluster statistics
    cluster_stats = {}
    for student_id, trajectory in trajectories.items():
        if trajectory:
            cluster_id = trajectory[0]['state'][0]  # First element of state is cluster
            if cluster_id not in cluster_stats:
                cluster_stats[cluster_id] = {
                    'count': 0,
                    'total_transitions': 0,
                    'total_reward': 0.0
                }
            cluster_stats[cluster_id]['count'] += 1
            cluster_stats[cluster_id]['total_transitions'] += len(trajectory)
            cluster_stats[cluster_id]['total_reward'] += sum(t['reward'] for t in trajectory)
    
    print(f"\nOverall Statistics:")
    print(f"  Total students: {total_students}")
    print(f"  Total transitions: {total_transitions}")
    print(f"  Average trajectory length: {avg_length:.1f}")
    
    print(f"\nPer-Cluster Statistics:")
    cluster_names = {0: 'Weak', 1: 'Medium', 2: 'Medium', 3: 'Strong', 4: 'Strong'}
    for cluster_id in sorted(cluster_stats.keys()):
        stats = cluster_stats[cluster_id]
        avg_len = stats['total_transitions'] / stats['count']
        avg_reward = stats['total_reward'] / stats['count']
        cluster_name = cluster_names.get(cluster_id, 'Unknown')
        print(f"  Cluster {cluster_id} ({cluster_name}):")
        print(f"    Students: {stats['count']}")
        print(f"    Avg length: {avg_len:.1f}")
        print(f"    Avg total reward: {avg_reward:.2f}")
    
    print("\n" + "=" * 70)
    print(f"✓ Trajectories saved to: {args.output}")
    print("=" * 70)


if __name__ == "__main__":
    main()
