#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Q-Table Coverage
=======================
Check xem test students có fall vào trained states không
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent))

from core import MoodleStateBuilder, StateDiscretizer


def extract_student_features(student_data: dict) -> dict:
    """Extract features từ student data"""
    return {
        'userid': student_data['userid'],
        'mean_module_grade': student_data.get('mean_module_grade', 0.5),
        'total_events': student_data.get('total_events', 0.5),
        'course_module': student_data.get('course_module', 0.5),
        'viewed': student_data.get('viewed', 0.5),
        'attempt': student_data.get('attempt', 0.5),
        'feedback_viewed': student_data.get('feedback_viewed', 0.5),
        'submitted': student_data.get('submitted', 0.5),
        'reviewed': student_data.get('reviewed', 0.5),
        'course_module_viewed': student_data.get('course_module_viewed', 0.5),
        'module_count': student_data.get('module_count', 0.5),
        'course_module_completion': student_data.get('course_module_completion', 0.5),
        'created': student_data.get('created', 0.5),
        'updated': student_data.get('updated', 0.5),
        'downloaded': student_data.get('downloaded', 0.5),
    }


def main():
    print("\n" + "="*70)
    print("🔍 DEBUG Q-TABLE COVERAGE")
    print("="*70)
    
    # Load data
    data_path = Path(__file__).parent.parent / 'data' / 'features_scaled_report.json'
    with open(data_path, 'r') as f:
        students_data = json.load(f)
    
    # Split train/test
    n_train = int(len(students_data) * 0.8)
    train_data = students_data[:n_train]
    test_data = students_data[n_train:]
    
    print(f"\nData:")
    print(f"  Train: {len(train_data)} students")
    print(f"  Test: {len(test_data)} students")
    
    # Create state builder & discretizer
    state_builder = MoodleStateBuilder()
    discretizer = StateDiscretizer(state_dim=12, n_bins=3)
    
    print(f"\nState space:")
    print(f"  {discretizer}")
    
    # Collect discrete states from training
    train_discrete_states = set()
    train_continuous_states = []
    
    for student_data in train_data:
        features = extract_student_features(student_data)
        state = state_builder.build_state(features)
        discrete_state = discretizer.discretize(state)
        
        train_discrete_states.add(discrete_state)
        train_continuous_states.append(state)
    
    print(f"\nTraining coverage:")
    print(f"  Unique discrete states: {len(train_discrete_states)}")
    print(f"  Possible states: {discretizer.get_state_space_size():,}")
    print(f"  Coverage: {len(train_discrete_states) / discretizer.get_state_space_size() * 100:.6f}%")
    
    # Check test students
    print(f"\n" + "="*70)
    print("TEST STUDENTS ANALYSIS")
    print("="*70)
    
    test_coverage = 0
    
    for i, student_data in enumerate(test_data, 1):
        features = extract_student_features(student_data)
        state = state_builder.build_state(features)
        discrete_state = discretizer.discretize(state)
        
        in_training = discrete_state in train_discrete_states
        test_coverage += in_training
        
        print(f"\nStudent {i} (ID: {features['userid']}):")
        print(f"  Continuous state: {state[:3]} ...")
        print(f"  Discrete state: {discrete_state[:3]} ...")
        print(f"  In training? {'✅ YES' if in_training else '❌ NO'}")
        
        if not in_training:
            # Find closest training state
            min_dist = float('inf')
            closest_state = None
            for train_state in train_continuous_states:
                dist = np.linalg.norm(state - train_state)
                if dist < min_dist:
                    min_dist = dist
                    closest_state = train_state
            
            closest_discrete = discretizer.discretize(closest_state)
            print(f"  Closest training state distance: {min_dist:.3f}")
            print(f"  Closest discrete: {closest_discrete[:3]} ...")
    
    print(f"\n" + "="*70)
    print(f"Test coverage: {test_coverage}/{len(test_data)} students in training states")
    print("="*70)
    
    # Analyze bin distribution
    print(f"\n" + "="*70)
    print("BIN DISTRIBUTION")
    print("="*70)
    
    feature_names = [
        'knowledge', 'engagement', 'struggle', 'submission', 'review',
        'resource_usage', 'assessment', 'collaborative', 'progress',
        'completion', 'diversity', 'consistency'
    ]
    
    # Collect all states
    all_states = []
    for student_data in students_data:
        features = extract_student_features(student_data)
        state = state_builder.build_state(features)
        all_states.append(state)
    
    all_states = np.array(all_states)
    
    print("\nFeature distributions:")
    for i, fname in enumerate(feature_names):
        values = all_states[:, i]
        print(f"\n{fname}:")
        print(f"  Min: {values.min():.3f}, Max: {values.max():.3f}, "
              f"Mean: {values.mean():.3f}, Std: {values.std():.3f}")
        
        # Count bins
        discrete_values = [discretizer.discretize(s)[i] for s in all_states]
        bin_counts = defaultdict(int)
        for v in discrete_values:
            bin_counts[v] += 1
        
        print(f"  Bin distribution: ", end="")
        for bin_idx in sorted(bin_counts.keys()):
            label = discretizer.get_bin_label(bin_idx)
            count = bin_counts[bin_idx]
            print(f"{label}={count} ", end="")
        print()


if __name__ == '__main__':
    main()
