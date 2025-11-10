#!/usr/bin/env python3
"""
Generate Large-Scale Simulation Data for Q-Learning Training
=============================================================

This script generates sufficient simulation data to achieve 20-30% state space coverage,
which is necessary for effective Q-Learning training.

Current State Space: 34,560 states (5 clusters × 36 modules × 4 progress × 4 score × 6 actions × 2 stuck)
Target Coverage: 20-30% → 6,912 - 10,368 unique states
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.simulator_v2 import StudentSimulatorV2


def analyze_coverage(trajectories, total_state_space=34560):
    """
    Analyze state space coverage from trajectories
    
    Args:
        trajectories: Dict of student_id -> trajectory
        total_state_space: Total possible states
        
    Returns:
        Dict with statistics
    """
    total_transitions = sum(len(t) for t in trajectories.values())
    
    # Count unique states
    unique_states = set()
    state_counts = {}
    
    for traj in trajectories.values():
        for trans in traj:
            state = tuple(trans['state'])
            unique_states.add(state)
            state_counts[state] = state_counts.get(state, 0) + 1
    
    n_unique = len(unique_states)
    coverage = (n_unique / total_state_space) * 100
    
    # Find most visited states
    top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'n_students': len(trajectories),
        'total_transitions': total_transitions,
        'unique_states': n_unique,
        'total_state_space': total_state_space,
        'coverage_percent': coverage,
        'avg_transitions_per_student': total_transitions / len(trajectories) if trajectories else 0,
        'top_visited_states': top_states
    }


def generate_training_data(
    n_students_per_cluster: int = 80,
    max_steps_per_student: int = 120,
    output_path: str = "data/simulated_trajectories_large.json",
    verbose: bool = True
):
    """
    Generate large-scale simulation data
    
    Args:
        n_students_per_cluster: Number of students per cluster (default: 80)
        max_steps_per_student: Max steps per student (default: 120)
        output_path: Output file path
        verbose: Print progress
        
    Returns:
        trajectories: Generated trajectories
    """
    
    print("=" * 80)
    print("🎓 LARGE-SCALE SIMULATION DATA GENERATION")
    print("=" * 80)
    
    # Initialize simulator
    print("\n1️⃣  Initializing simulator...")
    simulator = StudentSimulatorV2(
        course_structure_path="data/course_structure.json",
        cluster_profiles_path="data/cluster_profiles.json",
        use_learned_params=False,  # ✅ FIXED: Use static params to apply our fixes
        learning_curve_type='logistic',
        seed=42
    )
    
    # Configuration
    total_students = n_students_per_cluster * 5  # 5 clusters
    expected_transitions = total_students * max_steps_per_student * 0.8  # 80% completion rate
    
    print(f"\n2️⃣  Simulation Configuration:")
    print(f"  📊 Students per cluster: {n_students_per_cluster}")
    print(f"  📈 Max steps per student: {max_steps_per_student}")
    print(f"  👥 Total students: {total_students}")
    print(f"  🔄 Expected transitions: ~{int(expected_transitions):,}")
    print(f"  💾 Output: {output_path}")
    
    # Confirm if large dataset
    if n_students_per_cluster >= 100:
        print(f"\n⚠️  Large dataset generation (~{total_students} students)")
        print(f"  Estimated time: ~{total_students // 30}-{total_students // 20} minutes")
    
    # Run simulation
    print(f"\n3️⃣  Running simulation...")
    start_time = datetime.now()
    
    trajectories = simulator.simulate_batch(
        n_students_per_cluster=n_students_per_cluster,
        max_steps_per_student=max_steps_per_student,
        start_date=datetime(2024, 1, 1),
        verbose=verbose
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✓ Simulation completed in {duration:.1f} seconds")
    
    # Analyze coverage
    print(f"\n4️⃣  Analyzing state space coverage...")
    stats = analyze_coverage(trajectories, total_state_space=34560)
    
    print("\n" + "=" * 80)
    print("📊 SIMULATION STATISTICS")
    print("=" * 80)
    print(f"  Total students: {stats['n_students']}")
    print(f"  Total transitions: {stats['total_transitions']:,}")
    print(f"  Avg transitions/student: {stats['avg_transitions_per_student']:.1f}")
    print(f"  Unique states covered: {stats['unique_states']:,} / {stats['total_state_space']:,}")
    print(f"  State space coverage: {stats['coverage_percent']:.2f}%")
    print("=" * 80)
    
    # Quality assessment
    print(f"\n5️⃣  Quality Assessment:")
    coverage = stats['coverage_percent']
    
    if coverage >= 30:
        print("  ✅ EXCELLENT: Coverage >= 30% - Optimal for Q-Learning!")
        print("     → Q-table will have strong coverage")
        print("     → Recommendations will be high quality")
    elif coverage >= 20:
        print("  ✅ GOOD: Coverage 20-30% - Ready for production!")
        print("     → Q-table will have good coverage")
        print("     → Suitable for real-world deployment")
    elif coverage >= 10:
        print("  ⚠️  ACCEPTABLE: Coverage 10-20% - Usable but could improve")
        print("     → Q-table will be sparse")
        print("     → Consider generating more data")
    elif coverage >= 5:
        print("  ⚠️  MINIMAL: Coverage 5-10% - Testing only")
        print("     → Q-table will be very sparse")
        print("     → Increase n_students_per_cluster")
    else:
        print("  ❌ INSUFFICIENT: Coverage < 5% - Not recommended")
        print("     → Need significantly more data")
        print(f"     → Increase to at least {int(50 * 34560 / stats['unique_states'])} students per cluster")
    
    # Save trajectories
    print(f"\n6️⃣  Saving trajectories...")
    simulator.save_trajectories(trajectories, output_path)
    
    # Save statistics
    stats_path = output_path.replace('.json', '_stats.json')
    with open(stats_path, 'w', encoding='utf-8') as f:
        # Convert top_states to serializable format
        serializable_stats = stats.copy()
        serializable_stats['top_visited_states'] = [
            {'state': list(state), 'count': count} 
            for state, count in stats['top_visited_states']
        ]
        json.dump(serializable_stats, f, indent=2, ensure_ascii=False)
    print(f"✓ Statistics saved to: {stats_path}")
    
    print("\n" + "=" * 80)
    print("✅ DATA GENERATION COMPLETED!")
    print("=" * 80)
    
    # Next steps
    print(f"\n📋 NEXT STEPS:")
    print(f"  1. Train Q-Learning:")
    print(f"     python train_qlearning_v2.py --trajectory-file {output_path}")
    print(f"  2. Evaluate Q-table:")
    print(f"     python export_qtable_info.py")
    print(f"  3. Test API:")
    print(f"     python test_api_example.py")
    
    return trajectories


def main():
    """Main function with different preset configurations"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate simulation data for Q-Learning')
    parser.add_argument('--preset', type=str, default='production',
                       choices=['test', 'dev', 'production', 'optimal', 'custom'],
                       help='Preset configuration')
    parser.add_argument('--students', type=int, help='Students per cluster (for custom preset)')
    parser.add_argument('--steps', type=int, help='Max steps per student (for custom preset)')
    parser.add_argument('--output', type=str, default='data/simulated_trajectories_large.json',
                       help='Output file path')
    
    args = parser.parse_args()
    
    # Preset configurations
    presets = {
        'test': {
            'n_students_per_cluster': 10,
            'max_steps_per_student': 50,
            'description': 'Quick test (coverage ~3-5%)'
        },
        'dev': {
            'n_students_per_cluster': 30,
            'max_steps_per_student': 100,
            'description': 'Development (coverage ~8-12%)'
        },
        'production': {
            'n_students_per_cluster': 80,
            'max_steps_per_student': 120,
            'description': 'Production ready (coverage ~20-30%)'
        },
        'optimal': {
            'n_students_per_cluster': 150,
            'max_steps_per_student': 150,
            'description': 'Optimal quality (coverage ~35-45%)'
        }
    }
    
    # Select configuration
    if args.preset == 'custom':
        if not args.students or not args.steps:
            print("❌ Error: --students and --steps required for custom preset")
            return
        config = {
            'n_students_per_cluster': args.students,
            'max_steps_per_student': args.steps,
            'description': 'Custom configuration'
        }
    else:
        config = presets[args.preset]
    
    print(f"\n📦 Using preset: {args.preset.upper()}")
    print(f"   {config['description']}")
    print()
    
    # Generate data
    generate_training_data(
        n_students_per_cluster=config['n_students_per_cluster'],
        max_steps_per_student=config['max_steps_per_student'],
        output_path=args.output,
        verbose=True
    )


if __name__ == "__main__":
    main()
