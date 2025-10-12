#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization: System Architecture Diagram
===========================================
Tạo diagram minh họa kiến trúc hệ thống
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_architecture_diagram():
    """Vẽ diagram kiến trúc"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'Q-LEARNING ADAPTIVE LEARNING SYSTEM', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    ax.text(5, 11, 'Architecture Overview', 
            ha='center', va='center', fontsize=12, style='italic')
    
    # Colors
    color_data = '#E8F4F8'
    color_core = '#FFF4E6'
    color_agent = '#FFE6E6'
    color_util = '#E8F8F5'
    
    # Layer 1: Data Models (Top)
    y_start = 9.5
    
    # CourseStructure
    box1 = FancyBboxPatch((0.5, y_start), 2.5, 1.2, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_data, edgecolor='#2E86AB', linewidth=2)
    ax.add_patch(box1)
    ax.text(1.75, y_start + 0.9, 'CourseStructure', 
            ha='center', fontsize=11, fontweight='bold')
    ax.text(1.75, y_start + 0.5, '• Modules', ha='center', fontsize=8)
    ax.text(1.75, y_start + 0.3, '• Activities', ha='center', fontsize=8)
    ax.text(1.75, y_start + 0.1, '• Prerequisite Graph', ha='center', fontsize=8)
    
    # StudentProfile
    box2 = FancyBboxPatch((3.5, y_start), 2.5, 1.2, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_data, edgecolor='#2E86AB', linewidth=2)
    ax.add_patch(box2)
    ax.text(4.75, y_start + 0.9, 'StudentProfile', 
            ha='center', fontsize=11, fontweight='bold')
    ax.text(4.75, y_start + 0.5, '• Learning History', ha='center', fontsize=8)
    ax.text(4.75, y_start + 0.3, '• Grades', ha='center', fontsize=8)
    ax.text(4.75, y_start + 0.1, '• Derived Features', ha='center', fontsize=8)
    
    # LearningOutcome
    box3 = FancyBboxPatch((6.5, y_start), 2.5, 1.2, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_data, edgecolor='#2E86AB', linewidth=2)
    ax.add_patch(box3)
    ax.text(7.75, y_start + 0.9, 'LearningOutcome', 
            ha='center', fontsize=11, fontweight='bold')
    ax.text(7.75, y_start + 0.5, '• Grade', ha='center', fontsize=8)
    ax.text(7.75, y_start + 0.3, '• Time Spent', ha='center', fontsize=8)
    ax.text(7.75, y_start + 0.1, '• Attempts', ha='center', fontsize=8)
    
    # Layer 2: Core Components (Middle)
    y_start = 6.5
    
    # StateBuilder
    box4 = FancyBboxPatch((0.5, y_start), 2.2, 1.8, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_core, edgecolor='#A23B72', linewidth=2)
    ax.add_patch(box4)
    ax.text(1.6, y_start + 1.5, 'StateBuilder', 
            ha='center', fontsize=11, fontweight='bold')
    ax.text(1.6, y_start + 1.1, 'Abstract', ha='center', fontsize=8, style='italic')
    ax.text(1.6, y_start + 0.7, '• build_state()', ha='left', fontsize=8)
    ax.text(1.6, y_start + 0.4, '• hash_state()', ha='left', fontsize=8)
    ax.text(1.6, y_start + 0.1, '→ State Vector', ha='center', fontsize=8, style='italic')
    
    # ActionSpace
    box5 = FancyBboxPatch((3.1, y_start), 1.8, 1.8, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_core, edgecolor='#A23B72', linewidth=2)
    ax.add_patch(box5)
    ax.text(4.0, y_start + 1.5, 'ActionSpace', 
            ha='center', fontsize=11, fontweight='bold')
    ax.text(4.0, y_start + 0.9, '• get_available()', ha='left', fontsize=8)
    ax.text(4.0, y_start + 0.5, '• apply_filters()', ha='left', fontsize=8)
    ax.text(4.0, y_start + 0.1, '→ Valid Actions', ha='center', fontsize=8, style='italic')
    
    # RewardCalculator
    box6 = FancyBboxPatch((5.3, y_start), 2.2, 1.8, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_core, edgecolor='#A23B72', linewidth=2)
    ax.add_patch(box6)
    ax.text(6.4, y_start + 1.5, 'RewardCalculator', 
            ha='center', fontsize=11, fontweight='bold')
    ax.text(6.4, y_start + 1.1, 'Abstract', ha='center', fontsize=8, style='italic')
    ax.text(6.4, y_start + 0.7, '• Grade reward', ha='left', fontsize=8)
    ax.text(6.4, y_start + 0.4, '• Difficulty match', ha='left', fontsize=8)
    ax.text(6.4, y_start + 0.1, '→ Reward [-1, 1]', ha='center', fontsize=8, style='italic')
    
    # Layer 3: Q-Learning Agent (Core)
    y_start = 3.5
    
    box7 = FancyBboxPatch((1.5, y_start), 6.0, 2.2, 
                          boxstyle="round,pad=0.15", 
                          facecolor=color_agent, edgecolor='#C73E1D', linewidth=3)
    ax.add_patch(box7)
    ax.text(4.5, y_start + 1.85, '⭐ QLearningAgent ⭐', 
            ha='center', fontsize=13, fontweight='bold')
    ax.text(4.5, y_start + 1.5, 'Q-Table: Dict[(state_hash, action_id)] → Q-value', 
            ha='center', fontsize=9, style='italic')
    
    # Methods
    methods = [
        'get_q_value()',
        'get_best_action()',
        'choose_action()',
        'update() [Bellman]',
        'recommend(top_k)',
        'save() / load()'
    ]
    
    x_methods = [2.0, 3.5, 5.0, 2.0, 3.5, 5.0]
    y_methods = [y_start + 0.9, y_start + 0.9, y_start + 0.9,
                 y_start + 0.4, y_start + 0.4, y_start + 0.4]
    
    for method, x, y in zip(methods, x_methods, y_methods):
        ax.text(x, y, f'• {method}', ha='left', fontsize=8)
    
    # Layer 4: Output (Bottom)
    y_start = 1.0
    
    box8 = FancyBboxPatch((2.5, y_start), 4.0, 1.2, 
                          boxstyle="round,pad=0.1", 
                          facecolor=color_util, edgecolor='#18A558', linewidth=2)
    ax.add_patch(box8)
    ax.text(4.5, y_start + 0.8, '📊 RECOMMENDATIONS', 
            ha='center', fontsize=12, fontweight='bold')
    ax.text(4.5, y_start + 0.4, 'Top-K activities với Q-values', 
            ha='center', fontsize=9)
    ax.text(4.5, y_start + 0.1, '"You should learn: Activity X (Q=0.85)"', 
            ha='center', fontsize=8, style='italic')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2, color='#333333')
    
    # Data Models → Core
    ax.annotate('', xy=(1.6, 6.5), xytext=(1.75, 9.5), arrowprops=arrow_props)
    ax.annotate('', xy=(4.0, 6.5), xytext=(4.75, 9.5), arrowprops=arrow_props)
    ax.annotate('', xy=(6.4, 6.5), xytext=(7.75, 9.5), arrowprops=arrow_props)
    
    # Core → Agent
    ax.annotate('', xy=(3.0, 5.7), xytext=(1.6, 6.5), arrowprops=arrow_props)
    ax.annotate('', xy=(4.5, 5.7), xytext=(4.0, 6.5), arrowprops=arrow_props)
    ax.annotate('', xy=(6.0, 5.7), xytext=(6.4, 6.5), arrowprops=arrow_props)
    
    # Agent → Output
    ax.annotate('', xy=(4.5, 2.2), xytext=(4.5, 3.5), arrowprops=arrow_props)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=color_data, edgecolor='#2E86AB', label='Data Models'),
        mpatches.Patch(facecolor=color_core, edgecolor='#A23B72', label='Core Components'),
        mpatches.Patch(facecolor=color_agent, edgecolor='#C73E1D', label='Q-Learning Agent'),
        mpatches.Patch(facecolor=color_util, edgecolor='#18A558', label='Output'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    # Footer
    ax.text(5, 0.3, 'Design: Abstract State Representation → Generalization Across Courses', 
            ha='center', fontsize=9, style='italic', color='#666666')
    
    plt.tight_layout()
    return fig

def main():
    """Generate and save diagram"""
    print("🎨 Generating architecture diagram...")
    
    fig = create_architecture_diagram()
    
    # Save
    output_file = 'architecture_diagram.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"✅ Diagram saved: {output_file}")
    print("\n📊 Diagram shows:")
    print("   - Data Models (CourseStructure, StudentProfile, Outcome)")
    print("   - Core Components (StateBuilder, ActionSpace, RewardCalculator)")
    print("   - Q-Learning Agent (Q-table, methods)")
    print("   - Recommendations output")
    
    # Show
    plt.show()

if __name__ == '__main__':
    main()
