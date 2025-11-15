#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Path Simulator - Script chính
=======================================
Simulate quá trình học với đầy đủ thông tin về state transitions,
action selection, reward calculation, và LO mastery tracking
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from core.learning_path_simulator import LearningPathSimulator


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
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize simulator
    print("=" * 80)
    print("LEARNING PATH SIMULATOR")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Q-table: {args.qtable}")
    print(f"  Output: {args.output}")
    print(f"  Students per cluster: {args.students}")
    print(f"  Steps per student: {args.steps}")
    print(f"  Clusters: {', '.join(args.clusters)}")
    print(f"  Verbose: {args.verbose}")
    print()
    
    simulator = LearningPathSimulator(
        qtable_path=args.qtable if Path(args.qtable).exists() else None,
        verbose=args.verbose,
        save_logs=not args.no_save
    )
    
    # Prepare students configuration
    students_config = []
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
    print(f"Average midterm score: {metadata['avg_midterm_score']:.2f}/20")
    
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
        print(f"  {cluster.upper():10s}: "
              f"reward={avg_reward:6.2f}, "
              f"midterm={avg_midterm:5.2f}/20")
    
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

