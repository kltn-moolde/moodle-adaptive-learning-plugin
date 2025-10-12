# -*- coding: utf-8 -*-
"""
DEMO PHASE 1: Hệ thống AI Gợi ý Học tập Thông minh
==================================================

File demo để test và minh họa các tính năng của Phase 1
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase1_enhanced_learning_system import *
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Cấu hình hiển thị
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

def demo_data_analysis():
    """Demo phân tích dữ liệu"""
    print("=" * 60)
    print("📊 PHÂN TÍCH DỮ LIỆU HỌC TẬP")
    print("=" * 60)
    
    # Tải và xử lý dữ liệu
    processor = DataProcessor("../data/features_scaled_report.json")
    processor.create_enhanced_features()
    
    print(f"\n📈 Thống kê tổng quan:")
    print(f"   • Tổng số sinh viên: {len(processor.df)}")
    print(f"   • Số features: {len(processor.df.columns)}")
    print(f"   • Điểm trung bình: {processor.df['mean_module_grade'].mean():.3f}")
    print(f"   • Engagement score trung bình: {processor.df['engagement_score'].mean():.3f}")
    
    # Phân tích learning styles
    print(f"\n🎨 Phân bố Learning Styles:")
    style_counts = processor.df['learning_style'].value_counts()
    for style, count in style_counts.items():
        print(f"   • {style}: {count} sinh viên ({count/len(processor.df)*100:.1f}%)")
    
    # Phân tích performance levels
    print(f"\n📊 Phân bố Performance Levels:")
    perf_counts = processor.df['performance_level'].value_counts()
    for level, count in perf_counts.items():
        print(f"   • {level}: {count} sinh viên ({count/len(processor.df)*100:.1f}%)")
    
    # Phân tích weak/strong areas
    print(f"\n🔍 Phân tích Weak Areas:")
    all_weak = []
    for areas in processor.df['weak_areas']:
        all_weak.extend(areas)
    weak_counts = pd.Series(all_weak).value_counts()
    for area, count in weak_counts.items():
        print(f"   • {area}: {count} lần được đề cập")
    
    print(f"\n💪 Phân tích Strong Areas:")
    all_strong = []
    for areas in processor.df['strong_areas']:
        all_strong.extend(areas)
    strong_counts = pd.Series(all_strong).value_counts()
    for area, count in strong_counts.items():
        print(f"   • {area}: {count} lần được đề cập")

def demo_recommendation_system():
    """Demo hệ thống gợi ý"""
    print("\n" + "=" * 60)
    print("🤖 HỆ THỐNG GỢI Ý THÔNG MINH")
    print("=" * 60)
    
    # Khởi tạo hệ thống
    processor = DataProcessor("../data/features_scaled_report.json")
    processor.create_enhanced_features()
    student_profiles = processor.create_student_profiles()
    
    reward_system = EnhancedRewardSystem()
    
    # Tạo Q-agents
    q_agents = {}
    n_states = len(LearningState)
    n_actions = len(LearningState)
    
    for cluster_id in range(3):
        agent = EnhancedQLearningAgent(
            n_states=n_states,
            n_actions=n_actions,
            learning_rate=0.1,
            discount=0.95,
            epsilon=0.1
        )
        q_agents[cluster_id] = agent
    
    recommendation_system = IntelligentRecommendationSystem(q_agents, reward_system)
    
    # Demo gợi ý cho từng loại sinh viên
    print("\n🎯 DEMO GỢI Ý CHO CÁC LOẠI SINH VIÊN:")
    
    # Tìm ví dụ cho từng performance level
    performance_examples = {}
    for level in PerformanceLevel:
        examples = [p for p in student_profiles if p.performance_level == level]
        if examples:
            performance_examples[level] = examples[0]
    
    for level, profile in performance_examples.items():
        print(f"\n--- {level.value.upper()} PERFORMER ---")
        print(f"Sinh viên ID: {profile.user_id}")
        print(f"Learning Style: {profile.learning_style.value}")
        print(f"Engagement Score: {profile.engagement_score:.3f}")
        print(f"Weak Areas: {profile.weak_areas}")
        print(f"Strong Areas: {profile.strong_areas}")
        
        # Tạo gợi ý
        recommendation = recommendation_system.get_personalized_recommendation(profile)
        
        print(f"\n🎯 GỢI Ý CÁ NHÂN HÓA:")
        print(f"   📚 Hoạt động: {recommendation.recommended_state.value}")
        print(f"   🎯 Độ tin cậy: {recommendation.confidence_score:.3f}")
        print(f"   💡 Lý do: {recommendation.reasoning}")
        print(f"   📈 Lợi ích dự kiến: {recommendation.expected_benefit:.3f}")
        print(f"   ⏱️  Thời gian: {recommendation.time_estimate} phút")
        print(f"   📊 Độ khó: {recommendation.difficulty_level}")
        print(f"   🔗 Prerequisites: {[s.value for s in recommendation.prerequisites]}")

def demo_reward_system():
    """Demo hệ thống reward"""
    print("\n" + "=" * 60)
    print("🏆 HỆ THỐNG REWARD NÂNG CAO")
    print("=" * 60)
    
    reward_system = EnhancedRewardSystem()
    
    # Tạo profile mẫu
    sample_profile = StudentProfile(
        user_id=9999,
        cluster_id=0,
        learning_style=LearningStyle.VISUAL,
        performance_level=PerformanceLevel.GOOD,
        engagement_score=0.7,
        completion_rate=0.8,
        time_preference="evening",
        weak_areas=['quiz'],
        strong_areas=['assignment'],
        learning_goals=['improve_performance'],
        current_state=LearningState.VIEW_COURSE,
        learning_history=[],
        performance_trend="improving"
    )
    
    print("\n📊 DEMO TÍNH REWARD CHO CÁC HOẠT ĐỘNG:")
    
    # Test reward cho các states khác nhau
    test_states = [
        LearningState.VIEW_COURSE,
        LearningState.START_ASSIGNMENT,
        LearningState.SUBMIT_ASSIGNMENT,
        LearningState.START_QUIZ,
        LearningState.SUBMIT_QUIZ,
        LearningState.SEEK_HELP,
        LearningState.REVIEW_MISTAKES
    ]
    
    for state in test_states:
        reward = reward_system.calculate_reward(
            LearningState.VIEW_COURSE,  # current state
            state,  # next state
            sample_profile,
            "normal"
        )
        
        print(f"   {state.value:<25}: {reward:.3f}")
    
    print(f"\n💡 GIẢI THÍCH REWARD:")
    print(f"   • Base reward: Giá trị cơ bản của hoạt động")
    print(f"   • Performance multiplier: Điều chỉnh theo mức độ hiệu suất")
    print(f"   • Learning style multiplier: Điều chỉnh theo phong cách học")
    print(f"   • Engagement bonus: Thưởng dựa trên mức độ tham gia")
    print(f"   • Completion bonus: Thưởng dựa trên tỷ lệ hoàn thành")
    print(f"   • Progress bonus: Thưởng khi tiến bộ (không lặp state)")
    print(f"   • Difficulty penalty: Phạt khi chuyển đổi quá nhanh")

def demo_learning_states():
    """Demo các learning states"""
    print("\n" + "=" * 60)
    print("📚 CÁC TRẠNG THÁI HỌC TẬP")
    print("=" * 60)
    
    print("\n🎯 DANH SÁCH CÁC STATES:")
    for i, state in enumerate(LearningState):
        print(f"   {i:2d}. {state.value}")
    
    print(f"\n📊 THỐNG KÊ:")
    print(f"   • Tổng số states: {len(LearningState)}")
    print(f"   • States cơ bản: 3 (view_course, view_module, view_resource)")
    print(f"   • States Assignment: 4 (view, start, submit, feedback)")
    print(f"   • States Quiz: 4 (view, start, submit, review)")
    print(f"   • States tương tác: 4 (grades, progress, discussion, download)")
    print(f"   • States đặc biệt: 3 (help, review_mistakes, plan_study)")

def create_visualization():
    """Tạo visualization cho demo"""
    print("\n" + "=" * 60)
    print("📊 TẠO BIỂU ĐỒ MINH HỌA")
    print("=" * 60)
    
    # Tải dữ liệu
    processor = DataProcessor("../data/features_scaled_report.json")
    processor.create_enhanced_features()
    
    # Tạo figure với subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Phân bố Performance Levels
    perf_counts = processor.df['performance_level'].value_counts()
    axes[0, 0].pie(perf_counts.values, labels=perf_counts.index, autopct='%1.1f%%')
    axes[0, 0].set_title('Phân bố Performance Levels', fontweight='bold')
    
    # 2. Phân bố Learning Styles
    style_counts = processor.df['learning_style'].value_counts()
    axes[0, 1].bar(style_counts.index, style_counts.values, color='skyblue')
    axes[0, 1].set_title('Phân bố Learning Styles', fontweight='bold')
    axes[0, 1].set_ylabel('Số lượng sinh viên')
    
    # 3. Engagement Score vs Performance
    axes[1, 0].scatter(processor.df['engagement_score'], 
                      processor.df['mean_module_grade'],
                      alpha=0.7, s=100)
    axes[1, 0].set_xlabel('Engagement Score')
    axes[1, 0].set_ylabel('Mean Module Grade')
    axes[1, 0].set_title('Engagement vs Performance', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Feature correlation heatmap
    features = ['engagement_score', 'assignment_completion', 'quiz_participation', 
               'resource_utilization', 'feedback_engagement', 'mean_module_grade']
    corr_matrix = processor.df[features].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1, 1])
    axes[1, 1].set_title('Feature Correlation Matrix', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('phase1_demo_visualization.png', dpi=300, bbox_inches='tight')
    print("✅ Biểu đồ đã được lưu: phase1_demo_visualization.png")
    
    plt.show()

def main():
    """Hàm chính cho demo"""
    print("🚀 DEMO PHASE 1: HỆ THỐNG AI GỢI Ý HỌC TẬP THÔNG MINH")
    print("=" * 70)
    
    try:
        # 1. Demo phân tích dữ liệu
        demo_data_analysis()
        
        # 2. Demo learning states
        demo_learning_states()
        
        # 3. Demo reward system
        demo_reward_system()
        
        # 4. Demo recommendation system
        demo_recommendation_system()
        
        # 5. Tạo visualization
        create_visualization()
        
        print("\n" + "=" * 70)
        print("✅ DEMO PHASE 1 HOÀN THÀNH!")
        print("=" * 70)
        print("\n🎯 CÁC TÍNH NĂNG ĐÃ DEMO:")
        print("   • Phân tích dữ liệu học tập chi tiết")
        print("   • 18 trạng thái học tập được định nghĩa")
        print("   • Hệ thống reward nâng cao với nhiều yếu tố")
        print("   • Gợi ý cá nhân hóa dựa trên profile")
        print("   • Visualization dữ liệu và kết quả")
        
        print("\n🚀 SẴN SÀNG CHO PHASE 2:")
        print("   • Hệ thống gợi ý real-time")
        print("   • Adaptive learning path generator")
        print("   • Performance monitoring system")
        print("   • Mobile app interface")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
