#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Path Simulator - Script chính
=======================================
Simulate quá trình học với đầy đủ thông tin về state transitions,
action selection, reward calculation, và LO mastery tracking
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.simulation.simulator import LearningPathSimulator


def main():
    parser = argparse.ArgumentParser(
        description='Simulate learning path với đầy đủ logging và tracking'
    )
    parser.add_argument(
        '--qtable',
        type=str,
        default='models/qtable_best.pkl',
        help='Path to trained Q-table (default: models/qtable_best.pkl)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/simulated/learning_path_simulation.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--students',
        type=int,
        default=3,
        help='Number of students per cluster to simulate'
    )
    parser.add_argument(
        '--steps',
        type=int,
        default=30,
        help='Number of learning steps per student'
    )
    parser.add_argument(
        '--clusters',
        nargs='+',
        default=['weak', 'medium', 'strong'],
        help='Clusters to simulate (default: weak medium strong)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed logs'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save logs to JSON'
    )
    parser.add_argument(
        '--sim_params_path',
        type=str,
        default=None,
        help='Path to simulate parameters JSON file (e.g., training/simulate_params/simulate_parameters_course_670.json)'
    )
    parser.add_argument(
        '--use_param_policy',
        action='store_true',
        help='Use action probabilities from simulate params instead of Q-learning policy'
    )
    parser.add_argument(
        '--num_students',
        type=int,
        default=None,
        help='Total number of students to simulate (auto-distributes by cluster_mix ratio). Overrides --students'
    )
    parser.add_argument(
        '--cluster_mix',
        type=float,
        nargs=3,
        default=[0.2, 0.6, 0.2],
        metavar=('WEAK', 'MEDIUM', 'STRONG'),
        help='Cluster distribution ratio for auto-generated students (default: 0.2 0.6 0.2)'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build cluster mix dict
    cluster_mix = {
        'weak': args.cluster_mix[0],
        'medium': args.cluster_mix[1],
        'strong': args.cluster_mix[2]
    }
    
    # Initialize simulator
    print("=" * 80)
    print("LEARNING PATH SIMULATOR")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Q-table: {args.qtable}")
    print(f"  Output: {args.output}")
    if args.num_students:
        print(f"  Total students: {args.num_students}")
        print(f"  Cluster mix (weak/medium/strong): {cluster_mix['weak']:.1%}/{cluster_mix['medium']:.1%}/{cluster_mix['strong']:.1%}")
    else:
        print(f"  Students per cluster: {args.students}")
        print(f"  Clusters: {', '.join(args.clusters)}")
    print(f"  Steps per student: {args.steps}")
    print(f"  Simulate params: {args.sim_params_path if args.sim_params_path else 'None'}")
    print(f"  Use param policy: {args.use_param_policy}")
    print(f"  Verbose: {args.verbose}")
    print()
    
    simulator = LearningPathSimulator(
        qtable_path=args.qtable if Path(args.qtable).exists() else None,
        verbose=args.verbose,
        save_logs=not args.no_save,
        sim_params_path=args.sim_params_path,
        use_param_policy=args.use_param_policy
    )
    
    # Prepare students configuration
    students_config = []
    
    if args.num_students:
        # Auto-generate students using cluster mix
        for i in range(1, args.num_students + 1):
            students_config.append({
                'student_id': 1000 + i,
                'cluster': None,  # Will be assigned by simulator
                'n_steps': args.steps
            })
        # Let simulator generate the config with proper cluster distribution
        print("\n" + "=" * 80)
        print("STARTING SIMULATION")
        print("=" * 80)
        
        results = simulator.simulate_multiple_students(
            students_config=None,
            output_path=args.output if not args.no_save else None,
            n_students=args.num_students,
            cluster_mix=cluster_mix
        )
    else:
        # Manual cluster-based configuration
        student_id = 1000
        
        for cluster in args.clusters:
            for i in range(args.students):
                students_config.append({
                    'student_id': student_id,
                    'cluster': cluster,
                    'n_steps': args.steps
                })
                student_id += 1
        
        # Run simulation
        print("\n" + "=" * 80)
        print("STARTING SIMULATION")
        print("=" * 80)
        
        results = simulator.simulate_multiple_students(
            students_config=students_config,
            output_path=args.output if not args.no_save else None
        )
    
    # Print summary
    print("\n" + "=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    
    metadata = results['simulation_metadata']
    print(f"\nTotal students: {metadata['total_students']}")
    print(f"Average reward: {metadata['avg_reward']:.2f}")
    print(f"Average midterm score: {metadata['avg_midterm_score']:.2f}/20 ({metadata['avg_midterm_score']/2.0:.2f}/10)")
    
    # Per-cluster summary
    print("\nPer-cluster statistics:")
    cluster_stats = {}
    for result in results['students']:
        cluster = result['cluster']
        if cluster not in cluster_stats:
            cluster_stats[cluster] = {
                'count': 0,
                'total_reward': 0.0,
                'total_midterm': 0.0
            }
        
        cluster_stats[cluster]['count'] += 1
        cluster_stats[cluster]['total_reward'] += result['total_reward']
        cluster_stats[cluster]['total_midterm'] += \
            result['lo_summary']['midterm_prediction']['predicted_score']
    
    for cluster, stats in cluster_stats.items():
        count = stats['count']
        avg_reward = stats['total_reward'] / count
        avg_midterm = stats['total_midterm'] / count
        avg_midterm_10 = avg_midterm / 2.0
        print(f"  {cluster.upper():10s}: "
              f"reward={avg_reward:6.2f}, "
              f"midterm={avg_midterm:5.2f}/20 ({avg_midterm_10:4.2f}/10)")
    
    # LO mastery summary
    print("\nLO Mastery Summary:")
    all_weak_los = []
    for result in results['students']:
        weak_los = result['lo_summary']['weak_los']
        all_weak_los.extend([lo['lo_id'] for lo in weak_los])
    
    from collections import Counter
    lo_counts = Counter(all_weak_los)
    print(f"  Most common weak LOs:")
    for lo_id, count in lo_counts.most_common(5):
        pct = count / metadata['total_students'] * 100
        print(f"    {lo_id}: {count} students ({pct:.1f}%)")
    
    if not args.no_save:
        print(f"\n✓ Results saved to {args.output}")
    
    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()

