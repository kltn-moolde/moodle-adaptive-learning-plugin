#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra chi tiết Lesson 0 trong Q-table
"""

import pickle
import numpy as np
from pathlib import Path
from collections import defaultdict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.rl.action_space import ActionSpace
    ACTION_SPACE_AVAILABLE = True
except ImportError:
    ACTION_SPACE_AVAILABLE = False

# Action mapping
ACTION_NAMES = {
    0: "view_assignment (past)",
    1: "view_content (past)",
    2: "attempt_quiz (past)",
    3: "review_quiz (past)",
    4: "post_forum (past)",
    5: "view_assignment (current)",
    6: "view_content (current)",
    7: "submit_assignment (current)",
    8: "attempt_quiz (current)",
    9: "submit_quiz (current)",
    10: "review_quiz (current)",
    11: "post_forum (current)",
    12: "view_content (future)",
    13: "attempt_quiz (future)",
    14: "post_forum (future)",
}

def get_action_name(action_id: int) -> str:
    """Get action name from ID"""
    return ACTION_NAMES.get(action_id, f"Action_{action_id}")

def parse_state_string(state_str: str) -> tuple:
    """Parse state string to tuple"""
    import ast
    try:
        return ast.literal_eval(state_str)
    except:
        return None

def main():
    # Load Q-table
    qtable_path = Path(__file__).parent / 'models' / 'qtable.pkl'
    
    print("=" * 80)
    print("KIỂM TRA CHI TIẾT LESSON = 0")
    print("=" * 80)
    
    with open(qtable_path, 'rb') as f:
        data = pickle.load(f)
    
    q_table = data['q_table']
    
    # Collect all states with lesson = 0
    lesson_0_states = []
    
    for state_key, actions in q_table.items():
        state = parse_state_string(state_key) if isinstance(state_key, str) else state_key
        if isinstance(state, tuple) and len(state) >= 6:
            cluster, lesson, progress, score, phase, engagement = state[:6]
            if lesson == 0:
                lesson_0_states.append((state, actions))
    
    print(f"\n📊 Tổng số states với Lesson = 0: {len(lesson_0_states)}")
    print(f"   (Chiếm {len(lesson_0_states)/len(q_table)*100:.1f}% tổng số states)")
    
    # Analyze distribution
    clusters = defaultdict(int)
    progress_bins = defaultdict(int)
    score_bins = defaultdict(int)
    phases = defaultdict(int)
    engagements = defaultdict(int)
    
    for state, _ in lesson_0_states:
        cluster, lesson, progress, score, phase, engagement = state[:6]
        clusters[cluster] += 1
        progress_bins[progress] += 1
        score_bins[score] += 1
        phases[phase] += 1
        engagements[engagement] += 1
    
    print(f"\n🔢 Phân bố theo Cluster:")
    for cluster in sorted(clusters.keys()):
        print(f"   - Cluster {cluster}: {clusters[cluster]} states")
    
    print(f"\n📈 Phân bố theo Progress:")
    for progress in sorted(progress_bins.keys()):
        print(f"   - Progress {progress:.2f}: {progress_bins[progress]} states")
    
    print(f"\n🎯 Phân bố theo Score:")
    for score in sorted(score_bins.keys()):
        print(f"   - Score {score:.2f}: {score_bins[score]} states")
    
    print(f"\n🎓 Phân bố theo Learning Phase:")
    phase_names = {0: "Pre-Learning", 1: "Active Learning", 2: "Reflective Learning"}
    for phase in sorted(phases.keys()):
        print(f"   - {phase_names.get(phase, f'Phase {phase}')}: {phases[phase]} states")
    
    print(f"\n⚡ Phân bố theo Engagement Level:")
    engagement_names = {0: "Low", 1: "Medium", 2: "High"}
    for engagement in sorted(engagements.keys()):
        print(f"   - {engagement_names.get(engagement, f'Engagement {engagement}')}: {engagements[engagement]} states")
    
    # Find best actions for lesson 0
    print(f"\n" + "=" * 80)
    print("TOP 10 ACTIONS CHO LESSON 0")
    print("=" * 80)
    
    state_action_pairs = []
    for state, actions in lesson_0_states:
        if isinstance(actions, dict):
            for action, q_value in actions.items():
                state_action_pairs.append((state, action, q_value))
    
    state_action_pairs.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n🏆 Top 10 Q-values cao nhất:")
    for i, (state, action, q_value) in enumerate(state_action_pairs[:10], 1):
        cluster, lesson, progress, score, phase, engagement = state[:6]
        phase_name = {0: "Pre", 1: "Active", 2: "Reflective"}.get(phase, "?")
        engagement_name = {0: "Low", 1: "Medium", 2: "High"}.get(engagement, "?")
        action_name = get_action_name(action)
        
        print(f"\n   {i}. Q-value: {q_value:.4f}")
        print(f"      State: C={cluster}, L={lesson}, Prog={progress:.2f}, Score={score:.2f}")
        print(f"             Phase={phase_name}, Engage={engagement_name}")
        print(f"      Action: {action_name}")
    
    # Analyze best actions by state characteristics
    print(f"\n" + "=" * 80)
    print("HÀNH ĐỘNG TỐT NHẤT THEO ĐẶC ĐIỂM STATE")
    print("=" * 80)
    
    # Group by (cluster, phase, engagement)
    grouped_actions = defaultdict(list)
    
    for state, actions in lesson_0_states:
        if isinstance(actions, dict) and actions:
            cluster, lesson, progress, score, phase, engagement = state[:6]
            best_action = max(actions.items(), key=lambda x: x[1])
            grouped_actions[(cluster, phase, engagement)].append(best_action)
    
    print(f"\n📋 Best actions theo (Cluster, Phase, Engagement):")
    for (cluster, phase, engagement), action_list in sorted(grouped_actions.items()):
        phase_name = {0: "Pre", 1: "Active", 2: "Reflective"}.get(phase, "?")
        engagement_name = {0: "Low", 1: "Medium", 2: "High"}.get(engagement, "?")
        
        # Count action frequency
        action_counts = defaultdict(int)
        for action, q_value in action_list:
            action_counts[action] += 1
        
        most_common_action = max(action_counts.items(), key=lambda x: x[1])
        avg_q = np.mean([q for _, q in action_list])
        
        print(f"\n   Cluster {cluster}, {phase_name}, {engagement_name}:")
        print(f"      Most common: {get_action_name(most_common_action[0])} ({most_common_action[1]} times)")
        print(f"      Avg Q-value: {avg_q:.4f}")
        print(f"      Total states: {len(action_list)}")
    
    # Check if lesson 0 appears in other lessons
    print(f"\n" + "=" * 80)
    print("KIỂM TRA CÁC LESSON KHÁC")
    print("=" * 80)
    
    lesson_counts = defaultdict(int)
    for state_key in q_table.keys():
        state = parse_state_string(state_key) if isinstance(state_key, str) else state_key
        if isinstance(state, tuple) and len(state) >= 6:
            lesson = state[1]
            lesson_counts[lesson] += 1
    
    print(f"\n📚 Phân bố theo Lesson ID:")
    for lesson in sorted(lesson_counts.keys()):
        percentage = lesson_counts[lesson] / len(q_table) * 100
        print(f"   - Lesson {lesson}: {lesson_counts[lesson]} states ({percentage:.1f}%)")
    
    # Check if lesson IDs are sequential
    print(f"\n🔍 Nhận xét:")
    if len(lesson_counts) < 6:
        print(f"   ⚠️  Chỉ có {len(lesson_counts)} lessons trong Q-table")
        print(f"   ⚠️  Thiếu lessons: {set(range(6)) - set(lesson_counts.keys())}")
    
    if lesson_counts[0] > max([lesson_counts[i] for i in lesson_counts if i != 0], default=0):
        print(f"   ⚠️  Lesson 0 có nhiều states nhất - có thể là lesson mặc định hoặc fallback")
    
    print("\n" + "=" * 80)
    print("✅ PHÂN TÍCH HOÀN TẤT")
    print("=" * 80)

if __name__ == "__main__":
    main()
