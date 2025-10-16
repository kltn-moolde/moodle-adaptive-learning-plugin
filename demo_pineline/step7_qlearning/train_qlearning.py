#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning Training Pipeline
=============================
Training pipeline cho Q-Learning agent với simulated data
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from tqdm import tqdm

from core.qlearning_agent_v2 import QLearningAgentV2
from core.data_simulator import StudentDataSimulator

logger = logging.getLogger(__name__)


class QLearningTrainer:
    """
    Training pipeline cho Q-Learning agent
    
    Features:
    - Load simulated data
    - Train Q-Learning agent
    - Evaluate on test set
    - Compute metrics
    """
    
    def __init__(self, 
                 agent: QLearningAgentV2,
                 train_data_path: str,
                 test_data_path: str):
        """
        Args:
            agent: QLearningAgentV2 instance
            train_data_path: Path to training CSV
            test_data_path: Path to test CSV
        """
        self.agent = agent
        self.train_df = pd.read_csv(train_data_path)
        self.test_df = pd.read_csv(test_data_path)
        
        # Training history - Extended version
        self.history = {
            'episode_rewards': [],
            'episode_lengths': [],
            'avg_q_values': [],
            # New: Per-epoch metrics
            'epoch_avg_grades': [],  # Avg grade across all students per epoch
            'epoch_completion_rates': [],  # Completion rate per epoch
            'epoch_avg_time_spent': [],  # Avg time per epoch
            # New: Per-student progress tracking
            'student_progress': {}  # {student_id: {'grades': [...], 'rewards': [...], 'completions': [...]}}
        }
        
        logger.info(f"Trainer initialized:")
        logger.info(f"  Train: {len(self.train_df)} records, {self.train_df['student_id'].nunique()} students")
        logger.info(f"  Test: {len(self.test_df)} records, {self.test_df['student_id'].nunique()} students")
    
    def extract_state_from_record(self, record: pd.Series) -> np.ndarray:
        """Extract state vector from data record"""
        feature_names = [
            'mean_module_grade', 'total_events', 'course_module',
            'viewed', 'attempt', 'feedback_viewed', 'submitted', 'reviewed',
            'course_module_viewed', 'module_count', 'course_module_completion',
            'created', 'updated', 'downloaded'
        ]
        
        # Build feature dict
        features = {}
        for fname in feature_names:
            if fname in record:
                features[fname] = record[fname]
            else:
                features[fname] = 0.5  # Default
        
        # Use state builder
        state = self.agent.state_builder.build_state(features)
        return state
    
    def compute_reward(self, record: pd.Series) -> float:
        """
        Compute reward from learning outcome
        
        Components:
        - Grade: Học được nhiều -> reward cao
        - Time efficiency: Học nhanh -> reward cao
        - Completion: Hoàn thành -> reward cao
        """
        grade = record.get('grade', 0.0)
        time_spent = record.get('time_spent', 15)  # minutes
        completed = record.get('completed', False)
        
        # Grade reward (0-1)
        grade_reward = grade
        
        # Time efficiency reward (shorter time = higher reward)
        # Normalize time to [0, 1], invert
        time_normalized = np.clip(time_spent / 60, 0, 1)  # 60 min = max
        time_reward = 1.0 - time_normalized
        
        # Completion bonus
        completion_reward = 1.0 if completed else 0.0
        
        # Weighted combination
        reward = (
            0.5 * grade_reward +
            0.2 * time_reward +
            0.3 * completion_reward
        )
        
        return reward
    
    def train_episode(self, student_df: pd.DataFrame, epsilon: float = 0.1) -> Tuple[float, int, Dict]:
        """
        Train một episode (one student's trajectory)
        
        Args:
            student_df: DataFrame of one student's trajectory
            epsilon: Exploration rate
        
        Returns:
            (total_reward, episode_length, episode_metrics)
        """
        total_reward = 0.0
        episode_length = len(student_df)
        
        # Track episode metrics
        episode_metrics = {
            'grades': [],
            'rewards': [],
            'completions': [],
            'time_spent': []
        }
        
        # Sort by step
        student_df = student_df.sort_values('step')
        
        # Track completed resources
        completed_resources = []
        
        for idx, record in student_df.iterrows():
            # Current state
            state = self.extract_state_from_record(record)
            
            # Action (resource completed)
            action_id = str(record['resource_id'])
            
            # Find action object
            action = None
            for a in self.agent.action_space.get_all_actions():
                if a.action_id == action_id:
                    action = a
                    break
            
            if action is None:
                logger.warning(f"Action {action_id} not found in action space")
                continue
            
            # Reward
            reward = self.compute_reward(record)
            total_reward += reward
            
            # Track metrics for this step
            episode_metrics['grades'].append(record['grade'])
            episode_metrics['rewards'].append(reward)
            episode_metrics['completions'].append(1 if record['completed'] else 0)
            episode_metrics['time_spent'].append(record['time_spent'])
            
            # Next state and available actions
            next_idx = idx + 1
            if next_idx < len(student_df):
                next_record = student_df.iloc[next_idx]
                next_state = self.extract_state_from_record(next_record)
                
                # Next available actions (exclude already completed)
                next_completed = completed_resources + [action_id]
                next_available_actions = [
                    a for a in self.agent.action_space.get_all_actions()
                    if a.action_id not in next_completed
                ]
            else:
                # Terminal state
                next_state = state  # Same state (no next)
                next_available_actions = []  # No more actions
            
            # Update Q-table
            self.agent.update(state, action_id, reward, next_state, next_available_actions)
            
            # Mark resource as completed
            completed_resources.append(action_id)
        
        return total_reward, episode_length, episode_metrics
    
    def train(self, n_epochs: int = 10, epsilon_decay: float = 0.95):
        """
        Train agent on training data
        
        Args:
            n_epochs: Number of training epochs
            epsilon_decay: Decay rate for exploration
        """
        logger.info(f"Training for {n_epochs} epochs...")
        
        epsilon = self.agent.epsilon
        
        for epoch in range(n_epochs):
            logger.info(f"\nEpoch {epoch + 1}/{n_epochs} (epsilon={epsilon:.3f})")
            
            # Shuffle students
            unique_students = self.train_df['student_id'].unique()
            np.random.shuffle(unique_students)
            
            epoch_rewards = []
            epoch_lengths = []
            epoch_grades = []
            epoch_completions = []
            epoch_time_spent = []
            
            for student_id in tqdm(unique_students, desc=f"Epoch {epoch+1}"):
                student_df = self.train_df[self.train_df['student_id'] == student_id]
                
                total_reward, length, metrics = self.train_episode(student_df, epsilon)
                epoch_rewards.append(total_reward)
                epoch_lengths.append(length)
                
                # Aggregate metrics
                epoch_grades.extend(metrics['grades'])
                epoch_completions.extend(metrics['completions'])
                epoch_time_spent.extend(metrics['time_spent'])
                
                # Track per-student progress (convert student_id to str for JSON serialization)
                student_id_str = str(student_id)
                if student_id_str not in self.history['student_progress']:
                    self.history['student_progress'][student_id_str] = {
                        'epoch_avg_grades': [],
                        'epoch_avg_rewards': [],
                        'epoch_completion_rates': []
                    }
                
                self.history['student_progress'][student_id_str]['epoch_avg_grades'].append(float(np.mean(metrics['grades'])))
                self.history['student_progress'][student_id_str]['epoch_avg_rewards'].append(float(np.mean(metrics['rewards'])))
                self.history['student_progress'][student_id_str]['epoch_completion_rates'].append(float(np.mean(metrics['completions'])))
            
            # Decay epsilon
            epsilon *= epsilon_decay
            self.agent.epsilon = epsilon
            
            # Log statistics
            avg_reward = np.mean(epoch_rewards)
            avg_length = np.mean(epoch_lengths)
            avg_q = np.mean([v for v in self.agent.Q.values()])
            avg_grade = np.mean(epoch_grades)
            completion_rate = np.mean(epoch_completions)
            avg_time = np.mean(epoch_time_spent)
            
            self.history['episode_rewards'].append(float(avg_reward))
            self.history['episode_lengths'].append(float(avg_length))
            self.history['avg_q_values'].append(float(avg_q))
            self.history['epoch_avg_grades'].append(float(avg_grade))
            self.history['epoch_completion_rates'].append(float(completion_rate))
            self.history['epoch_avg_time_spent'].append(float(avg_time))
            
            logger.info(f"  Avg reward: {avg_reward:.4f}")
            logger.info(f"  Avg grade: {avg_grade:.4f}")
            logger.info(f"  Completion rate: {completion_rate:.2%}")
            logger.info(f"  Avg time spent: {avg_time:.2f} min")
            logger.info(f"  Avg episode length: {avg_length:.2f}")
            logger.info(f"  Avg Q-value: {avg_q:.4f}")
            logger.info(f"  Q-table size: {len(self.agent.Q)}")
        
        logger.info("\n✓ Training completed!")
    
    def evaluate(self, use_test_set: bool = True) -> Dict:
        """
        Evaluate agent performance
        
        Args:
            use_test_set: Use test set (True) or train set (False)
        
        Returns:
            Dict of evaluation metrics
        """
        logger.info(f"\nEvaluating on {'test' if use_test_set else 'train'} set...")
        
        df = self.test_df if use_test_set else self.train_df
        unique_students = df['student_id'].unique()
        
        metrics = {
            'n_students': len(unique_students),
            'total_records': len(df),
            'avg_reward': 0.0,
            'avg_grade': 0.0,
            'completion_rate': 0.0,
            'recommendation_accuracy': 0.0,  # % of recommended actions actually taken
            'avg_q_value': 0.0
        }
        
        all_rewards = []
        all_grades = []
        all_completions = []
        correct_recommendations = 0
        total_recommendations = 0
        all_q_values = []
        
        for student_id in tqdm(unique_students, desc="Evaluating"):
            student_df = df[df['student_id'] == student_id].sort_values('step')
            
            completed_resources = []
            
            for idx, record in student_df.iterrows():
                state = self.extract_state_from_record(record)
                actual_action_id = str(record['resource_id'])
                
                # Get available actions (chưa complete)
                available_actions = [
                    a for a in self.agent.action_space.get_all_actions()
                    if a.action_id not in [str(r) for r in completed_resources]
                ]
                
                if available_actions:
                    # Get recommendation
                    recommendations = self.agent.recommend(
                        state, 
                        available_actions, 
                        top_k=3,
                        use_heuristic_fallback=False
                    )
                    
                    # Check if actual action is in top-k recommendations
                    recommended_ids = [r['action_id'] for r in recommendations]
                    if actual_action_id in recommended_ids:
                        correct_recommendations += 1
                    total_recommendations += 1
                    
                    # Record Q-value
                    discrete_state = tuple(self.agent.discretizer.discretize(state))
                    for a in available_actions:
                        if a.action_id == actual_action_id:
                            q_val = self.agent.Q.get((discrete_state, a.action_id), 0.0)
                            all_q_values.append(q_val)
                            break
                
                # Record outcomes
                reward = self.compute_reward(record)
                all_rewards.append(reward)
                all_grades.append(record['grade'])
                all_completions.append(1 if record['completed'] else 0)
                
                completed_resources.append(record['resource_id'])
        
        # Compute metrics
        metrics['avg_reward'] = float(np.mean(all_rewards))
        metrics['avg_grade'] = float(np.mean(all_grades))
        metrics['completion_rate'] = float(np.mean(all_completions))
        metrics['recommendation_accuracy'] = float(correct_recommendations / total_recommendations if total_recommendations > 0 else 0.0)
        metrics['avg_q_value'] = float(np.mean(all_q_values) if all_q_values else 0.0)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Evaluation Results ({'Test' if use_test_set else 'Train'} Set)")
        logger.info(f"{'='*70}")
        logger.info(f"Students: {metrics['n_students']}")
        logger.info(f"Records: {metrics['total_records']}")
        logger.info(f"Avg Reward: {metrics['avg_reward']:.4f}")
        logger.info(f"Avg Grade: {metrics['avg_grade']:.4f}")
        logger.info(f"Completion Rate: {metrics['completion_rate']:.2%}")
        logger.info(f"Recommendation Accuracy: {metrics['recommendation_accuracy']:.2%}")
        logger.info(f"Avg Q-value: {metrics['avg_q_value']:.4f}")
        logger.info(f"{'='*70}\n")
        
        return metrics
    
    def save_training_results(self, output_dir: str):
        """Save training history and metrics"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save history
        history_path = output_path / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        logger.info(f"✓ Training history saved: {history_path}")
        
        # Evaluate and save metrics
        train_metrics = self.evaluate(use_test_set=False)
        test_metrics = self.evaluate(use_test_set=True)
        
        metrics = {
            'train': train_metrics,
            'test': test_metrics
        }
        
        metrics_path = output_path / 'evaluation_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"✓ Evaluation metrics saved: {metrics_path}")


def main():
    """Main training script"""
    print("\n" + "="*70)
    print("Q-Learning Training Pipeline")
    print("="*70)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Paths
    base_path = Path(__file__).parent  # step7_qlearning/
    
    # Step 1: Generate simulated data (if not exists)
    print("\n" + "-"*70)
    print("Step 1: Generate Simulated Data")
    print("-"*70)
    
    simulated_dir = base_path / "data/simulated"
    train_path = simulated_dir / "train_data.csv"
    test_path = simulated_dir / "test_data.csv"
    
    if not train_path.exists() or not test_path.exists():
        logger.info("Generating simulated data...")
        simulator = StudentDataSimulator(
            cluster_stats_path=str(base_path / "../data/processed/cluster_full_statistics.json"),
            course_structure_path=str(base_path / "data/course_structure.json"),
            real_features_path=str(base_path / "data/features_scaled_report.json")
        )
        
        train_df, test_df = simulator.generate_dataset(
            n_students=100,
            train_ratio=0.8,
            n_steps_per_student=10
        )
        
        simulator.save_dataset(train_df, test_df, str(simulated_dir))
    else:
        logger.info("Simulated data already exists, skipping generation")
    
    # Step 2: Initialize Q-Learning Agent
    print("\n" + "-"*70)
    print("Step 2: Initialize Q-Learning Agent")
    print("-"*70)
    
    agent = QLearningAgentV2.create_from_course(
        str(base_path / "data/course_structure.json"),
        n_bins=3,
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.3
    )
    
    logger.info(f"Agent initialized: {agent}")
    
    # Step 3: Train
    print("\n" + "-"*70)
    print("Step 3: Train Q-Learning Agent")
    print("-"*70)
    
    trainer = QLearningTrainer(
        agent=agent,
        train_data_path=str(train_path),
        test_data_path=str(test_path)
    )
    
    trainer.train(n_epochs=10, epsilon_decay=0.95)
    
    # Step 4: Save results
    print("\n" + "-"*70)
    print("Step 4: Save Results")
    print("-"*70)
    
    results_dir = base_path / "results"
    trainer.save_training_results(str(results_dir))
    
    # Save trained model
    model_path = base_path / "models/qlearning_trained.pkl"
    agent.save(str(model_path))
    logger.info(f"✓ Trained model saved: {model_path}")
    
    print("\n" + "="*70)
    print("✅ Training pipeline completed!")
    print("="*70)


if __name__ == '__main__':
    main()
