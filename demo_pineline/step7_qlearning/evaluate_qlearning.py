#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluation Metrics and Visualization
=====================================
Đánh giá hiệu suất của Q-Learning agent và visualize kết quả
"""

import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)


class QLearningEvaluator:
    """
    Đánh giá và visualize Q-Learning performance
    
    Metrics:
    1. Learning Curve: Reward over epochs
    2. Recommendation Accuracy: Top-K accuracy
    3. Grade Improvement: Predicted vs Actual
    4. Completion Rate: Resource completion
    5. Q-table Coverage: State-action coverage
    """
    
    def __init__(self, results_dir: str):
        """
        Args:
            results_dir: Directory containing training results
        """
        self.results_dir = Path(results_dir)
        
        # Load results
        self.history = self._load_json('training_history.json')
        self.metrics = self._load_json('evaluation_metrics.json')
        
        logger.info(f"Evaluator initialized from {results_dir}")
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON file"""
        path = self.results_dir / filename
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def plot_learning_curve(self, save_path: str = None):
        """Plot learning curve (reward over epochs)"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        epochs = range(1, len(self.history['episode_rewards']) + 1)
        
        # Subplot 1: Episode Rewards
        axes[0].plot(epochs, self.history['episode_rewards'], marker='o', linewidth=2)
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Average Reward')
        axes[0].set_title('Learning Curve: Average Reward per Epoch')
        axes[0].grid(True, alpha=0.3)
        
        # Subplot 2: Episode Lengths
        axes[1].plot(epochs, self.history['episode_lengths'], marker='s', linewidth=2, color='orange')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Average Episode Length')
        axes[1].set_title('Average Episode Length per Epoch')
        axes[1].grid(True, alpha=0.3)
        
        # Subplot 3: Q-values
        axes[2].plot(epochs, self.history['avg_q_values'], marker='^', linewidth=2, color='green')
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('Average Q-value')
        axes[2].set_title('Average Q-value per Epoch')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Learning curve saved: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_train_vs_test(self, save_path: str = None):
        """Plot train vs test metrics comparison"""
        train_metrics = self.metrics.get('train', {})
        test_metrics = self.metrics.get('test', {})
        
        metric_names = ['avg_reward', 'avg_grade', 'completion_rate', 'recommendation_accuracy']
        train_values = [train_metrics.get(m, 0) for m in metric_names]
        test_values = [test_metrics.get(m, 0) for m in metric_names]
        
        x = np.arange(len(metric_names))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars1 = ax.bar(x - width/2, train_values, width, label='Train', alpha=0.8)
        bars2 = ax.bar(x + width/2, test_values, width, label='Test', alpha=0.8)
        
        ax.set_ylabel('Score')
        ax.set_title('Train vs Test Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels([
            'Avg Reward',
            'Avg Grade',
            'Completion Rate',
            'Recommendation\nAccuracy'
        ])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Train vs test plot saved: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_metrics_heatmap(self, save_path: str = None):
        """Plot metrics heatmap"""
        train_metrics = self.metrics.get('train', {})
        test_metrics = self.metrics.get('test', {})
        
        # Prepare data
        metric_names = ['avg_reward', 'avg_grade', 'completion_rate', 'recommendation_accuracy', 'avg_q_value']
        data = []
        
        for name in metric_names:
            data.append([
                train_metrics.get(name, 0),
                test_metrics.get(name, 0)
            ])
        
        df = pd.DataFrame(data, 
                         index=[n.replace('_', ' ').title() for n in metric_names],
                         columns=['Train', 'Test'])
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df, annot=True, fmt='.4f', cmap='YlGnBu', ax=ax, 
                   cbar_kws={'label': 'Score'}, vmin=0, vmax=1)
        ax.set_title('Performance Metrics Heatmap')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Metrics heatmap saved: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_report(self, output_path: str = None):
        """Generate comprehensive evaluation report"""
        report_lines = []
        
        report_lines.append("="*70)
        report_lines.append("Q-LEARNING EVALUATION REPORT")
        report_lines.append("="*70)
        report_lines.append("")
        
        # Training Summary
        report_lines.append("TRAINING SUMMARY")
        report_lines.append("-"*70)
        report_lines.append(f"Total Epochs: {len(self.history.get('episode_rewards', []))}")
        report_lines.append(f"Final Avg Reward: {self.history.get('episode_rewards', [0])[-1]:.4f}")
        report_lines.append(f"Final Avg Q-value: {self.history.get('avg_q_values', [0])[-1]:.4f}")
        report_lines.append("")
        
        # Train Metrics
        report_lines.append("TRAIN SET PERFORMANCE")
        report_lines.append("-"*70)
        train_metrics = self.metrics.get('train', {})
        for key, value in train_metrics.items():
            if isinstance(value, float):
                report_lines.append(f"{key.replace('_', ' ').title()}: {value:.4f}")
            else:
                report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        report_lines.append("")
        
        # Test Metrics
        report_lines.append("TEST SET PERFORMANCE")
        report_lines.append("-"*70)
        test_metrics = self.metrics.get('test', {})
        for key, value in test_metrics.items():
            if isinstance(value, float):
                report_lines.append(f"{key.replace('_', ' ').title()}: {value:.4f}")
            else:
                report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        report_lines.append("")
        
        # Generalization Analysis
        report_lines.append("GENERALIZATION ANALYSIS")
        report_lines.append("-"*70)
        
        for metric in ['avg_reward', 'avg_grade', 'recommendation_accuracy']:
            train_val = train_metrics.get(metric, 0)
            test_val = test_metrics.get(metric, 0)
            gap = train_val - test_val
            gap_pct = (gap / train_val * 100) if train_val > 0 else 0
            
            report_lines.append(f"{metric.replace('_', ' ').title()}:")
            report_lines.append(f"  Train: {train_val:.4f}")
            report_lines.append(f"  Test:  {test_val:.4f}")
            report_lines.append(f"  Gap:   {gap:.4f} ({gap_pct:.2f}%)")
            report_lines.append("")
        
        # Key Insights
        report_lines.append("KEY INSIGHTS")
        report_lines.append("-"*70)
        
        # Insight 1: Learning progress
        rewards = self.history.get('episode_rewards', [])
        if len(rewards) >= 2:
            improvement = rewards[-1] - rewards[0]
            report_lines.append(f"1. Reward improved by {improvement:.4f} ({improvement/rewards[0]*100:.1f}%) over training")
        
        # Insight 2: Recommendation accuracy
        rec_acc = test_metrics.get('recommendation_accuracy', 0)
        if rec_acc > 0.5:
            report_lines.append(f"2. Strong recommendation accuracy ({rec_acc:.2%}) indicates good policy learning")
        else:
            report_lines.append(f"2. Moderate recommendation accuracy ({rec_acc:.2%}) suggests room for improvement")
        
        # Insight 3: Generalization
        train_reward = train_metrics.get('avg_reward', 0)
        test_reward = test_metrics.get('avg_reward', 0)
        if abs(train_reward - test_reward) / train_reward < 0.1:
            report_lines.append(f"3. Good generalization (train-test gap < 10%)")
        else:
            report_lines.append(f"3. Potential overfitting (train-test gap > 10%)")
        
        report_lines.append("")
        report_lines.append("="*70)
        
        report_text = "\n".join(report_lines)
        
        # Print to console
        print(report_text)
        
        # Save to file
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"✓ Report saved: {output_path}")
        
        return report_text
    
    def generate_all_visualizations(self, output_dir: str = None):
        """Generate all visualization plots"""
        if output_dir is None:
            output_dir = self.results_dir / "visualizations"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Generating visualizations...")
        
        # Learning curve
        self.plot_learning_curve(save_path=str(output_path / "learning_curve.png"))
        
        # Train vs test
        self.plot_train_vs_test(save_path=str(output_path / "train_vs_test.png"))
        
        # Metrics heatmap
        self.plot_metrics_heatmap(save_path=str(output_path / "metrics_heatmap.png"))
        
        logger.info(f"✓ All visualizations saved to {output_path}")


def main():
    """Main evaluation script"""
    print("\n" + "="*70)
    print("Q-Learning Evaluation")
    print("="*70)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Paths
    base_path = Path(__file__).parent.parent
    results_dir = base_path / "results"
    
    if not results_dir.exists():
        logger.error(f"Results directory not found: {results_dir}")
        logger.error("Please run training first!")
        return
    
    # Initialize evaluator
    evaluator = QLearningEvaluator(str(results_dir))
    
    # Generate report
    report_path = results_dir / "evaluation_report.txt"
    evaluator.generate_report(output_path=str(report_path))
    
    # Generate visualizations
    evaluator.generate_all_visualizations(output_dir=str(results_dir / "visualizations"))
    
    print("\n" + "="*70)
    print("✅ Evaluation completed!")
    print("="*70)


if __name__ == '__main__':
    main()
