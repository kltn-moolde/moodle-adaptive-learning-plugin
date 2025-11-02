#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Agent
================
Tabular Q-Learning implementation for adaptive learning recommendations
"""

import numpy as np
import pickle
from typing import Dict, Tuple, Optional, List
from collections import defaultdict


class QLearningAgent:
    """
    Q-Learning Agent for Moodle Adaptive Learning
    
    Uses tabular Q-learning with state hashing to handle continuous states
    
    Hyperparameters:
    - learning_rate (α): 0.1
    - discount_factor (γ): 0.95
    - epsilon (ε): 0.1 (exploration rate)
    """
    
    def __init__(
        self,
        n_actions: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        state_decimals: int = 1,
        state_bins: Optional[List[float]] = None
    ):
        """
        Initialize Q-Learning Agent
        
        Args:
            n_actions: Number of possible actions
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
            epsilon: Exploration rate (ε)
            state_decimals: Decimal places for state hashing (used if state_bins=None)
            state_bins: Custom bin edges for state discretization (e.g., [0, 0.25, 0.5, 0.75, 1.0])
        """
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.state_decimals = state_decimals
        self.state_bins = state_bins  # ✅ New: Support custom bins
        
        # Q-table: {state_hash: {action_id: q_value}}
        self.q_table: Dict[Tuple, Dict[int, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        
        # Training statistics
        self.training_stats = {
            'episodes': 0,
            'total_updates': 0,
            'avg_reward': 0.0,
            'states_visited': 0
        }
    
    def hash_state(self, state: np.ndarray) -> Tuple:
        """
        Hash state vector to tuple (for Q-table key)
        
        Args:
            state: State vector
        
        Returns:
            Tuple (hashable)
        """
        # ✅ Use custom bins if provided, otherwise use decimals
        if self.state_bins is not None:
            # Custom binning - find which bin interval each value belongs to
            discretized = []
            for val in state:
                # Handle edge case: val >= max bin
                if val >= self.state_bins[-1]:
                    discretized.append(self.state_bins[-2])  # Second to last bin
                else:
                    # Find the bin: bins[i] <= val < bins[i+1]
                    bin_value = self.state_bins[0]
                    for i in range(len(self.state_bins)-1):
                        if self.state_bins[i] <= val < self.state_bins[i+1]:
                            bin_value = self.state_bins[i]
                            break
                    discretized.append(bin_value)
            return tuple(discretized)
        else:
            return tuple(np.round(state, decimals=self.state_decimals))
    
    def get_q_value(self, state: np.ndarray, action_id: int) -> float:
        """
        Get Q-value for (state, action) pair
        
        Args:
            state: State vector
            action_id: Action ID
        
        Returns:
            Q-value
        """
        state_hash = self.hash_state(state)
        return self.q_table[state_hash][action_id]
    
    def get_max_q_value(self, state: np.ndarray) -> float:
        """
        Get maximum Q-value for a state
        
        Args:
            state: State vector
        
        Returns:
            Max Q-value
        """
        state_hash = self.hash_state(state)
        
        if not self.q_table[state_hash]:
            return 0.0
        
        return max(self.q_table[state_hash].values())
    
    def select_action(
        self,
        state: np.ndarray,
        available_actions: List[int],
        explore: bool = True
    ) -> int:
        """
        Select action using ε-greedy policy
        
        Args:
            state: Current state
            available_actions: List of available action IDs
            explore: Whether to use exploration
        
        Returns:
            Selected action ID
        """
        if not available_actions:
            raise ValueError("No available actions")
        
        # Exploration
        if explore and np.random.random() < self.epsilon:
            return np.random.choice(available_actions)
        
        # Exploitation: choose best action
        state_hash = self.hash_state(state)
        q_values = {
            action_id: self.q_table[state_hash][action_id]
            for action_id in available_actions
        }
        
        # If all Q-values are 0, choose randomly
        if all(v == 0 for v in q_values.values()):
            return np.random.choice(available_actions)
        
        # Choose action with highest Q-value
        return max(q_values.items(), key=lambda x: x[1])[0]
    
    def update(
        self,
        state: np.ndarray,
        action_id: int,
        reward: float,
        next_state: np.ndarray,
        done: bool = False
    ):
        """
        Update Q-value using Q-learning update rule
        
        Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]
        
        Args:
            state: Current state
            action_id: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        state_hash = self.hash_state(state)
        
        # Current Q-value
        current_q = self.q_table[state_hash][action_id]
        
        # Max Q-value for next state
        if done:
            max_next_q = 0.0
        else:
            max_next_q = self.get_max_q_value(next_state)
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        # Update Q-table
        self.q_table[state_hash][action_id] = new_q
        
        # Update stats
        self.training_stats['total_updates'] += 1
    
    def train_episode(
        self,
        initial_state: np.ndarray,
        episode_data: List[Dict]
    ) -> float:
        """
        Train on one episode
        
        Args:
            initial_state: Starting state
            episode_data: List of {action_id, reward, next_state, done}
        
        Returns:
            Total episode reward
        """
        total_reward = 0.0
        state = initial_state
        
        for step in episode_data:
            action_id = step['action_id']
            reward = step['reward']
            next_state = step['next_state']
            done = step.get('done', False)
            
            # Update Q-table
            self.update(state, action_id, reward, next_state, done)
            
            # Move to next state
            state = next_state
            total_reward += reward
        
        # Update stats
        self.training_stats['episodes'] += 1
        self.training_stats['avg_reward'] = (
            (self.training_stats['avg_reward'] * (self.training_stats['episodes'] - 1) + total_reward) /
            self.training_stats['episodes']
        )
        self.training_stats['states_visited'] = len(self.q_table)
        
        return total_reward
    
    def recommend_action(
        self,
        state: np.ndarray,
        available_actions: List[int],
        top_k: int = 3,
        fallback_random: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Recommend top-k actions for a state
        
        Args:
            state: Current state
            available_actions: List of available action IDs
            top_k: Number of recommendations
            fallback_random: If no learned Q-values, return random actions
        
        Returns:
            List of (action_id, q_value) sorted by Q-value
        """
        state_hash = self.hash_state(state)
        
        # Get Q-values for all available actions
        q_values = [
            (action_id, self.q_table[state_hash][action_id])
            for action_id in available_actions
        ]
        
        # Sort by Q-value (descending)
        q_values.sort(key=lambda x: x[1], reverse=True)
        
        # If all Q-values are 0 and fallback enabled, return random sample
        if fallback_random and all(q == 0 for _, q in q_values):
            # Sample random actions
            import random
            random_actions = random.sample(available_actions, min(top_k, len(available_actions)))
            return [(action_id, 0.0) for action_id in random_actions]
        
        return q_values[:top_k]
    
    def save(self, filepath: str):
        """
        Save Q-table and parameters to file
        
        Args:
            filepath: Path to save file
        """
        data = {
            'q_table': dict(self.q_table),
            'n_actions': self.n_actions,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'state_decimals': self.state_decimals,
            'state_bins': self.state_bins,  # ✅ Save bins for discretization
            'training_stats': self.training_stats
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filepath: str):
        """
        Load Q-table and parameters from file
        
        Args:
            filepath: Path to load file
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        # Reconstruct Q-table
        self.q_table = defaultdict(lambda: defaultdict(float))
        for state_hash, actions in data['q_table'].items():
            self.q_table[state_hash].update(actions)
        
        self.n_actions = data['n_actions']
        self.learning_rate = data['learning_rate']
        self.discount_factor = data['discount_factor']
        self.epsilon = data['epsilon']
        self.state_decimals = data['state_decimals']
        self.state_bins = data.get('state_bins', None)  # ✅ Load bins (with backward compat)
        self.training_stats = data.get('training_stats', self.training_stats)
    
    def get_statistics(self) -> Dict:
        """Get training statistics"""
        return {
            **self.training_stats,
            'q_table_size': len(self.q_table),
            'avg_actions_per_state': (
                np.mean([len(actions) for actions in self.q_table.values()])
                if self.q_table else 0
            )
        }


# Example usage
if __name__ == '__main__':
    print("=" * 70)
    print("Q-LEARNING AGENT TEST")
    print("=" * 70)
    
    # Create agent
    agent = QLearningAgent(n_actions=10, learning_rate=0.1, epsilon=0.1)
    
    # Sample state (12 dims)
    state = np.array([0.5, 0.6, 0.4, 0.3, 0.5, 0.6, 0.7, 0.2, 0.5, 0.6, 0.4, 0.7])
    
    # Available actions
    available_actions = [1, 2, 3, 4, 5]
    
    # Select action
    action = agent.select_action(state, available_actions)
    print(f"\nSelected action: {action}")
    
    # Simulate next state and reward
    next_state = state + np.random.randn(12) * 0.1
    reward = np.random.uniform(0, 1)
    
    # Update Q-table
    agent.update(state, action, reward, next_state)
    
    print(f"Updated Q-value: {agent.get_q_value(state, action):.4f}")
    
    # Train multiple episodes
    print("\nTraining 100 episodes...")
    for _ in range(100):
        episode_data = []
        for step in range(10):
            action = agent.select_action(state, available_actions)
            reward = np.random.uniform(0, 1)
            next_state = state + np.random.randn(12) * 0.1
            episode_data.append({
                'action_id': action,
                'reward': reward,
                'next_state': next_state,
                'done': step == 9
            })
            state = next_state
        
        agent.train_episode(state, episode_data)
    
    # Get statistics
    stats = agent.get_statistics()
    print(f"\nTraining Statistics:")
    print(f"  Episodes: {stats['episodes']}")
    print(f"  Total updates: {stats['total_updates']}")
    print(f"  Avg reward: {stats['avg_reward']:.4f}")
    print(f"  Q-table size: {stats['q_table_size']}")
    print(f"  Avg actions/state: {stats['avg_actions_per_state']:.2f}")
    
    # Get recommendations
    recommendations = agent.recommend_action(state, available_actions, top_k=3)
    print(f"\nTop 3 recommendations:")
    for i, (action_id, q_val) in enumerate(recommendations):
        print(f"  {i+1}. Action {action_id}: Q={q_val:.4f}")
