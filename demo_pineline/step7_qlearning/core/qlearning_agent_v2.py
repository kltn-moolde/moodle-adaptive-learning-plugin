"""
Q-Learning Agent V2
Implements Q-Learning algorithm for adaptive learning path recommendation

This module provides a Q-Learning agent that learns optimal learning paths
for students based on their cluster and current state.
"""

import numpy as np
import json
import pickle
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class QLearningAgentV2:
    """
    Q-Learning Agent with cluster-aware policy
    
    Features:
    - State-action Q-table
    - ε-greedy exploration
    - Temporal difference learning
    - Cluster-specific learning rates
    - Experience replay support
    """
    
    def __init__(
        self,
        n_actions: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        cluster_adaptive: bool = True
    ):
        """
        Initialize Q-Learning agent
        
        Args:
            n_actions: Number of possible actions
            learning_rate: Learning rate (α) for Q-updates
            discount_factor: Discount factor (γ) for future rewards
            epsilon: Initial exploration rate for ε-greedy policy
            epsilon_decay: Decay rate for epsilon per episode
            epsilon_min: Minimum epsilon value
            cluster_adaptive: Use cluster-specific learning rates
        """
        print("=" * 60)
        print("Initializing QLearningAgentV2...")
        print("=" * 60)
        
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.cluster_adaptive = cluster_adaptive
        
        # Q-table: Q[state][action] = value
        # Using defaultdict with lambda to return dict of zeros
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Statistics
        self.stats = {
            'episodes_trained': 0,
            'total_updates': 0,
            'epsilon_history': [epsilon],
            'q_table_size': 0
        }
        
        # Cluster-specific learning rates (if adaptive)
        if cluster_adaptive:
            self.cluster_learning_rates = {
                0: 0.15,  # Weak: higher LR (need more adaptation)
                1: 0.10,  # Medium
                2: 0.10,  # Medium
                3: 0.08,  # Strong: lower LR (more stable)
                4: 0.08   # Strong
            }
        else:
            self.cluster_learning_rates = {i: learning_rate for i in range(5)}
        
        print(f"\n✓ Configuration:")
        print(f"    n_actions: {n_actions}")
        print(f"    learning_rate: {learning_rate}")
        print(f"    discount_factor: {discount_factor}")
        print(f"    epsilon: {epsilon} → {epsilon_min} (decay: {epsilon_decay})")
        print(f"    cluster_adaptive: {cluster_adaptive}")
        
        if cluster_adaptive:
            print(f"\n✓ Cluster-specific learning rates:")
            for cluster_id, lr in self.cluster_learning_rates.items():
                print(f"    Cluster {cluster_id}: {lr:.3f}")
        
        print("=" * 60)
    
    def get_q_value(self, state: Tuple, action: int) -> float:
        """
        Get Q-value for state-action pair
        
        Args:
            state: State tuple
            action: Action ID
            
        Returns:
            Q-value (0.0 if never seen)
        """
        return self.q_table[state][action]
    
    def get_max_q_value(self, state: Tuple) -> float:
        """
        Get maximum Q-value for a state
        
        Args:
            state: State tuple
            
        Returns:
            Maximum Q-value across all actions
        """
        if state not in self.q_table or not self.q_table[state]:
            return 0.0
        return max(self.q_table[state].values())
    
    def get_best_action(self, state: Tuple) -> int:
        """
        Get best action for a state (exploitation)
        
        Args:
            state: State tuple
            
        Returns:
            Action with highest Q-value
        """
        if state not in self.q_table or not self.q_table[state]:
            # Random action if state never seen
            return np.random.randint(0, self.n_actions)
        
        # Get action with max Q-value
        q_values = self.q_table[state]
        max_q = max(q_values.values())
        
        # Handle ties by random selection
        best_actions = [a for a, q in q_values.items() if q == max_q]
        return np.random.choice(best_actions)
    
    def select_action(self, state: Tuple, valid_actions: Optional[List[int]] = None) -> int:
        """
        Select action using ε-greedy policy
        
        Args:
            state: Current state tuple
            valid_actions: List of valid action IDs (None = all actions)
            
        Returns:
            Selected action ID
        """
        # ε-greedy policy
        if np.random.random() < self.epsilon:
            # Exploration: random action
            if valid_actions:
                return np.random.choice(valid_actions)
            else:
                return np.random.randint(0, self.n_actions)
        else:
            # Exploitation: best action
            if valid_actions:
                # Get Q-values for valid actions only
                if state in self.q_table:
                    valid_q = {a: self.q_table[state].get(a, 0.0) for a in valid_actions}
                    max_q = max(valid_q.values())
                    best_actions = [a for a, q in valid_q.items() if q == max_q]
                    return np.random.choice(best_actions)
                else:
                    return np.random.choice(valid_actions)
            else:
                return self.get_best_action(state)
    
    def update(
        self,
        state: Tuple,
        action: int,
        reward: float,
        next_state: Tuple,
        is_terminal: bool = False
    ):
        """
        Update Q-value using Q-learning update rule
        
        Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            is_terminal: Whether next_state is terminal
        """
        # Get current Q-value
        current_q = self.get_q_value(state, action)
        
        # Get max Q-value for next state
        if is_terminal:
            max_next_q = 0.0
        else:
            max_next_q = self.get_max_q_value(next_state)
        
        # Q-learning update
        td_target = reward + self.discount_factor * max_next_q
        td_error = td_target - current_q
        
        # Get learning rate (cluster-adaptive if enabled)
        if self.cluster_adaptive and len(state) > 0:
            cluster_id = state[0]  # First element of state is cluster
            alpha = self.cluster_learning_rates.get(cluster_id, self.learning_rate)
        else:
            alpha = self.learning_rate
        
        # Update Q-value
        new_q = current_q + alpha * td_error
        self.q_table[state][action] = new_q
        
        # Update statistics
        self.stats['total_updates'] += 1
    
    def train_episode(self, trajectory: List[Dict], verbose: bool = False) -> Dict:
        """
        Train on a single trajectory (episode)
        
        Args:
            trajectory: List of transition dicts
            verbose: Print training info
            
        Returns:
            Episode statistics
        """
        total_reward = 0.0
        n_updates = 0
        
        for transition in trajectory:
            state = transition['state']
            action = transition['action']
            reward = transition['reward']
            next_state = transition['next_state']
            is_terminal = transition['is_terminal']
            
            # Update Q-value
            self.update(state, action, reward, next_state, is_terminal)
            
            total_reward += reward
            n_updates += 1
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Update statistics
        self.stats['episodes_trained'] += 1
        self.stats['epsilon_history'].append(self.epsilon)
        self.stats['q_table_size'] = len(self.q_table)
        
        episode_stats = {
            'total_reward': total_reward,
            'n_updates': n_updates,
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table)
        }
        
        if verbose:
            print(f"  Episode {self.stats['episodes_trained']}: "
                  f"reward={total_reward:.2f}, updates={n_updates}, "
                  f"ε={self.epsilon:.4f}, Q-table size={len(self.q_table)}")
        
        return episode_stats
    
    def train_batch(
        self,
        trajectories: Dict[int, List[Dict]],
        n_epochs: int = 1,
        shuffle: bool = True,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Train on multiple trajectories
        
        Args:
            trajectories: Dictionary mapping student_id -> trajectory
            n_epochs: Number of epochs to train
            shuffle: Shuffle trajectories each epoch
            verbose: Print progress
            
        Returns:
            List of epoch statistics
        """
        if verbose:
            print("\n" + "=" * 60)
            print("Training Q-Learning Agent")
            print("=" * 60)
            print(f"\nConfiguration:")
            print(f"  Trajectories: {len(trajectories)}")
            print(f"  Epochs: {n_epochs}")
            print(f"  Shuffle: {shuffle}")
        
        epoch_stats_list = []
        trajectory_list = list(trajectories.values())
        
        for epoch in range(n_epochs):
            if verbose:
                print(f"\n{'='*60}")
                print(f"Epoch {epoch+1}/{n_epochs}")
                print(f"{'='*60}")
            
            # Shuffle trajectories
            if shuffle:
                np.random.shuffle(trajectory_list)
            
            # Train on each trajectory
            epoch_rewards = []
            epoch_updates = []
            
            for i, trajectory in enumerate(trajectory_list):
                episode_stats = self.train_episode(trajectory, verbose=False)
                epoch_rewards.append(episode_stats['total_reward'])
                epoch_updates.append(episode_stats['n_updates'])
                
                # Print progress every 10 trajectories
                if verbose and (i + 1) % 10 == 0:
                    print(f"  Progress: {i+1}/{len(trajectory_list)} trajectories")
            
            # Epoch statistics
            epoch_stats = {
                'epoch': epoch + 1,
                'avg_reward': np.mean(epoch_rewards),
                'std_reward': np.std(epoch_rewards),
                'min_reward': np.min(epoch_rewards),
                'max_reward': np.max(epoch_rewards),
                'total_updates': sum(epoch_updates),
                'epsilon': self.epsilon,
                'q_table_size': len(self.q_table)
            }
            epoch_stats_list.append(epoch_stats)
            
            if verbose:
                print(f"\n  Epoch {epoch+1} Summary:")
                print(f"    Avg reward: {epoch_stats['avg_reward']:.2f} ± {epoch_stats['std_reward']:.2f}")
                print(f"    Reward range: [{epoch_stats['min_reward']:.2f}, {epoch_stats['max_reward']:.2f}]")
                print(f"    Total updates: {epoch_stats['total_updates']}")
                print(f"    Epsilon: {epoch_stats['epsilon']:.4f}")
                print(f"    Q-table size: {epoch_stats['q_table_size']} states")
        
        if verbose:
            print("\n" + "=" * 60)
            print("✓ Training completed!")
            print("=" * 60)
            print(f"\n  Final Statistics:")
            print(f"    Total episodes: {self.stats['episodes_trained']}")
            print(f"    Total updates: {self.stats['total_updates']}")
            print(f"    Q-table size: {len(self.q_table)} states")
            print(f"    Final epsilon: {self.epsilon:.4f}")
        
        return epoch_stats_list
    
    def save(self, filepath: str):
        """
        Save Q-table and agent configuration
        
        Args:
            filepath: Path to save file (.pkl or .json)
        """
        print(f"\nSaving agent to: {filepath}")
        
        # Convert Q-table to serializable format
        q_table_serializable = {}
        for state, actions in self.q_table.items():
            state_key = str(state)
            q_table_serializable[state_key] = dict(actions)
        
        data = {
            'q_table': q_table_serializable,
            'config': {
                'n_actions': self.n_actions,
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
                'cluster_adaptive': self.cluster_adaptive,
                'cluster_learning_rates': self.cluster_learning_rates
            },
            'stats': self.stats
        }
        
        # Save based on file extension
        if filepath.endswith('.pkl'):
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        elif filepath.endswith('.json'):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError("Filepath must end with .pkl or .json")
        
        print(f"✓ Saved Q-table with {len(self.q_table)} states")
    
    def load(self, filepath: str):
        """
        Load Q-table and agent configuration
        
        Args:
            filepath: Path to load file (.pkl or .json)
        """
        print(f"\nLoading agent from: {filepath}")
        
        # Load based on file extension
        if filepath.endswith('.pkl'):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
        elif filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError("Filepath must end with .pkl or .json")
        
        # Restore Q-table
        self.q_table = defaultdict(lambda: defaultdict(float))
        for state_key, actions in data['q_table'].items():
            state = eval(state_key)  # Convert string back to tuple
            self.q_table[state] = defaultdict(float, actions)
        
        # Restore config
        config = data['config']
        self.n_actions = config['n_actions']
        self.learning_rate = config['learning_rate']
        self.discount_factor = config['discount_factor']
        self.epsilon = config['epsilon']
        self.epsilon_decay = config['epsilon_decay']
        self.epsilon_min = config['epsilon_min']
        self.cluster_adaptive = config['cluster_adaptive']
        self.cluster_learning_rates = config['cluster_learning_rates']
        
        # Restore stats
        self.stats = data['stats']
        
        print(f"✓ Loaded Q-table with {len(self.q_table)} states")
        print(f"✓ Episodes trained: {self.stats['episodes_trained']}")
        print(f"✓ Total updates: {self.stats['total_updates']}")
    
    def get_statistics(self) -> Dict:
        """Get agent statistics"""
        return {
            **self.stats,
            'current_epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'avg_actions_per_state': np.mean([len(actions) for actions in self.q_table.values()]) if self.q_table else 0
        }
    
    def recommend_action(
        self,
        state: Tuple,
        available_actions: List[int],
        top_k: int = 3,
        fallback_random: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Recommend top-K actions for a given state
        
        Args:
            state: State tuple
            available_actions: List of available action IDs
            top_k: Number of recommendations to return
            fallback_random: If True, return random actions when state not in Q-table
            
        Returns:
            List of (action_id, q_value) tuples sorted by Q-value (descending)
        """
        if state not in self.q_table or not self.q_table[state]:
            # State never seen - return random or zero Q-values
            if fallback_random:
                selected = np.random.choice(available_actions, size=min(top_k, len(available_actions)), replace=False)
                return [(int(a), 0.0) for a in selected]
            else:
                # Return available actions with Q=0
                return [(a, 0.0) for a in available_actions[:top_k]]
        
        # Get Q-values for available actions
        q_values = self.q_table[state]
        action_q_pairs = [(a, q_values.get(a, 0.0)) for a in available_actions]
        
        # Sort by Q-value (descending)
        action_q_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-K
        return action_q_pairs[:top_k]


def test_qlearning_agent():
    """Test basic QLearningAgentV2 functionality"""
    print("=" * 60)
    print("Testing QLearningAgentV2")
    print("=" * 60)
    
    # Create agent
    agent = QLearningAgentV2(n_actions=10, learning_rate=0.1)
    
    # Test states (cluster, module, progress, score, action, stuck)
    state1 = (0, 5, 0.5, 0.7, 2, 0)
    state2 = (1, 10, 0.75, 0.8, 3, 0)
    
    print("\n1. Testing action selection:")
    action = agent.select_action(state1)
    print(f"  Selected action for {state1}: {action}")
    
    print("\n2. Testing Q-value update:")
    agent.update(state1, 3, 1.5, state2)
    print(f"  Q-value after update: {agent.get_q_value(state1, 3):.4f}")
    
    print("\n3. Testing save/load:")
    agent.save("test_model.pkl")
    print(f"  Saved model to test_model.pkl")
    
    print("\n4. Agent statistics:")
    stats = agent.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        elif isinstance(value, list):
            print(f"  {key}: (length {len(value)})")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ QLearningAgentV2 test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_qlearning_agent()
