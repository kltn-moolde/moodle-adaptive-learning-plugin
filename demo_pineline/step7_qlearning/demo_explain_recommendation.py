#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Explain Recommendation
=============================
Demonstrate how to use explain_recommendation() to provide transparent
recommendations to students.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.reward_calculator_v2 import RewardCalculatorV2


def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)


def demo_explain_recommendation():
    """Demo explain_recommendation functionality"""
    print_separator()
    print("DEMO: Explain Recommendation - Giải thích Gợi ý Học tập")
    print_separator()
    
    # Initialize calculator
    print("\n1. Khởi tạo RewardCalculatorV2...")
    calc = RewardCalculatorV2(
        cluster_profiles_path='data/cluster_profiles.json'
    )
    
    # Simulate some student states
    students = [
        {
            'id': 201,
            'name': 'Nguyễn Văn A',
            'cluster': 0,  # weak
            'mastery': {
                'LO1.1': 0.45,
                'LO1.2': 0.35,  # Very weak on important LO
                'LO2.2': 0.40,
                'LO2.4': 0.38
            }
        },
        {
            'id': 202,
            'name': 'Trần Thị B',
            'cluster': 1,  # medium
            'mastery': {
                'LO1.1': 0.65,
                'LO1.2': 0.55,
                'LO2.2': 0.50,
                'LO2.4': 0.60
            }
        },
        {
            'id': 203,
            'name': 'Lê Văn C',
            'cluster': 2,  # strong
            'mastery': {
                'LO1.1': 0.85,
                'LO1.2': 0.75,
                'LO2.2': 0.70,
                'LO2.4': 0.80
            }
        }
    ]
    
    # Simulate mastery states
    for student in students:
        calc.lo_mastery_cache[student['id']] = defaultdict(lambda: 0.5)
        for lo_id, mastery in student['mastery'].items():
            calc.lo_mastery_cache[student['id']][lo_id] = mastery
    
    print("\n2. Học sinh trong demo:")
    for student in students:
        cluster_level = calc.get_cluster_level(student['cluster'])
        print(f"   - {student['name']} (ID: {student['id']}, Cluster: {cluster_level})")
    
    # Demo recommendations for each student
    print("\n" + "=" * 80)
    
    for student in students:
        print(f"\n📚 GỢI Ý CHO: {student['name']} (Cluster: {calc.get_cluster_level(student['cluster'])})")
        print("-" * 80)
        
        # Get weak LOs
        weak_los = calc.get_weak_los_for_midterm(student['id'], threshold=0.7)
        
        if weak_los:
            print(f"\n🎯 Các LO cần cải thiện (mastery < 70%):")
            for lo_id, mastery, weight in weak_los[:3]:
                urgency = calc._calculate_urgency(mastery, weight)
                print(f"   - {lo_id}: mastery={mastery:.2f}, weight={weight*100:.0f}% → {urgency}")
        
        # Get recommended activities
        recommendations = calc.get_recommended_activities_for_weak_los(
            student_id=student['id'],
            top_k=3
        )
        
        if recommendations:
            print(f"\n📋 Top 3 Activities Được Gợi Ý:")
            
            for i, rec in enumerate(recommendations, 1):
                print(f"\n   {i}. Activity {rec['activity_id']} (Priority: {rec['priority_score']:.3f})")
                
                # Get detailed explanation
                explanation = calc.explain_recommendation(
                    activity_id=rec['activity_id'],
                    student_id=student['id'],
                    cluster_id=student['cluster'],
                    include_alternatives=False
                )
                
                why = explanation['why']
                print(f"      🎯 Target: {why['target_LO']}")
                print(f"      📊 Hiện tại: {why['current_mastery']} mastery")
                print(f"      📈 Trọng số GK: {why['midterm_weight']}")
                print(f"      ✨ Lợi ích: +{why['expected_gain']:.3f} mastery")
                print(f"      {why['urgency']}")
        
        print("\n" + "-" * 80)
    
    # Deep dive into one recommendation
    print("\n" + "=" * 80)
    print("\n🔍 PHÂN TÍCH CHI TIẾT MỘT GỢI Ý")
    print("=" * 80)
    
    student = students[0]  # Weak learner
    print(f"\nHọc sinh: {student['name']} (Cluster: weak)")
    
    # Get best recommendation
    recommendations = calc.get_recommended_activities_for_weak_los(
        student_id=student['id'],
        top_k=1
    )
    
    if recommendations:
        activity_id = recommendations[0]['activity_id']
        
        # Get detailed explanation with alternatives
        explanation = calc.explain_recommendation(
            activity_id=activity_id,
            student_id=student['id'],
            cluster_id=student['cluster'],
            include_alternatives=True
        )
        
        print(f"\n📚 {explanation['recommendation']}")
        print(f"\n🎯 MỤC TIÊU:")
        print(f"   LO: {explanation['why']['target_LO']}")
        print(f"   Mô tả: {explanation['why']['lo_description']}")
        
        print(f"\n📊 TÌNH TRẠNG HIỆN TẠI:")
        print(f"   Trình độ: {explanation['why']['current_mastery']} (mastery)")
        print(f"   Trọng số GK: {explanation['why']['midterm_weight']}")
        
        print(f"\n📈 LỢI ÍCH DỰ KIẾN:")
        print(f"   Tăng mastery: +{explanation['why']['expected_gain']}")
        print(f"   {explanation['why']['urgency']}")
        
        print(f"\n💡 CHIẾN LƯỢC HỌC TẬP:")
        print(f"   {explanation['why']['cluster_strategy']}")
        
        print(f"\n🔬 BẰNG CHỨNG:")
        print(f"   {explanation['why']['evidence']}")
        
        if 'additional_los' in explanation['why']:
            print(f"\n🎁 BONUS - Các LO khác cũng được cải thiện:")
            for lo_info in explanation['why']['additional_los']:
                print(f"   - {lo_info['lo_id']}: {lo_info['current_mastery']} → +{lo_info['midterm_weight']}")
        
        if 'alternatives' in explanation:
            print(f"\n🔄 CÁC LỰA CHỌN KHÁC:")
            for alt in explanation['alternatives']:
                print(f"   - Activity {alt['activity_id']}: {alt['rationale']}")
    
    print("\n" + "=" * 80)
    print("✓ Demo hoàn tất!")
    print("=" * 80)


if __name__ == '__main__':
    demo_explain_recommendation()
