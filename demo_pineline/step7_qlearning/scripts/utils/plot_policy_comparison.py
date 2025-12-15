"""
Plot Policy Comparison - Visualize Q-Learning vs Param Policy performance

This script creates comprehensive visualizations comparing Q-Learning and Param Policy:
1. Bar charts comparing key metrics (reward, midterm score, LO mastery)
2. Statistical tables with detailed comparison
3. Per-cluster performance analysis

Usage:
    python3 scripts/utils/plot_policy_comparison.py \\
        --comparison-report data/simulated/comparison_report.json \\
        --output plots/policy_comparison/

Author: Adaptive Learning System
Date: 2025-12-07
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from matplotlib.table import Table


class PolicyComparisonVisualizer:
    """Visualizer for Q-Learning vs Param Policy comparison"""
    
    def __init__(self, comparison_data: Dict[str, Any], output_dir: str = "plots/policy_comparison"):
        self.data = comparison_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        
        # Color scheme
        self.colors = {
            'q_learning': '#2E86AB',  # Blue
            'param_policy': '#A23B72',  # Purple
            'improvement': '#F18F01',  # Orange
            'positive': '#06A77D',  # Green
            'negative': '#D6564F'  # Red
        }
    
    def plot_overall_comparison(self, save_path: str = None):
        """Plot overall performance comparison with bar charts"""
        q_stats = self.data['q_learning_stats']
        p_stats = self.data['param_policy_stats']
        
        # Calculate improvements
        def calc_improvement(q_val, p_val):
            if p_val == 0:
                return 0
            return ((q_val - p_val) / p_val) * 100
        
        # Create figure with 2 subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Q-Learning vs Param Policy - Overall Performance Comparison', 
                     fontsize=16, fontweight='bold', y=1.02)
        
        # --- LEFT: Bar chart comparison ---
        metrics = ['Avg Reward', 'Avg Midterm\nScore (/10)', 'Avg LO\nMastery', 'Avg Weak\nLO Count']
        q_values = [
            q_stats['avg_reward'],
            q_stats.get('avg_midterm_score_10', q_stats['avg_midterm_score'] / 2.0),  # Hệ 10
            q_stats['avg_lo_mastery'] * 10,  # Scale to 0-10 for better visualization
            q_stats['avg_weak_lo_count']
        ]
        p_values = [
            p_stats['avg_reward'],
            p_stats.get('avg_midterm_score_10', p_stats['avg_midterm_score'] / 2.0),  # Hệ 10
            p_stats['avg_lo_mastery'] * 10,
            p_stats['avg_weak_lo_count']
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = axes[0].bar(x - width/2, q_values, width, label='Q-Learning',
                           color=self.colors['q_learning'], alpha=0.8, edgecolor='black', linewidth=1.2)
        bars2 = axes[0].bar(x + width/2, p_values, width, label='Param Policy',
                           color=self.colors['param_policy'], alpha=0.8, edgecolor='black', linewidth=1.2)
        
        axes[0].set_ylabel('Value', fontweight='bold')
        axes[0].set_title('Performance Metrics Comparison', fontweight='bold', pad=15)
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(metrics)
        axes[0].legend(loc='upper left', framealpha=0.9)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                axes[0].text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # --- RIGHT: Improvement percentage ---
        improvements = [
            calc_improvement(q_stats['avg_reward'], p_stats['avg_reward']),
            calc_improvement(q_stats.get('avg_midterm_score_10', q_stats['avg_midterm_score'] / 2.0), 
                           p_stats.get('avg_midterm_score_10', p_stats['avg_midterm_score'] / 2.0)),
            calc_improvement(q_stats['avg_lo_mastery'], p_stats['avg_lo_mastery']),
            calc_improvement(q_stats['avg_weak_lo_count'], p_stats['avg_weak_lo_count'])
        ]
        
        colors_imp = [self.colors['positive'] if imp > 0 else self.colors['negative'] 
                      for imp in improvements]
        
        bars = axes[1].barh(metrics, improvements, color=colors_imp, alpha=0.8, 
                            edgecolor='black', linewidth=1.2)
        axes[1].set_xlabel('Improvement (%)', fontweight='bold')
        axes[1].set_title('Q-Learning Improvement over Param Policy', fontweight='bold', pad=15)
        axes[1].axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        axes[1].grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, imp) in enumerate(zip(bars, improvements)):
            width = bar.get_width()
            label_x = width + (5 if width > 0 else -5)
            ha = 'left' if width > 0 else 'right'
            axes[1].text(label_x, bar.get_y() + bar.get_height()/2,
                        f'{imp:+.1f}%',
                        ha=ha, va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            pdf_path = str(save_path).replace('.png', '.pdf')
            plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved overall comparison chart to: {save_path}")
            print(f"✓ Saved overall comparison chart to: {pdf_path}")
        
        return fig
    
    def plot_cluster_comparison(self, save_path: str = None):
        """Plot per-cluster performance comparison"""
        q_clusters = self.data['q_learning_stats']['cluster_stats']
        p_clusters = self.data['param_policy_stats']['cluster_stats']
        
        # Get all clusters
        all_clusters = sorted(set(list(q_clusters.keys()) + list(p_clusters.keys())))
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Q-Learning vs Param Policy - Per-Cluster Performance', 
                     fontsize=16, fontweight='bold', y=0.995)
        
        metrics = ['avg_reward', 'avg_midterm_10', 'avg_lo_mastery']
        titles = ['Average Reward by Cluster', 'Average Midterm Score by Cluster', 
                  'Average LO Mastery by Cluster']
        ylabels = ['Reward', 'Midterm Score (0-10)', 'LO Mastery (0-1)']
        
        for idx, (metric, title, ylabel) in enumerate(zip(metrics, titles, ylabels)):
            ax = axes[idx // 2, idx % 2]
            
            q_values = []
            p_values = []
            labels = []
            
            for cluster in all_clusters:
                if cluster in q_clusters and cluster in p_clusters:
                    q_val = q_clusters[cluster].get(metric, q_clusters[cluster].get('avg_midterm', 0) / 2.0 if metric == 'avg_midterm_10' else 0)
                    p_val = p_clusters[cluster].get(metric, p_clusters[cluster].get('avg_midterm', 0) / 2.0 if metric == 'avg_midterm_10' else 0)
                    q_values.append(q_val)
                    p_values.append(p_val)
                    labels.append(f'Cluster {cluster}')
            
            x = np.arange(len(labels))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, q_values, width, label='Q-Learning',
                          color=self.colors['q_learning'], alpha=0.8, edgecolor='black', linewidth=1.2)
            bars2 = ax.bar(x + width/2, p_values, width, label='Param Policy',
                          color=self.colors['param_policy'], alpha=0.8, edgecolor='black', linewidth=1.2)
            
            ax.set_ylabel(ylabel, fontweight='bold')
            ax.set_title(title, fontweight='bold', pad=10)
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend(loc='upper left', framealpha=0.9)
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}',
                           ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # --- BOTTOM RIGHT: Statistical summary table ---
        ax = axes[1, 1]
        ax.axis('off')
        
        stat_test = self.data['statistical_test']
        
        table_data = [
            ['Metric', 'Value'],
            ['T-statistic', f"{stat_test['t_statistic']:.3f}"],
            ['P-value', f"{stat_test['p_value']:.4f}"],
            ['Significant?', '✓ YES' if stat_test['significant'] else '✗ NO'],
            ['', ''],
            ['Q-Learning Students', f"{self.data['q_learning_stats']['total_students']}"],
            ['Param Policy Students', f"{self.data['param_policy_stats']['total_students']}"],
        ]
        
        table = ax.table(cellText=table_data, cellLoc='left', loc='center',
                        colWidths=[0.6, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header row
        for i in range(2):
            cell = table[(0, i)]
            cell.set_facecolor('#2E86AB')
            cell.set_text_props(weight='bold', color='white')
        
        # Style significant row
        if stat_test['significant']:
            cell = table[(3, 1)]
            cell.set_facecolor('#06A77D')
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Statistical Test Results', fontweight='bold', pad=20, fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            pdf_path = str(save_path).replace('.png', '.pdf')
            plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved cluster comparison chart to: {save_path}")
            print(f"✓ Saved cluster comparison chart to: {pdf_path}")
        
        return fig
    
    def plot_comparison_table(self, save_path: str = None):
        """Create detailed comparison table visualization"""
        q_stats = self.data['q_learning_stats']
        p_stats = self.data['param_policy_stats']
        
        # Calculate improvements
        def calc_improvement(q_val, p_val):
            if p_val == 0:
                return 0
            return ((q_val - p_val) / p_val) * 100
        
        reward_imp = calc_improvement(q_stats['avg_reward'], p_stats['avg_reward'])
        q_midterm_10 = q_stats.get('avg_midterm_score_10', q_stats['avg_midterm_score'] / 2.0)
        p_midterm_10 = p_stats.get('avg_midterm_score_10', p_stats['avg_midterm_score'] / 2.0)
        midterm_imp = calc_improvement(q_midterm_10, p_midterm_10)
        lo_imp = calc_improvement(q_stats['avg_lo_mastery'], p_stats['avg_lo_mastery'])
        weak_lo_imp = calc_improvement(q_stats['avg_weak_lo_count'], p_stats['avg_weak_lo_count'])
        
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        table_data = [
            ['Metric', 'Q-Learning', 'Param Policy', 'Improvement', 'Winner'],
            # Overall metrics
            ['OVERALL PERFORMANCE', '', '', '', ''],
            ['Average Reward', 
             f"{q_stats['avg_reward']:.2f} (±{q_stats['std_reward']:.2f})",
             f"{p_stats['avg_reward']:.2f} (±{p_stats['std_reward']:.2f})",
             f"{reward_imp:+.1f}%",
             '✓' if reward_imp > 0 else '✗'],
            ['Average Midterm Score (/10)',
             f"{q_midterm_10:.2f} (±{q_stats.get('std_midterm_score_10', q_stats['std_midterm_score'] / 2.0):.2f})",
             f"{p_midterm_10:.2f} (±{p_stats.get('std_midterm_score_10', p_stats['std_midterm_score'] / 2.0):.2f})",
             f"{midterm_imp:+.1f}%",
             '✓' if midterm_imp > 0 else '✗'],
            ['Average LO Mastery',
             f"{q_stats['avg_lo_mastery']:.3f} (±{q_stats['std_lo_mastery']:.3f})",
             f"{p_stats['avg_lo_mastery']:.3f} (±{p_stats['std_lo_mastery']:.3f})",
             f"{lo_imp:+.1f}%",
             '✓' if lo_imp > 0 else '✗'],
            ['Average Weak LO Count',
             f"{q_stats['avg_weak_lo_count']:.2f}",
             f"{p_stats['avg_weak_lo_count']:.2f}",
             f"{weak_lo_imp:+.1f}%",
             '✓' if weak_lo_imp > 0 else '✗'],
        ]
        
        # Add cluster-specific data
        q_clusters = q_stats['cluster_stats']
        p_clusters = p_stats['cluster_stats']
        all_clusters = sorted(set(list(q_clusters.keys()) + list(p_clusters.keys())))
        
        for cluster in all_clusters:
            if cluster in q_clusters and cluster in p_clusters:
                q_c = q_clusters[cluster]
                p_c = p_clusters[cluster]
                
                table_data.append(['', '', '', '', ''])
                table_data.append([f'CLUSTER {cluster}', '', '', '', ''])
                
                # Reward
                reward_imp = ((q_c['avg_reward'] - p_c['avg_reward']) / p_c['avg_reward'] * 100) if p_c['avg_reward'] != 0 else 0
                table_data.append([
                    f"  Reward (n={q_c['count']})",
                    f"{q_c['avg_reward']:.2f}",
                    f"{p_c['avg_reward']:.2f}",
                    f"{reward_imp:+.1f}%",
                    '✓' if reward_imp > 0 else '✗'
                ])
                
                # Midterm (hệ 10)
                q_midterm_10 = q_c.get('avg_midterm_10', q_c['avg_midterm'] / 2.0)
                p_midterm_10 = p_c.get('avg_midterm_10', p_c['avg_midterm'] / 2.0)
                midterm_imp = ((q_midterm_10 - p_midterm_10) / p_midterm_10 * 100) if p_midterm_10 != 0 else 0
                table_data.append([
                    f"  Midterm Score (/10)",
                    f"{q_midterm_10:.2f}",
                    f"{p_midterm_10:.2f}",
                    f"{midterm_imp:+.1f}%",
                    '✓' if midterm_imp > 0 else '✗'
                ])
                
                # LO Mastery
                lo_imp = ((q_c['avg_lo_mastery'] - p_c['avg_lo_mastery']) / p_c['avg_lo_mastery'] * 100) if p_c['avg_lo_mastery'] != 0 else 0
                table_data.append([
                    f"  LO Mastery",
                    f"{q_c['avg_lo_mastery']:.3f}",
                    f"{p_c['avg_lo_mastery']:.3f}",
                    f"{lo_imp:+.1f}%",
                    '✓' if lo_imp > 0 else '✗'
                ])
        
        # Add statistical test
        stat_test = self.data['statistical_test']
        table_data.append(['', '', '', '', ''])
        table_data.append(['STATISTICAL TEST', '', '', '', ''])
        table_data.append(['T-statistic', f"{stat_test['t_statistic']:.3f}", '', '', ''])
        table_data.append(['P-value', f"{stat_test['p_value']:.6f}", '', 
                          'Significant' if stat_test['significant'] else 'Not Significant', ''])
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='left', loc='center',
                        colWidths=[0.3, 0.2, 0.2, 0.15, 0.1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        # Style table
        for i, row in enumerate(table_data):
            for j in range(5):
                cell = table[(i, j)]
                
                # Header row
                if i == 0:
                    cell.set_facecolor('#2E86AB')
                    cell.set_text_props(weight='bold', color='white', ha='center')
                # Section headers
                elif row[0] in ['OVERALL PERFORMANCE', 'STATISTICAL TEST'] or 'CLUSTER' in row[0]:
                    cell.set_facecolor('#E0E0E0')
                    cell.set_text_props(weight='bold')
                # Winner column - green for win, red for loss
                elif j == 4 and row[j] == '✓':
                    cell.set_facecolor('#D4EDDA')
                    cell.set_text_props(color='#155724', weight='bold', ha='center')
                elif j == 4 and row[j] == '✗':
                    cell.set_facecolor('#F8D7DA')
                    cell.set_text_props(color='#721C24', weight='bold', ha='center')
                # Improvement column - color based on sign
                elif j == 3 and '+' in str(row[j]):
                    cell.set_text_props(color='#155724', weight='bold')
                elif j == 3 and '-' in str(row[j]):
                    cell.set_text_props(color='#721C24', weight='bold')
        
        plt.title('Q-Learning vs Param Policy - Detailed Comparison Table', 
                 fontsize=16, fontweight='bold', pad=20)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            pdf_path = str(save_path).replace('.png', '.pdf')
            plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved comparison table to: {save_path}")
            print(f"✓ Saved comparison table to: {pdf_path}")
        
        return fig
    
    def create_all_plots(self):
        """Generate all comparison plots"""
        print("\n" + "="*80)
        print("GENERATING POLICY COMPARISON VISUALIZATIONS")
        print("="*80 + "\n")
        
        # 1. Overall comparison
        print("Creating overall comparison chart...")
        self.plot_overall_comparison(
            save_path=self.output_dir / "overall_comparison.png"
        )
        
        # 2. Cluster comparison
        print("Creating per-cluster comparison chart...")
        self.plot_cluster_comparison(
            save_path=self.output_dir / "cluster_comparison.png"
        )
        
        # 3. Detailed table
        print("Creating detailed comparison table...")
        self.plot_comparison_table(
            save_path=self.output_dir / "comparison_table.png"
        )
        
        print("\n" + "="*80)
        print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        print(f"✓ Output directory: {self.output_dir}")
        print("="*80 + "\n")
        
        plt.close('all')


def main():
    parser = argparse.ArgumentParser(
        description='Plot Q-Learning vs Param Policy comparison visualizations'
    )
    parser.add_argument(
        '--comparison-report',
        type=str,
        required=True,
        help='Path to comparison report JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='plots/policy_comparison',
        help='Output directory for plots (default: plots/policy_comparison)'
    )
    
    args = parser.parse_args()
    
    # Load comparison data
    print(f"\nLoading comparison report from: {args.comparison_report}")
    with open(args.comparison_report, 'r', encoding='utf-8') as f:
        comparison_data = json.load(f)
    
    # Create visualizations
    visualizer = PolicyComparisonVisualizer(
        comparison_data=comparison_data,
        output_dir=args.output
    )
    visualizer.create_all_plots()
    
    print("\nGenerated files:")
    print(f"  1. {args.output}/overall_comparison.png - Bar charts of key metrics")
    print(f"  2. {args.output}/cluster_comparison.png - Per-cluster performance analysis")
    print(f"  3. {args.output}/comparison_table.png - Detailed comparison table")


if __name__ == '__main__':
    main()
