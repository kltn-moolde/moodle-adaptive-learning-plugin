#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Usage - GMM-Based Pipeline
==================================
Demonstrates how to use the GMM-based Moodle Analytics Pipeline
"""

import logging
from core import (
    MoodleAnalyticsPipeline,
    FeatureExtractor,
    FeatureSelector,
    OptimalClusterFinder,
    GMMDataGenerator,
    ValidationMetrics
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_full_pipeline():
    """
    Example 1: Run full pipeline với default parameters
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Full Pipeline (Default Parameters)")
    print("="*80)
    
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs/example1')
    
    results = pipeline.run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv'
    )
    
    print(f"\n✅ Completed!")
    print(f"   Optimal K: {results['optimal_k']}")
    print(f"   Quality Score: {results['validation_results']['overall_quality_score']['score']:.1f}%")


def example_2_custom_parameters():
    """
    Example 2: Custom parameters
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Parameters")
    print("="*80)
    
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs/example2')
    
    results = pipeline.run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv',
        n_synthetic_students=300,         # More synthetic students
        variance_threshold=0.02,          # Stricter variance filtering
        correlation_threshold=0.90,       # Stricter correlation filtering
        max_features=10,                  # Limit to top 10 features
        k_range=range(3, 8)              # Test k=3 to k=7 only
    )
    
    print(f"\n✅ Completed!")
    print(f"   Features selected: {len(results['selected_features'])}")
    print(f"   Optimal K: {results['optimal_k']}")
    print(f"   Quality Score: {results['validation_results']['overall_quality_score']['score']:.1f}%")


def example_3_step_by_step():
    """
    Example 3: Step-by-step execution (manual control)
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Step-by-Step Execution")
    print("="*80)
    
    import pandas as pd
    import json
    
    output_dir = 'outputs/example3'
    
    # Step 1: Feature Extraction
    print("\n🔵 Step 1: Feature Extraction")
    extractor = FeatureExtractor()
    features_scaled = extractor.process_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv',
        output_dir=f'{output_dir}/features'
    )
    print(f"   ✓ Extracted {len(features_scaled.columns)-1} features")
    
    # Step 2: Feature Selection
    print("\n🔵 Step 2: Feature Selection")
    selector = FeatureSelector(variance_threshold=0.01, correlation_threshold=0.95)
    selected_features = selector.process_pipeline(
        df=features_scaled,
        output_dir=f'{output_dir}/feature_selection',
        max_features=15
    )
    print(f"   ✓ Selected {len(selected_features)} features")
    
    # Step 3: Optimal Clustering
    print("\n🔵 Step 3: Finding Optimal Clusters")
    X_selected = features_scaled[selected_features].values
    finder = OptimalClusterFinder(k_range=range(2, 11))
    optimal_k, optimal_gmm = finder.process_pipeline(
        X=X_selected,
        output_dir=f'{output_dir}/optimal_clusters',
        random_state=42
    )
    print(f"   ✓ Optimal K: {optimal_k}")
    
    # Step 4: GMM Data Generation
    print("\n🔵 Step 4: GMM Data Generation")
    generator = GMMDataGenerator(optimal_gmm=optimal_gmm)
    synthetic_data = generator.process_pipeline(
        features_path=f'{output_dir}/features/features_scaled.json',
        selected_features=selected_features,
        optimal_k=optimal_k,
        n_synthetic=200,
        output_dir=f'{output_dir}/gmm_generation',
        random_state=42
    )
    print(f"   ✓ Generated {len(synthetic_data)} synthetic students")
    
    # Step 5: Validation
    print("\n🔵 Step 5: Validation")
    
    # Save real data with clusters
    real_data_with_clusters = features_scaled.copy()
    real_data_with_clusters['cluster'] = generator.real_data['cluster']
    real_path = f'{output_dir}/gmm_generation/real_students_with_clusters.csv'
    real_data_with_clusters.to_csv(real_path, index=False)
    
    validator = ValidationMetrics()
    validation_results = validator.process_pipeline(
        real_path=real_path,
        synthetic_path=f'{output_dir}/gmm_generation/synthetic_students_gmm.csv',
        features=selected_features,
        output_dir=f'{output_dir}/validation'
    )
    
    quality_score = validation_results['overall_quality_score']['score']
    quality_grade = validation_results['overall_quality_score']['grade']
    
    print(f"   ✓ Quality Score: {quality_score:.1f}% ({quality_grade})")
    
    print("\n✅ All steps completed!")


