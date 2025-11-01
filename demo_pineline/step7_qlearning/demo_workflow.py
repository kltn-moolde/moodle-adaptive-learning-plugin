#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Workflow Example
==========================
Demo toàn bộ workflow từ simulation → training → recommendations
"""

import os
import json
import numpy as np

from core.state_builder import MoodleStateBuilder
from core.action_space import ActionSpace
from core.reward_calculator import RewardCalculator
from core.qlearning_agent import QLearningAgent
from core.simulator import LearningSimulator


def main():
    print("=" * 70)
    print("Q-LEARNING WORKFLOW DEMO")
    print("=" * 70)
    
    # Setup paths
    data_dir = 'data'
    course_path = os.path.join(data_dir, 'course_structure.json')
    profiles_path = os.path.join(data_dir, 'cluster_profiles.json')
    model_path = 'models/qlearning_model.pkl'
    
    # === STEP 1: Initialize Components ===
    print("\n[STEP 1] Initializing components...")
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(course_path)
    reward_calculator = RewardCalculator(profiles_path)
    simulator = LearningSimulator(state_builder, action_space, reward_calculator)
    
    print(f"  ✓ Action space: {action_space.get_action_count()} actions")
    print(f"  ✓ Clusters: {reward_calculator.get_cluster_count()}")
    
    # === STEP 2: Simulate Learning Data ===
    print("\n[STEP 2] Simulating learning data...")
    interactions = simulator.simulate_batch(n_students=5, n_actions_per_student=10)
    
    stats = simulator.get_simulation_stats(interactions)
    print(f"  ✓ Generated {stats['total_interactions']} interactions")
    print(f"  ✓ Avg score: {stats['avg_score']:.2f}")
    print(f"  ✓ Completion: {stats['completion_rate']:.1%}")
    
    # === STEP 3: Train Q-Learning ===
    print("\n[STEP 3] Training Q-learning agent...")
    agent = QLearningAgent(
        n_actions=action_space.get_action_count(),
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.1
    )
    
    # Organize into episodes
    episodes = {}
    for interaction in interactions:
        sid = interaction.student_id
        if sid not in episodes:
            episodes[sid] = []
        
        episodes[sid].append({
            'action_id': interaction.action_id,
            'reward': interaction.reward,
            'next_state': np.array(interaction.state_after),
            'done': False
        })
    
    # Mark last as done
    for sid in episodes:
        if episodes[sid]:
            episodes[sid][-1]['done'] = True
    
    # Train
    for epoch in range(3):
        for sid, episode_data in episodes.items():
            initial_state = np.array(interactions[0].state_before)
            agent.train_episode(initial_state, episode_data)
    
    agent_stats = agent.get_statistics()
    print(f"  ✓ Trained {agent_stats['episodes']} episodes")
    print(f"  ✓ Q-table size: {agent_stats['q_table_size']} states")
    print(f"  ✓ Avg reward: {agent_stats['avg_reward']:.2f}")
    
    # === STEP 4: Generate Recommendations ===
    print("\n[STEP 4] Generating recommendations...")
    
    # Sample student states
    sample_states = {
        'Weak student': np.array([0.3, 0.4, 0.6, 0.2, 0.3, 0.4, 0.3, 0.2, 0.3, 0.4, 0.3, 0.5]),
        'Average student': np.array([0.6, 0.6, 0.3, 0.5, 0.5, 0.6, 0.6, 0.4, 0.6, 0.6, 0.5, 0.7]),
        'Strong student': np.array([0.9, 0.9, 0.1, 0.8, 0.8, 0.9, 0.9, 0.7, 0.9, 0.9, 0.8, 0.9])
    }
    
    available_actions = [a.id for a in action_space.get_actions()[:10]]  # First 10
    
    for student_type, state in sample_states.items():
        print(f"\n  {student_type}:")
        recs = agent.recommend_action(state, available_actions, top_k=3)
        
        for i, (action_id, q_val) in enumerate(recs):
            action = action_space.get_action_by_id(action_id)
            print(f"    {i+1}. {action.name[:40]:40s} (Q={q_val:.3f})")
    
    # === STEP 5: Summary ===
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    
    print("\n📊 Summary:")
    print(f"  • Simulated {stats['unique_students']} students")
    print(f"  • Generated {stats['total_interactions']} interactions")
    print(f"  • Trained Q-table with {agent_stats['q_table_size']} states")
    print(f"  • Ready to provide personalized recommendations")
    
    print("\n🎯 Next Steps:")
    print("  1. Run with more students: simulate_learning_data.py --n-students 100")
    print("  2. Train full model: train_qlearning_v2.py --epochs 10")
    print("  3. Setup daily updates: update_daily_qtable.py (cron job)")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
