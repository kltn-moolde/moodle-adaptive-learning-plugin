#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clustering Analyzer Module
==========================
Phân cụm học sinh và phân tích clusters
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score
import json
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ClusteringAnalyzer:
    """
    Phân cụm học sinh và visualize results
    
    Features:
    - Determine optimal K using Elbow + Silhouette
    - Perform KMeans clustering
    - Visualize clusters (PCA, radar charts)
    - Calculate cluster statistics
    """
    
    def __init__(self, n_clusters: int = None):
        self.n_clusters = n_clusters
        self.kmeans = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.cluster_stats = {}
        self.features_scaled = None
        self.X_scaled = None
        self.feature_cols = None
        
    def load_features(self, features_path: str) -> pd.DataFrame:
        """Load features from JSON file"""
        logger.info(f"Loading features from: {features_path}")
        
        with open(features_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        logger.info(f"✓ Loaded {len(df)} students")
        
        return df
    
    def prepare_data(self, df: pd.DataFrame, feature_selection: list = None):
        """
        Prepare data for clustering
        
        Args:
            df: Features DataFrame
            feature_selection: List of features to use (None = use important ones)
        """
        logger.info("Preparing data for clustering...")
        
        if feature_selection is None:
            # Select important features
            feature_selection = [
                'total_events',
                'mean_module_grade',
                'viewed',
                'submitted',
                'created',
                'module_count'
            ]
            
            # Add event features if exist
            event_cols = [col for col in df.columns if 'event' in col.lower()]
            feature_selection.extend(event_cols[:5])  # Top 5 event features
        
        # Filter existing columns
        self.feature_cols = [col for col in feature_selection if col in df.columns]
        
        logger.info(f"  Selected {len(self.feature_cols)} features")
        
        self.features_scaled = df
        X = df[self.feature_cols].values
        
        # Standardize
        self.X_scaled = self.scaler.fit_transform(X)
        
        return self.X_scaled
    
    def find_optimal_clusters(self, k_range: range = range(2, 8), output_dir: str = None):
        """
        Find optimal number of clusters using Elbow + Silhouette
        
        Args:
            k_range: Range of K to test
            output_dir: Directory to save plot
        """
        logger.info("Finding optimal number of clusters...")
        
        inertias = []
        silhouette_scores = []
        db_scores = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(self.X_scaled)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(self.X_scaled, labels))
            db_scores.append(davies_bouldin_score(self.X_scaled, labels))
        
        # Plot
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Elbow
        axes[0].plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Number of Clusters (k)', fontsize=12)
        axes[0].set_ylabel('Inertia', fontsize=12)
        axes[0].set_title('Elbow Method', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Silhouette
        axes[1].plot(k_range, silhouette_scores, 'go-', linewidth=2, markersize=8)
        axes[1].set_xlabel('Number of Clusters (k)', fontsize=12)
        axes[1].set_ylabel('Silhouette Score', fontsize=12)
        axes[1].set_title('Silhouette Analysis', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        # Davies-Bouldin
        axes[2].plot(k_range, db_scores, 'ro-', linewidth=2, markersize=8)
        axes[2].set_xlabel('Number of Clusters (k)', fontsize=12)
        axes[2].set_ylabel('Davies-Bouldin Score', fontsize=12)
        axes[2].set_title('Davies-Bouldin Index (lower is better)', 
                         fontsize=14, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'optimal_k_analysis.png', dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {output_path / 'optimal_k_analysis.png'}")
        
        plt.show()
        
        # Recommend optimal K
        optimal_k = k_range[np.argmax(silhouette_scores)]
        logger.info(f"✓ Recommended optimal K = {optimal_k}")
        
        return optimal_k
    
    def fit_clustering(self, n_clusters: int = None):
        """
        Perform KMeans clustering
        
        Args:
            n_clusters: Number of clusters (None = use initialized value)
        """
        if n_clusters:
            self.n_clusters = n_clusters
            
        logger.info(f"Performing KMeans clustering with k={self.n_clusters}...")
        
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=20)
        self.features_scaled['cluster'] = self.kmeans.fit_predict(self.X_scaled)
        
        # Calculate statistics
        self._calculate_cluster_stats()
        
        logger.info(f"✓ Clustering completed")
        
        return self.features_scaled['cluster']
    
    def _calculate_cluster_stats(self):
        """Calculate statistics for each cluster"""
        logger.info("Calculating cluster statistics...")
        
        self.cluster_stats = {}
        
        for i in range(self.n_clusters):
            cluster_data = self.features_scaled[self.features_scaled['cluster'] == i]
            
            stats = {
                'size': int(len(cluster_data)),
                'percentage': float(len(cluster_data) / len(self.features_scaled) * 100),
                'mean_grade': float(cluster_data['mean_module_grade'].mean()) 
                               if 'mean_module_grade' in cluster_data.columns else 0,
                'mean_events': float(cluster_data['total_events'].mean())
                                if 'total_events' in cluster_data.columns else 0,
                'feature_statistics': {}
            }
            
            # Feature statistics
            for col in self.feature_cols:
                if col in cluster_data.columns:
                    stats['feature_statistics'][col] = {
                        'mean': float(cluster_data[col].mean()),
                        'std': float(cluster_data[col].std()),
                        'min': float(cluster_data[col].min()),
                        'max': float(cluster_data[col].max())
                    }
            
            self.cluster_stats[f'cluster_{i}'] = stats
            
            logger.info(f"  Cluster {i}: {stats['size']} students "
                       f"({stats['percentage']:.1f}%)")
    
    def visualize_clusters(self, output_dir: str = None):
        """
        Visualize clusters using PCA
        
        Args:
            output_dir: Directory to save plots
        """
        logger.info("Visualizing clusters...")
        
        # PCA transformation
        X_pca = self.pca.fit_transform(self.X_scaled)
        
        # Create visualization DataFrame
        viz_df = pd.DataFrame({
            'PC1': X_pca[:, 0],
            'PC2': X_pca[:, 1],
            'Cluster': self.features_scaled['cluster'],
            'Grade': self.features_scaled.get('mean_module_grade', 0)
        })
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        # Plot 1: Clusters
        for i in range(self.n_clusters):
            cluster_data = viz_df[viz_df['Cluster'] == i]
            axes[0].scatter(cluster_data['PC1'], cluster_data['PC2'],
                           c=colors[i % len(colors)], label=f'Cluster {i}',
                           s=100, alpha=0.6, edgecolors='black', linewidth=1)
        
        axes[0].set_xlabel(f'PC1 ({self.pca.explained_variance_ratio_[0]*100:.1f}%)', 
                          fontsize=12)
        axes[0].set_ylabel(f'PC2 ({self.pca.explained_variance_ratio_[1]*100:.1f}%)', 
                          fontsize=12)
        axes[0].set_title('Student Clusters (PCA)', fontsize=14, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Grade heatmap
        scatter = axes[1].scatter(viz_df['PC1'], viz_df['PC2'],
                                 c=viz_df['Grade'], cmap='RdYlGn',
                                 s=100, alpha=0.6, edgecolors='black', linewidth=1)
        axes[1].set_xlabel(f'PC1 ({self.pca.explained_variance_ratio_[0]*100:.1f}%)', 
                          fontsize=12)
        axes[1].set_ylabel(f'PC2 ({self.pca.explained_variance_ratio_[1]*100:.1f}%)', 
                          fontsize=12)
        axes[1].set_title('Performance Heatmap', fontsize=14, fontweight='bold')
        plt.colorbar(scatter, ax=axes[1], label='Grade')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'cluster_visualization.png', 
                       dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {output_path / 'cluster_visualization.png'}")
        
        plt.show()
    
    def visualize_cluster_profiles(self, output_dir: str = None):
        """
        Visualize cluster profiles using radar charts
        
        Args:
            output_dir: Directory to save plot
        """
        logger.info("Creating cluster profile radar charts...")
        
        # Select features for radar chart
        profile_features = [col for col in self.feature_cols[:7]]
        
        # Calculate mean for each cluster
        cluster_profiles = {}
        for i in range(self.n_clusters):
            cluster_data = self.features_scaled[self.features_scaled['cluster'] == i]
            profile = cluster_data[profile_features].mean()
            cluster_profiles[f'Cluster {i}'] = profile
        
        profile_df = pd.DataFrame(cluster_profiles).T
        
        # Radar chart
        fig, axes = plt.subplots(1, self.n_clusters, 
                                figsize=(6*self.n_clusters, 5),
                                subplot_kw=dict(projection='polar'))
        
        if self.n_clusters == 1:
            axes = [axes]
        
        angles = np.linspace(0, 2 * np.pi, len(profile_features), endpoint=False).tolist()
        angles += angles[:1]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        for idx, (cluster_name, row) in enumerate(profile_df.iterrows()):
            values = row.tolist()
            values += values[:1]
            
            axes[idx].plot(angles, values, 'o-', linewidth=2, color=colors[idx % len(colors)])
            axes[idx].fill(angles, values, alpha=0.25, color=colors[idx % len(colors)])
            axes[idx].set_xticks(angles[:-1])
            axes[idx].set_xticklabels(profile_features, size=8)
            axes[idx].set_ylim(0, 1)
            
            cluster_id = int(cluster_name.split()[1])
            cluster_size = self.cluster_stats[f'cluster_{cluster_id}']['size']
            axes[idx].set_title(f'{cluster_name}\n({cluster_size} students)',
                              fontsize=12, fontweight='bold', pad=20)
            axes[idx].grid(True)
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'cluster_profiles.png', 
                       dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {output_path / 'cluster_profiles.png'}")
        
        plt.show()
    
    def save_results(self, output_dir: str):
        """
        Save clustering results
        
        Args:
            output_dir: Directory to save outputs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save clustered data
        clustered_path = output_path / 'clustered_students.csv'
        self.features_scaled.to_csv(clustered_path, index=False)
        logger.info(f"✓ Saved: {clustered_path}")
        
        # Save cluster statistics
        stats_path = output_path / 'cluster_statistics.json'
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.cluster_stats, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved: {stats_path}")
    
    def process_pipeline(self, features_path: str, output_dir: str, 
                        n_clusters: int = None, find_optimal: bool = True):
        """
        Run complete clustering pipeline
        
        Args:
            features_path: Path to features JSON
            output_dir: Directory to save outputs
            n_clusters: Number of clusters (None = find optimal)
            find_optimal: Whether to run optimal K analysis
        """
        logger.info("="*70)
        logger.info("CLUSTERING ANALYSIS PIPELINE")
        logger.info("="*70)
        
        # Load features
        df = self.load_features(features_path)
        
        # Prepare data
        self.prepare_data(df)
        
        # Find optimal K if needed
        if find_optimal and n_clusters is None:
            optimal_k = self.find_optimal_clusters(output_dir=output_dir)
            self.n_clusters = optimal_k
        elif n_clusters:
            self.n_clusters = n_clusters
        
        # Fit clustering
        self.fit_clustering()
        
        # Visualize
        self.visualize_clusters(output_dir)
        self.visualize_cluster_profiles(output_dir)
        
        # Save results
        self.save_results(output_dir)
        
        logger.info("="*70)
        logger.info("✅ CLUSTERING ANALYSIS COMPLETED")
        logger.info("="*70)
        
        return self.features_scaled, self.cluster_stats


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    analyzer = ClusteringAnalyzer()
    df, stats = analyzer.process_pipeline(
        features_path='../outputs/features/features_scaled.json',
        output_dir='../outputs/clustering',
        find_optimal=True
    )
    
    print(f"\n📊 Created {analyzer.n_clusters} clusters")
    print(f"✓ Silhouette Score: {silhouette_score(analyzer.X_scaled, df['cluster']):.3f}")
