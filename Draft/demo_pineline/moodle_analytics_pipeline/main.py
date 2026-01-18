#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle Analytics Pipeline - Main Entry Point (KMeans + GMM-based)
==================================================================
Complete end-to-end pipeline:
Feature Extraction → Feature Selection → Optimal Clustering (KMeans + Voting) → GMM Generation → Validation
"""

import logging
from pathlib import Path
from core import (
    FeatureExtractor,
    FeatureSelector,
    OptimalClusterFinder,
    ComparisonVisualizer,
    ClusterProfiler,
    ClusteringVisualizer
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MoodleAnalyticsPipeline:
    """
    Streamlined KMeans analytics pipeline (no GMM)
    
    Pipeline flow:
    1. Feature Extraction: Extract và normalize features từ raw data
    2. Feature Selection: Chọn features tối ưu (variance + correlation filtering)
    3. Optimal Clustering: Tìm số cụm tối ưu với KMeans + Voting (Elbow, Silhouette, Davies-Bouldin)
    4. Clustering Visualization: Visualize before/after clustering
    5. Cluster Profiling with AI: Mô tả và diễn giải từng cụm
    6. Visualization: Biểu đồ và trực quan hóa các cụm và đặc trưng
    """
    
    def __init__(self, base_output_dir: str = 'outputs'):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directories
        self.feature_dir = self.base_output_dir / 'features'
        self.feature_selection_dir = self.base_output_dir / 'feature_selection'
        self.optimal_clusters_dir = self.base_output_dir / 'optimal_clusters'
        self.clustering_viz_dir = self.base_output_dir / 'clustering_visualization'
        self.comparison_dir = self.base_output_dir / 'comparison'
        self.cluster_profiling_dir = self.base_output_dir / 'cluster_profiling'
        
        # Components
        self.feature_extractor = FeatureExtractor()
        self.feature_selector = FeatureSelector()
        self.cluster_finder = OptimalClusterFinder()
        self.clustering_visualizer = ClusteringVisualizer(reduction_method='pca')
        self.comparison_visualizer = ComparisonVisualizer()
        self.cluster_profiler = None  # Initialize on demand
        
    def run_full_pipeline(self, 
                         grades_path: str,
                         logs_path: str,
                         variance_threshold: float = 0.01,
                         correlation_threshold: float = 0.95,
                         max_features: int = None,
                         k_range: range = range(2, 11),
                         enable_llm_profiling: bool = True,
                         llm_provider: str = 'gemini',
                         reduction_method: str = 'pca'):
        """
        Run complete GMM-based pipeline từ đầu đến cuối
        
        Args:
            grades_path: Path to grades CSV file
            logs_path: Path to logs CSV file
            variance_threshold: Variance threshold for feature selection (0-1)
            correlation_threshold: Correlation threshold for feature selection (0-1)
            max_features: Maximum features to select (None = no limit)
            k_range: Range of k values to test for optimal clustering
        """
        logger.info("\n" + "="*80)
        logger.info("MOODLE ANALYTICS PIPELINE - GMM-BASED EXECUTION")
        logger.info("="*80)
        
        # ========== PHASE 1: FEATURE EXTRACTION ==========
        logger.info("\n📊 PHASE 1: Feature Extraction")
        logger.info("-"*80)
        
        features_scaled = self.feature_extractor.process_pipeline(
            grades_path=grades_path,
            logs_path=logs_path,
            output_dir=str(self.feature_dir)
        )
        
        # ========== PHASE 2: FEATURE SELECTION ==========
        logger.info("\n🔍 PHASE 2: Feature Selection (Variance + Correlation Filtering)")
        logger.info("-"*80)
        
        self.feature_selector = FeatureSelector(
            variance_threshold=variance_threshold,
            correlation_threshold=correlation_threshold
        )
        
        selected_features = self.feature_selector.process_pipeline(
            df=features_scaled,
            output_dir=str(self.feature_selection_dir),
            max_features=max_features
        )
        
        # ========== PHASE 3: OPTIMAL CLUSTERING ==========
        logger.info("\n🎯 PHASE 3: Finding Optimal Number of Clusters (KMeans + Voting)")
        logger.info("-"*80)
        
        # Prepare data for clustering (selected features only)
        X_selected = features_scaled[selected_features].values
        
        self.cluster_finder = OptimalClusterFinder(k_range=k_range)
        optimal_k, optimal_kmeans = self.cluster_finder.process_pipeline(
            X=X_selected,
            output_dir=str(self.optimal_clusters_dir),
            random_state=42
        )
        
        # ========== PHASE 4: CLUSTERING VISUALIZATION (NEW) ==========
        logger.info("\n📈 PHASE 4: Clustering Visualization (Before/After)")
        logger.info("-"*80)
        
        self.clustering_visualizer = ClusteringVisualizer(
            reduction_method=reduction_method,
            random_state=42
        )
        
        viz_results = self.clustering_visualizer.process_pipeline(
            X=X_selected,
            labels=optimal_kmeans.labels_,
            output_dir=str(self.clustering_viz_dir),
            n_clusters=optimal_k
        )
        
        # ========== PHASE 5: PREPARE DATA WITH CLUSTERS ==========
        # Prepare real data with assigned clusters
        real_data_with_clusters = features_scaled.copy()
        real_data_with_clusters['cluster'] = optimal_kmeans.labels_
        real_path = self.optimal_clusters_dir / 'real_students_with_clusters.csv'
        real_data_with_clusters.to_csv(real_path, index=False)
        
        # ========== PHASE 6: CLUSTER PROFILING (LLM-POWERED) ==========
        if enable_llm_profiling:
            logger.info("\n🤖 PHASE 6: Cluster Profiling with AI")
            logger.info("-"*80)
            
            try:
                # Initialize profiler
                self.cluster_profiler = ClusterProfiler(llm_provider=llm_provider)
                
                # Load real data with clusters
                import pandas as pd
                real_clustered = pd.read_csv(
                    real_path
                )
                
                # Profile clusters
                cluster_profiles = self.cluster_profiler.profile_all_clusters(
                    df=real_clustered,
                    cluster_col='cluster'
                )
                
                # Save profiles
                self.cluster_profiler.save_profiles(str(self.cluster_profiling_dir))
                
                logger.info(f"\n✓ Generated AI-powered profiles for {len(cluster_profiles['cluster_stats'])} clusters")
                
            except Exception as e:
                logger.warning(f"Cluster profiling failed: {e}")
                logger.warning("Continuing without LLM profiling...")
        else:
            logger.info("\n⏭️ PHASE 6: Cluster Profiling (Skipped)")
            
        # ========== PHASE 7: ADDITIONAL VISUALIZATION ==========
        logger.info("\n📊 PHASE 7: Additional Visualization")
        logger.info("-"*80)
        try:
            # Visualize distributions and cluster separation
            self.comparison_visualizer.process_pipeline(
                real_path=str(real_path),
                features=selected_features[:15],
                output_dir=str(self.comparison_dir)
            )
        except Exception as e:
            logger.warning(f"Visualization phase encountered an issue: {e}")

        # ========== PIPELINE COMPLETE ==========
        logger.info("\n" + "="*80)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        
        logger.info(f"\n📁 Output directories:")
        logger.info(f"  Features:              {self.feature_dir}")
        logger.info(f"  Feature Selection:     {self.feature_selection_dir}")
        logger.info(f"  Optimal Clusters:      {self.optimal_clusters_dir}")
        logger.info(f"  Clustering Viz:        {self.clustering_viz_dir}")
        logger.info(f"  Additional Viz:        {self.comparison_dir}")
        if enable_llm_profiling:
            logger.info(f"  Cluster Profiling:     {self.cluster_profiling_dir}")
        
        return {
            'features': features_scaled,
            'selected_features': selected_features,
            'optimal_k': optimal_k,
            'real_data': real_data_with_clusters,
            'visualization': viz_results
        }


def main():
    """Main entry point - KMeans-only pipeline"""
    # Initialize pipeline
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs')
    
    # Run full GMM-based pipeline
    results = pipeline.run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.csv',
        logs_path='../data/udk_moodle_log_course_670.csv',
        variance_threshold=0.01,
        correlation_threshold=0.95,
        max_features=15,
        k_range=range(2, 11),
        reduction_method='pca'  # or 'tsne'
    )
    
    print("\n" + "="*80)
    print("📊 PIPELINE SUMMARY (KMeans)")
    print("="*80)
    print(f"Real students:        {len(results['real_data'])}")
    print(f"Optimal clusters (k): {results['optimal_k']}")
    print(f"Features extracted:   {len(results['features'].columns) - 1}")
    print(f"Features selected:    {len(results['selected_features'])}")
    print(f"\nVisualization method: {results['visualization']['reduction_method'].upper()}")
    
    print("\n✅ All outputs saved to 'outputs/' directory")
    print("="*80)
    print(f"Real students:        {len(results['real_data'])}")
    print(f"Optimal clusters (k): {results['optimal_k']}")
    print(f"Features extracted:   {len(results['features'].columns) - 1}")
    print(f"Features selected:    {len(results['selected_features'])}")
    
    print("\n✅ All outputs saved to 'outputs/' directory")
    print("="*80)


if __name__ == '__main__':
    main()
