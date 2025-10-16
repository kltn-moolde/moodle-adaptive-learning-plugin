#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Set Evaluation
===================
Evaluate trained Q-Learning agent on test set and compare with train set
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict
import logging

from core.qlearning_agent_v2 import QLearningAgentV2

logger = logging.getLogger(__name__)


def compute_reward(record: pd.Series) -> float:
    """Compute reward from learning outcome (same as trainer)"""
    grade = record.get('grade', 0.0)
    time_spent = record.get('time_spent', 15)
    completed = record.get('completed', False)
    
    grade_reward = grade
    time_normalized = np.clip(time_spent / 60, 0, 1)
    time_reward = 1.0 - time_normalized
    completion_reward = 1.0 if completed else 0.0
    
    reward = (
        0.5 * grade_reward +
        0.2 * time_reward +
        0.3 * completion_reward
    )
    
    return reward


def evaluate_on_dataset(agent: QLearningAgentV2, df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict:
    """
    Evaluate agent on a dataset
    
    Returns:
        Dict of metrics per student
    """
    logger.info(f"\nEvaluating on {dataset_name}...")
    
    unique_students = df['student_id'].unique()
    
    student_metrics = {}
    
    for student_id in unique_students:
        student_df = df[df['student_id'] == student_id].sort_values('step')
        
        grades = []
        rewards = []
        completions = []
        q_values = []
        recommendation_matches = 0
        total_steps = 0
        
        for idx, record in student_df.iterrows():
            # Extract state
            feature_names = [
                'mean_module_grade', 'total_events', 'course_module',
                'viewed', 'attempt', 'feedback_viewed', 'submitted', 'reviewed',
                'course_module_viewed', 'module_count', 'course_module_completion',
                'created', 'updated', 'downloaded'
            ]
            
            features = {}
            for fname in feature_names:
                if fname in record:
                    features[fname] = record[fname]
                else:
                    features[fname] = 0.5
            
            state = agent.state_builder.build_state(features)
            actual_action_id = str(record['resource_id'])
            
            # Get agent's recommendation
            # Get available actions (for simplicity, assume all actions available)
            available_actions = agent.action_space.get_all_actions()
            
            if available_actions:
                recommendations = agent.recommend(
                    state,
                    available_actions,
                    top_k=3,
                    use_heuristic_fallback=False
                )
                
                # Check if actual action is in top-3
                recommended_ids = [r['action_id'] for r in recommendations]
                if actual_action_id in recommended_ids:
                    recommendation_matches += 1
                total_steps += 1
                
                # Get Q-value for actual action
                discrete_state = tuple(agent.discretizer.discretize(state))
                q_val = agent.Q.get((discrete_state, actual_action_id), 0.0)
                q_values.append(q_val)
            
            # Record metrics
            reward = compute_reward(record)
            grades.append(record['grade'])
            rewards.append(reward)
            completions.append(1 if record['completed'] else 0)
        
        # Aggregate metrics for this student
        student_metrics[str(student_id)] = {
            'avg_grade': float(np.mean(grades)),
            'avg_reward': float(np.mean(rewards)),
            'completion_rate': float(np.mean(completions)),
            'avg_q_value': float(np.mean(q_values)) if q_values else 0.0,
            'recommendation_accuracy': float(recommendation_matches / total_steps) if total_steps > 0 else 0.0,
            'n_steps': len(grades)
        }
    
    # Overall statistics
    overall_metrics = {
        'n_students': len(unique_students),
        'avg_grade': float(np.mean([m['avg_grade'] for m in student_metrics.values()])),
        'avg_reward': float(np.mean([m['avg_reward'] for m in student_metrics.values()])),
        'completion_rate': float(np.mean([m['completion_rate'] for m in student_metrics.values()])),
        'avg_q_value': float(np.mean([m['avg_q_value'] for m in student_metrics.values() if m['avg_q_value'] > 0])),
        'recommendation_accuracy': float(np.mean([m['recommendation_accuracy'] for m in student_metrics.values()])),
    }
    
    logger.info(f"\n{'='*70}")
    logger.info(f"{dataset_name} Results:")
    logger.info(f"{'='*70}")
    logger.info(f"Students: {overall_metrics['n_students']}")
    logger.info(f"Avg Grade: {overall_metrics['avg_grade']:.4f}")
    logger.info(f"Avg Reward: {overall_metrics['avg_reward']:.4f}")
    logger.info(f"Completion Rate: {overall_metrics['completion_rate']:.2%}")
    logger.info(f"Avg Q-value: {overall_metrics['avg_q_value']:.4f}")
    logger.info(f"Recommendation Accuracy (top-3): {overall_metrics['recommendation_accuracy']:.2%}")
    logger.info(f"{'='*70}\n")
    
    return {
        'overall': overall_metrics,
        'per_student': student_metrics
    }


def plot_train_vs_test_comparison(train_results: Dict, test_results: Dict):
    """Plot comparison between train and test sets"""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Train vs Test Set Comparison', fontsize=16)
    
    metrics = ['avg_grade', 'avg_reward', 'completion_rate', 'avg_q_value', 'recommendation_accuracy']
    titles = ['Average Grade', 'Average Reward', 'Completion Rate', 'Average Q-value', 'Recommendation Accuracy (top-3)']
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    
    for idx, (metric, title, color) in enumerate(zip(metrics, titles, colors)):
        row = idx // 3
        col = idx % 3
        
        train_val = train_results['overall'][metric]
        test_val = test_results['overall'][metric]
        
        axes[row, col].bar(['Train', 'Test'], [train_val, test_val], color=[color, 'lightgray'], alpha=0.7)
        axes[row, col].set_ylabel(title)
        axes[row, col].set_title(title)
        axes[row, col].grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        axes[row, col].text(0, train_val, f'{train_val:.3f}', ha='center', va='bottom', fontsize=10)
        axes[row, col].text(1, test_val, f'{test_val:.3f}', ha='center', va='bottom', fontsize=10)
    
    # Hide last subplot
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig('results/train_vs_test_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/train_vs_test_comparison.png")
    plt.show()


def plot_student_distribution_comparison(train_results: Dict, test_results: Dict):
    """Plot distribution of student metrics for train vs test"""
    
    # Extract per-student metrics
    train_grades = [m['avg_grade'] for m in train_results['per_student'].values()]
    test_grades = [m['avg_grade'] for m in test_results['per_student'].values()]
    
    train_rewards = [m['avg_reward'] for m in train_results['per_student'].values()]
    test_rewards = [m['avg_reward'] for m in test_results['per_student'].values()]
    
    train_completion = [m['completion_rate'] for m in train_results['per_student'].values()]
    test_completion = [m['completion_rate'] for m in test_results['per_student'].values()]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle('Student Metrics Distribution: Train vs Test', fontsize=16)
    
    # Grade distribution
    axes[0].hist(train_grades, bins=20, alpha=0.5, label='Train', color='blue')
    axes[0].hist(test_grades, bins=20, alpha=0.5, label='Test', color='orange')
    axes[0].set_xlabel('Average Grade')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Grade Distribution')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Reward distribution
    axes[1].hist(train_rewards, bins=20, alpha=0.5, label='Train', color='blue')
    axes[1].hist(test_rewards, bins=20, alpha=0.5, label='Test', color='orange')
    axes[1].set_xlabel('Average Reward')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Reward Distribution')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Completion rate distribution
    axes[2].hist(train_completion, bins=20, alpha=0.5, label='Train', color='blue')
    axes[2].hist(test_completion, bins=20, alpha=0.5, label='Test', color='orange')
    axes[2].set_xlabel('Completion Rate')
    axes[2].set_ylabel('Frequency')
    axes[2].set_title('Completion Rate Distribution')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/train_vs_test_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/train_vs_test_distribution.png")
    plt.show()


def main():
    """Main evaluation script"""
    print("\n" + "="*70)
    print("Test Set Evaluation")
    print("="*70)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    base_path = Path(__file__).parent
    
    # Load trained agent
    print("\n1. Loading trained agent...")
    model_path = base_path / "models/qlearning_trained.pkl"
    if not model_path.exists():
        print(f"❌ Error: Model not found at {model_path}")
        print("Please train the model first by running: python3 train_qlearning.py")
        return
    
    # Create agent first, then load
    agent = QLearningAgentV2.create_from_course(
        str(base_path / "data/course_structure.json"),
        n_bins=3,
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.3
    )
    agent.load(str(model_path))
    print(f"✓ Loaded agent: {agent}")
    
    # Load data
    print("\n2. Loading data...")
    train_df = pd.read_csv(base_path / "data/simulated/train_data.csv")
    test_df = pd.read_csv(base_path / "data/simulated/test_data.csv")
    print(f"✓ Train: {len(train_df)} records, {train_df['student_id'].nunique()} students")
    print(f"✓ Test: {len(test_df)} records, {test_df['student_id'].nunique()} students")
    
    # Evaluate on train set
    print("\n3. Evaluating on train set...")
    train_results = evaluate_on_dataset(agent, train_df, "Train Set")
    
    # Evaluate on test set
    print("\n4. Evaluating on test set...")
    test_results = evaluate_on_dataset(agent, test_df, "Test Set")
    
    # Save results
    print("\n5. Saving results...")
    results = {
        'train': train_results,
        'test': test_results
    }
    
    results_path = base_path / "results/test_evaluation.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Saved: {results_path}")
    
    # Visualize comparisons
    print("\n6. Generating visualizations...")
    plot_train_vs_test_comparison(train_results, test_results)
    plot_student_distribution_comparison(train_results, test_results)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Summary:")
    print("="*70)
    print(f"Train Set:")
    print(f"  - Avg Grade: {train_results['overall']['avg_grade']:.4f}")
    print(f"  - Recommendation Accuracy: {train_results['overall']['recommendation_accuracy']:.2%}")
    print(f"\nTest Set:")
    print(f"  - Avg Grade: {test_results['overall']['avg_grade']:.4f}")
    print(f"  - Recommendation Accuracy: {test_results['overall']['recommendation_accuracy']:.2%}")
    
    # Generalization gap
    grade_gap = abs(train_results['overall']['avg_grade'] - test_results['overall']['avg_grade'])
    acc_gap = abs(train_results['overall']['recommendation_accuracy'] - test_results['overall']['recommendation_accuracy'])
    
    print(f"\n📈 Generalization:")
    print(f"  - Grade gap: {grade_gap:.4f} ({'good' if grade_gap < 0.05 else 'needs improvement'})")
    print(f"  - Accuracy gap: {acc_gap:.2%} ({'good' if acc_gap < 0.05 else 'needs improvement'})")
    
    if test_results['overall']['avg_grade'] >= train_results['overall']['avg_grade'] * 0.95:
        print("\n✅ Model generalizes well to test set!")
    else:
        print("\n⚠️ Model may be overfitting to train set.")
    
    print("\n" + "="*70)
    print("✅ Evaluation completed!")
    print("="*70)


if __name__ == '__main__':
    main()
