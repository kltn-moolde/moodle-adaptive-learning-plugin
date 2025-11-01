#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Cluster Profiling with LLM
====================================
Demonstrates how to use ClusterProfiler to analyze and describe clusters
"""

import logging
import pandas as pd
from core import ClusterProfiler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def example_basic_profiling():
    """
    Example 1: Basic cluster profiling with Gemini
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Cluster Profiling")
    print("="*80)
    
    # Load real data with clusters
    df = pd.read_csv('outputs/gmm_generation/real_students_with_clusters.csv')
    
    print(f"\nLoaded {len(df)} students with {df['cluster'].nunique()} clusters")
    print(f"Cluster distribution:\n{df['cluster'].value_counts().sort_index()}")
    
    # Initialize profiler with Gemini (free)
    profiler = ClusterProfiler(llm_provider='gemini')
    
    # Profile all clusters
    profiles = profiler.profile_all_clusters(df, cluster_col='cluster')
    
    # Save results
    profiler.save_profiles('outputs/cluster_profiling')
    
    print("\n✓ Profiling completed!")
    print(f"✓ Results saved to: outputs/cluster_profiling/")
    
    return profiles


def example_display_profiles():
    """
    Example 2: Display AI-generated profiles
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Display Cluster Profiles")
    print("="*80)
    
    # Load profiles from JSON
    import json
    with open('outputs/cluster_profiling/cluster_profiles.json', 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    # Display each cluster profile
    for cluster_id in sorted(profiles['cluster_stats'].keys(), key=int):
        data = profiles['cluster_stats'][cluster_id]
        ai_profile = data.get('ai_profile', {})
        
        print(f"\n{'='*80}")
        print(f"CLUSTER {cluster_id}: {ai_profile.get('name', 'N/A')}")
        print(f"{'='*80}")
        print(f"\n📊 Statistics:")
        print(f"   • Students: {data['n_students']} ({data['percentage']:.1f}%)")
        print(f"\n📝 Description:")
        print(f"   {ai_profile.get('description', 'N/A')}")
        print(f"\n💪 Strengths:")
        for strength in ai_profile.get('strengths', []):
            print(f"   • {strength}")
        print(f"\n⚠️ Weaknesses:")
        for weakness in ai_profile.get('weaknesses', []):
            print(f"   • {weakness}")
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(ai_profile.get('recommendations', []), 1):
            print(f"   {i}. {rec}")


def example_compare_clusters():
    """
    Example 3: Compare clusters side by side
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Cluster Comparison")
    print("="*80)
    
    import json
    with open('outputs/cluster_profiling/cluster_profiles.json', 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    # Create comparison table
    comparison_data = []
    
    for cluster_id in sorted(profiles['cluster_stats'].keys(), key=int):
        data = profiles['cluster_stats'][cluster_id]
        ai_profile = data.get('ai_profile', {})
        
        comparison_data.append({
            'Cluster': f"{cluster_id}: {ai_profile.get('name', 'N/A')}",
            'Students': f"{data['n_students']} ({data['percentage']:.1f}%)",
            'Top Strength': ai_profile.get('strengths', ['N/A'])[0] if ai_profile.get('strengths') else 'N/A',
            'Main Action': ai_profile.get('recommendations', ['N/A'])[0] if ai_profile.get('recommendations') else 'N/A'
        })
    
    # Display as table
    df_comparison = pd.DataFrame(comparison_data)
    print("\n" + df_comparison.to_string(index=False))


def example_export_for_teachers():
    """
    Example 4: Export summary for teachers
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Export Teacher Summary")
    print("="*80)
    
    import json
    from pathlib import Path
    
    with open('outputs/cluster_profiling/cluster_profiles.json', 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    # Create teacher-friendly summary
    summary_lines = []
    summary_lines.append("# Báo Cáo Phân Nhóm Học Sinh\n")
    summary_lines.append(f"**Tổng số học sinh**: {profiles['total_students']}\n")
    summary_lines.append(f"**Số nhóm**: {profiles['n_clusters']}\n")
    summary_lines.append("\n---\n")
    
    for cluster_id in sorted(profiles['cluster_stats'].keys(), key=int):
        data = profiles['cluster_stats'][cluster_id]
        ai_profile = data.get('ai_profile', {})
        
        summary_lines.append(f"\n## Nhóm {cluster_id}: {ai_profile.get('name', 'N/A')}\n")
        summary_lines.append(f"\n**Số lượng**: {data['n_students']} học sinh ({data['percentage']:.1f}%)\n")
        summary_lines.append(f"\n**Mô tả**: {ai_profile.get('description', 'N/A')}\n")
        summary_lines.append(f"\n**Đề xuất cho giáo viên**:\n")
        for i, rec in enumerate(ai_profile.get('recommendations', []), 1):
            summary_lines.append(f"{i}. {rec}\n")
        summary_lines.append("\n---\n")
    
    # Save
    output_path = Path('outputs/cluster_profiling/teacher_summary.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(summary_lines)
    
    print(f"\n✓ Teacher summary saved to: {output_path}")
    print("\nPreview:")
    print(''.join(summary_lines[:20]))  # Show first 20 lines


def example_single_cluster_analysis():
    """
    Example 5: Analyze a single cluster in detail
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Single Cluster Deep Dive")
    print("="*80)
    
    import json
    
    with open('outputs/cluster_profiling/cluster_profiles.json', 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    # Pick cluster with most students
    cluster_sizes = {int(k): v['n_students'] 
                    for k, v in profiles['cluster_stats'].items()}
    largest_cluster = max(cluster_sizes, key=cluster_sizes.get)
    
    print(f"\nAnalyzing largest cluster: {largest_cluster}")
    
    data = profiles['cluster_stats'][str(largest_cluster)]
    ai_profile = data.get('ai_profile', {})
    
    print(f"\n{'='*80}")
    print(f"DETAILED ANALYSIS: CLUSTER {largest_cluster}")
    print(f"{'='*80}")
    
    print(f"\n1. OVERVIEW")
    print(f"   Name: {ai_profile.get('name', 'N/A')}")
    print(f"   Size: {data['n_students']} students ({data['percentage']:.1f}% of total)")
    
    print(f"\n2. CHARACTERISTICS")
    print(f"   {ai_profile.get('description', 'N/A')}")
    
    print(f"\n3. TOP DISTINGUISHING FEATURES")
    for feat_data in data['top_distinguishing_features'][:5]:
        feat = feat_data['feature']
        interp = feat_data['interpretation']
        z = feat_data['z_score']
        print(f"   • {feat}: {interp} (z-score: {z:.2f})")
    
    print(f"\n4. SWOT ANALYSIS")
    print(f"   Strengths:")
    for s in ai_profile.get('strengths', []):
        print(f"     + {s}")
    print(f"   Weaknesses:")
    for w in ai_profile.get('weaknesses', []):
        print(f"     - {w}")
    
    print(f"\n5. ACTION PLAN")
    for i, rec in enumerate(ai_profile.get('recommendations', []), 1):
        print(f"   Step {i}: {rec}")


if __name__ == '__main__':
    import sys
    
    print("\n" + "="*80)
    print("CLUSTER PROFILING EXAMPLES")
    print("="*80)
    print("\nAvailable examples:")
    print("  1. Basic profiling (run profiler)")
    print("  2. Display profiles")
    print("  3. Compare clusters")
    print("  4. Export for teachers")
    print("  5. Single cluster deep dive")
    print("  all - Run all examples")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nSelect example (1-5 or 'all'): ").strip()
    
    try:
        if choice == '1':
            example_basic_profiling()
        elif choice == '2':
            example_display_profiles()
        elif choice == '3':
            example_compare_clusters()
        elif choice == '4':
            example_export_for_teachers()
        elif choice == '5':
            example_single_cluster_analysis()
        elif choice == 'all':
            example_basic_profiling()
            example_display_profiles()
            example_compare_clusters()
            example_export_for_teachers()
            example_single_cluster_analysis()
        else:
            print("Invalid choice!")
            
    except FileNotFoundError:
        print("\n❌ Error: Profile files not found!")
        print("Please run example 1 first to generate profiles.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
