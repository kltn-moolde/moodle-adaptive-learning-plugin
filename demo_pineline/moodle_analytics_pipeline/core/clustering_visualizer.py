#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clustering Visualization Module
================================
Visualize data before and after clustering with 2D scatter plots using PCA/t-SNE
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import logging

logger = logging.getLogger(__name__)


class ClusteringVisualizer:
    """
    Visualize clustering results in 2D space
    Shows before (all same color) and after (different colors per cluster)
    """
    
    def __init__(self, reduction_method='pca', random_state=42):
        """
        Initialize visualizer
        
        Args:
            reduction_method: 'pca' or 'tsne' for dimensionality reduction
            random_state: Random state for reproducibility
        """
        self.reduction_method = reduction_method
        self.random_state = random_state
        
    def reduce_dimensions(self, X, method='pca'):
        """
        Reduce data to 2D for visualization
        
        Args:
            X: Feature matrix (n_samples, n_features)
            method: 'pca' or 'tsne'
            
        Returns:
            X_2d: 2D representation (n_samples, 2)
        """
        if method == 'pca':
            reducer = PCA(n_components=2, random_state=self.random_state)
            X_2d = reducer.fit_transform(X)
            explained_var = reducer.explained_variance_ratio_
            logger.info(f"PCA explained variance: {explained_var[0]:.3f}, {explained_var[1]:.3f} (total: {sum(explained_var):.3f})")
        elif method == 'tsne':
            reducer = TSNE(n_components=2, random_state=self.random_state, perplexity=30, n_iter=1000)
            X_2d = reducer.fit_transform(X)
            logger.info("t-SNE dimensionality reduction completed")
        else:
            raise ValueError(f"Unknown reduction method: {method}")
            
        return X_2d
    
    def plot_before_after_clustering(self, X, labels, output_dir, n_clusters=6):
        """
        Create before/after clustering visualization
        
        Args:
            X: Feature matrix (n_samples, n_features)
            labels: Cluster labels (n_samples,)
            output_dir: Output directory path
            n_clusters: Number of clusters
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"\n📊 Creating Before/After Clustering Visualization ({self.reduction_method.upper()})")
        logger.info(f"  Data shape: {X.shape}")
        logger.info(f"  Number of clusters: {n_clusters}")
        
        # Reduce to 2D
        X_2d = self.reduce_dimensions(X, method=self.reduction_method)
        
        # Create figure with 2 subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Define colors
        before_color = '#808080'  # Gray for all points before clustering
        after_colors = sns.color_palette('husl', n_clusters)
        
        # ========== LEFT: BEFORE CLUSTERING ==========
        ax1 = axes[0]
        ax1.scatter(X_2d[:, 0], X_2d[:, 1], 
                   c=before_color, 
                   alpha=0.6, 
                   s=50,
                   edgecolors='white',
                   linewidth=0.5)
        
        ax1.set_title('Trước Phân Cụm\n(Tất cả sinh viên - chưa phân nhóm)', 
                     fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlabel(f'{self.reduction_method.upper()} Component 1', fontsize=11)
        ax1.set_ylabel(f'{self.reduction_method.upper()} Component 2', fontsize=11)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Add info text
        info_text = f'Tổng số sinh viên: {len(X_2d)}'
        ax1.text(0.02, 0.98, info_text,
                transform=ax1.transAxes,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                verticalalignment='top',
                fontsize=10)
        
        # ========== RIGHT: AFTER CLUSTERING ==========
        ax2 = axes[1]
        
        # Plot each cluster with different color
        for i in range(n_clusters):
            mask = labels == i
            cluster_points = X_2d[mask]
            
            ax2.scatter(cluster_points[:, 0], cluster_points[:, 1],
                       c=[after_colors[i]],
                       label=f'Cụm {i+1} (n={np.sum(mask)})',
                       alpha=0.7,
                       s=50,
                       edgecolors='white',
                       linewidth=0.5)
        
        ax2.set_title(f'Sau Phân Cụm K-Means\n({n_clusters} nhóm sinh viên)', 
                     fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel(f'{self.reduction_method.upper()} Component 1', fontsize=11)
        ax2.set_ylabel(f'{self.reduction_method.upper()} Component 2', fontsize=11)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Legend
        ax2.legend(loc='best', framealpha=0.9, fontsize=9)
        
        # Tight layout
        plt.tight_layout()
        
        # Save outputs
        png_path = output_dir / 'clustering_before_after.png'
        pdf_path = output_dir / 'clustering_before_after.pdf'
        
        plt.savefig(png_path, dpi=300, bbox_inches='tight')
        plt.savefig(pdf_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✓ Saved visualization:")
        logger.info(f"  PNG: {png_path}")
        logger.info(f"  PDF: {pdf_path}")
        
        return {
            'X_2d': X_2d,
            'png_path': str(png_path),
            'pdf_path': str(pdf_path),
            'reduction_method': self.reduction_method
        }
    
    def process_pipeline(self, X, labels, output_dir, n_clusters=6):
        """
        Main pipeline method for clustering visualization
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            output_dir: Output directory
            n_clusters: Number of clusters
            
        Returns:
            dict: Visualization results
        """
        return self.plot_before_after_clustering(
            X=X,
            labels=labels,
            output_dir=output_dir,
            n_clusters=n_clusters
        )
