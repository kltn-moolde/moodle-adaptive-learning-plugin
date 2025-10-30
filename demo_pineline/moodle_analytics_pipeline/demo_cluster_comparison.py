#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Cluster Comparison Demo
==================================
Demonstrates how to use ClusterComparison module independently
"""

from core import ClusterComparison
import json


def demo_cluster_comparison():
    """Demo cluster comparison với existing data"""
    
    print("\n" + "="*80)
    print("CLUSTER COMPARISON DEMO")
    print("="*80)
    
    # Initialize
    comparison = ClusterComparison()
    
    # Run comparison
    print("\n🔍 Running cluster comparison analysis...")
    metrics = comparison.process_pipeline(
        real_path='outputs/clustering/clustered_students.csv',
        simulated_path='outputs/simulation/simulated_students.csv',
        n_clusters=5,  # Adjust based on your data
        output_dir='outputs/cluster_comparison'
    )
    
    # Display results
    print("\n" + "="*80)
    print("📊 COMPARISON RESULTS")
    print("="*80)
    
    if 'overall_similarity_score' in metrics:
        overall = metrics['overall_similarity_score']
        print(f"\n🎯 Overall Similarity Score: {overall['score']:.2f}%")
        print(f"   Grade: {overall['grade']}")
        print(f"   {overall['interpretation']}")
    
    print("\n" + "-"*80)
    print("DETAILED METRICS")
    print("-"*80)
    
    if 'silhouette_score' in metrics:
        sil = metrics['silhouette_score']
        print(f"\nSilhouette Score:")
        print(f"  Real:       {sil['real']:.4f}")
        print(f"  Simulated:  {sil['simulated']:.4f}")
        print(f"  Difference: {sil['difference']:.4f}")
    
    if 'davies_bouldin_index' in metrics:
        db = metrics['davies_bouldin_index']
        print(f"\nDavies-Bouldin Index:")
        print(f"  Real:       {db['real']:.4f}")
        print(f"  Simulated:  {db['simulated']:.4f}")
        print(f"  Difference: {db['difference']:.4f}")
    
    if 'calinski_harabasz_score' in metrics:
        ch = metrics['calinski_harabasz_score']
        print(f"\nCalinski-Harabasz Score:")
        print(f"  Real:       {ch['real']:.2f}")
        print(f"  Simulated:  {ch['simulated']:.2f}")
        print(f"  Difference: {ch['difference']:.2f}")
    
    if 'cluster_center_distance' in metrics:
        center = metrics['cluster_center_distance']
        print(f"\nCluster Center Distance:")
        print(f"  Mean:  {center['mean_distance']:.4f}")
        print(f"  Std:   {center['std_distance']:.4f}")
        print(f"  Range: [{center['min_distance']:.4f}, {center['max_distance']:.4f}]")
    
    if 'cluster_size_distribution' in metrics:
        dist = metrics['cluster_size_distribution']
        print(f"\nCluster Size Distribution:")
        print(f"  Wasserstein Distance: {dist['wasserstein_distance']:.4f}")
        print(f"  Real Distribution:      {dist['real_distribution']}")
        print(f"  Simulated Distribution: {dist['simulated_distribution']}")
    
    if 'feature_distribution_similarity' in metrics:
        feat = metrics['feature_distribution_similarity']
        print(f"\nFeature Distribution Similarity:")
        print(f"  Mean Distance: {feat['mean_distance']:.4f}")
        print(f"  Top Features:")
        for f in feat['features'][:5]:
            print(f"    {f['feature']}: {f['distance']:.4f}")
    
    print("\n" + "="*80)
    print("📁 OUTPUTS")
    print("="*80)
    print("\nGenerated files in 'outputs/cluster_comparison/':")
    print("  ✅ cluster_pca_comparison.png         - Side-by-side PCA plots")
    print("  ✅ cluster_sizes_comparison.png       - Cluster size bar chart")
    print("  ✅ cluster_profiles_comparison.png    - Radar charts")
    print("  ✅ feature_distributions_comparison.png - Feature histograms")
    print("  ✅ similarity_metrics_dashboard.png   - Metrics dashboard")
    print("  ✅ cluster_comparison_report.json     - Complete metrics (JSON)")
    print("  ✅ cluster_comparison_report.txt      - Human-readable report")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETED")
    print("="*80)
    
    return metrics


def interpret_similarity_score(score: float):
    """Interpret và explain similarity score"""
    
    print("\n" + "="*80)
    print("📖 SIMILARITY SCORE INTERPRETATION GUIDE")
    print("="*80)
    
    print(f"\nYour Score: {score:.2f}%\n")
    
    print("Score Ranges:")
    print("  90-100%: Excellent - Simulated data very closely matches real data")
    print("           → Perfect for privacy-preserving data sharing")
    print("           → Suitable for model training and testing")
    
    print("\n  80-89%:  Very Good - Simulated data closely resembles real data")
    print("           → Good for most research purposes")
    print("           → Minor differences in edge cases")
    
    print("\n  70-79%:  Good - Simulated data has similar patterns")
    print("           → Acceptable for many applications")
    print("           → May need tuning for critical use cases")
    
    print("\n  60-69%:  Fair - Some similarity present")
    print("           → Consider adjusting simulation parameters")
    print("           → Review cluster statistics")
    
    print("\n  50-59%:  Moderate - Partial resemblance")
    print("           → Increase simulation noise or adjust parameters")
    print("           → Check feature extraction quality")
    
    print("\n  <50%:    Poor - Significant differences")
    print("           → Review entire pipeline")
    print("           → May need more real data or better features")
    
    print("\n" + "="*80)


def compare_different_noise_levels():
    """Demo: Compare simulations with different noise levels"""
    
    print("\n" + "="*80)
    print("NOISE LEVEL COMPARISON DEMO")
    print("="*80)
    
    print("\nThis would compare multiple simulations with different noise levels:")
    print("  - Low noise (0.05):   More similar to real data")
    print("  - Medium noise (0.1):  Balanced similarity and diversity")
    print("  - High noise (0.2):    More diverse but less similar")
    
    print("\nTo run this, generate multiple simulations with different noise levels")
    print("and compare each one using ClusterComparison.")


if __name__ == '__main__':
    import sys
    
    print("\n" + "#"*80)
    print("# CLUSTER COMPARISON STANDALONE DEMO")
    print("#"*80)
    
    # Check if data exists
    import os
    if not os.path.exists('outputs/clustering/clustered_students.csv'):
        print("\n❌ Error: Real data not found!")
        print("   Please run main pipeline first: python main.py")
        sys.exit(1)
    
    if not os.path.exists('outputs/simulation/simulated_students.csv'):
        print("\n❌ Error: Simulated data not found!")
        print("   Please run main pipeline first: python main.py")
        sys.exit(1)
    
    # Run demo
    metrics = demo_cluster_comparison()
    
    # Interpret score
    if 'overall_similarity_score' in metrics:
        score = metrics['overall_similarity_score']['score']
        interpret_similarity_score(score)
    
    # Additional info
    print("\n" + "="*80)
    print("💡 NEXT STEPS")
    print("="*80)
    print("\n1. Review the generated visualizations in 'outputs/cluster_comparison/'")
    print("2. Read the detailed report: cluster_comparison_report.txt")
    print("3. If similarity score is low, try:")
    print("   - Adjusting simulation noise level")
    print("   - Using more features")
    print("   - Increasing number of simulated students")
    print("4. Use the JSON report for programmatic analysis")
    
    print("\n" + "#"*80)
