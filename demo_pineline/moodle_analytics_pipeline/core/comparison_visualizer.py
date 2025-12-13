#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Visualizer Module
==========================
Visualize cluster data and feature distributions
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class ComparisonVisualizer:
    """
    Visualize cluster data and feature distributions
    
    Features:
    - Feature distributions by cluster
    - Cluster proportion visualization
    - Feature correlation heatmaps
    """
    
    def __init__(self):
        self.data = None
        
    def load_data(self, data_path: str):
        """
        Load clustered data for visualization
        
        Args:
            data_path: Path to data (JSON or CSV)
        """
        logger.info("Loading data for visualization...")
        
        if data_path.endswith('.json'):
            import json
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = pd.DataFrame(json.load(f))
        else:
            self.data = pd.read_csv(data_path)
        
        logger.info(f"✓ Loaded: {len(self.data)} students")
    
    def visualize_distributions(self, features: List[str], output_dir: str = None):
        """
        Visualize feature distributions by cluster
        
        Args:
            features: List of features to visualize
            output_dir: Directory to save plots
        """
        logger.info(f"Visualizing distributions for {len(features)} features...")
        
        n_features = min(len(features), 9)  # Limit to 9 for readability
        features = features[:n_features]
        n_cols = 3
        n_rows = (n_features + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
        axes = axes.flatten() if n_features > 1 else [axes]
        
        has_clusters = 'cluster' in self.data.columns
        
        for idx, feature in enumerate(features):
            ax = axes[idx]
            
            if feature not in self.data.columns:
                ax.text(0.5, 0.5, f'{feature}\nnot found', 
                       ha='center', va='center')
                ax.set_title(feature)
                continue
            
            # Plot by cluster if available
            if has_clusters:
                for cluster in sorted(self.data['cluster'].unique()):
                    cluster_data = self.data[self.data['cluster'] == cluster][feature].dropna()
                    ax.hist(cluster_data, bins=15, alpha=0.6, 
                           label=f'Cluster {cluster}', edgecolor='black')
                ax.legend(fontsize=8, loc='upper right')
            else:
                ax.hist(self.data[feature].dropna(), bins=20, 
                       alpha=0.7, color='steelblue', edgecolor='black')
            
            ax.set_xlabel(feature, fontsize=9)
            ax.set_ylabel('Frequency', fontsize=9)
            ax.set_title(f'{feature}', fontweight='bold', fontsize=10)
            ax.grid(alpha=0.3)
        
        # Hide extra subplots
        for idx in range(n_features, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            viz_path = output_path / 'feature_distributions.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {viz_path}")
            plt.close()
        else:
            plt.show()
    
    def visualize_cluster_proportions(self, output_dir: str = None):
        """
        Visualize cluster distribution
        
        Args:
            output_dir: Directory to save plot
        """
        if 'cluster' not in self.data.columns:
            logger.warning("No cluster column found, skipping cluster visualization")
            return
        
        logger.info("Visualizing cluster proportions...")
        
        # Get proportions
        proportions = self.data['cluster'].value_counts(normalize=True).sort_index()
        counts = self.data['cluster'].value_counts().sort_index()
        
        # Plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart
        x = np.arange(len(proportions))
        ax1.bar(x, proportions.values, alpha=0.8, color='steelblue', edgecolor='black')
        ax1.set_xlabel('Cluster', fontsize=12)
        ax1.set_ylabel('Proportion', fontsize=12)
        ax1.set_title('Cluster Distribution (Proportions)', fontsize=13, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(proportions.index)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add percentage labels
        for i, val in enumerate(proportions.values):
            ax1.text(i, val + 0.01, f'{val*100:.1f}%', ha='center', fontsize=9)
        
        # Pie chart
        ax2.pie(counts.values, labels=[f'Cluster {i}' for i in counts.index],
               autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
        ax2.set_title(f'Cluster Distribution ({len(self.data)} students)', 
                     fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            viz_path = output_path / 'cluster_distribution.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {viz_path}")
            plt.close()
        else:
            plt.show()
    
    def visualize_correlation_matrix(self, features: List[str], output_dir: str = None):
        """
        Visualize correlation matrix for selected features
        
        Args:
            features: List of features
            output_dir: Directory to save plot
        """
        logger.info("Creating correlation heatmap...")
        
        # Select available features
        available_features = [f for f in features if f in self.data.columns]
        
        if len(available_features) < 2:
            logger.warning("Not enough features for correlation matrix")
            return
        
        # Calculate correlation
        corr_matrix = self.data[available_features].corr()
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   ax=ax)
        ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            viz_path = output_path / 'correlation_matrix.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {viz_path}")
            plt.close()
        else:
            plt.show()
    
    def process_pipeline(self, real_path: str, features: List[str], 
                        output_dir: str, **kwargs):
        """
        Run full visualization pipeline
        
        Args:
            real_path: Path to clustered data
            features: List of features to visualize
            output_dir: Output directory
            **kwargs: Additional arguments (ignored for compatibility)
        """
        logger.info("="*70)
        logger.info("VISUALIZATION PIPELINE")
        logger.info("="*70)
        
        # Load data
        self.load_data(real_path)
        
        # Visualize distributions
        self.visualize_distributions(features, output_dir)
        
        # Visualize cluster proportions
        self.visualize_cluster_proportions(output_dir)
        
        # Correlation matrix
        self.visualize_correlation_matrix(features, output_dir)
        
        logger.info("\n✅ Visualization pipeline completed")
        
        return {}


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    visualizer = ComparisonVisualizer()
    visualizer.process_pipeline(
        real_path='../outputs/optimal_clusters/real_students_with_clusters.csv',
        features=['mean_module_grade', 'total_events', 'viewed', 
                 'submitted', 'created', 'module_count'],
        output_dir='../outputs/comparison'
    )
