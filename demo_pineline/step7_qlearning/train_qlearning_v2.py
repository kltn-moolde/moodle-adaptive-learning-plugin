#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train Q-Learning Model
=======================
Train Q-learning agent from simulated data
"""

import os
import argparse
import json
import numpy as np
from typing import List, Dict

from core.state_builder import MoodleStateBuilder
from core.action_space import ActionSpace
from core.reward_calculator import RewardCalculator
from core.qlearning_agent import QLearningAgent


def load_simulated_data(filepath: str) -> List[Dict]:
    """Load simulated interaction data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def prepare_training_episodes(
    interactions: List[Dict],
    state_builder: MoodleStateBuilder
) -> Dict[int, List[Dict]]:
    """
    Organize interactions into episodes per student
    
    Args:
        interactions: List of simulated interactions
        state_builder: State builder instance
    
    Returns:
        Dict {student_id: episode_data}
    """
    episodes = {}
    
    for interaction in interactions:
        student_id = interaction['student_id']
        
        if student_id not in episodes:
            episodes[student_id] = []
        
        # Convert state lists back to numpy
        state_before = np.array(interaction['state_before'])
        state_after = np.array(interaction['state_after'])
        
        episodes[student_id].append({
            'action_id': interaction['action_id'],
            'reward': interaction['reward'],
            'next_state': state_after,
            'done': False  # Can implement episode termination logic
        })
    
    # Mark last interaction of each student as done
    for student_id in episodes:
        if episodes[student_id]:
            episodes[student_id][-1]['done'] = True
    
    return episodes


def train_qlearning(
    data_path: str = 'data/simulated/latest_simulation.json',
    model_output: str = 'models/qlearning_model.pkl',
    learning_rate: float = 0.1,
    discount_factor: float = 0.95,
    epsilon: float = 0.1,
    n_epochs: int = 10
):
    """
    Train Q-learning model from simulated data
    
    Args:
        data_path: Path to simulated data JSON
        model_output: Output path for trained model
        learning_rate: Learning rate (α)
        discount_factor: Discount factor (γ)
        epsilon: Exploration rate (ε)
        n_epochs: Number of training epochs
    """
    print("=" * 70)
    print("TRAIN Q-LEARNING MODEL")
    print("=" * 70)
    
    # Load components
    print("\n[1/5] Loading components...")
    data_dir = 'data'
    course_structure_path = os.path.join(data_dir, 'course_structure.json')
    cluster_profiles_path = os.path.join(data_dir, 'cluster_profiles.json')
    
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(course_structure_path)
    reward_calculator = RewardCalculator(cluster_profiles_path)
    
    n_actions = action_space.get_action_count()
    print(f"  ✓ Action space size: {n_actions}")
    
    # Initialize agent
    print("\n[2/5] Initializing Q-learning agent...")
    agent = QLearningAgent(
        n_actions=n_actions,
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon=epsilon
    )
    print(f"  ✓ Agent initialized")
    print(f"    - Learning rate: {learning_rate}")
    print(f"    - Discount factor: {discount_factor}")
    print(f"    - Epsilon: {epsilon}")
    
    # Load training data
    print(f"\n[3/5] Loading training data...")
    if not os.path.exists(data_path):
        print(f"  ✗ Data file not found: {data_path}")
        print("  Please run simulate_learning_data.py first")
        return
    
    interactions = load_simulated_data(data_path)
    print(f"  ✓ Loaded {len(interactions)} interactions")
    
    # Prepare episodes
    print("\n[4/5] Preparing training episodes...")
    episodes = prepare_training_episodes(interactions, state_builder)
    print(f"  ✓ Prepared {len(episodes)} student episodes")
    
    # Training loop
    print(f"\n[5/5] Training for {n_epochs} epochs...")
    
    for epoch in range(n_epochs):
        total_reward = 0.0
        n_episodes = 0
        
        for student_id, episode_data in episodes.items():
            if not episode_data:
                continue
            
            # Get initial state
            initial_state = np.array(interactions[0]['state_before'])
            
            # Train on episode
            episode_reward = agent.train_episode(initial_state, episode_data)
            total_reward += episode_reward
            n_episodes += 1
        
        avg_reward = total_reward / n_episodes if n_episodes > 0 else 0
        
        print(f"  Epoch {epoch+1}/{n_epochs}: "
              f"Avg reward = {avg_reward:.3f}, "
              f"Q-table size = {len(agent.q_table)}")
    
    # Get final statistics
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    
    stats = agent.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Episodes trained: {stats['episodes']}")
    print(f"  Total Q-updates: {stats['total_updates']}")
    print(f"  Q-table size: {stats['q_table_size']} states")
    print(f"  Avg actions/state: {stats['avg_actions_per_state']:.2f}")
    print(f"  Avg reward: {stats['avg_reward']:.3f}")
    
    # Save model
    print(f"\nSaving model...")
    os.makedirs(os.path.dirname(model_output), exist_ok=True)
    agent.save(model_output)
    print(f"  ✓ Model saved to: {model_output}")
    
    print("\n" + "=" * 70)
    print("✅ TRAINING SUCCESSFUL")
    print("=" * 70)
    
    return model_output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Train Q-learning model from simulated data'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='data/simulated/latest_simulation.json',
        help='Path to simulated data JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='models/qlearning_model.pkl',
        help='Output path for trained model'
    )
    parser.add_argument(
        '--lr',
        type=float,
        default=0.1,
        help='Learning rate (default: 0.1)'
    )
    parser.add_argument(
        '--gamma',
        type=float,
        default=0.95,
        help='Discount factor (default: 0.95)'
    )
    parser.add_argument(
        '--epsilon',
        type=float,
        default=0.1,
        help='Exploration rate (default: 0.1)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Number of training epochs (default: 10)'
    )
    
    args = parser.parse_args()
    
    train_qlearning(
        data_path=args.data,
        model_output=args.output,
        learning_rate=args.lr,
        discount_factor=args.gamma,
        epsilon=args.epsilon,
        n_epochs=args.epochs
    )
