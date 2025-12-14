#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cluster Mix Feature
========================
Quick test to verify cluster-mix distribution works correctly
"""

import sys
from pathlib import Path
from collections import Counter

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from training.train_qlearning import _generate_students_by_mix

def test_cluster_mix():
    """Test cluster mix distribution"""
    print("=" * 80)
    print("TESTING CLUSTER MIX FEATURE")
    print("=" * 80)
    
    # Test 1: Default distribution (0.2, 0.6, 0.2)
    print("\n[Test 1] Default distribution (20% weak, 60% medium, 20% strong)")
    print("-" * 80)
    students = _generate_students_by_mix(100, None)
    cluster_counts = Counter(s.cluster for s in students)
    print(f"Total students: {len(students)}")
    print(f"Distribution: weak={cluster_counts['weak']}, medium={cluster_counts['medium']}, strong={cluster_counts['strong']}")
    print(f"Percentages: weak={cluster_counts['weak']/len(students):.1%}, medium={cluster_counts['medium']/len(students):.1%}, strong={cluster_counts['strong']/len(students):.1%}")
    
    # Test 2: Custom distribution (0.1, 0.8, 0.1)
    print("\n[Test 2] Custom distribution (10% weak, 80% medium, 10% strong)")
    print("-" * 80)
    students = _generate_students_by_mix(100, {'weak': 0.1, 'medium': 0.8, 'strong': 0.1})
    cluster_counts = Counter(s.cluster for s in students)
    print(f"Total students: {len(students)}")
    print(f"Distribution: weak={cluster_counts['weak']}, medium={cluster_counts['medium']}, strong={cluster_counts['strong']}")
    print(f"Percentages: weak={cluster_counts['weak']/len(students):.1%}, medium={cluster_counts['medium']/len(students):.1%}, strong={cluster_counts['strong']/len(students):.1%}")
    
    # Test 3: Equal distribution (0.33, 0.33, 0.34)
    print("\n[Test 3] Equal distribution (~33% each)")
    print("-" * 80)
    students = _generate_students_by_mix(90, {'weak': 0.33, 'medium': 0.33, 'strong': 0.34})
    cluster_counts = Counter(s.cluster for s in students)
    print(f"Total students: {len(students)}")
    print(f"Distribution: weak={cluster_counts['weak']}, medium={cluster_counts['medium']}, strong={cluster_counts['strong']}")
    print(f"Percentages: weak={cluster_counts['weak']/len(students):.1%}, medium={cluster_counts['medium']/len(students):.1%}, strong={cluster_counts['strong']/len(students):.1%}")
    
    # Test 4: Small number of students
    print("\n[Test 4] Small number (15 students with 0.2, 0.6, 0.2)")
    print("-" * 80)
    students = _generate_students_by_mix(15, {'weak': 0.2, 'medium': 0.6, 'strong': 0.2})
    cluster_counts = Counter(s.cluster for s in students)
    print(f"Total students: {len(students)}")
    print(f"Distribution: weak={cluster_counts['weak']}, medium={cluster_counts['medium']}, strong={cluster_counts['strong']}")
    print(f"Student IDs by cluster:")
    for cluster in ['weak', 'medium', 'strong']:
        ids = [s.id for s in students if s.cluster == cluster]
        print(f"  {cluster}: {ids}")
    
    print("\n" + "=" * 80)
    print("✓ All tests completed!")
    print("=" * 80)

if __name__ == '__main__':
    test_cluster_mix()
