#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train Q-Learning from Real Moodle Logs
=======================================
Train Q-learning agent từ episodes được extract từ log thô
"""

import os
import json
import argparse
import numpy as np
from typing import List, Dict

from core.state_builder import MoodleStateBuilder
from core.action_space import ActionSpace
from core.reward_calculator import RewardCalculator
from core.qlearning_agent import QLearningAgent


def load_episodes(episodes_path: str) -> List[Dict]:
    """Load episodes from JSON"""
    print(f"Loading episodes from {episodes_path}...")
    
    with open(episodes_path, 'r', encoding='utf-8') as f:
        episodes = json.load(f)
    
    print(f"  ✓ Loaded {len(episodes)} episodes")
    
    return episodes


def convert_features_to_state(features: Dict, state_builder: MoodleStateBuilder) -> np.ndarray:
    """
    Convert feature dict to state vector
    
    ⚠️ IMPORTANT: Features MUST match what moodle_log_processor.calculate_state_features() returns:
    - knowledge_level
    - engagement_level
    - struggle_indicator
    - submission_activity
    - review_activity
    - resource_usage
    - assessment_engagement
    - collaborative_activity
    - overall_progress
    - module_completion_rate
    - activity_diversity
    - completion_consistency
    
    Args:
        features: Dict with 12 features (from moodle_log_processor)
        state_builder: State builder instance
    
    Returns:
        State vector (12D) - same order as state_builder.build_state()
    """
    # Extract 12 features in EXACT order matching state_builder
    state = np.array([
        features.get('knowledge_level', 0.5),
        features.get('engagement_level', 0.0),
        features.get('struggle_indicator', 0.0),
        features.get('submission_activity', 0.0),
        features.get('review_activity', 0.0),
        features.get('resource_usage', 0.0),
        features.get('assessment_engagement', 0.0),
        features.get('collaborative_activity', 0.0),
        features.get('overall_progress', 0.0),
        features.get('module_completion_rate', 0.0),
        features.get('activity_diversity', 0.0),
        features.get('completion_consistency', 0.0)
    ], dtype=np.float32)
    
    # All values should already be in [0, 1] from moodle_log_processor
    # But clip just in case
    state = np.clip(state, 0.0, 1.0)
    
    return state


def map_action_to_id(action: Dict, action_space: ActionSpace) -> int:
    """
    Map action dict to action ID
    
    Args:
        action: Action dict {'type': 'quiz', 'module': 'quiz', ...}
        action_space: Action space instance
    
    Returns:
        Action ID (or random if not found)
    """
    # Try to find matching action in action space
    action_type = action['type']
    
    if action_type == 'quiz':
        actions = action_space.get_actions_by_type('quiz')
    elif action_type == 'assignment':
        actions = action_space.get_actions_by_type('assign')
    elif action_type == 'resource':
        actions = action_space.get_actions_by_type('resource')
    else:
        actions = action_space.get_actions()
    
    if len(actions) > 0:
        # Return first matching action (or random)
        return np.random.choice([a.id for a in actions])
    else:
        # Fallback: random action
        return np.random.randint(0, action_space.get_action_count())


def train_from_episodes(
    episodes: List[Dict],
    action_space: ActionSpace,
    state_builder: MoodleStateBuilder,
    n_epochs: int = 10,
    learning_rate: float = 0.1,
    gamma: float = 0.95,
    epsilon: float = 0.1
) -> QLearningAgent:
    """
    Train Q-learning agent from episodes
    
    Args:
        episodes: List of training episodes
        action_space: Action space
        state_builder: State builder
        n_epochs: Number of training epochs
        learning_rate: Learning rate (α)
        gamma: Discount factor (γ)
        epsilon: Exploration rate (ε)
    
    Returns:
        Trained Q-learning agent
    """
    print("\n" + "=" * 70)
    print("TRAINING Q-LEARNING FROM REAL LOGS")
    print("=" * 70)
    
    # Initialize agent
    agent = QLearningAgent(
        n_actions=action_space.get_action_count(),
        learning_rate=learning_rate,
        discount_factor=gamma,
        epsilon=epsilon
    )
    
    print(f"\nAgent parameters:")
    print(f"  Learning rate (α): {learning_rate}")
    print(f"  Discount factor (γ): {gamma}")
    print(f"  Exploration rate (ε): {epsilon}")
    
    # Train for multiple epochs
    for epoch in range(n_epochs):
        print(f"\n--- Epoch {epoch + 1}/{n_epochs} ---")
        
        epoch_rewards = []
        
        # Shuffle episodes
        np.random.shuffle(episodes)
        
        # Train on each episode
        for i, episode in enumerate(episodes):
            # Convert features to state
            state_before = convert_features_to_state(
                episode['state_before'],
                state_builder
            )
            state_after = convert_features_to_state(
                episode['state_after'],
                state_builder
            )
            
            # Map action to ID
            action_id = map_action_to_id(episode['action'], action_space)
            
            # Get reward
            reward = episode['reward']
            
            # Update Q-table
            agent.update(state_before, action_id, reward, state_after)
            
            epoch_rewards.append(reward)
            
            # Progress
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(episodes)} episodes", end='\r')
        
        # Epoch stats
        avg_reward = np.mean(epoch_rewards)
        print(f"\n  Avg reward: {avg_reward:.3f}")
        print(f"  Q-table size: {len(agent.q_table)} states")
    
    # Final stats
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    
    stats = agent.get_statistics()
    print(f"\nFinal statistics:")
    print(f"  Q-table size: {stats['q_table_size']} states")
    print(f"  Total updates: {stats['total_updates']}")
    print(f"  Avg actions/state: {stats['avg_actions_per_state']:.2f}")
    
    return agent


def main():
    parser = argparse.ArgumentParser(description='Train Q-learning from real Moodle logs')
    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to training episodes JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='models/qlearning_from_logs.pkl',
        help='Output model path'
    )
    parser.add_argument(
        '--course-structure',
        type=str,
        default='data/course_structure.json',
        help='Path to course structure'
    )
    parser.add_argument(
        '--cluster-profiles',
        type=str,
        default='data/cluster_profiles.json',
        help='Path to cluster profiles'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--lr',
        type=float,
        default=0.1,
        help='Learning rate'
    )
    parser.add_argument(
        '--gamma',
        type=float,
        default=0.95,
        help='Discount factor'
    )
    parser.add_argument(
        '--epsilon',
        type=float,
        default=0.1,
        help='Exploration rate'
    )
    
    args = parser.parse_args()
    
    # Load episodes
    episodes = load_episodes(args.data)
    
    # Initialize components
    print("\nInitializing components...")
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(args.course_structure)
    
    print(f"  ✓ State builder: 12 dimensions")
    print(f"  ✓ Action space: {action_space.get_action_count()} actions")
    
    # Train
    agent = train_from_episodes(
        episodes=episodes,
        action_space=action_space,
        state_builder=state_builder,
        n_epochs=args.epochs,
        learning_rate=args.lr,
        gamma=args.gamma,
        epsilon=args.epsilon
    )
    
    # Save model
    print(f"\nSaving model to {args.output}...")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    agent.save(args.output)
    print(f"  ✓ Model saved")
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nModel saved to: {args.output}")
    print(f"Episodes trained: {len(episodes)}")
    print(f"Q-table size: {len(agent.q_table)} states")
    print("\nNext steps:")
    print(f"  1. Test model: python demo_workflow.py --model {args.output}")
    print(f"  2. Daily updates: python update_daily_qtable.py --model {args.output}")


if __name__ == '__main__':
    main()
