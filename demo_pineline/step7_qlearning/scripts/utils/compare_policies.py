#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare Policies - So sánh Q-Learning vs Param Policy
======================================================
Compare performance metrics between different recommendation policies
"""

import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def load_simulation_results(filepath: str) -> Dict[str, Any]:
    """Load simulation results from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_statistics(students: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate statistics from student results"""
    
    # Overall metrics
    total_rewards = [s['total_reward'] for s in students]
    midterm_scores = [
        s['lo_summary']['midterm_prediction']['predicted_score'] 
        for s in students
    ]
    # Điểm hệ 10
    midterm_scores_10 = [score / 2.0 for score in midterm_scores]  # 20 -> 10
    
    avg_lo_masteries = [
        np.mean(list(s['lo_summary']['current_mastery'].values()))
        for s in students
    ]
    
    # Reward breakdown analysis
    reward_components = defaultdict(list)
    for student in students:
        for transition in student.get('transitions', []):
            breakdown = transition.get('reward_breakdown', {})
            for component, value in breakdown.items():
                reward_components[component].append(value)
    
    # Per-cluster metrics
    cluster_stats = defaultdict(lambda: {
        'rewards': [],
        'midterm_scores': [],
        'lo_masteries': []
    })
    
    for student in students:
        cluster = student['cluster']
        cluster_stats[cluster]['rewards'].append(student['total_reward'])
        cluster_stats[cluster]['midterm_scores'].append(
            student['lo_summary']['midterm_prediction']['predicted_score']
        )
        cluster_stats[cluster]['lo_masteries'].append(
            np.mean(list(student['lo_summary']['current_mastery'].values()))
        )
    
    # Weak LO counts
    weak_lo_counts = [
        len(s['lo_summary']['weak_los']) 
        for s in students
    ]
    
    # Aggregate reward components
    avg_reward_components = {
        component: np.mean(values) if values else 0.0
        for component, values in reward_components.items()
    }
    
    return {
        'total_students': len(students),
        'avg_reward': np.mean(total_rewards),
        'std_reward': np.std(total_rewards),
        'avg_midterm_score': np.mean(midterm_scores),
        'std_midterm_score': np.std(midterm_scores),
        'avg_midterm_score_10': np.mean(midterm_scores_10),  # Hệ 10
        'std_midterm_score_10': np.std(midterm_scores_10),   # Hệ 10
        'avg_lo_mastery': np.mean(avg_lo_masteries),
        'std_lo_mastery': np.std(avg_lo_masteries),
        'avg_weak_lo_count': np.mean(weak_lo_counts),
        'reward_breakdown': avg_reward_components,  # Breakdown components
        'cluster_stats': {
            cluster: {
                'count': len(stats['rewards']),
                'avg_reward': np.mean(stats['rewards']),
                'avg_midterm': np.mean(stats['midterm_scores']),
                'avg_midterm_10': np.mean(stats['midterm_scores']) / 2.0,  # Hệ 10
                'avg_lo_mastery': np.mean(stats['lo_masteries'])
            }
            for cluster, stats in cluster_stats.items()
        }
    }


def compare_policies(
    q_learning_file: str,
    param_policy_file: str,
    output_file: str = None
) -> Dict[str, Any]:
    """
    Compare Q-Learning vs Param Policy performance
    
    Args:
        q_learning_file: Path to Q-Learning simulation results
        param_policy_file: Path to Param Policy simulation results
        output_file: Optional path to save comparison report
    
    Returns:
        Comparison statistics
    """
    print("="*80)
    print("POLICY COMPARISON: Q-Learning vs Param Policy")
    print("="*80)
    
    # Load results
    print("\nLoading simulation results...")
    q_results = load_simulation_results(q_learning_file)
    p_results = load_simulation_results(param_policy_file)
    
    print(f"  Q-Learning:   {len(q_results['students'])} students")
    print(f"  Param Policy: {len(p_results['students'])} students")
    
    # Calculate statistics
    print("\nCalculating statistics...")
    q_stats = calculate_statistics(q_results['students'])
    p_stats = calculate_statistics(p_results['students'])
    
    # Compare metrics
    print("\n" + "="*80)
    print("OVERALL PERFORMANCE")
    print("="*80)
    
    metrics = [
        ('Avg Reward', 'avg_reward', True),
        ('Avg Midterm Score (/20)', 'avg_midterm_score', True),
        ('Avg Midterm Score (/10)', 'avg_midterm_score_10', True),  # Thêm hệ 10
        ('Avg LO Mastery', 'avg_lo_mastery', True),
        ('Avg Weak LO Count', 'avg_weak_lo_count', False)  # Lower is better
    ]
    
    comparison = {}
    
    print(f"\n{'Metric':<25} {'Q-Learning':<15} {'Param Policy':<15} {'Improvement':<12}")
    print("-"*80)
    
    for metric_name, metric_key, higher_is_better in metrics:
        q_val = q_stats[metric_key]
        p_val = p_stats[metric_key]
        
        if higher_is_better:
            improvement = ((q_val - p_val) / p_val) * 100 if p_val != 0 else 0
            symbol = "✓" if improvement > 0 else "✗"
        else:
            improvement = ((p_val - q_val) / p_val) * 100 if p_val != 0 else 0
            symbol = "✓" if improvement > 0 else "✗"
        
        print(f"{metric_name:<25} {q_val:<15.2f} {p_val:<15.2f} {improvement:>+6.1f}% {symbol}")
        
        comparison[metric_key] = {
            'q_learning': q_val,
            'param_policy': p_val,
            'improvement_pct': improvement
        }
    
    # Per-cluster comparison
    print("\n" + "="*80)
    print("PER-CLUSTER PERFORMANCE")
    print("="*80)
    
    for cluster in ['weak', 'medium', 'strong']:
        if cluster not in q_stats['cluster_stats'] or cluster not in p_stats['cluster_stats']:
            continue
        
        print(f"\n{cluster.upper()} Cluster:")
        print(f"  Students: Q={q_stats['cluster_stats'][cluster]['count']}, "
              f"P={p_stats['cluster_stats'][cluster]['count']}")
        
        q_cluster = q_stats['cluster_stats'][cluster]
        p_cluster = p_stats['cluster_stats'][cluster]
        
        for metric in ['avg_reward', 'avg_midterm', 'avg_midterm_10', 'avg_lo_mastery']:
            q_val = q_cluster[metric]
            p_val = p_cluster[metric]
            improvement = ((q_val - p_val) / p_val) * 100 if p_val != 0 else 0
            symbol = "✓" if improvement > 0 else "✗"
            
            metric_name = metric.replace('avg_', '').replace('_', ' ').title()
            print(f"    {metric_name:<18}: Q={q_val:>6.2f}, P={p_val:>6.2f}, "
                  f"Δ={improvement:>+5.1f}% {symbol}")
    
    # Statistical significance (simple t-test indication)
    print("\n" + "="*80)
    print("STATISTICAL SUMMARY")
    print("="*80)
    
    q_rewards = [s['total_reward'] for s in q_results['students']]
    p_rewards = [s['total_reward'] for s in p_results['students']]
    
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(q_rewards, p_rewards)
    
    print(f"\nReward Distribution:")
    print(f"  Q-Learning:   μ={np.mean(q_rewards):.2f}, σ={np.std(q_rewards):.2f}")
    print(f"  Param Policy: μ={np.mean(p_rewards):.2f}, σ={np.std(p_rewards):.2f}")
    print(f"  T-statistic:  {t_stat:.3f}")
    print(f"  P-value:      {p_value:.4f}")
    
    if p_value < 0.05:
        print(f"  → Statistically significant difference (p < 0.05) ✓")
    else:
        print(f"  → No significant difference (p ≥ 0.05)")
    
    # Reward breakdown comparison
    print("\n" + "="*80)
    print("REWARD BREAKDOWN ANALYSIS")
    print("="*80)
    print("\nWhy reward differs but midterm score similar?")
    print("\nQ-Learning reward components (avg per transition):")
    for component, value in sorted(q_stats.get('reward_breakdown', {}).items()):
        print(f"  {component:<30}: {value:>8.4f}")
    
    print("\nParam Policy reward components (avg per transition):")
    for component, value in sorted(p_stats.get('reward_breakdown', {}).items()):
        print(f"  {component:<30}: {value:>8.4f}")
    
    print("\nKey insight:")
    print("  • Reward = LO mastery + engagement + progress + action diversity")
    print("  • Midterm score = weighted sum of LO mastery ONLY")
    print("  • Q-Learning may optimize engagement/diversity → higher reward")
    print("  • But if final LO mastery similar → midterm score similar")
    
    # Conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    reward_improvement = comparison['avg_reward']['improvement_pct']
    midterm_improvement = comparison['avg_midterm_score']['improvement_pct']
    
    if reward_improvement > 5 and midterm_improvement > 3:
        print("\n✅ Q-Learning SIGNIFICANTLY OUTPERFORMS Param Policy")
        print("   → Recommended for deployment")
    elif reward_improvement > 0 and midterm_improvement > 0:
        print("\n✓ Q-Learning performs better than Param Policy")
        print("   → Consider deployment with monitoring")
    elif reward_improvement > -5 and midterm_improvement > -3:
        print("\n⚠️  Q-Learning comparable to Param Policy")
        print("   → May need further tuning")
    else:
        print("\n✗ Q-Learning underperforms compared to Param Policy")
        print("   → Needs retraining or reward function adjustment")
    
    # Save comparison report
    report = {
        'q_learning_file': q_learning_file,
        'param_policy_file': param_policy_file,
        'q_learning_stats': q_stats,
        'param_policy_stats': p_stats,
        'comparison': comparison,
        'statistical_test': {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    }
    
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy types to native Python types
        def convert_numpy_types(obj):
            if isinstance(obj, (np.integer, np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        report_converted = convert_numpy_types(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_converted, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Comparison report saved to: {output_file}")
    
    print("\n" + "="*80)
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description='Compare Q-Learning vs Param Policy performance'
    )
    parser.add_argument(
        '--q-learning',
        type=str,
        required=True,
        help='Path to Q-Learning simulation results JSON'
    )
    parser.add_argument(
        '--param-policy',
        type=str,
        required=True,
        help='Path to Param Policy simulation results JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/simulated/comparison_report.json',
        help='Path to save comparison report'
    )
    
    args = parser.parse_args()
    
    compare_policies(
        q_learning_file=args.q_learning,
        param_policy_file=args.param_policy,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
