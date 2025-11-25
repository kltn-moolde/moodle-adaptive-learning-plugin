#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync Pipeline Data
==================
Bridge script to sync synthetic student data from moodle_analytics_pipeline
to step7_qlearning for training.

This ensures Q-learning training uses the same synthetic students generated
by the GMM pipeline, maintaining cluster_id consistency.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any


# Path configuration
PIPELINE_ROOT = Path(__file__).resolve().parent.parent / 'moodle_analytics_pipeline'
QLEARNING_ROOT = Path(__file__).resolve().parent.parent / 'step7_qlearning'

PIPELINE_OUTPUTS = PIPELINE_ROOT / 'outputs' / 'gmm_generation'
PIPELINE_CLUSTER_PROFILES = PIPELINE_ROOT / 'outputs' / 'cluster_profiling'

QLEARNING_DATA = QLEARNING_ROOT / 'data'


def sync_synthetic_students():
    """
    Copy synthetic_students_gmm.csv from pipeline to qlearning data folder
    """
    print("=" * 70)
    print("SYNC SYNTHETIC STUDENTS")
    print("=" * 70)
    
    source = PIPELINE_OUTPUTS / 'synthetic_students_gmm.csv'
    target = QLEARNING_DATA / 'synthetic_students_gmm.csv'
    
    if not source.exists():
        print(f"✗ Source file not found: {source}")
        print("  Please run moodle_analytics_pipeline first to generate synthetic data")
        return False
    
    # Create target directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    shutil.copy2(source, target)
    print(f"✓ Copied synthetic students: {source} → {target}")
    
    # Count lines to show stats
    with open(target, 'r') as f:
        n_students = sum(1 for _ in f) - 1  # exclude header
    
    print(f"  Total synthetic students: {n_students}")
    
    return True


def sync_cluster_profiles():
    """
    Copy cluster_profiles.json from pipeline to qlearning data folder
    This ensures API has latest cluster definitions for prediction
    """
    print("\n" + "=" * 70)
    print("SYNC CLUSTER PROFILES")
    print("=" * 70)
    
    source = PIPELINE_CLUSTER_PROFILES / 'cluster_profiles.json'
    target = QLEARNING_DATA / 'cluster_profiles.json'
    
    if not source.exists():
        print(f"✗ Source file not found: {source}")
        print("  Please run moodle_analytics_pipeline first to generate cluster profiles")
        return False
    
    # Create target directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    shutil.copy2(source, target)
    print(f"✓ Copied cluster profiles: {source} → {target}")
    
    # Load and show stats
    with open(target, 'r') as f:
        profiles = json.load(f)
    
    n_clusters = len(profiles.get('cluster_stats', {}))
    print(f"  Total clusters: {n_clusters}")
    
    for cluster_key, cluster_data in profiles.get('cluster_stats', {}).items():
        cluster_id = cluster_data.get('cluster_id', cluster_key)
        n_students = cluster_data.get('n_students', 0)
        percentage = cluster_data.get('percentage', 0)
        
        ai_profile = cluster_data.get('ai_profile', {})
        profile_name = ai_profile.get('profile_name', f'Cluster {cluster_id}')
        
        print(f"    Cluster {cluster_id} ({profile_name}): {n_students} students ({percentage:.1f}%)")
    
    return True


def verify_sync():
    """
    Verify that synced files are valid and compatible
    """
    print("\n" + "=" * 70)
    print("VERIFY SYNC")
    print("=" * 70)
    
    # Check synthetic students
    synthetic_file = QLEARNING_DATA / 'synthetic_students_gmm.csv'
    if not synthetic_file.exists():
        print("✗ Synthetic students file not found")
        return False
    
    # Check cluster profiles
    profiles_file = QLEARNING_DATA / 'cluster_profiles.json'
    if not profiles_file.exists():
        print("✗ Cluster profiles file not found")
        return False
    
    # Load and validate
    with open(profiles_file, 'r') as f:
        profiles = json.load(f)
    
    cluster_ids = set(profiles.get('cluster_stats', {}).keys())
    
    # Read CSV to check cluster column
    import csv
    with open(synthetic_file, 'r') as f:
        reader = csv.DictReader(f)
        first_row = next(reader, None)
        
        if first_row and 'cluster' in first_row:
            csv_cluster = first_row['cluster']
            print(f"✓ Synthetic students have cluster column (sample: {csv_cluster})")
        else:
            print("✗ Synthetic students missing cluster column")
            return False
    
    print(f"✓ Cluster profiles define {len(cluster_ids)} clusters")
    print(f"✓ Files are compatible and ready for training")
    
    return True


def main():
    """Main sync function"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PIPELINE → Q-LEARNING DATA SYNC" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Check if both projects exist
    if not PIPELINE_ROOT.exists():
        print(f"✗ Pipeline project not found: {PIPELINE_ROOT}")
        print("  Please ensure both projects are in the same parent directory")
        return
    
    if not QLEARNING_ROOT.exists():
        print(f"✗ Q-learning project not found: {QLEARNING_ROOT}")
        print("  Please ensure both projects are in the same parent directory")
        return
    
    print(f"Pipeline root: {PIPELINE_ROOT}")
    print(f"Q-learning root: {QLEARNING_ROOT}")
    print()
    
    # Sync files
    success = True
    success &= sync_synthetic_students()
    success &= sync_cluster_profiles()
    
    if success:
        success &= verify_sync()
    
    print("\n" + "=" * 70)
    if success:
        print("✓ SYNC COMPLETE")
        print()
        print("Next steps:")
        print("  1. Use synthetic_students_gmm.csv for Q-learning training")
        print("  2. API will use cluster_profiles.json for cluster prediction")
        print("  3. Run: python train_qlearning_v2.py --use-synthetic")
    else:
        print("✗ SYNC FAILED")
        print()
        print("Please ensure moodle_analytics_pipeline has been run successfully")
    print("=" * 70)


if __name__ == '__main__':
    main()
