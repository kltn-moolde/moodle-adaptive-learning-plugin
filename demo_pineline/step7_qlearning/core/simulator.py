#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Simulator
==================
Mô phỏng hành vi học tập của học viên dựa trên cluster profiles
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from .state_builder import MoodleStateBuilder
from .action_space import ActionSpace, LearningAction
from .reward_calculator import RewardCalculator


@dataclass
class SimulatedInteraction:
    """Một interaction mô phỏng"""
    student_id: int
    cluster_id: int
    action_id: int
    action_name: str
    action_type: str
    timestamp: str
    completed: bool
    score: float
    time_spent: int  # minutes
    attempts: int
    reward: float
    state_before: List[float]
    state_after: List[float]


class LearningSimulator:
    """
    Simulator for Moodle Learning Behaviors
    
    Mô phỏng hành vi học tập dựa trên:
    1. Cluster profiles (hành vi điển hình)
    2. Action space (các hoạt động có sẵn)
    3. Student state (trạng thái học viên)
    """
    
    def __init__(
        self,
        state_builder: MoodleStateBuilder,
        action_space: ActionSpace,
        reward_calculator: RewardCalculator
    ):
        """
        Initialize simulator
        
        Args:
            state_builder: State builder instance
            action_space: Action space instance
            reward_calculator: Reward calculator instance
        """
        self.state_builder = state_builder
        self.action_space = action_space
        self.reward_calculator = reward_calculator
        
        # Simulation parameters
        # Try to derive cluster behaviors from provided cluster profiles (if loaded)
        # Fallback to the hard-coded defaults in _define_cluster_behaviors
        derived = self._build_behaviors_from_profiles()
        if derived:
            self.cluster_behaviors = derived
        else:
            self.cluster_behaviors = self._define_cluster_behaviors()
    
    def _define_cluster_behaviors(self) -> Dict[int, Dict]:
        """
        Define behavior patterns cho mỗi cluster
        
        Returns:
            Dict {cluster_id: behavior_params}
        """
        return {
            # Cluster 0: Weak students
            0: {
                'completion_rate': 0.4,
                'avg_score': 0.45,
                'avg_attempts': 3.5,
                'time_multiplier': 1.5,
                'prefer_easy': True,
                'engagement': 0.4
            },
            # Cluster 1: Struggling students
            1: {
                'completion_rate': 0.5,
                'avg_score': 0.55,
                'avg_attempts': 2.8,
                'time_multiplier': 1.3,
                'prefer_easy': True,
                'engagement': 0.5
            },
            # Cluster 2: Average students (low engagement)
            2: {
                'completion_rate': 0.6,
                'avg_score': 0.65,
                'avg_attempts': 2.0,
                'time_multiplier': 1.0,
                'prefer_easy': False,
                'engagement': 0.6
            },
            # Cluster 3: Average students (high engagement)
            3: {
                'completion_rate': 0.75,
                'avg_score': 0.75,
                'avg_attempts': 1.5,
                'time_multiplier': 0.9,
                'prefer_easy': False,
                'engagement': 0.75
            },
            # Cluster 4: Strong students
            4: {
                'completion_rate': 0.85,
                'avg_score': 0.85,
                'avg_attempts': 1.2,
                'time_multiplier': 0.7,
                'prefer_easy': False,
                'engagement': 0.85
            },
            # Cluster 5: Excellent students
            5: {
                'completion_rate': 0.95,
                'avg_score': 0.92,
                'avg_attempts': 1.0,
                'time_multiplier': 0.6,
                'prefer_easy': False,
                'engagement': 0.9
            }
        }

    def _build_behaviors_from_profiles(self) -> Dict[int, Dict]:
        """
        Attempt to derive cluster behavior parameters from loaded cluster profiles.

        Mapping heuristics (if data available):
         - avg_score <- mean_module_grade
         - engagement <- total_events or viewed
         - completion_rate <- module_count
         - avg_attempts <- attempt (fallback 2.0)
         - time_multiplier: inverse relation with avg_score
         - prefer_easy: True if avg_score < 0.6

        Returns empty dict if no usable profiles found.
        """
        profiles = getattr(self.reward_calculator, 'cluster_profiles', None)
        overall = None
        # Try to get overall stats too for fallbacks
        try:
            with open(getattr(self.reward_calculator, 'cluster_profiles_path'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                overall = data.get('overall_stats', {}).get('mean', {})
        except Exception:
            overall = None

        if not profiles:
            return {}

        behaviors: Dict[int, Dict] = {}
        for cid_str, info in profiles.items():
            # cluster ids in file may be strings
            try:
                cid = int(cid_str)
            except Exception:
                continue

            feature_means = info.get('feature_means', {}) if isinstance(info, dict) else {}

            # Helpers to extract feature with fallbacks
            def _get_feat(key_list, fallback=None):
                for k in key_list:
                    if k in feature_means:
                        return feature_means.get(k)
                    if overall and k in overall:
                        return overall.get(k)
                return fallback

            avg_score = _get_feat(['mean_module_grade', 'mean_module_grade'], 0.6)
            engagement = _get_feat(['total_events', 'viewed'], 0.5)
            completion_rate = _get_feat(['module_count', 'module_count'], 0.5)
            avg_attempts = _get_feat(['attempt', 'attempt'], 2.0)

            # Normalize / clip and apply simple heuristics
            try:
                avg_score = float(avg_score)
            except Exception:
                avg_score = 0.6
            try:
                engagement = float(engagement)
            except Exception:
                engagement = 0.5
            try:
                completion_rate = float(completion_rate)
            except Exception:
                completion_rate = 0.5
            try:
                avg_attempts = float(avg_attempts)
            except Exception:
                avg_attempts = 2.0

            # Derive time multiplier: higher skill -> less time
            time_multiplier = max(0.5, 1.5 - (avg_score - 0.5))

            behaviors[cid] = {
                'completion_rate': float(np.clip(completion_rate, 0, 1)),
                'avg_score': float(np.clip(avg_score, 0, 1)),
                'avg_attempts': max(1.0, avg_attempts),
                'time_multiplier': float(np.clip(time_multiplier, 0.5, 2.0)),
                'prefer_easy': bool(avg_score < 0.6),
                'engagement': float(np.clip(engagement, 0, 1))
            }

        # If we got at least one behavior, return it
        return behaviors if behaviors else {}
    
    def simulate_student_learning(
        self,
        student_id: int,
        cluster_id: int,
        initial_state: np.ndarray,
        n_actions: int = 20,
        start_date: Optional[datetime] = None
    ) -> List[SimulatedInteraction]:
        """
        Mô phỏng quá trình học tập của 1 học viên
        
        Args:
            student_id: Student ID
            cluster_id: Cluster ID (0-5)
            initial_state: Initial state vector
            n_actions: Number of actions to simulate
            start_date: Starting date (default: now)
        
        Returns:
            List of simulated interactions
        """
        if start_date is None:
            start_date = datetime.now()
        
        interactions = []
        current_state = initial_state.copy()
        current_date = start_date
        
        behavior = self.cluster_behaviors[cluster_id]
        available_actions = self.action_space.get_actions()
        
        for i in range(n_actions):
            # Select action based on cluster behavior
            action = self._select_action_for_cluster(
                cluster_id, available_actions, current_state
            )
            
            if action is None:
                break
            
            # Simulate interaction outcome
            outcome = self._simulate_outcome(cluster_id, action, current_state)
            
            # Calculate reward
            reward = self.reward_calculator.calculate_reward(
                cluster_id, action, outcome, current_state
            )
            
            # Update state
            next_state = self._update_state(current_state, action, outcome)
            
            # Create interaction record
            interaction = SimulatedInteraction(
                student_id=student_id,
                cluster_id=cluster_id,
                action_id=action.id,
                action_name=action.name,
                action_type=action.type,
                timestamp=current_date.isoformat(),
                completed=outcome['completed'],
                score=outcome['score'],
                time_spent=outcome['time_spent'],
                attempts=outcome['attempts'],
                reward=reward,
                state_before=current_state.tolist(),
                state_after=next_state.tolist()
            )
            
            interactions.append(interaction)
            
            # Update for next iteration
            current_state = next_state
            current_date += timedelta(hours=np.random.randint(1, 48))
        
        return interactions
    
    def _select_action_for_cluster(
        self,
        cluster_id: int,
        available_actions: List[LearningAction],
        state: np.ndarray
    ) -> Optional[LearningAction]:
        """
        Select action based on cluster behavior
        
        Args:
            cluster_id: Cluster ID
            available_actions: List of available actions
            state: Current state
        
        Returns:
            Selected action
        """
        if not available_actions:
            return None
        
        behavior = self.cluster_behaviors[cluster_id]
        
        # Filter actions based on preferences
        if behavior['prefer_easy']:
            # Prefer easy/medium activities
            preferred = [
                a for a in available_actions 
                if a.difficulty in ['easy', 'medium']
            ]
            if not preferred:
                preferred = available_actions
        else:
            # Accept all difficulties
            preferred = available_actions
        
        # Weak clusters prefer resources first
        if cluster_id <= 1:
            content_actions = [a for a in preferred if a.purpose == 'content']
            if content_actions and np.random.random() < 0.4:
                return np.random.choice(content_actions)
        
        # Strong clusters prefer assessments
        if cluster_id >= 4:
            assessment_actions = [a for a in preferred if a.purpose == 'assessment']
            if assessment_actions and np.random.random() < 0.6:
                return np.random.choice(assessment_actions)
        
        # Random selection from preferred
        return np.random.choice(preferred)
    
    def _simulate_outcome(
        self,
        cluster_id: int,
        action: LearningAction,
        state: np.ndarray
    ) -> Dict:
        """
        Simulate outcome of an action
        
        Args:
            cluster_id: Cluster ID
            action: Action to simulate
            state: Current state
        
        Returns:
            Outcome dict
        """
        behavior = self.cluster_behaviors[cluster_id]
        
        # Completion
        completed = np.random.random() < behavior['completion_rate']
        
        # Score (if completed)
        if completed:
            # Base score from cluster behavior
            base_score = behavior['avg_score']
            
            # Adjust by difficulty
            if action.difficulty == 'easy':
                score = np.clip(base_score + np.random.uniform(0, 0.2), 0, 1)
            elif action.difficulty == 'hard':
                score = np.clip(base_score - np.random.uniform(0, 0.15), 0, 1)
            else:
                score = np.clip(base_score + np.random.uniform(-0.1, 0.1), 0, 1)
        else:
            score = np.random.uniform(0, 0.3)
        
        # Attempts
        attempts = max(1, int(np.random.normal(behavior['avg_attempts'], 0.5)))
        
        # Time spent (minutes)
        base_time = 30 if action.purpose == 'assessment' else 15
        time_spent = int(base_time * behavior['time_multiplier'] * np.random.uniform(0.5, 1.5))
        
        return {
            'completed': completed,
            'score': score,
            'time_spent': time_spent,
            'attempts': attempts
        }
    
    def _update_state(
        self,
        state: np.ndarray,
        action: LearningAction,
        outcome: Dict
    ) -> np.ndarray:
        """
        Update state based on action outcome
        
        State dimensions:
        0: knowledge_level
        1: engagement_level
        2: struggle_indicator
        3-7: activity patterns
        8-11: completion metrics
        
        Args:
            state: Current state
            action: Action taken
            outcome: Action outcome
        
        Returns:
            Updated state
        """
        new_state = state.copy()
        
        # Update knowledge level (slow change)
        if outcome['completed'] and outcome['score'] > 0.7:
            new_state[0] = np.clip(new_state[0] + 0.05, 0, 1)
        elif outcome['score'] < 0.5:
            new_state[0] = np.clip(new_state[0] - 0.02, 0, 1)
        
        # Update engagement level
        if outcome['completed']:
            new_state[1] = np.clip(new_state[1] + 0.03, 0, 1)
        else:
            new_state[1] = np.clip(new_state[1] - 0.05, 0, 1)
        
        # Update struggle indicator
        if outcome['attempts'] > 2 and outcome['score'] < 0.6:
            new_state[2] = np.clip(new_state[2] + 0.1, 0, 1)
        else:
            new_state[2] = np.clip(new_state[2] - 0.05, 0, 1)
        
        # Update activity patterns (3-7)
        if action.purpose == 'assessment':
            new_state[6] = np.clip(new_state[6] + 0.05, 0, 1)  # assessment_engagement
        elif action.purpose == 'content':
            new_state[5] = np.clip(new_state[5] + 0.05, 0, 1)  # resource_usage
        
        # Update completion metrics (8-11)
        if outcome['completed']:
            new_state[8] = np.clip(new_state[8] + 0.05, 0, 1)  # overall_progress
            new_state[9] = np.clip(new_state[9] + 0.03, 0, 1)  # module_completion_rate
        
        return new_state
    
    def simulate_batch(
        self,
        n_students: int,
        cluster_distribution: Optional[Dict[int, float]] = None,
        n_actions_per_student: int = 20
    ) -> List[SimulatedInteraction]:
        """
        Simulate multiple students
        
        Args:
            n_students: Number of students to simulate
            cluster_distribution: Distribution of clusters (default: uniform)
            n_actions_per_student: Actions per student
        
        Returns:
            List of all interactions
        """
        if cluster_distribution is None:
            # Uniform distribution
            cluster_distribution = {i: 1/6 for i in range(6)}
        
        all_interactions = []
        
        for student_id in range(n_students):
            # Assign cluster
            cluster_id = np.random.choice(
                list(cluster_distribution.keys()),
                p=list(cluster_distribution.values())
            )
            
            # Generate initial state
            behavior = self.cluster_behaviors[cluster_id]
            initial_state = self._generate_initial_state(behavior)
            
            # Simulate learning
            interactions = self.simulate_student_learning(
                student_id=student_id,
                cluster_id=cluster_id,
                initial_state=initial_state,
                n_actions=n_actions_per_student
            )
            
            all_interactions.extend(interactions)
        
        return all_interactions
    
    def _generate_initial_state(self, behavior: Dict) -> np.ndarray:
        """
        Generate initial state based on cluster behavior
        
        Args:
            behavior: Cluster behavior params
        
        Returns:
            Initial state vector (12 dims)
        """
        # Generate state matching cluster characteristics
        state = np.zeros(12)
        
        # Performance (0-2)
        state[0] = behavior['avg_score'] + np.random.uniform(-0.1, 0.1)  # knowledge
        state[1] = behavior['engagement'] + np.random.uniform(-0.05, 0.05)  # engagement
        state[2] = (1 - behavior['avg_score']) * 0.5  # struggle
        
        # Activity patterns (3-7)
        base_activity = behavior['engagement']
        state[3:8] = base_activity + np.random.uniform(-0.1, 0.1, 5)
        
        # Completion metrics (8-11)
        state[8] = behavior['completion_rate'] * 0.3  # initial progress
        state[9] = behavior['completion_rate'] * 0.5
        state[10] = np.random.uniform(0.2, 0.6)  # diversity
        state[11] = np.random.uniform(0.4, 0.8)  # consistency
        
        return np.clip(state, 0, 1)
    
    def save_simulated_data(self, interactions: List[SimulatedInteraction], filepath: str):
        """
        Save simulated data to JSON
        
        Args:
            interactions: List of interactions
            filepath: Output file path
        """
        data = [asdict(i) for i in interactions]
        
        # Convert numpy types to Python types
        for item in data:
            for key, value in item.items():
                if isinstance(value, (np.integer, np.floating)):
                    item[key] = value.item()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_simulation_stats(self, interactions: List[SimulatedInteraction]) -> Dict:
        """
        Get statistics from simulated data
        
        Args:
            interactions: List of interactions
        
        Returns:
            Statistics dict
        """
        if not interactions:
            return {}
        
        return {
            'total_interactions': len(interactions),
            'unique_students': len(set(i.student_id for i in interactions)),
            'cluster_distribution': {
                cid: sum(1 for i in interactions if i.cluster_id == cid)
                for cid in range(6)
            },
            'avg_score': np.mean([i.score for i in interactions]),
            'completion_rate': sum(i.completed for i in interactions) / len(interactions),
            'avg_attempts': np.mean([i.attempts for i in interactions]),
            'avg_time_spent': np.mean([i.time_spent for i in interactions]),
            'avg_reward': np.mean([i.reward for i in interactions])
        }


# Example usage
if __name__ == '__main__':
    import os
    
    # Setup
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(os.path.join(data_dir, 'course_structure.json'))
    reward_calc = RewardCalculator(os.path.join(data_dir, 'cluster_profiles.json'))
    
    simulator = LearningSimulator(state_builder, action_space, reward_calc)
    
    print("=" * 70)
    print("LEARNING SIMULATOR TEST")
    print("=" * 70)
    
    # Simulate batch
    print("\nSimulating 10 students with 15 actions each...")
    interactions = simulator.simulate_batch(n_students=10, n_actions_per_student=15)
    
    # Get stats
    stats = simulator.get_simulation_stats(interactions)
    
    print(f"\nSimulation Statistics:")
    print(f"  Total interactions: {stats['total_interactions']}")
    print(f"  Unique students: {stats['unique_students']}")
    print(f"  Avg score: {stats['avg_score']:.2f}")
    print(f"  Completion rate: {stats['completion_rate']:.2%}")
    print(f"  Avg attempts: {stats['avg_attempts']:.2f}")
    print(f"  Avg time spent: {stats['avg_time_spent']:.1f} min")
    print(f"  Avg reward: {stats['avg_reward']:.2f}")
    
    print(f"\nCluster distribution:")
    for cid, count in stats['cluster_distribution'].items():
        print(f"  Cluster {cid}: {count} interactions")
    
    # Save sample
    output_path = os.path.join(data_dir, 'simulated', 'sample_simulation.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    simulator.save_simulated_data(interactions[:10], output_path)
    print(f"\nSaved sample to: {output_path}")
