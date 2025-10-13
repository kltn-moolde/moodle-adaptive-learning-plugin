#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Agent v2.0
=====================
Refactored để work với MoodleStateBuilder và ActionSpace mới

Changes from v1:
- State: MoodleStateBuilder (12 dims) thay vì AbstractStateBuilder (22 dims)
- Action: ActionSpace với resource IDs thay vì CourseStructure activities
- Simplified API
"""

import numpy as np
import pickle
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from pathlib import Path

from .state_discretizer import StateDiscretizer
from .heuristic_recommender import HeuristicRecommender

from .moodle_state_builder import MoodleStateBuilder
from .action_space import ActionSpace, Action


class QLearningAgentV2:
    """
    Q-Learning Agent v2.0 - Moodle Integration
    
    Q-Learning formula:
    Q(s,a) ← Q(s,a) + α[r + γ·max_a' Q(s',a') - Q(s,a)]
    
    Components:
    - State: 12-dim vector từ Moodle logs
    - Action: Resource IDs từ course structure
    - Q-table: Dict[(state_hash, action_id)] = Q-value
    """
    
    def __init__(self,
                 state_builder: MoodleStateBuilder,
                 action_space: ActionSpace,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 0.1,
                 n_bins: int = 3):
        """
        Initialize Q-Learning Agent
        
        Args:
            state_builder: MoodleStateBuilder instance
            action_space: ActionSpace instance
            learning_rate: Alpha (0-1)
            discount_factor: Gamma (0-1)
            epsilon: Exploration rate for epsilon-greedy
            n_bins: Number of bins for state discretization (3 or 5)
        """
        self.state_builder = state_builder
        self.action_space = action_space
        
        # State discretizer
        state_dim = state_builder.get_state_dimension()
        self.discretizer = StateDiscretizer(state_dim=state_dim, n_bins=n_bins)
        
        # Heuristic fallback
        self.heuristic = HeuristicRecommender()
        
        # Hyperparameters
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        # Q-table: (discrete_state, action_id) -> Q-value
        self.Q: Dict[Tuple, float] = {}  # Changed from defaultdict to regular dict
        self._default_q_value = 0.0  # Default for unseen state-action pairs
        
        # Statistics
        self.training_updates = 0
        self.reward_history: List[float] = []
    
    def get_q_value(self, state: np.ndarray, action_id: str) -> float:
        """
        Lấy Q-value cho (state, action)
        
        Args:
            state: State vector (12 dims)
            action_id: Action ID (resource ID)
        
        Returns:
            Q-value (default 0.0 nếu chưa explore)
        """
        discrete_state = self.discretizer.discretize(state)
        return self.Q.get((discrete_state, action_id), self._default_q_value)
    
    def set_q_value(self, state: np.ndarray, action_id: str, value: float):
        """Set Q-value"""
        discrete_state = self.discretizer.discretize(state)
        self.Q[(discrete_state, action_id)] = value
    
    def get_best_action(self,
                       state: np.ndarray,
                       available_actions: List[Action]) -> Optional[Action]:
        """
        Lấy best action theo Q-values (greedy)
        
        Args:
            state: State vector
            available_actions: List of available actions
        
        Returns:
            Best action hoặc None nếu không có action
        """
        if not available_actions:
            return None
        
        # Get Q-values for all available actions
        q_values = {
            action: self.get_q_value(state, action.action_id)
            for action in available_actions
        }
        
        # Return action with max Q-value
        best_action = max(q_values, key=q_values.get)
        return best_action
    
    def choose_action(self,
                     state: np.ndarray,
                     available_actions: List[Action],
                     explore: bool = True) -> Optional[Action]:
        """
        Chọn action theo epsilon-greedy policy
        
        Args:
            state: State vector
            available_actions: List of available actions
            explore: Enable exploration (epsilon-greedy)
        
        Returns:
            Selected action
        """
        if not available_actions:
            return None
        
        # Epsilon-greedy
        if explore and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best action
            return self.get_best_action(state, available_actions)
    
    def update(self,
              state: np.ndarray,
              action_id: str,
              reward: float,
              next_state: np.ndarray,
              next_available_actions: List[Action]) -> float:
        """
        Q-Learning update
        
        Q(s,a) ← Q(s,a) + α[r + γ·max_a' Q(s',a') - Q(s,a)]
        
        Args:
            state: Current state
            action_id: Action taken
            reward: Reward received
            next_state: Next state
            next_available_actions: Available actions in next state
        
        Returns:
            New Q-value
        """
        # Current Q-value
        current_q = self.get_q_value(state, action_id)
        
        # Max Q-value for next state
        if next_available_actions:
            next_q_values = [
                self.get_q_value(next_state, a.action_id)
                for a in next_available_actions
            ]
            max_next_q = max(next_q_values)
        else:
            # Terminal state
            max_next_q = 0.0
        
        # Bellman update
        new_q = current_q + self.alpha * (
            reward + self.gamma * max_next_q - current_q
        )
        
        # Update Q-table
        self.set_q_value(state, action_id, new_q)
        
        # Statistics
        self.training_updates += 1
        self.reward_history.append(reward)
        
        return new_q
    
    def recommend(self,
                 state: np.ndarray,
                 available_actions: List[Action],
                 top_k: int = 5,
                 use_heuristic_fallback: bool = True) -> List[Dict]:
        """
        Gợi ý top-k actions dựa trên Q-values với heuristic fallback
        
        Args:
            state: Student state
            available_actions: Available actions
            top_k: Number of recommendations
            use_heuristic_fallback: Use heuristic nếu tất cả Q-values = 0
        
        Returns:
            List of recommendations với Q-values và heuristic scores
        """
        if not available_actions:
            return []
        
        # Calculate Q-values
        recommendations = []
        has_nonzero_q = False
        
        for action in available_actions:
            q_value = self.get_q_value(state, action.action_id)
            if q_value != 0:
                has_nonzero_q = True
            
            rec = action.to_dict()
            rec['q_value'] = q_value
            recommendations.append(rec)
        
        # Check if we need heuristic fallback
        if not has_nonzero_q and use_heuristic_fallback:
            # All Q-values = 0 → Use heuristic
            heuristic_recs = self.heuristic.recommend(
                state, 
                available_actions, 
                top_k=top_k
            )
            
            # Merge Q-values with heuristic scores
            for i, rec in enumerate(recommendations):
                # Find matching heuristic rec
                matching_heuristic = next(
                    (h for h in heuristic_recs 
                     if h['action_id'] == rec['action_id']),
                    None
                )
                
                if matching_heuristic:
                    rec['heuristic_score'] = matching_heuristic['heuristic_score']
                    rec['student_profile'] = matching_heuristic['student_profile']
                else:
                    rec['heuristic_score'] = 0.0
            
            # Sort by heuristic score
            recommendations.sort(key=lambda x: x.get('heuristic_score', 0), reverse=True)
            
            # Mark as heuristic-based
            for rec in recommendations[:top_k]:
                rec['recommendation_method'] = 'heuristic'
        else:
            # Sort by Q-value descending
            recommendations.sort(key=lambda x: x['q_value'], reverse=True)
            
            # Mark as Q-learning-based
            for rec in recommendations[:top_k]:
                rec['recommendation_method'] = 'q_learning'
        
        return recommendations[:top_k]
    
    def initialize_q_table(self, student_states: List[np.ndarray]):
        """
        Pre-initialize Q-table với possible states từ training data
        
        Args:
            student_states: List of state vectors từ training students
        """
        # Get all unique discrete states
        discrete_states = set()
        for state in student_states:
            discrete_state = self.discretizer.discretize(state)
            discrete_states.add(discrete_state)
        
        # Get all actions
        all_actions = self.action_space.get_all_actions()
        
        # Initialize Q-table
        for discrete_state in discrete_states:
            for action in all_actions:
                key = (discrete_state, action.action_id)
                if key not in self.Q:
                    self.Q[key] = self._default_q_value
        
        print(f"✅ Q-table initialized with {len(discrete_states)} states × "
              f"{len(all_actions)} actions = {len(self.Q)} entries")
    
    def get_statistics(self) -> Dict:
        """
        Lấy thống kê về training
        
        Returns:
            Dict with statistics
        """
        stats = {
            'q_table_size': len(self.Q),
            'training_updates': self.training_updates,
            'total_actions': self.action_space.get_action_space_size(),
        }
        
        if self.reward_history:
            stats['reward_stats'] = {
                'mean': float(np.mean(self.reward_history)),
                'std': float(np.std(self.reward_history)),
                'min': float(np.min(self.reward_history)),
                'max': float(np.max(self.reward_history)),
                'total_episodes': len(self.reward_history)
            }
        
        return stats
    
    def save(self, filepath: str):
        """
        Save agent to file
        
        Args:
            filepath: Path to save file (.pkl or .json)
        """
        path = Path(filepath)
        
        # Prepare data
        data = {
            'hyperparameters': {
                'alpha': self.alpha,
                'gamma': self.gamma,
                'epsilon': self.epsilon
            },
            'q_table': {
                str(k): v for k, v in self.Q.items()
            },
            'statistics': self.get_statistics()
        }
        
        if path.suffix == '.json':
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            # Save as pickle (default)
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        
        print(f"✅ Agent saved to: {filepath}")
    
    def load(self, filepath: str):
        """
        Load agent from file
        
        Args:
            filepath: Path to saved file
        """
        path = Path(filepath)
        
        if path.suffix == '.json':
            # Load from JSON
            with open(filepath, 'r') as f:
                data = json.load(f)
        else:
            # Load from pickle
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
        
        # Restore hyperparameters
        self.alpha = data['hyperparameters']['alpha']
        self.gamma = data['hyperparameters']['gamma']
        self.epsilon = data['hyperparameters']['epsilon']
        
        # Restore Q-table
        self.Q = defaultdict(lambda: 0.0)
        for k_str, v in data['q_table'].items():
            k = eval(k_str)  # Convert string back to tuple
            self.Q[k] = v
        
        # Restore statistics
        stats = data['statistics']
        self.training_updates = stats.get('training_updates', 0)
        
        print(f"✅ Agent loaded from: {filepath}")
        print(f"   Q-table size: {len(self.Q)}")
        print(f"   Training updates: {self.training_updates}")
    
    @staticmethod
    def create_from_course(course_json_path: str,
                          learning_rate: float = 0.1,
                          discount_factor: float = 0.95,
                          epsilon: float = 0.1,
                          n_bins: int = 3) -> 'QLearningAgentV2':
        """
        Factory method: Create agent từ course structure JSON
        
        Args:
            course_json_path: Path to course structure JSON
            learning_rate: Alpha
            discount_factor: Gamma
            epsilon: Exploration rate
            n_bins: Number of bins for state discretization
        
        Returns:
            QLearningAgentV2 instance
        """
        state_builder = MoodleStateBuilder()
        action_space = ActionSpace.load_from_file(course_json_path)
        
        return QLearningAgentV2(
            state_builder=state_builder,
            action_space=action_space,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon=epsilon,
            n_bins=n_bins
        )
    
    def __repr__(self) -> str:
        return (
            f"QLearningAgentV2("
            f"Q-table_size={len(self.Q)}, "
            f"actions={self.action_space.get_action_space_size()}, "
            f"bins={self.discretizer.n_bins}, "
            f"alpha={self.alpha}, "
            f"gamma={self.gamma}, "
            f"epsilon={self.epsilon})"
        )


# Backward compatibility alias
QLearningAgent = QLearningAgentV2
