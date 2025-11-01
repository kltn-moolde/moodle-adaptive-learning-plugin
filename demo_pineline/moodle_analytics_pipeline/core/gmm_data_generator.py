#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMM Data Generator Module (KMeans-based)
=========================================
Generate synthetic student data using Gaussian Mixture Model (GMM)
sampling from KMeans clusters - thay thế rule-based simulation
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class GMMDataGenerator:
    """
    Generate synthetic student data using GMM sampling from KMeans clusters
    
    Workflow:
    1. Load real features data (scaled)
    2. Use trained KMeans model to get clusters
    3. For each cluster, fit GMM and sample synthetic data
    4. Inverse transform to original scale
    5. Assign cluster labels
    6. Validate distribution similarity
    """
    
    def __init__(self, optimal_kmeans: KMeans = None):
        """
        Args:
            optimal_kmeans: Pre-trained KMeans model (if None, will train new one)
        """
        self.kmeans = optimal_kmeans
        self.scaler = StandardScaler()
        self.feature_names = []
        self.real_data = None
        self.synthetic_data = None
        self.cluster_mapping = {}  # Map cluster ID to quality label
        self.cluster_gmms = {}  # GMM for each cluster
        
    def load_real_data(self, features_path: str, 
                      selected_features: List[str] = None) -> pd.DataFrame:
        """
        Load real features data
        
        Args:
            features_path: Path to features JSON
            selected_features: List of features to use (None = use all numeric)
            
        Returns:
            DataFrame of real features
        """
        logger.info(f"Loading real data from: {features_path}")
        
        with open(features_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # Select features
        if selected_features:
            # Ensure all selected features exist
            available = [f for f in selected_features if f in df.columns]
            if len(available) < len(selected_features):
                missing = set(selected_features) - set(available)
                logger.warning(f"Missing features: {missing}")
            self.feature_names = available
        else:
            # Use all numeric features except userid
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            self.feature_names = [col for col in numeric_cols if col != 'userid']
        
        logger.info(f"✓ Loaded {len(df)} students with {len(self.feature_names)} features")
        
        self.real_data = df
        return df
    
    def fit_gmm(self, n_components: int, random_state: int = 42):
        """
        Fit KMeans và GMM cho mỗi cluster
        
        Args:
            n_components: Number of clusters (optimal k)
            random_state: Random seed
        """
        logger.info(f"Fitting KMeans with {n_components} clusters and GMM for each cluster...")
        
        # Prepare data
        X = self.real_data[self.feature_names].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Use pre-trained KMeans or fit new one
        if self.kmeans is None or self.kmeans.n_clusters != n_components:
            logger.info(f"  Training new KMeans with k={n_components}...")
            self.kmeans = KMeans(n_clusters=n_components, 
                                random_state=random_state, 
                                n_init=10)
            self.kmeans.fit(X_scaled)
        
        # Assign cluster labels to real data
        labels = self.kmeans.labels_
        self.real_data['cluster'] = labels
        
        logger.info(f"✓ KMeans fitted successfully")
        
        # Fit GMM for each cluster
        from sklearn.mixture import GaussianMixture
        for cluster_id in sorted(np.unique(labels)):
            cluster_mask = labels == cluster_id
            X_cluster = X_scaled[cluster_mask]
            
            # Check if cluster has enough samples for GMM
            if len(X_cluster) < 2:
                logger.warning(f"  ⚠ Cluster {cluster_id}: Only {len(X_cluster)} sample(s), using mean+std instead of GMM")
                # Store cluster statistics instead of GMM
                self.cluster_gmms[int(cluster_id)] = {
                    'type': 'stats',
                    'mean': X_cluster.mean(axis=0),
                    'std': np.ones(X_cluster.shape[1]) * 0.1,  # Small std for single sample
                    'data': X_cluster
                }
            else:
                # Fit GMM with 1 component per cluster (captures cluster distribution)
                gmm = GaussianMixture(n_components=1, 
                                     covariance_type='full',
                                     random_state=random_state)
                gmm.fit(X_cluster)
                self.cluster_gmms[int(cluster_id)] = {
                    'type': 'gmm',
                    'model': gmm
                }
                
                logger.info(f"  ✓ Cluster {cluster_id}: {len(X_cluster)} samples, GMM fitted")
        
        # Create cluster mapping (based on mean feature values)
        self._create_cluster_mapping()
    
    def _create_cluster_mapping(self):
        """
        Tạo mapping từ cluster ID sang quality label (giỏi/khá/yếu)
        Dựa trên mean values của features trong mỗi cluster
        """
        logger.info("Creating cluster quality mapping...")
        
        cluster_means = {}
        for cluster_id in sorted(self.real_data['cluster'].unique()):
            cluster_df = self.real_data[self.real_data['cluster'] == cluster_id]
            mean_vals = cluster_df[self.feature_names].mean().mean()  # Overall mean
            cluster_means[cluster_id] = mean_vals
        
        # Sort clusters by mean (descending)
        sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
        
        # Assign labels
        n_clusters = len(sorted_clusters)
        quality_labels = []
        
        if n_clusters == 3:
            quality_labels = ['giỏi', 'khá', 'yếu']
        elif n_clusters == 4:
            quality_labels = ['giỏi', 'khá', 'trung bình', 'yếu']
        elif n_clusters == 5:
            quality_labels = ['xuất sắc', 'giỏi', 'khá', 'trung bình', 'yếu']
        else:
            # Generic labels
            quality_labels = [f'nhóm_{i+1}' for i in range(n_clusters)]
        
        for i, (cluster_id, _) in enumerate(sorted_clusters):
            self.cluster_mapping[cluster_id] = quality_labels[i] if i < len(quality_labels) else f'nhóm_{i+1}'
        
        logger.info(f"  Cluster mapping:")
        for cluster_id, label in self.cluster_mapping.items():
            count = len(self.real_data[self.real_data['cluster'] == cluster_id])
            pct = count / len(self.real_data) * 100
            logger.info(f"    Cluster {cluster_id} → '{label}' ({count} students, {pct:.1f}%)")
    
    def generate_synthetic_data(self, n_samples: int, 
                                random_state: int = 42) -> pd.DataFrame:
        """
        Generate synthetic data bằng cách sample từ GMM của mỗi cluster
        
        Args:
            n_samples: Number of synthetic students to generate
            random_state: Random seed
            
        Returns:
            DataFrame of synthetic students
        """
        logger.info(f"Generating {n_samples} synthetic students...")
        
        np.random.seed(random_state)
        
        # Tính số samples cho mỗi cluster dựa trên distribution của real data
        cluster_counts = self.real_data['cluster'].value_counts(normalize=True)
        samples_per_cluster = {int(k): int(v * n_samples) for k, v in cluster_counts.items()}
        
        # Adjust để đảm bảo tổng = n_samples
        total = sum(samples_per_cluster.values())
        if total < n_samples:
            # Add remaining to largest cluster
            largest_cluster = max(samples_per_cluster, key=samples_per_cluster.get)
            samples_per_cluster[largest_cluster] += (n_samples - total)
        
        logger.info(f"  Sampling from each cluster:")
        for cluster_id, count in samples_per_cluster.items():
            logger.info(f"    Cluster {cluster_id}: {count} samples")
        
        # Generate samples from each cluster's GMM or stats
        all_samples = []
        all_labels = []
        
        for cluster_id, n_cluster_samples in samples_per_cluster.items():
            if n_cluster_samples == 0:
                continue
            
            cluster_info = self.cluster_gmms[cluster_id]
            
            if cluster_info['type'] == 'gmm':
                # Sample from GMM
                gmm = cluster_info['model']
                X_cluster_scaled, _ = gmm.sample(n_cluster_samples)
            else:
                # Sample from Gaussian distribution with mean+std
                mean = cluster_info['mean']
                std = cluster_info['std']
                X_cluster_scaled = np.random.normal(
                    loc=mean, 
                    scale=std, 
                    size=(n_cluster_samples, len(mean))
                )
            
            all_samples.append(X_cluster_scaled)
            all_labels.extend([cluster_id] * n_cluster_samples)
        
        # Combine all samples
        X_synth_scaled = np.vstack(all_samples)
        y_synth = np.array(all_labels)
        
        # Inverse transform to original scale
        X_synth = self.scaler.inverse_transform(X_synth_scaled)
        
        # Clip values to reasonable ranges [0, 1] assuming normalized features
        X_synth = np.clip(X_synth, 0, 1)
        
        # Create DataFrame
        synthetic_df = pd.DataFrame(X_synth, columns=self.feature_names)
        
        # Add userid (synthetic IDs starting from 100000)
        synthetic_df['userid'] = range(100000, 100000 + len(synthetic_df))
        
        # Add cluster labels
        synthetic_df['cluster'] = y_synth
        
        # Add quality labels
        synthetic_df['group'] = synthetic_df['cluster'].map(self.cluster_mapping)
        
        self.synthetic_data = synthetic_df
        
        logger.info(f"✓ Generated {len(synthetic_df)} synthetic students")
        logger.info(f"  Cluster distribution:")
        for cluster_id in sorted(synthetic_df['cluster'].unique()):
            count = len(synthetic_df[synthetic_df['cluster'] == cluster_id])
            pct = count / len(synthetic_df) * 100
            quality = self.cluster_mapping.get(int(cluster_id), 'unknown')
            logger.info(f"    Cluster {cluster_id} ('{quality}'): {count} ({pct:.1f}%)")
        
        return synthetic_df
    
    def visualize_comparison(self, output_dir: str):
        """
        Visualize real vs synthetic data comparison
        
        Args:
            output_dir: Directory to save plots
        """
        logger.info("Creating real vs synthetic comparison visualizations...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # ========== Plot 1: PCA Visualization ==========
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Real data PCA
        X_real = self.real_data[self.feature_names].values
        pca = PCA(n_components=2, random_state=42)
        X_real_pca = pca.fit_transform(X_real)
        
        scatter_real = axes[0].scatter(X_real_pca[:, 0], X_real_pca[:, 1],
                                      c=self.real_data['cluster'], cmap='viridis',
                                      alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontweight='bold')
        axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontweight='bold')
        axes[0].set_title('Real Data - Cluster Distribution (PCA)', 
                         fontweight='bold', fontsize=13)
        axes[0].grid(alpha=0.3)
        plt.colorbar(scatter_real, ax=axes[0], label='Cluster')
        
        # Synthetic data PCA
        X_synth = self.synthetic_data[self.feature_names].values
        X_synth_pca = pca.transform(X_synth)
        
        scatter_synth = axes[1].scatter(X_synth_pca[:, 0], X_synth_pca[:, 1],
                                       c=self.synthetic_data['cluster'], cmap='viridis',
                                       alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        axes[1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontweight='bold')
        axes[1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontweight='bold')
        axes[1].set_title('Synthetic Data - Cluster Distribution (PCA)', 
                         fontweight='bold', fontsize=13)
        axes[1].grid(alpha=0.3)
        plt.colorbar(scatter_synth, ax=axes[1], label='Cluster')
        
        plt.suptitle('Real vs Synthetic Data - PCA Comparison', 
                    fontsize=15, fontweight='bold')
        plt.tight_layout()
        
        viz_path = output_path / 'real_vs_synthetic_pca.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  ✓ Saved: {viz_path}")
        
        # ========== Plot 2: Feature Distributions (Top 6 features) ==========
        top_features = self.feature_names[:min(6, len(self.feature_names))]
        n_cols = 3
        n_rows = 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 8))
        axes = axes.flatten()
        
        for i, feature in enumerate(top_features):
            ax = axes[i]
            
            # Real distribution
            ax.hist(self.real_data[feature].dropna(), bins=30, alpha=0.5, 
                   label='Real', color='blue', density=True)
            
            # Synthetic distribution
            ax.hist(self.synthetic_data[feature].dropna(), bins=30, alpha=0.5,
                   label='Synthetic', color='red', density=True)
            
            ax.set_xlabel(feature, fontweight='bold', fontsize=9)
            ax.set_ylabel('Density', fontweight='bold', fontsize=9)
            ax.set_title(f'{feature}', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)
        
        # Hide unused subplots
        for i in range(len(top_features), len(axes)):
            axes[i].axis('off')
        
        plt.suptitle('Feature Distribution Comparison - Real vs Synthetic', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        viz_path = output_path / 'feature_distributions_comparison.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  ✓ Saved: {viz_path}")
        
        # ========== Plot 3: Correlation Matrix Comparison ==========
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Real correlation
        corr_real = self.real_data[self.feature_names].corr()
        sns.heatmap(corr_real, annot=False, cmap='coolwarm', center=0,
                   vmin=-1, vmax=1, ax=axes[0], square=True,
                   cbar_kws={'label': 'Correlation'})
        axes[0].set_title('Real Data - Correlation Matrix', 
                         fontweight='bold', fontsize=13)
        
        # Synthetic correlation
        corr_synth = self.synthetic_data[self.feature_names].corr()
        sns.heatmap(corr_synth, annot=False, cmap='coolwarm', center=0,
                   vmin=-1, vmax=1, ax=axes[1], square=True,
                   cbar_kws={'label': 'Correlation'})
        axes[1].set_title('Synthetic Data - Correlation Matrix', 
                         fontweight='bold', fontsize=13)
        
        plt.suptitle('Correlation Matrix Comparison', 
                    fontsize=15, fontweight='bold')
        plt.tight_layout()
        
        viz_path = output_path / 'correlation_comparison.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  ✓ Saved: {viz_path}")
    
    def save_synthetic_data(self, output_dir: str):
        """
        Save synthetic data and metadata
        
        Args:
            output_dir: Directory to save outputs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save CSV
        csv_path = output_path / 'synthetic_students_gmm.csv'
        self.synthetic_data.to_csv(csv_path, index=False)
        logger.info(f"  ✓ Saved: {csv_path}")
        
        # Save JSON
        json_path = output_path / 'synthetic_students_gmm.json'
        self.synthetic_data.to_json(json_path, orient='records', 
                                    force_ascii=False, indent=2)
        logger.info(f"  ✓ Saved: {json_path}")
        
        # Save summary
        summary = {
            'total_synthetic_students': int(len(self.synthetic_data)),
            'total_real_students': int(len(self.real_data)),
            'n_features': len(self.feature_names),
            'features_used': self.feature_names,
            'kmeans_parameters': {
                'n_clusters': int(self.kmeans.n_clusters),
                'n_iter': int(self.kmeans.n_iter_)
            },
            'gmm_clusters': {
                str(k): v['type'] for k, v in self.cluster_gmms.items()
            },
            'cluster_distribution': {},
            # Convert cluster_mapping keys to int for JSON serialization
            'cluster_mapping': {int(k): v for k, v in self.cluster_mapping.items()}
        }
        
        for cluster_id in sorted(self.synthetic_data['cluster'].unique()):
            count = len(self.synthetic_data[self.synthetic_data['cluster'] == cluster_id])
            # Convert numpy int64 to Python int for JSON serialization
            cluster_id_int = int(cluster_id)
            summary['cluster_distribution'][f'cluster_{cluster_id_int}'] = {
                'count': int(count),
                'percentage': float(count / len(self.synthetic_data) * 100),
                'quality_label': self.cluster_mapping.get(cluster_id_int, 'unknown')
            }
        
        summary_path = output_path / 'gmm_generation_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ Saved: {summary_path}")
    
    def process_pipeline(self, features_path: str, selected_features: List[str],
                        optimal_k: int, n_synthetic: int, 
                        output_dir: str, random_state: int = 42) -> pd.DataFrame:
        """
        Complete GMM generation pipeline
        
        Args:
            features_path: Path to real features JSON
            selected_features: List of selected features
            optimal_k: Optimal number of clusters
            n_synthetic: Number of synthetic students to generate
            output_dir: Directory to save outputs
            random_state: Random seed
            
        Returns:
            DataFrame of synthetic students
        """
        logger.info("="*70)
        logger.info("GMM DATA GENERATION PIPELINE")
        logger.info("="*70)
        
        # Load real data
        self.load_real_data(features_path, selected_features)
        
        # Fit GMM
        self.fit_gmm(n_components=optimal_k, random_state=random_state)
        
        # Generate synthetic data
        synthetic_df = self.generate_synthetic_data(n_synthetic, random_state)
        
        # Visualize
        self.visualize_comparison(output_dir)
        
        # Save
        self.save_synthetic_data(output_dir)
        
        logger.info("="*70)
        logger.info("✅ GMM GENERATION COMPLETED")
        logger.info("="*70)
        
        return synthetic_df


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    generator = GMMDataGenerator()
    
    synthetic = generator.process_pipeline(
        features_path='../outputs/features/features_scaled.json',
        selected_features=None,  # Use all
        optimal_k=3,
        n_synthetic=200,
        output_dir='../outputs/gmm_generation',
        random_state=42
    )
    
    print(f"\n✅ Generated {len(synthetic)} synthetic students")
    print(synthetic.head())
