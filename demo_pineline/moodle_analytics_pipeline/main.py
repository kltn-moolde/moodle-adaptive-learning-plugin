#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle Analytics Pipeline - Main Entry Point
=============================================
Complete end-to-end pipeline: Feature Extraction → Clustering → Simulation → Comparison
"""

import logging
from pathlib import Path
from core import (
    FeatureExtractor,
    ClusteringAnalyzer,
    DataSimulator,
    ComparisonVisualizer,
    ClusterComparison
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
    Complete analytics pipeline
    
    Pipeline flow:
    1. Feature Extraction: Extract và normalize features từ raw data
    2. Clustering Analysis: Phân cụm học sinh
    3. Data Simulation: Simulate dựa trên cluster statistics
    4. Comparison: So sánh real vs simulated data
    """
    
    def __init__(self, base_output_dir: str = 'outputs'):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directories
        self.feature_dir = self.base_output_dir / 'features'
        self.clustering_dir = self.base_output_dir / 'clustering'
        self.simulation_dir = self.base_output_dir / 'simulation'
        self.comparison_dir = self.base_output_dir / 'comparison'
        self.cluster_comparison_dir = self.base_output_dir / 'cluster_comparison'
        
        # Components
        self.feature_extractor = FeatureExtractor()
        self.clustering_analyzer = ClusteringAnalyzer()
        self.data_simulator = None  # Initialize later
        self.comparison_visualizer = ComparisonVisualizer()
        self.cluster_comparison = ClusterComparison()
        
    def run_full_pipeline(self, 
                         grades_path: str,
                         logs_path: str,
                         n_clusters: int = None,
                         n_simulated_students: int = 100,
                         simulation_noise: float = 0.1):
        """
        Run complete pipeline từ đầu đến cuối
        
        Args:
            grades_path: Path to grades CSV file
            logs_path: Path to logs CSV file
            n_clusters: Number of clusters (None = auto-detect)
            n_simulated_students: Number of students to simulate
            simulation_noise: Noise level for simulation (0-1)
        """
        logger.info("\n" + "="*80)
        logger.info("MOODLE ANALYTICS PIPELINE - FULL EXECUTION")
        logger.info("="*80)
        
        # ========== PHASE 1: FEATURE EXTRACTION ==========
        logger.info("\n📊 PHASE 1: Feature Extraction")
        logger.info("-"*80)
        
        features_scaled = self.feature_extractor.process_pipeline(
            grades_path=grades_path,
            logs_path=logs_path,
            output_dir=str(self.feature_dir)
        )
        
        # ========== PHASE 2: CLUSTERING ANALYSIS ==========
        logger.info("\n🎯 PHASE 2: Clustering Analysis")
        logger.info("-"*80)
        
        clustered_data, cluster_stats = self.clustering_analyzer.process_pipeline(
            features_path=str(self.feature_dir / 'features_scaled.json'),
            output_dir=str(self.clustering_dir),
            n_clusters=n_clusters,
            find_optimal=(n_clusters is None)
        )
        
        # ========== PHASE 3: DATA SIMULATION ==========
        logger.info("\n🔮 PHASE 3: Data Simulation")
        logger.info("-"*80)
        
        self.data_simulator = DataSimulator(
            cluster_stats_path=str(self.clustering_dir / 'cluster_statistics.json')
        )
        
        simulated_data = self.data_simulator.process_pipeline(
            n_students=n_simulated_students,
            output_dir=str(self.simulation_dir),
            noise_level=simulation_noise
        )
        
        # ========== PHASE 4: COMPARISON & VISUALIZATION ==========
        logger.info("\n📈 PHASE 4: Comparison & Visualization")
        logger.info("-"*80)
        
        # Get common features for comparison
        common_features = [col for col in clustered_data.columns 
                          if col in simulated_data.columns and col != 'userid']
        common_features = common_features[:15]  # Limit to top 15
        
        self.comparison_visualizer.process_pipeline(
            real_path=str(self.clustering_dir / 'clustered_students.csv'),
            simulated_path=str(self.simulation_dir / 'simulated_students.csv'),
            features=common_features,
            output_dir=str(self.comparison_dir)
        )
        
        # ========== PHASE 5: CLUSTER COMPARISON ==========
        logger.info("\n🔍 PHASE 5: Cluster Comparison Analysis")
        logger.info("-"*80)
        
        # Get number of clusters from clustered data
        n_clusters = clustered_data['cluster'].nunique()
        
        cluster_metrics = self.cluster_comparison.process_pipeline(
            real_path=str(self.clustering_dir / 'clustered_students.csv'),
            simulated_path=str(self.simulation_dir / 'simulated_students.csv'),
            n_clusters=n_clusters,
            output_dir=str(self.cluster_comparison_dir),
            features=common_features
        )
        
        # ========== PIPELINE COMPLETE ==========
        logger.info("\n" + "="*80)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        
        logger.info(f"\n📁 Output directories:")
        logger.info(f"  Features:           {self.feature_dir}")
        logger.info(f"  Clustering:         {self.clustering_dir}")
        logger.info(f"  Simulation:         {self.simulation_dir}")
        logger.info(f"  Comparison:         {self.comparison_dir}")
        logger.info(f"  Cluster Analysis:   {self.cluster_comparison_dir}")
        
        # Print similarity score
        if 'overall_similarity_score' in cluster_metrics:
            score_info = cluster_metrics['overall_similarity_score']
            logger.info(f"\n🎯 Overall Similarity Score: {score_info['score']:.2f}% (Grade: {score_info['grade']})")
            logger.info(f"   {score_info['interpretation']}")
        
        return {
            'features': features_scaled,
            'clustered_data': clustered_data,
            'cluster_stats': cluster_stats,
            'simulated_data': simulated_data,
            'cluster_comparison_metrics': cluster_metrics
        }


def main():
    """Main entry point"""
    
    # Initialize pipeline
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs')
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv',
        n_clusters=None,  # Auto-detect optimal K
        n_simulated_students=150,
        simulation_noise=0.15
    )
    
    print("\n" + "="*80)
    print("📊 PIPELINE SUMMARY")
    print("="*80)
    print(f"Real students:       {len(results['clustered_data'])}")
    print(f"Simulated students:  {len(results['simulated_data'])}")
    print(f"Number of clusters:  {results['clustered_data']['cluster'].nunique()}")
    print(f"Features extracted:  {len(results['features'].columns) - 1}")
    
    # Similarity metrics
    if 'cluster_comparison_metrics' in results:
        metrics = results['cluster_comparison_metrics']
        if 'overall_similarity_score' in metrics:
            score_info = metrics['overall_similarity_score']
            print(f"\n🎯 SIMILARITY ANALYSIS")
            print(f"Overall Score:       {score_info['score']:.2f}%")
            print(f"Grade:               {score_info['grade']}")
            print(f"Quality:             {score_info['interpretation']}")
    
    print("\n✅ All outputs saved to 'outputs/' directory")
    print("="*80)


if __name__ == '__main__':
    main()
