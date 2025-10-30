#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Usage of Moodle Analytics Pipeline
==========================================
Demonstrates different ways to use the pipeline
"""

from main import MoodleAnalyticsPipeline
from core import (FeatureExtractor, ClusteringAnalyzer, DataSimulator, 
                  ComparisonVisualizer, ClusterComparison)


def example_1_full_pipeline():
    """Example 1: Run complete pipeline with default settings"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Full Pipeline (Auto-detect K)")
    print("="*80)
    
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs/example1')
    
    results = pipeline.run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv',
        n_clusters=None,  # Auto-detect
        n_simulated_students=100,
        simulation_noise=0.1
    )
    
    print(f"\n✅ Processed {len(results['clustered_data'])} students")
    print(f"✅ Generated {len(results['simulated_data'])} simulated students")
    
    if 'cluster_comparison_metrics' in results:
        score = results['cluster_comparison_metrics']['overall_similarity_score']
        print(f"✅ Similarity Score: {score['score']:.2f}% (Grade: {score['grade']})")
    

def example_2_fixed_clusters():
    """Example 2: Run pipeline with fixed number of clusters"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Full Pipeline (Fixed K=5)")
    print("="*80)
    
    pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs/example2')
    
    results = pipeline.run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv',
        n_clusters=5,  # Fixed K
        n_simulated_students=200,
        simulation_noise=0.15
    )
    
    print(f"\n✅ Created exactly 5 clusters")
    print(f"✅ Simulated 200 students with 15% noise")


def example_3_modular_usage():
    """Example 3: Use individual modules separately"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Modular Usage")
    print("="*80)
    
    # Step 1: Feature Extraction
    print("\n📊 Step 1: Feature Extraction...")
    extractor = FeatureExtractor()
    features = extractor.process_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv',
        output_dir='outputs/example3/features'
    )
    print(f"✅ Extracted {len(features.columns)-1} features")
    
    # Step 2: Clustering
    print("\n🎯 Step 2: Clustering Analysis...")
    analyzer = ClusteringAnalyzer()
    clustered, stats = analyzer.process_pipeline(
        features_path='outputs/example3/features/features_scaled.json',
        output_dir='outputs/example3/clustering',
        n_clusters=4
    )
    print(f"✅ Clustered into 4 groups")
    
    # Step 3: Simulation
    print("\n🔮 Step 3: Data Simulation...")
    simulator = DataSimulator('outputs/example3/clustering/cluster_statistics.json')
    simulated = simulator.process_pipeline(
        n_students=150,
        output_dir='outputs/example3/simulation',
        noise_level=0.12
    )
    print(f"✅ Simulated 150 students")
    
    # Step 4: Comparison
    print("\n📈 Step 4: Comparison...")
    visualizer = ComparisonVisualizer()
    common_features = [col for col in clustered.columns 
                      if col in simulated.columns and col != 'userid'][:10]
    
    visualizer.process_pipeline(
        real_path='outputs/example3/clustering/clustered_students.csv',
        simulated_path='outputs/example3/simulation/simulated_students.csv',
        features=common_features,
        output_dir='outputs/example3/comparison'
    )
    print(f"✅ Comparison complete")


def example_4_quick_start():
    """Example 4: Simplest possible usage"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Quick Start (One-Liner)")
    print("="*80)
    
    # Single function call
    MoodleAnalyticsPipeline().run_full_pipeline(
        grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../data/udk_moodle_log_course_670.filtered.csv'
    )
    
    print(f"\n✅ Done! Check 'outputs/' directory")


def main():
    """Run all examples"""
    
    print("\n" + "#"*80)
    print("# MOODLE ANALYTICS PIPELINE - USAGE EXAMPLES")
    print("#"*80)
    
    # Choose which examples to run
    examples = {
        '1': ('Full Pipeline (Auto K)', example_1_full_pipeline),
        '2': ('Full Pipeline (Fixed K)', example_2_fixed_clusters),
        '3': ('Modular Usage', example_3_modular_usage),
        '4': ('Quick Start', example_4_quick_start)
    }
    
    print("\nAvailable examples:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    
    choice = input("\nSelect example to run (1-4, or 'all'): ").strip()
    
    if choice.lower() == 'all':
        for desc, func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"❌ Error in {desc}: {e}")
    elif choice in examples:
        desc, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Invalid choice")
    
    print("\n" + "#"*80)
    print("# EXAMPLES COMPLETED")
    print("#"*80)


if __name__ == '__main__':
    main()
