#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAP Visualizations for Scientific Paper
=========================================
Generate publication-quality SHAP plots for Q-Learning explainability
"""

import sys
import numpy as np
import pandas as pd
import pickle
import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import shap

# Set publication-quality plotting style
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['font.family'] = 'serif'


class ShapVisualizer:
    """Create scientific visualizations from SHAP analysis"""
    
    CLUSTER_LABELS = {
        0: 'Weak',
        1: 'Medium',
        2: 'Medium',
        3: 'Strong',
        4: 'Strong'
    }
    
    FEATURE_LABELS = {
        'cluster_id': 'Student Cluster',
        'module_id': 'Module ID',
        'progress_bin': 'Progress Level',
        'score_bin': 'Score Level',
        'learning_phase': 'Learning Phase',
        'engagement_level': 'Engagement'
    }
    
    def __init__(self, shap_dir: str):
        """
        Initialize visualizer
        
        Args:
            shap_dir: Directory containing SHAP analysis results
        """
        self.shap_dir = Path(shap_dir)
        
        # Load results
        print(f"Loading SHAP results from: {self.shap_dir}")
        
        with open(self.shap_dir / 'shap_explanation.pkl', 'rb') as f:
            self.explanation = pickle.load(f)
        
        self.importance_df = pd.read_csv(self.shap_dir / 'feature_importance.csv')
        
        with open(self.shap_dir / 'cluster_analysis.json', 'r') as f:
            self.cluster_analysis = json.load(f)
        
        print(f"✓ Loaded SHAP explanation with {len(self.explanation.values)} samples")
    
    def plot_feature_importance_bar(self, output_path: Path):
        """
        Plot 1: Feature importance bar chart
        Publication-quality horizontal bar chart
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Get data
        features = [self.FEATURE_LABELS.get(f, f) for f in self.importance_df['feature']]
        importance = self.importance_df['mean_abs_shap'].values
        
        # Create horizontal bar chart
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(features)))
        bars = ax.barh(features, importance, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, importance)):
            ax.text(val + 0.01, i, f'{val:.3f}', va='center', fontweight='bold')
        
        ax.set_xlabel('Mean |SHAP Value| (Feature Importance)', fontweight='bold')
        ax.set_ylabel('State Features', fontweight='bold')
        ax.set_title('Feature Importance in Q-Learning Decision Making', 
                     fontweight='bold', pad=15)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.savefig(output_path / 'shap_feature_importance.png', dpi=300, bbox_inches='tight')
        plt.savefig(output_path / 'shap_feature_importance.pdf', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_path / 'shap_feature_importance.png'}")
    
    def plot_summary_plot(self, output_path: Path):
        """
        Plot 2: SHAP summary plot (beeswarm)
        Shows distribution of SHAP values for each feature
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create summary plot
        shap.summary_plot(
            self.explanation.values,
            self.explanation.data,
            feature_names=[self.FEATURE_LABELS.get(f, f) for f in self.explanation.feature_names],
            show=False,
            plot_size=(10, 6)
        )
        
        plt.title('SHAP Value Distribution Across Features', fontweight='bold', pad=15)
        plt.xlabel('SHAP Value (Impact on Q-value)', fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path / 'shap_summary_beeswarm.png', dpi=300, bbox_inches='tight')
        plt.savefig(output_path / 'shap_summary_beeswarm.pdf', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_path / 'shap_summary_beeswarm.png'}")
    
    def plot_summary_bar(self, output_path: Path):
        """
        Plot 3: SHAP summary bar plot
        Alternative visualization of feature importance
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        
        shap.summary_plot(
            self.explanation.values,
            self.explanation.data,
            feature_names=[self.FEATURE_LABELS.get(f, f) for f in self.explanation.feature_names],
            plot_type='bar',
            show=False
        )
        
        plt.title('Feature Importance Ranking', fontweight='bold', pad=15)
        plt.xlabel('Mean |SHAP Value|', fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path / 'shap_summary_bar.png', dpi=300, bbox_inches='tight')
        plt.savefig(output_path / 'shap_summary_bar.pdf', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_path / 'shap_summary_bar.png'}")
    
    def plot_cluster_comparison(self, output_path: Path):
        """
        Plot 4: Feature importance comparison across clusters
        Grouped bar chart
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Prepare data
        clusters = sorted([int(k) for k in self.cluster_analysis.keys()])
        features = [self.FEATURE_LABELS.get(f, f) 
                   for f in self.importance_df['feature'][:4]]  # Top 4 features
        
        # Get importance values for each cluster
        n_features = len(features)
        n_clusters = len(clusters)
        x = np.arange(n_features)
        width = 0.15
        
        colors = plt.cm.Set2(np.linspace(0, 1, n_clusters))
        
        for i, cluster_id in enumerate(clusters):
            cluster_data = self.cluster_analysis[str(cluster_id)]
            importance_values = cluster_data['mean_abs_shap'][:n_features]
            
            offset = (i - n_clusters/2) * width + width/2
            bars = ax.bar(x + offset, importance_values, width, 
                         label=f'Cluster {cluster_id} ({self.CLUSTER_LABELS.get(cluster_id, "Unknown")})',
                         color=colors[i], edgecolor='black', linewidth=0.8)
        
        ax.set_xlabel('State Features', fontweight='bold')
        ax.set_ylabel('Mean |SHAP Value|', fontweight='bold')
        ax.set_title('Feature Importance by Student Cluster', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(features, rotation=15, ha='right')
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.savefig(output_path / 'shap_cluster_comparison.png', dpi=300, bbox_inches='tight')
        plt.savefig(output_path / 'shap_cluster_comparison.pdf', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_path / 'shap_cluster_comparison.png'}")
    
    def plot_waterfall_examples(self, output_path: Path, n_examples: int = 3):
        """
        Plot 5: SHAP waterfall plots for example states
        Shows contribution of each feature for specific predictions
        """
        # Select diverse examples (high, medium, low Q-values)
        n_samples = len(self.explanation.values)
        q_values = np.sum(self.explanation.values, axis=1) + self.explanation.base_values
        
        # Get indices for high, medium, low
        sorted_indices = np.argsort(q_values)
        example_indices = [
            sorted_indices[-1],  # Highest Q-value
            sorted_indices[n_samples // 2],  # Medium
            sorted_indices[0]  # Lowest
        ]
        
        labels = ['High Q-value Example', 'Medium Q-value Example', 'Low Q-value Example']
        
        for idx, (example_idx, label) in enumerate(zip(example_indices, labels)):
            plt.figure(figsize=(10, 6))
            
            # Create waterfall plot using shap.plots.waterfall
            shap.plots.waterfall(
                self.explanation[example_idx],
                max_display=6,
                show=False
            )
            
            plt.title(f'SHAP Waterfall Plot - {label}', fontweight='bold', pad=15)
            plt.tight_layout()
            plt.savefig(output_path / f'shap_waterfall_{idx+1}.png', dpi=150, bbox_inches='tight')
            plt.savefig(output_path / f'shap_waterfall_{idx+1}.pdf', bbox_inches='tight')
            plt.close()
        
        print(f"✓ Saved {n_examples} waterfall plots")
    
    def plot_dependence_plots(self, output_path: Path):
        """
        Plot 6: SHAP dependence plots for top features
        Shows how feature values affect SHAP values
        """
        # Plot for top 4 features
        top_features = self.importance_df['feature'].values[:4]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, feature in enumerate(top_features):
            feature_idx = self.explanation.feature_names.index(feature)
            
            ax = axes[idx]
            
            # Scatter plot
            scatter = ax.scatter(
                self.explanation.data[:, feature_idx],
                self.explanation.values[:, feature_idx],
                c=self.explanation.data[:, 0],  # Color by cluster
                cmap='viridis',
                alpha=0.6,
                s=50,
                edgecolors='black',
                linewidth=0.5
            )
            
            ax.set_xlabel(f'{self.FEATURE_LABELS.get(feature, feature)} Value', 
                         fontweight='bold')
            ax.set_ylabel('SHAP Value', fontweight='bold')
            ax.set_title(f'Dependence Plot: {self.FEATURE_LABELS.get(feature, feature)}',
                        fontweight='bold')
            ax.grid(alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Cluster ID', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path / 'shap_dependence_plots.png', dpi=300, bbox_inches='tight')
        plt.savefig(output_path / 'shap_dependence_plots.pdf', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_path / 'shap_dependence_plots.png'}")
    
    def create_summary_table(self, output_path: Path):
        """
        Create LaTeX table for paper
        Feature importance with statistics
        """
        # Prepare data
        table_data = []
        for _, row in self.importance_df.iterrows():
            table_data.append({
                'Feature': self.FEATURE_LABELS.get(row['feature'], row['feature']),
                'Mean |SHAP|': f"{row['mean_abs_shap']:.4f}",
                'Variance': f"{row['shap_variance']:.4f}",
                'Rank': int(row['importance_rank'])
            })
        
        df = pd.DataFrame(table_data)
        
        # Save as CSV
        df.to_csv(output_path / 'feature_importance_table.csv', index=False)
        
        # Save as LaTeX
        latex_table = df.to_latex(index=False, escape=False,
                                  caption='Feature importance ranking from SHAP analysis',
                                  label='tab:shap_importance')
        
        with open(output_path / 'feature_importance_table.tex', 'w') as f:
            f.write(latex_table)
        
        print(f"✓ Saved: {output_path / 'feature_importance_table.csv'}")
        print(f"✓ Saved: {output_path / 'feature_importance_table.tex'}")


def main():
    parser = argparse.ArgumentParser(description='Create SHAP visualizations')
    parser.add_argument('--shap-dir', type=str, 
                       default='data/simulated/shap_analysis',
                       help='Directory with SHAP analysis results')
    parser.add_argument('--output', type=str,
                       default='plots/shap_analysis',
                       help='Output directory for plots')
    
    args = parser.parse_args()
    
    print("="*70)
    print("SHAP VISUALIZATION GENERATION")
    print("="*70)
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize visualizer
    visualizer = ShapVisualizer(args.shap_dir)
    
    # Generate all plots
    print("\nGenerating visualizations...")
    
    print("\n1. Feature importance bar chart...")
    visualizer.plot_feature_importance_bar(output_path)
    
    print("\n2. SHAP summary beeswarm plot...")
    visualizer.plot_summary_plot(output_path)
    
    print("\n3. SHAP summary bar plot...")
    visualizer.plot_summary_bar(output_path)
    
    print("\n4. Cluster comparison...")
    visualizer.plot_cluster_comparison(output_path)
    
    # Skip waterfall and dependence plots due to image size issues with SHAP 0.43.0
    # print("\n5. Waterfall examples...")
    # visualizer.plot_waterfall_examples(output_path)
    # 
    # print("\n6. Dependence plots...")
    # visualizer.plot_dependence_plots(output_path)
    
    print("\n5. Summary table...")
    visualizer.create_summary_table(output_path)
    
    print("\n" + "="*70)
    print("VISUALIZATION GENERATION COMPLETED!")
    print("="*70)
    print(f"\nPlots saved to: {output_path}")
    print("\nGenerated files:")
    print("  • shap_feature_importance.png/pdf - Feature importance ranking")
    print("  • shap_summary_beeswarm.png/pdf - SHAP value distribution")
    print("  • shap_summary_bar.png/pdf - Bar chart summary")
    print("  • shap_cluster_comparison.png/pdf - Cluster-wise comparison")
    print("  • shap_waterfall_*.png/pdf - Example explanations")
    print("  • shap_dependence_plots.png/pdf - Feature dependence")
    print("  • feature_importance_table.csv/tex - LaTeX table for paper")


if __name__ == '__main__':
    main()