def example_4_analyze_results():
    """
    Example 4: Analyze and print detailed results
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Analyze Results")
    print("="*80)
    
    import json
    
    # Load validation report
    with open('outputs/example1/validation/validation_report.json', 'r') as f:
        validation = json.load(f)
    
    print("\n📊 VALIDATION SUMMARY")
    print("-"*80)
    
    # Overall metrics
    if 'overall_metrics' in validation:
        metrics = validation['overall_metrics']
        print(f"Features Tested:       {metrics['total_features_tested']}")
        print(f"KS Tests Passed:       {metrics['ks_tests_passed']} ({metrics['ks_pass_rate']*100:.1f}%)")
        print(f"Avg Mean Error:        {metrics['avg_mean_error']:.4f}")
        print(f"Avg Std Error:         {metrics['avg_std_error']:.4f}")
    
    # Quality score
    if 'overall_quality_score' in validation:
        score_info = validation['overall_quality_score']
        print(f"\n🎯 QUALITY SCORE: {score_info['score']:.1f}%")
        print(f"   Grade: {score_info['grade']}")
        print(f"   {score_info['interpretation']}")
    
    # Detailed KS tests
    print("\n📋 DETAILED KS TEST RESULTS")
    print("-"*80)
    for i, ks_test in enumerate(validation.get('ks_tests', [])[:10], 1):
        status = "✓" if ks_test['similar'] else "✗"
        print(f"{i:2d}. {ks_test['feature']:30s} p={ks_test['p_value']:.4f}  {status}")
    
    # Correlation comparison
    if 'correlation_comparison' in validation:
        corr = validation['correlation_comparison']
        print(f"\n🔗 CORRELATION SIMILARITY: {corr['similarity_score']:.3f} ({corr['interpretation']})")
    
    # Cluster comparison
    if 'cluster_comparison' in validation:
        cluster = validation['cluster_comparison']
        print(f"\n👥 CLUSTER DISTRIBUTION COMPARISON")
        print(f"   Chi-square p-value: {cluster['p_value']:.4f}")
        print(f"   Similar: {cluster['similar']}")


def example_5_generate_more_synthetic():
    """
    Example 5: Generate thêm synthetic data từ trained GMM
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Generate More Synthetic Data")
    print("="*80)
    
    import json
    import pandas as pd
    from sklearn.mixture import GaussianMixture
    from pathlib import Path
    
    # Load previous results
    with open('outputs/example1/gmm_generation/gmm_generation_summary.json', 'r') as f:
        summary = json.load(f)
    
    with open('outputs/example1/features/features_scaled.json', 'r') as f:
        features = pd.DataFrame(json.load(f))
    
    selected_features = summary['features_used']
    optimal_k = summary['gmm_parameters']['n_components']
    
    print(f"Previous generation:")
    print(f"  Features: {len(selected_features)}")
    print(f"  Optimal K: {optimal_k}")
    
    # Re-train GMM (or load if you saved the model)
    print(f"\n🔄 Re-training GMM...")
    X = features[selected_features].values
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    gmm = GaussianMixture(n_components=optimal_k, random_state=42)
    gmm.fit(X_scaled)
    
    # Generate NEW synthetic data
    print(f"🔮 Generating 500 NEW synthetic students...")
    generator = GMMDataGenerator(optimal_gmm=gmm)
    generator.load_real_data(
        'outputs/example1/features/features_scaled.json',
        selected_features
    )
    generator.gmm = gmm
    generator.scaler = scaler
    generator._create_cluster_mapping()
    
    new_synthetic = generator.generate_synthetic_data(n_samples=500, random_state=123)
    
    # Save
    output_dir = Path('outputs/example5')
    output_dir.mkdir(parents=True, exist_ok=True)
    new_synthetic.to_csv(output_dir / 'new_synthetic_500.csv', index=False)
    
    print(f"   ✓ Generated {len(new_synthetic)} new synthetic students")
    print(f"   ✓ Saved to outputs/example5/new_synthetic_500.csv")


if __name__ == '__main__':
    # Uncomment to run examples
    
    # Run all examples
    example_1_full_pipeline()
    # example_2_custom_parameters()
    # example_3_step_by_step()
    # example_4_analyze_results()
    # example_5_generate_more_synthetic()
    
    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETED")
    print("="*80)
