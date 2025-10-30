#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Comparison Module
=========================
So sánh chi tiết clustering giữa real data và simulated data
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist
from scipy.stats import wasserstein_distance

logger = logging.getLogger(__name__)


class ClusterComparison:
    """So sánh clustering giữa real và simulated data"""
    
    def __init__(self):
        self.real_data = None
        self.simulated_data = None
        self.real_clusters = None
        self.simulated_clusters = None
        self.real_kmeans = None
        self.simulated_kmeans = None
        self.comparison_metrics = {}
        
    def load_data(self, real_path: str, simulated_path: str):
        """Load real và simulated data"""
        logger.info(f"Loading real data from: {real_path}")
        self.real_data = pd.read_csv(real_path)
        
        logger.info(f"Loading simulated data from: {simulated_path}")
        self.simulated_data = pd.read_csv(simulated_path)
        
        logger.info(f"Real data: {len(self.real_data)} students")
        logger.info(f"Simulated data: {len(self.simulated_data)} students")
        
    def perform_clustering(self, n_clusters: int, features: List[str] = None):
        """
        Thực hiện clustering trên cả real và simulated data
        
        Args:
            n_clusters: Số clusters
            features: List features để cluster (None = dùng tất cả trừ userid và cluster)
        """
        logger.info(f"\n🎯 Performing clustering with K={n_clusters}")
        
        # Get features
        if features is None:
            exclude_cols = ['userid', 'cluster', 'cluster_new']
            features = [col for col in self.real_data.columns 
                       if col not in exclude_cols and not col.startswith('cluster')]
        
        # Lấy common features giữa real và simulated (và chỉ numeric columns)
        common_features = []
        for f in features:
            if (f in self.real_data.columns and 
                f in self.simulated_data.columns and
                pd.api.types.is_numeric_dtype(self.real_data[f]) and
                pd.api.types.is_numeric_dtype(self.simulated_data[f])):
                common_features.append(f)
        
        logger.info(f"Using {len(common_features)} common features")
        
        # Prepare data - ensure numeric
        X_real = self.real_data[common_features].fillna(0).astype(float)
        X_simulated = self.simulated_data[common_features].fillna(0).astype(float)
        
        # Clustering real data
        logger.info("Clustering real data...")
        self.real_kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.real_clusters = self.real_kmeans.fit_predict(X_real)
        
        # Clustering simulated data
        logger.info("Clustering simulated data...")
        self.simulated_kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.simulated_clusters = self.simulated_kmeans.fit_predict(X_simulated)
        
        # Add cluster assignments
        self.real_data['cluster_new'] = self.real_clusters
        self.simulated_data['cluster_new'] = self.simulated_clusters
        
        return common_features
    
    def calculate_similarity_metrics(self, features: List[str]) -> Dict:
        """
        Tính các metrics đánh giá độ tương đồng
        
        Returns:
            Dictionary chứa các metrics
        """
        logger.info("\n📊 Calculating similarity metrics...")
        
        X_real = self.real_data[features].fillna(0)
        X_simulated = self.simulated_data[features].fillna(0)
        
        metrics = {}
        
        # 1. Cluster Quality Metrics
        logger.info("Computing cluster quality metrics...")
        
        # Silhouette Score (cao hơn = tốt hơn, range: -1 to 1)
        try:
            real_silhouette = silhouette_score(X_real, self.real_clusters)
            sim_silhouette = silhouette_score(X_simulated, self.simulated_clusters)
            metrics['silhouette_score'] = {
                'real': float(real_silhouette),
                'simulated': float(sim_silhouette),
                'difference': float(abs(real_silhouette - sim_silhouette)),
                'interpretation': 'Lower difference = Better similarity'
            }
        except Exception as e:
            logger.warning(f"Could not compute silhouette score: {e}")
        
        # Davies-Bouldin Index (thấp hơn = tốt hơn)
        try:
            real_db = davies_bouldin_score(X_real, self.real_clusters)
            sim_db = davies_bouldin_score(X_simulated, self.simulated_clusters)
            metrics['davies_bouldin_index'] = {
                'real': float(real_db),
                'simulated': float(sim_db),
                'difference': float(abs(real_db - sim_db)),
                'interpretation': 'Lower difference = Better similarity'
            }
        except Exception as e:
            logger.warning(f"Could not compute Davies-Bouldin: {e}")
        
        # Calinski-Harabasz Score (cao hơn = tốt hơn)
        try:
            real_ch = calinski_harabasz_score(X_real, self.real_clusters)
            sim_ch = calinski_harabasz_score(X_simulated, self.simulated_clusters)
            metrics['calinski_harabasz_score'] = {
                'real': float(real_ch),
                'simulated': float(sim_ch),
                'difference': float(abs(real_ch - sim_ch)),
                'interpretation': 'Lower difference = Better similarity'
            }
        except Exception as e:
            logger.warning(f"Could not compute Calinski-Harabasz: {e}")
        
        # 2. Cluster Center Distance
        logger.info("Computing cluster center similarity...")
        real_centers = self.real_kmeans.cluster_centers_
        sim_centers = self.simulated_kmeans.cluster_centers_
        
        # Euclidean distance giữa cluster centers
        center_distances = cdist(real_centers, sim_centers, metric='euclidean')
        min_distances = center_distances.min(axis=1)
        
        metrics['cluster_center_distance'] = {
            'mean_distance': float(min_distances.mean()),
            'std_distance': float(min_distances.std()),
            'max_distance': float(min_distances.max()),
            'min_distance': float(min_distances.min()),
            'interpretation': 'Lower distance = More similar cluster centers'
        }
        
        # 3. Cluster Size Distribution
        logger.info("Comparing cluster size distributions...")
        real_sizes = pd.Series(self.real_clusters).value_counts(normalize=True).sort_index()
        sim_sizes = pd.Series(self.simulated_clusters).value_counts(normalize=True).sort_index()
        
        # Wasserstein distance (Earth Mover's Distance)
        try:
            cluster_dist = wasserstein_distance(real_sizes.values, sim_sizes.values)
            metrics['cluster_size_distribution'] = {
                'real_distribution': real_sizes.to_dict(),
                'simulated_distribution': sim_sizes.to_dict(),
                'wasserstein_distance': float(cluster_dist),
                'interpretation': 'Lower distance = More similar distributions'
            }
        except Exception as e:
            logger.warning(f"Could not compute Wasserstein distance: {e}")
        
        # 4. Feature Distribution Similarity
        logger.info("Comparing feature distributions...")
        feature_similarities = []
        for feature in features[:10]:  # Top 10 features
            real_vals = X_real[feature].values
            sim_vals = X_simulated[feature].values
            
            # Wasserstein distance for each feature
            try:
                dist = wasserstein_distance(real_vals, sim_vals)
                feature_similarities.append({
                    'feature': feature,
                    'distance': float(dist)
                })
            except:
                pass
        
        metrics['feature_distribution_similarity'] = {
            'features': feature_similarities,
            'mean_distance': float(np.mean([f['distance'] for f in feature_similarities])),
            'interpretation': 'Lower distance = More similar feature distributions'
        }
        
        # 5. Overall Similarity Score (0-100, higher = better)
        logger.info("Computing overall similarity score...")
        
        # Normalize các metrics và tính weighted average
        scores = []
        
        if 'silhouette_score' in metrics:
            # Silhouette difference: 0-2 range → invert to 0-1 (0=identical)
            sil_score = 1 - (metrics['silhouette_score']['difference'] / 2)
            scores.append(sil_score * 100)
        
        if 'cluster_center_distance' in metrics:
            # Normalize by max possible distance (assume ~10)
            center_score = max(0, 1 - (metrics['cluster_center_distance']['mean_distance'] / 10))
            scores.append(center_score * 100)
        
        if 'cluster_size_distribution' in metrics:
            # Wasserstein: 0-1 range typically
            dist_score = max(0, 1 - metrics['cluster_size_distribution']['wasserstein_distance'])
            scores.append(dist_score * 100)
        
        if 'feature_distribution_similarity' in metrics:
            # Feature distances
            feat_score = max(0, 1 - (metrics['feature_distribution_similarity']['mean_distance'] / 5))
            scores.append(feat_score * 100)
        
        overall_score = np.mean(scores) if scores else 0
        
        metrics['overall_similarity_score'] = {
            'score': float(overall_score),
            'scale': '0-100 (higher = better)',
            'interpretation': self._interpret_similarity_score(overall_score),
            'grade': self._grade_similarity(overall_score)
        }
        
        self.comparison_metrics = metrics
        return metrics
    
    def _interpret_similarity_score(self, score: float) -> str:
        """Interpret similarity score"""
        if score >= 90:
            return "Excellent - Simulated data very closely matches real data"
        elif score >= 80:
            return "Very Good - Simulated data closely resembles real data"
        elif score >= 70:
            return "Good - Simulated data has similar patterns to real data"
        elif score >= 60:
            return "Fair - Simulated data shows some similarity to real data"
        elif score >= 50:
            return "Moderate - Simulated data partially resembles real data"
        else:
            return "Poor - Simulated data differs significantly from real data"
    
    def _grade_similarity(self, score: float) -> str:
        """Grade similarity score"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        else:
            return "D"
    
    def visualize_cluster_comparison(self, features: List[str], output_dir: str):
        """Tạo các biểu đồ so sánh clusters"""
        logger.info("\n📈 Creating cluster comparison visualizations...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Side-by-side PCA comparison
        self._plot_pca_comparison(features, output_path)
        
        # 2. Cluster size comparison
        self._plot_cluster_sizes(output_path)
        
        # 3. Cluster profile comparison (radar charts)
        self._plot_cluster_profiles(features, output_path)
        
        # 4. Feature distribution comparison
        self._plot_feature_distributions(features, output_path)
        
        # 5. Similarity metrics dashboard
        self._plot_metrics_dashboard(output_path)
        
        logger.info(f"✅ Visualizations saved to: {output_path}")
    
    def _plot_pca_comparison(self, features: List[str], output_path: Path):
        """PCA comparison side-by-side"""
        logger.info("Creating PCA comparison plot...")
        
        X_real = self.real_data[features].fillna(0)
        X_sim = self.simulated_data[features].fillna(0)
        
        # PCA
        pca = PCA(n_components=2, random_state=42)
        real_pca = pca.fit_transform(X_real)
        sim_pca = pca.transform(X_sim)
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Real data
        scatter1 = axes[0].scatter(real_pca[:, 0], real_pca[:, 1], 
                                   c=self.real_clusters, cmap='viridis',
                                   alpha=0.6, s=50)
        axes[0].set_title('Real Data Clusters (PCA)', fontsize=14, fontweight='bold')
        axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        plt.colorbar(scatter1, ax=axes[0], label='Cluster')
        
        # Simulated data
        scatter2 = axes[1].scatter(sim_pca[:, 0], sim_pca[:, 1],
                                   c=self.simulated_clusters, cmap='viridis',
                                   alpha=0.6, s=50)
        axes[1].set_title('Simulated Data Clusters (PCA)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        axes[1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        plt.colorbar(scatter2, ax=axes[1], label='Cluster')
        
        plt.tight_layout()
        plt.savefig(output_path / 'cluster_pca_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_cluster_sizes(self, output_path: Path):
        """So sánh cluster sizes"""
        logger.info("Creating cluster size comparison plot...")
        
        real_sizes = pd.Series(self.real_clusters).value_counts().sort_index()
        sim_sizes = pd.Series(self.simulated_clusters).value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(real_sizes))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, real_sizes.values, width, 
                       label='Real', color='steelblue', alpha=0.8)
        bars2 = ax.bar(x + width/2, sim_sizes.values, width,
                       label='Simulated', color='coral', alpha=0.8)
        
        ax.set_xlabel('Cluster', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
        ax.set_title('Cluster Size Comparison: Real vs Simulated', 
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f'Cluster {i}' for i in real_sizes.index])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path / 'cluster_sizes_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_cluster_profiles(self, features: List[str], output_path: Path):
        """Radar charts so sánh cluster profiles"""
        logger.info("Creating cluster profile comparison...")
        
        n_clusters = len(np.unique(self.real_clusters))
        top_features = features[:8]  # Top 8 features
        
        fig, axes = plt.subplots(2, (n_clusters + 1) // 2, 
                                figsize=(5 * ((n_clusters + 1) // 2), 10),
                                subplot_kw=dict(projection='polar'))
        axes = axes.flatten() if n_clusters > 1 else [axes]
        
        angles = np.linspace(0, 2 * np.pi, len(top_features), endpoint=False).tolist()
        angles += angles[:1]
        
        for cluster_id in range(n_clusters):
            ax = axes[cluster_id]
            
            # Real cluster profile
            real_mask = self.real_clusters == cluster_id
            real_profile = self.real_data.loc[real_mask, top_features].mean().values.tolist()
            real_profile += real_profile[:1]
            
            # Simulated cluster profile
            sim_mask = self.simulated_clusters == cluster_id
            sim_profile = self.simulated_data.loc[sim_mask, top_features].mean().values.tolist()
            sim_profile += sim_profile[:1]
            
            # Plot
            ax.plot(angles, real_profile, 'o-', linewidth=2, 
                   label='Real', color='steelblue')
            ax.fill(angles, real_profile, alpha=0.25, color='steelblue')
            
            ax.plot(angles, sim_profile, 'o-', linewidth=2,
                   label='Simulated', color='coral')
            ax.fill(angles, sim_profile, alpha=0.25, color='coral')
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(top_features, size=8)
            ax.set_ylim(0, 1)
            ax.set_title(f'Cluster {cluster_id}', fontweight='bold', pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            ax.grid(True)
        
        plt.suptitle('Cluster Profile Comparison: Real vs Simulated',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(output_path / 'cluster_profiles_comparison.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_feature_distributions(self, features: List[str], output_path: Path):
        """So sánh distribution của top features"""
        logger.info("Creating feature distribution comparison...")
        
        top_features = features[:6]
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, feature in enumerate(top_features):
            ax = axes[idx]
            
            real_vals = self.real_data[feature].fillna(0)
            sim_vals = self.simulated_data[feature].fillna(0)
            
            ax.hist(real_vals, bins=30, alpha=0.6, label='Real', 
                   color='steelblue', density=True)
            ax.hist(sim_vals, bins=30, alpha=0.6, label='Simulated',
                   color='coral', density=True)
            
            ax.set_xlabel(feature, fontsize=10)
            ax.set_ylabel('Density', fontsize=10)
            ax.set_title(f'{feature} Distribution', fontsize=11, fontweight='bold')
            ax.legend()
            ax.grid(alpha=0.3)
        
        plt.suptitle('Feature Distribution Comparison: Real vs Simulated',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path / 'feature_distributions_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_metrics_dashboard(self, output_path: Path):
        """Dashboard hiển thị similarity metrics"""
        logger.info("Creating metrics dashboard...")
        
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Overall Similarity Score (gauge)
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_similarity_gauge(ax1)
        
        # 2. Silhouette Score Comparison
        if 'silhouette_score' in self.comparison_metrics:
            ax2 = fig.add_subplot(gs[1, 0])
            self._plot_metric_comparison(ax2, 'silhouette_score', 'Silhouette Score')
        
        # 3. Davies-Bouldin Comparison
        if 'davies_bouldin_index' in self.comparison_metrics:
            ax3 = fig.add_subplot(gs[1, 1])
            self._plot_metric_comparison(ax3, 'davies_bouldin_index', 
                                        'Davies-Bouldin Index')
        
        # 4. Cluster Center Distance
        if 'cluster_center_distance' in self.comparison_metrics:
            ax4 = fig.add_subplot(gs[2, 0])
            data = self.comparison_metrics['cluster_center_distance']
            ax4.bar(['Mean Distance'], [data['mean_distance']], color='purple', alpha=0.7)
            ax4.set_ylabel('Euclidean Distance')
            ax4.set_title('Cluster Center Distance', fontweight='bold')
            ax4.grid(axis='y', alpha=0.3)
        
        # 5. Cluster Size Distribution Distance
        if 'cluster_size_distribution' in self.comparison_metrics:
            ax5 = fig.add_subplot(gs[2, 1])
            data = self.comparison_metrics['cluster_size_distribution']
            ax5.bar(['Wasserstein Distance'], [data['wasserstein_distance']], 
                   color='orange', alpha=0.7)
            ax5.set_ylabel('Distance')
            ax5.set_title('Cluster Size Distribution Distance', fontweight='bold')
            ax5.grid(axis='y', alpha=0.3)
        
        plt.suptitle('Cluster Similarity Metrics Dashboard', 
                     fontsize=16, fontweight='bold')
        plt.savefig(output_path / 'similarity_metrics_dashboard.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_similarity_gauge(self, ax):
        """Plot gauge meter cho overall similarity score"""
        if 'overall_similarity_score' not in self.comparison_metrics:
            return
        
        score = self.comparison_metrics['overall_similarity_score']['score']
        grade = self.comparison_metrics['overall_similarity_score']['grade']
        
        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        r = np.ones(100)
        
        # Color segments
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
        segments = [(0, 50), (50, 60), (60, 70), (70, 85), (85, 100)]
        
        for i, (start, end) in enumerate(segments):
            mask = (theta >= start * np.pi / 100) & (theta <= end * np.pi / 100)
            ax.fill_between(theta[mask], 0, r[mask], color=colors[i], alpha=0.3)
        
        # Needle
        needle_angle = score * np.pi / 100
        ax.plot([0, needle_angle], [0, 0.9], 'k-', linewidth=3)
        ax.plot(needle_angle, 0.9, 'ko', markersize=10)
        
        # Text
        ax.text(np.pi/2, -0.3, f'{score:.1f}%', 
               ha='center', va='center', fontsize=24, fontweight='bold')
        ax.text(np.pi/2, -0.5, f'Grade: {grade}',
               ha='center', va='center', fontsize=16)
        ax.text(np.pi/2, -0.7, 
               self.comparison_metrics['overall_similarity_score']['interpretation'],
               ha='center', va='center', fontsize=10, style='italic', wrap=True)
        
        ax.set_xlim(0, np.pi)
        ax.set_ylim(-0.8, 1.1)
        ax.axis('off')
        ax.set_title('Overall Similarity Score', fontsize=14, fontweight='bold', pad=20)
    
    def _plot_metric_comparison(self, ax, metric_key: str, title: str):
        """Bar chart so sánh 1 metric"""
        data = self.comparison_metrics[metric_key]
        
        values = [data['real'], data['simulated']]
        labels = ['Real', 'Simulated']
        colors = ['steelblue', 'coral']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7)
        ax.set_ylabel('Score')
        ax.set_title(title, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10)
    
    def save_comparison_report(self, output_dir: str):
        """Save detailed comparison report"""
        logger.info("\n💾 Saving comparison report...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # JSON report
        json_path = output_path / 'cluster_comparison_report.json'
        with open(json_path, 'w') as f:
            json.dump(self.comparison_metrics, f, indent=2)
        logger.info(f"✅ JSON report saved: {json_path}")
        
        # Text report
        txt_path = output_path / 'cluster_comparison_report.txt'
        with open(txt_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("CLUSTER COMPARISON REPORT\n")
            f.write("Real Data vs Simulated Data\n")
            f.write("="*80 + "\n\n")
            
            # Overall Score
            if 'overall_similarity_score' in self.comparison_metrics:
                overall = self.comparison_metrics['overall_similarity_score']
                f.write(f"OVERALL SIMILARITY SCORE: {overall['score']:.2f}%\n")
                f.write(f"Grade: {overall['grade']}\n")
                f.write(f"Interpretation: {overall['interpretation']}\n\n")
            
            f.write("-"*80 + "\n\n")
            
            # Detail metrics
            for key, value in self.comparison_metrics.items():
                if key == 'overall_similarity_score':
                    continue
                    
                f.write(f"{key.upper().replace('_', ' ')}\n")
                f.write("-" * 40 + "\n")
                
                if isinstance(value, dict):
                    for k, v in value.items():
                        if k != 'interpretation':
                            f.write(f"  {k}: {v}\n")
                    if 'interpretation' in value:
                        f.write(f"  → {value['interpretation']}\n")
                
                f.write("\n")
        
        logger.info(f"✅ Text report saved: {txt_path}")
    
    def process_pipeline(self, 
                        real_path: str,
                        simulated_path: str,
                        n_clusters: int,
                        output_dir: str,
                        features: List[str] = None) -> Dict:
        """
        Complete comparison pipeline
        
        Args:
            real_path: Path to real clustered data
            simulated_path: Path to simulated data
            n_clusters: Number of clusters
            output_dir: Output directory
            features: List of features (None = auto-detect)
        
        Returns:
            Comparison metrics dictionary
        """
        logger.info("\n" + "="*80)
        logger.info("CLUSTER COMPARISON PIPELINE")
        logger.info("="*80)
        
        # Load data
        self.load_data(real_path, simulated_path)
        
        # Perform clustering
        common_features = self.perform_clustering(n_clusters, features)
        
        # Calculate metrics
        metrics = self.calculate_similarity_metrics(common_features)
        
        # Visualizations
        self.visualize_cluster_comparison(common_features, output_dir)
        
        # Save report
        self.save_comparison_report(output_dir)
        
        logger.info("\n" + "="*80)
        logger.info("✅ CLUSTER COMPARISON COMPLETED")
        logger.info("="*80)
        
        return metrics


if __name__ == '__main__':
    # Test
    comparison = ClusterComparison()
    
    metrics = comparison.process_pipeline(
        real_path='../outputs/clustering/clustered_students.csv',
        simulated_path='../outputs/simulation/simulated_students.csv',
        n_clusters=5,
        output_dir='../outputs/cluster_comparison'
    )
    
    print("\n" + "="*80)
    print("COMPARISON METRICS")
    print("="*80)
    print(json.dumps(metrics, indent=2))
