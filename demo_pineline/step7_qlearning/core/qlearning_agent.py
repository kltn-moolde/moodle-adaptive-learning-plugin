#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Agent
================
Core Q-Learning agent cho adaptive learning recommendation
"""

import numpy as np
import pickle
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from models.course_structure import CourseStructure
from models.student_profile import StudentProfile
from models.outcome import LearningOutcome
from .state_builder import AbstractStateBuilder, DefaultStateBuilder
from .action_space import ActionSpace
from .reward_calculator import RewardCalculator, DefaultRewardCalculator


class QLearningAgent:
    """
    Q-Learning Agent
    
    Học policy: π(state) → best_action
    để maximize tổng reward (learning outcomes)
    
    Q-table: Dict[(state_hash, action_id)] = Q-value
    """
    
    def __init__(self,
                 course_structure: CourseStructure,
                 state_builder: Optional[AbstractStateBuilder] = None,
                 action_space: Optional[ActionSpace] = None,
                 reward_calculator: Optional[RewardCalculator] = None,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 0.1,
                 cluster_benchmarks: Optional[Dict] = None):
        """
        Initialize Q-Learning Agent
        
        Args:
            course_structure: CourseStructure object
            state_builder: Custom state builder (optional)
            action_space: Custom action space (optional)
            reward_calculator: Custom reward calculator (optional)
            learning_rate: Alpha (0-1)
            discount_factor: Gamma (0-1)
            epsilon: Exploration rate (0-1)
            cluster_benchmarks: Cluster statistics for reward calculation
        """
        self.course_structure = course_structure
        
        # Components
        self.state_builder = state_builder or DefaultStateBuilder(course_structure)
        self.action_space = action_space or ActionSpace(course_structure)
        self.reward_calculator = reward_calculator or DefaultRewardCalculator(
            course_structure, cluster_benchmarks
        )
        
        # Hyperparameters
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        # Q-table: (state_hash, action_id) -> Q-value
        self.Q: Dict[Tuple, float] = defaultdict(lambda: 0.0)
        
        # Training history
        self.training_history: List[Dict] = []
    
    def get_q_value(self, state: np.ndarray, action_id: str) -> float:
        """
        Lấy Q-value cho (state, action) pair
        
        Args:
            state: State vector
            action_id: Action ID
        
        Returns:
            Q-value
        """
        state_hash = self.state_builder.hash_state(state)
        return self.Q[(state_hash, action_id)]
    
    def set_q_value(self, state: np.ndarray, action_id: str, value: float):
        """
        Set Q-value
        
        Args:
            state: State vector
            action_id: Action ID
            value: Q-value
        """
        state_hash = self.state_builder.hash_state(state)
        self.Q[(state_hash, action_id)] = value
    
    def get_best_action(self, 
                       student_profile: StudentProfile,
                       current_timestamp: Optional[int] = None) -> Tuple[str, float]:
        """
        Lấy action tốt nhất (exploitation)
        
        Args:
            student_profile: StudentProfile object
            current_timestamp: Current timestamp
        
        Returns:
            (best_action_id, q_value)
        """
        available_actions = self.action_space.get_available_actions(student_profile)
        
        if not available_actions:
            return None, 0.0
        
        # Calculate Q-values for all available actions
        q_values = {}
        for action_id in available_actions:
            state = self.state_builder.build_state(
                student_profile, action_id, current_timestamp
            )
            q_values[action_id] = self.get_q_value(state, action_id)
        
        # Choose best action
        best_action = max(q_values, key=q_values.get)
        return best_action, q_values[best_action]
    
    def choose_action(self,
                     student_profile: StudentProfile,
                     current_timestamp: Optional[int] = None) -> Optional[str]:
        """
        Chọn action với epsilon-greedy
        
        Args:
            student_profile: StudentProfile object
            current_timestamp: Current timestamp
        
        Returns:
            action_id hoặc None
        """
        available_actions = self.action_space.get_available_actions(student_profile)
        
        if not available_actions:
            return None
        
        # Epsilon-greedy
        if np.random.random() < self.epsilon:
            # Exploration: Random action
            return np.random.choice(available_actions)
        else:
            # Exploitation: Best action
            best_action, _ = self.get_best_action(student_profile, current_timestamp)
            return best_action
    
    def update(self,
               student_profile: StudentProfile,
               action_id: str,
               outcome: LearningOutcome,
               next_student_profile: StudentProfile,
               current_timestamp: Optional[int] = None) -> Tuple[float, float]:
        """
        Update Q-value theo Bellman equation
        
        Q(s, a) = Q(s, a) + α * [R + γ * max Q(s', a') - Q(s, a)]
        
        Args:
            student_profile: Profile TRƯỚC action
            action_id: Action đã thực hiện
            outcome: Learning outcome
            next_student_profile: Profile SAU action
            current_timestamp: Timestamp
        
        Returns:
            (new_q_value, reward)
        """
        # Current state and Q-value
        state = self.state_builder.build_state(
            student_profile, action_id, current_timestamp
        )
        current_q = self.get_q_value(state, action_id)
        
        # Reward
        reward = self.reward_calculator.calculate_reward(
            student_profile, action_id, outcome
        )
        
        # Next state: Max Q-value
        next_actions = self.action_space.get_available_actions(next_student_profile)
        
        if next_actions:
            # Not terminal
            max_next_q = max([
                self.get_q_value(
                    self.state_builder.build_state(
                        next_student_profile, a, current_timestamp
                    ),
                    a
                )
                for a in next_actions
            ])
        else:
            # Terminal state
            max_next_q = 0.0
        
        # Bellman update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        
        # Store
        self.set_q_value(state, action_id, new_q)
        
        # Log
        self.training_history.append({
            'student_id': student_profile.student_id,
            'action': action_id,
            'reward': reward,
            'q_value': new_q,
            'outcome': outcome.to_dict(),
        })
        
        return new_q, reward
    
    def recommend(self,
                 student_profile: StudentProfile,
                 top_k: int = 1,
                 current_timestamp: Optional[int] = None) -> List[Dict]:
        """
        Gợi ý top-K activities cho sinh viên
        
        Args:
            student_profile: StudentProfile object
            top_k: Số lượng recommendations
            current_timestamp: Current timestamp
        
        Returns:
            List of recommendations: [{
                'activity_id': str,
                'activity_name': str,
                'activity_type': str,
                'q_value': float,
                'difficulty': float,
                'estimated_minutes': int,
                ...
            }]
        """
        available_actions = self.action_space.get_available_actions(student_profile)
        
        if not available_actions:
            return []
        
        # Calculate Q-values
        q_values = {}
        for action_id in available_actions:
            state = self.state_builder.build_state(
                student_profile, action_id, current_timestamp
            )
            q_values[action_id] = self.get_q_value(state, action_id)
        
        # Sort by Q-value
        sorted_actions = sorted(q_values.items(), key=lambda x: x[1], reverse=True)
        
        # Build recommendations
        recommendations = []
        for action_id, q_value in sorted_actions[:top_k]:
            activity = self.course_structure.activities[action_id]
            
            recommendations.append({
                'activity_id': action_id,
                'activity_name': activity.name,
                'activity_type': activity.activity_type.value,
                'q_value': q_value,
                'difficulty': activity.difficulty,
                'estimated_minutes': activity.estimated_minutes,
                'module_id': activity.module_id,
                'module_name': self.course_structure.modules[activity.module_id].name,
                'prerequisites_met': all(
                    p in student_profile.get_completed_activities()
                    for p in activity.prerequisites
                ),
            })
        
        return recommendations
    
    def save(self, filepath: str):
        """
        Lưu model (Q-table + config)
        
        Args:
            filepath: Path to save file
        """
        data = {
            'Q': dict(self.Q),
            'course_id': self.course_structure.course_id,
            'hyperparameters': {
                'alpha': self.alpha,
                'gamma': self.gamma,
                'epsilon': self.epsilon,
            },
            'training_history': self.training_history,
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"✅ Model saved to {filepath}")
    
    def load(self, filepath: str):
        """
        Load model
        
        Args:
            filepath: Path to model file
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.Q = defaultdict(lambda: 0.0, data['Q'])
        self.training_history = data.get('training_history', [])
        
        # Check course compatibility
        if data['course_id'] != self.course_structure.course_id:
            print(
                f"⚠️  Warning: Model trained on course {data['course_id']}, "
                f"but loading for course {self.course_structure.course_id}"
            )
        
        print(f"✅ Model loaded from {filepath}")
        print(f"   Q-table size: {len(self.Q)}")
        print(f"   Training history: {len(self.training_history)} updates")
    
    @classmethod
    def load_from_file(cls,
                      filepath: str,
                      course_structure: CourseStructure,
                      **kwargs) -> 'QLearningAgent':
        """
        Load agent from file
        
        Args:
            filepath: Path to model file
            course_structure: CourseStructure object
            **kwargs: Additional arguments for agent initialization
        
        Returns:
            QLearningAgent
        """
        agent = cls(course_structure, **kwargs)
        agent.load(filepath)
        return agent
    
    def get_statistics(self) -> Dict:
        """
        Lấy thống kê về Q-table và training
        
        Returns:
            Statistics dict
        """
        if not self.Q:
            return {
                'q_table_size': 0,
                'training_updates': 0,
            }
        
        q_values = list(self.Q.values())
        
        stats = {
            'q_table_size': len(self.Q),
            'unique_states': len(set(k[0] for k in self.Q.keys())),
            'unique_actions': len(set(k[1] for k in self.Q.keys())),
            'q_value_stats': {
                'mean': np.mean(q_values),
                'std': np.std(q_values),
                'min': np.min(q_values),
                'max': np.max(q_values),
            },
            'training_updates': len(self.training_history),
        }
        
        if self.training_history:
            rewards = [h['reward'] for h in self.training_history]
            stats['reward_stats'] = {
                'mean': np.mean(rewards),
                'std': np.std(rewards),
                'min': np.min(rewards),
                'max': np.max(rewards),
            }
        
        return stats
    
    def __repr__(self) -> str:
        return (
            f"QLearningAgent(course='{self.course_structure.course_id}', "
            f"Q-table_size={len(self.Q)}, "
            f"alpha={self.alpha}, gamma={self.gamma}, epsilon={self.epsilon})"
        )
