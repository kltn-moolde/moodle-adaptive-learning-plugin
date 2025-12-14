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
    GMMDataGenerator,
    ValidationMetrics,
    ComparisonVisualizer,
    ClusterProfiler
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
    Complete KMeans + GMM-based analytics pipeline
    
    Pipeline flow:
    1. Feature Extraction: Extract và normalize features từ raw data
    2. Feature Selection: Chọn features tối ưu (variance + correlation filtering)
    3. Optimal Clustering: Tìm số cụm tối ưu với KMeans + Voting (Elbow, Silhouette, Davies-Bouldin)
    4. GMM Data Generation: Sinh data synthetic từ GMM per cluster
    5. Validation: Validate similarity giữa real và synthetic (KS test, correlation, chi-square)
    6. Visualization & Comparison: Tổng hợp và so sánh kết quả
    """
    
    def __init__(self, base_output_dir: str = 'outputs'):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directories
        self.feature_dir = self.base_output_dir / 'features'
        self.feature_selection_dir = self.base_output_dir / 'feature_selection'
        self.optimal_clusters_dir = self.base_output_dir / 'optimal_clusters'
        self.gmm_generation_dir = self.base_output_dir / 'gmm_generation'
        self.validation_dir = self.base_output_dir / 'validation'
        self.comparison_dir = self.base_output_dir / 'comparison'
        self.cluster_profiling_dir = self.base_output_dir / 'cluster_profiling'
        
        # Components
        self.feature_extractor = FeatureExtractor()
        self.feature_selector = FeatureSelector()
        self.cluster_finder = OptimalClusterFinder()
        self.gmm_generator = GMMDataGenerator()
        self.validator = ValidationMetrics()
        self.comparison_visualizer = ComparisonVisualizer()
        self.cluster_profiler = None  # Initialize on demand
        
    def run_full_pipeline(self, 
                         grades_path: str,
                         logs_path: str,
                         n_synthetic_students: int = 100,
                         variance_threshold: float = 0.01,
                         correlation_threshold: float = 0.95,
                         max_features: int = None,
                         k_range: range = range(2, 11),
                         enable_llm_profiling: bool = True,
                         llm_provider: str = 'gemini'):
        """
        Run complete GMM-based pipeline từ đầu đến cuối
        
        Args:
            grades_path: Path to grades CSV file
            logs_path: Path to logs CSV file
            n_synthetic_students: Number of synthetic students to generate
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
        
        # ========== PHASE 4: GMM DATA GENERATION ==========
        logger.info("\n🔮 PHASE 4: GMM Data Generation (from KMeans clusters)")
        logger.info("-"*80)
        
        self.gmm_generator = GMMDataGenerator(optimal_kmeans=optimal_kmeans)
        
        synthetic_data = self.gmm_generator.process_pipeline(
            features_path=str(self.feature_dir / 'features_scaled.json'),
            selected_features=selected_features,
            optimal_k=optimal_k,
            n_synthetic=n_synthetic_students,
            output_dir=str(self.gmm_generation_dir),
            random_state=42
        )
        
        # ========== PHASE 5: VALIDATION ==========
        logger.info("\n✅ PHASE 5: Validation (Real vs Synthetic)")
        logger.info("-"*80)
        
        # Save real data with clusters for comparison
        real_data_with_clusters = features_scaled.copy()
        real_data_with_clusters['cluster'] = self.gmm_generator.real_data['cluster']
        real_path = self.gmm_generation_dir / 'real_students_with_clusters.csv'
        real_data_with_clusters.to_csv(real_path, index=False)
        
        validation_results = self.validator.process_pipeline(
            real_path=str(real_path),
            synthetic_path=str(self.gmm_generation_dir / 'synthetic_students_gmm.csv'),
            features=selected_features,
            output_dir=str(self.validation_dir)
        )
        
        # ========== PHASE 6: ADDITIONAL COMPARISON ==========
        logger.info("\n📈 PHASE 6: Additional Comparison & Visualization")
        logger.info("-"*80)
        
        # Use comparison visualizer for additional plots
        try:
            self.comparison_visualizer.process_pipeline(
                real_path=str(real_path),
                simulated_path=str(self.gmm_generation_dir / 'synthetic_students_gmm.csv'),
                features=selected_features[:15],  # Top 15 features
                output_dir=str(self.comparison_dir)
            )
        except Exception as e:
            logger.warning(f"Additional comparison failed: {e}")
        
        # ========== PHASE 7: CLUSTER PROFILING (LLM-POWERED) ==========
        if enable_llm_profiling:
            logger.info("\n🤖 PHASE 7: Cluster Profiling with AI")
            logger.info("-"*80)
            
            try:
                # Initialize profiler
                self.cluster_profiler = ClusterProfiler(llm_provider=llm_provider)
                
                # Load real data with clusters
                import pandas as pd
                real_clustered = pd.read_csv(
                    self.gmm_generation_dir / 'real_students_with_clusters.csv'
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
            logger.info("\n⏭️ PHASE 7: Cluster Profiling (Skipped)")
        
        # ========== PIPELINE COMPLETE ==========
        logger.info("\n" + "="*80)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        
        logger.info(f"\n📁 Output directories:")
        logger.info(f"  Features:           {self.feature_dir}")
        logger.info(f"  Feature Selection:  {self.feature_selection_dir}")
        logger.info(f"  Optimal Clusters:   {self.optimal_clusters_dir}")
        logger.info(f"  GMM Generation:     {self.gmm_generation_dir}")
        logger.info(f"  Validation:         {self.validation_dir}")
        logger.info(f"  Comparison:         {self.comparison_dir}")
        if enable_llm_profiling:
            logger.info(f"  Cluster Profiling:  {self.cluster_profiling_dir}")
        
        # Print quality score
        if 'overall_quality_score' in validation_results:
            score_info = validation_results['overall_quality_score']
            logger.info(f"\n🎯 Overall Quality Score: {score_info['score']:.1f}% (Grade: {score_info['grade']})")
            logger.info(f"   {score_info['interpretation']}")
        
        return {
            'features': features_scaled,
            'selected_features': selected_features,
            'optimal_k': optimal_k,
            'real_data': self.gmm_generator.real_data,
            'synthetic_data': synthetic_data,
            'validation_results': validation_results
        }


def main():
    """Main entry point - GMM-based pipeline"""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / 'data'

    # Initialize pipeline
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs')
    
    # Run full GMM-based pipeline
    results = pipeline.run_full_pipeline(
        grades_path=str(data_dir / 'udk_moodle_grades_course_670.csv'),
        logs_path=str(data_dir / 'udk_moodle_log_course_670.csv'),
        n_synthetic_students=5000,
        variance_threshold=0.01,
        correlation_threshold=0.95,
        max_features=15,
        k_range=range(2, 11)
    )
    
    print("\n" + "="*80)
    print("📊 PIPELINE SUMMARY (GMM-BASED)")
    print("="*80)
    print(f"Real students:        {len(results['real_data'])}")
    print(f"Synthetic students:   {len(results['synthetic_data'])}")
    print(f"Optimal clusters (k): {results['optimal_k']}")
    print(f"Features extracted:   {len(results['features'].columns) - 1}")
    print(f"Features selected:    {len(results['selected_features'])}")
    
    # Quality metrics
    if 'validation_results' in results:
        val_results = results['validation_results']
        if 'overall_quality_score' in val_results:
            score_info = val_results['overall_quality_score']
            print(f"\n🎯 QUALITY ANALYSIS")
            print(f"Overall Score:        {score_info['score']:.1f}%")
            print(f"Grade:                {score_info['grade']}")
            print(f"Quality:              {score_info['interpretation']}")
        
        if 'overall_metrics' in val_results:
            metrics = val_results['overall_metrics']
            print(f"\nKS Tests Passed:      {metrics['ks_tests_passed']}/{metrics['total_features_tested']} ({metrics['ks_pass_rate']*100:.1f}%)")
    
    print("\n✅ All outputs saved to 'outputs/' directory")
    print("="*80)


if __name__ == '__main__':
    main()
