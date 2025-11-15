#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Training Visualizer - Trực quan hóa kết quả Q-Learning
=====================================================
Visualize student learning progression, LO mastery, và midterm predictions
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import json
from pathlib import Path
from collections import defaultdict

from core.student import Student
from core.qlearning_agent_v2 import QLearningAgentV2
from core.action_space import ActionSpace
from core.reward_calculator_v2 import RewardCalculatorV2
from core.activity_recommender import ActivityRecommender


class TrainingVisualizer:
    """
    Visualize Q-Learning training results
    
    Features:
    - Learning curves (reward progression)
    - LO mastery heatmaps
    - Student performance comparison
    - Midterm score predictions
    - Action distribution analysis
    """
    
    def __init__(
        self,
        qtable_path: str = 'models/qtable.pkl',
        output_dir: str = 'plots/training'
    ):
        """
        Initialize visualizer
        
        Args:
            qtable_path: Path to trained Q-table
            output_dir: Directory to save plots
        """
        self.qtable_path = qtable_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load components
        self.action_space = ActionSpace()
        self.agent = QLearningAgentV2(n_actions=self.action_space.get_action_count())
        self.agent.load(qtable_path)
        
        self.reward_calc = RewardCalculatorV2(
            cluster_profiles_path='data/cluster_profiles.json'
        )
        
        # Activity recommender
        self.recommender = ActivityRecommender(
            po_lo_path='data/Po_Lo.json',
            course_structure_path='data/course_structure.json'
        )
        
        # Load LO mappings
        with open('data/Po_Lo.json', 'r', encoding='utf-8') as f:
            po_lo_data = json.load(f)
        
        self.lo_mappings = defaultdict(list)
        self.lo_names = {}
        for lo in po_lo_data['learning_outcomes']:
            # Use description as name (or just ID if no description)
            self.lo_names[lo['id']] = lo.get('description', lo['id'])[:50]  # Truncate for display
            for activity_id in lo.get('activity_ids', []):
                self.lo_mappings[activity_id].append(lo['id'])
        
        # Midterm LO weights
        with open('data/midterm_lo_weights.json', 'r', encoding='utf-8') as f:
            midterm_data = json.load(f)
        self.midterm_weights = midterm_data['lo_weights']
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
        
        print(f"✓ TrainingVisualizer initialized")
        print(f"  Output directory: {self.output_dir}")
    
    def simulate_student_trajectory(
        self,
        student: Student,
        n_steps: int = 30,
        track_history: bool = True
    ) -> Dict:
        """
        Simulate student with trained agent and track metrics
        
        Args:
            student: Student instance
            n_steps: Number of steps
            track_history: Track detailed history
            
        Returns:
            Dict with trajectory data
        """
        history = {
            'rewards': [],
            'scores': [],
            'progress': [],
            'lo_mastery': defaultdict(list),
            'actions': [],
            'modules': []
        }
        
        # Reset epsilon for greedy policy
        old_epsilon = self.agent.epsilon
        self.agent.epsilon = 0.0
        
        for step in range(n_steps):
            if student.is_finished:
                break
            
            # Get state and action
            state = student.get_state()
            action_idx = self.agent.select_action(state)
            action = self.action_space.get_action_by_index(action_idx).to_tuple()
            
            # Get activity recommendation
            recommendation = self.recommender.recommend_activity(
                action=action,
                module_idx=student.module_idx,
                lo_mastery=student.lo_mastery,
                previous_activities=getattr(student, 'activity_history', [])
            )
            activity_id = recommendation['activity_id']
            
            # Execute
            result = student.do_action(action, activity_id, self.lo_mappings)
            outcome = result['outcome']
            
            # Calculate reward
            reward = self.reward_calc.calculate_reward(
                state=state,
                action={'type': action[0], 'difficulty': 'medium'},
                outcome=outcome,
                student_id=student.id,
                activity_id=activity_id
            )
            
            # Track metrics
            if track_history:
                history['rewards'].append(reward)
                history['scores'].append(student.score)
                history['progress'].append(student.progress)
                history['actions'].append(action[0])
                history['modules'].append(student.module_idx)
                
                # Track LO mastery
                for lo_id in self.lo_names.keys():
                    history['lo_mastery'][lo_id].append(student.lo_mastery[lo_id])
        
        # Restore epsilon
        self.agent.epsilon = old_epsilon
        
        return history
    
    def predict_midterm_score(self, student: Student) -> Dict:
        """
        Predict midterm score based on LO mastery
        
        Args:
            student: Student instance
            
        Returns:
            Dict with prediction details
        """
        weighted_score = 0.0
        total_weight = 0.0
        lo_contributions = {}
        
        for lo_id, weight in self.midterm_weights.items():
            mastery = student.lo_mastery[lo_id]
            contribution = mastery * weight
            weighted_score += contribution
            total_weight += weight
            lo_contributions[lo_id] = {
                'mastery': mastery,
                'weight': weight,
                'contribution': contribution
            }
        
        # Normalize to 0-100 scale
        predicted_score = (weighted_score / total_weight) * 100 if total_weight > 0 else 50
        
        return {
            'predicted_score': predicted_score,
            'total_weight': total_weight,
            'lo_contributions': lo_contributions,
            'confidence': min(len(student.score_history) / 20.0, 1.0)  # Confidence based on data
        }
    
    def visualize_student_learning(
        self,
        cluster: str,
        student_id: int = 1,
        n_steps: int = 50,
        save: bool = True
    ):
        """
        Visualize single student learning progression
        
        Args:
            cluster: 'weak', 'medium', 'strong'
            student_id: Student ID
            n_steps: Number of steps to simulate
            save: Save plot to file
        """
        print(f"\n📊 Visualizing {cluster} learner (ID {student_id})...")
        
        # Create student and simulate
        student = Student(student_id, cluster)
        history = self.simulate_student_trajectory(student, n_steps=n_steps)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f'{cluster.upper()} Learner - Learning Progression (Student {student_id})', 
                     fontsize=16, fontweight='bold')
        
        # 1. Reward progression
        ax1 = axes[0, 0]
        steps = range(len(history['rewards']))
        ax1.plot(steps, history['rewards'], 'b-', alpha=0.6, linewidth=1)
        # Moving average
        window = 5
        if len(history['rewards']) >= window:
            ma = np.convolve(history['rewards'], np.ones(window)/window, mode='valid')
            ax1.plot(range(window-1, len(history['rewards'])), ma, 'r-', linewidth=2, label=f'MA({window})')
        ax1.set_xlabel('Step')
        ax1.set_ylabel('Reward')
        ax1.set_title('Reward Progression')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Score progression
        ax2 = axes[0, 1]
        ax2.plot(steps, history['scores'], 'g-', linewidth=2)
        ax2.axhline(y=0.7, color='orange', linestyle='--', alpha=0.5, label='Pass threshold (70%)')
        ax2.set_xlabel('Step')
        ax2.set_ylabel('Average Score')
        ax2.set_title('Score Improvement')
        ax2.set_ylim([0, 1])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Module progress
        ax3 = axes[1, 0]
        ax3.plot(steps, history['modules'], 'purple', linewidth=2, marker='o', markersize=3)
        ax3.set_xlabel('Step')
        ax3.set_ylabel('Module Index')
        ax3.set_title('Module Progression')
        ax3.set_yticks(range(0, 6))
        ax3.grid(True, alpha=0.3)
        
        # 4. LO Mastery progression (top 5 important LOs)
        ax4 = axes[1, 1]
        # Get top LOs by midterm weight
        top_los = sorted(self.midterm_weights.items(), key=lambda x: x[1], reverse=True)[:5]
        for lo_id, weight in top_los:
            if lo_id in history['lo_mastery'] and history['lo_mastery'][lo_id]:
                label = f"{lo_id} (weight={weight:.2f})"
                ax4.plot(steps, history['lo_mastery'][lo_id], linewidth=2, label=label, alpha=0.8)
        ax4.set_xlabel('Step')
        ax4.set_ylabel('Mastery Level')
        ax4.set_title('Top 5 LO Mastery (by Midterm Weight)')
        ax4.set_ylim([0, 1])
        ax4.legend(fontsize=8, loc='best')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = self.output_dir / f'learning_progression_{cluster}_student{student_id}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved to {filename}")
        
        plt.show()
        
        # Print final statistics
        stats = student.get_statistics()
        print(f"\n  Final Statistics:")
        print(f"    Total actions: {stats['total_actions']}")
        print(f"    Module reached: {stats['module_idx'] + 1}/6")
        print(f"    Final score: {stats['score']:.3f}")
        print(f"    Avg LO mastery: {stats['avg_lo_mastery']:.3f}")
        print(f"    Total reward: {sum(history['rewards']):.2f}")
    
    def compare_clusters(
        self,
        n_students_per_cluster: int = 5,
        n_steps: int = 40,
        save: bool = True
    ):
        """
        Compare learning across different clusters
        
        Args:
            n_students_per_cluster: Number of students per cluster
            n_steps: Steps per student
            save: Save plot
        """
        print(f"\n📊 Comparing clusters ({n_students_per_cluster} students each)...")
        
        cluster_data = defaultdict(lambda: {
            'rewards': [],
            'scores': [],
            'lo_mastery': [],
            'final_modules': []
        })
        
        student_id = 1
        for cluster in ['weak', 'medium', 'strong']:
            print(f"  Simulating {cluster} learners...")
            for _ in range(n_students_per_cluster):
                student = Student(student_id, cluster)
                history = self.simulate_student_trajectory(student, n_steps=n_steps)
                
                cluster_data[cluster]['rewards'].append(history['rewards'])
                cluster_data[cluster]['scores'].append(history['scores'])
                cluster_data[cluster]['lo_mastery'].append(student.lo_mastery)
                cluster_data[cluster]['final_modules'].append(student.module_idx)
                
                student_id += 1
        
        # Create comparison plots
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Cluster Comparison - Learning Effectiveness', fontsize=16, fontweight='bold')
        
        colors = {'weak': 'red', 'medium': 'orange', 'strong': 'green'}
        
        # 1. Average reward progression
        ax1 = axes[0, 0]
        for cluster in ['weak', 'medium', 'strong']:
            rewards = cluster_data[cluster]['rewards']
            # Compute mean across students
            max_len = max(len(r) for r in rewards)
            padded = [r + [r[-1]]*(max_len - len(r)) for r in rewards]
            mean_rewards = np.mean(padded, axis=0)
            steps = range(len(mean_rewards))
            ax1.plot(steps, mean_rewards, color=colors[cluster], linewidth=2, 
                    label=f'{cluster.capitalize()} (n={n_students_per_cluster})', alpha=0.8)
        ax1.set_xlabel('Step')
        ax1.set_ylabel('Average Reward')
        ax1.set_title('Reward Progression by Cluster')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Score improvement
        ax2 = axes[0, 1]
        for cluster in ['weak', 'medium', 'strong']:
            scores = cluster_data[cluster]['scores']
            max_len = max(len(s) for s in scores)
            padded = [s + [s[-1]]*(max_len - len(s)) for s in scores]
            mean_scores = np.mean(padded, axis=0)
            steps = range(len(mean_scores))
            ax2.plot(steps, mean_scores, color=colors[cluster], linewidth=2, 
                    label=f'{cluster.capitalize()}', alpha=0.8)
        ax2.axhline(y=0.7, color='gray', linestyle='--', alpha=0.5, label='Pass threshold')
        ax2.set_xlabel('Step')
        ax2.set_ylabel('Average Score')
        ax2.set_title('Score Progression by Cluster')
        ax2.set_ylim([0, 1])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Final module distribution
        ax3 = axes[1, 0]
        module_data = []
        labels = []
        for cluster in ['weak', 'medium', 'strong']:
            modules = [m + 1 for m in cluster_data[cluster]['final_modules']]  # 1-indexed
            module_data.append(modules)
            labels.append(cluster.capitalize())
        
        bp = ax3.boxplot(module_data, labels=labels, patch_artist=True, notch=True)
        for patch, cluster in zip(bp['boxes'], ['weak', 'medium', 'strong']):
            patch.set_facecolor(colors[cluster])
            patch.set_alpha(0.6)
        ax3.set_ylabel('Final Module Reached')
        ax3.set_title('Module Completion by Cluster')
        ax3.set_ylim([0, 7])
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. LO mastery heatmap
        ax4 = axes[1, 1]
        # Get average mastery for top LOs
        top_los = sorted(self.midterm_weights.items(), key=lambda x: x[1], reverse=True)[:7]
        lo_ids = [lo[0] for lo in top_los]
        
        mastery_matrix = []
        for cluster in ['weak', 'medium', 'strong']:
            cluster_avg = []
            for lo_id in lo_ids:
                masteries = [m[lo_id] for m in cluster_data[cluster]['lo_mastery']]
                cluster_avg.append(np.mean(masteries))
            mastery_matrix.append(cluster_avg)
        
        im = ax4.imshow(mastery_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        ax4.set_xticks(range(len(lo_ids)))
        ax4.set_xticklabels(lo_ids, rotation=45, ha='right')
        ax4.set_yticks(range(3))
        ax4.set_yticklabels(['Weak', 'Medium', 'Strong'])
        ax4.set_title('Average LO Mastery by Cluster')
        
        # Add text annotations
        for i in range(3):
            for j in range(len(lo_ids)):
                text = ax4.text(j, i, f'{mastery_matrix[i][j]:.2f}',
                               ha="center", va="center", color="black", fontsize=9)
        
        plt.colorbar(im, ax=ax4, label='Mastery Level')
        
        plt.tight_layout()
        
        if save:
            filename = self.output_dir / 'cluster_comparison.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved to {filename}")
        
        plt.show()
    
    def visualize_midterm_predictions(
        self,
        n_students_per_cluster: int = 10,
        n_steps: int = 40,
        save: bool = True
    ):
        """
        Visualize midterm score predictions
        
        Args:
            n_students_per_cluster: Number of students per cluster
            n_steps: Steps to simulate
            save: Save plot
        """
        print(f"\n📊 Generating midterm predictions ({n_students_per_cluster} students/cluster)...")
        
        predictions_data = defaultdict(list)
        
        student_id = 1
        for cluster in ['weak', 'medium', 'strong']:
            for _ in range(n_students_per_cluster):
                student = Student(student_id, cluster)
                history = self.simulate_student_trajectory(student, n_steps=n_steps)
                
                # Get prediction
                prediction = self.predict_midterm_score(student)
                predictions_data[cluster].append({
                    'student_id': student_id,
                    'predicted_score': prediction['predicted_score'],
                    'confidence': prediction['confidence'],
                    'final_avg_score': student.score * 100,
                    'avg_lo_mastery': np.mean(list(student.lo_mastery.values()))
                })
                
                student_id += 1
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Midterm Score Predictions', fontsize=16, fontweight='bold')
        
        colors = {'weak': 'red', 'medium': 'orange', 'strong': 'green'}
        
        # 1. Distribution of predictions
        ax1 = axes[0]
        for cluster in ['weak', 'medium', 'strong']:
            scores = [p['predicted_score'] for p in predictions_data[cluster]]
            ax1.hist(scores, bins=10, alpha=0.5, color=colors[cluster], 
                    label=f'{cluster.capitalize()} (μ={np.mean(scores):.1f})', edgecolor='black')
        
        ax1.axvline(x=50, color='red', linestyle='--', alpha=0.5, label='Fail threshold')
        ax1.axvline(x=70, color='orange', linestyle='--', alpha=0.5, label='Pass threshold')
        ax1.axvline(x=85, color='green', linestyle='--', alpha=0.5, label='Good threshold')
        ax1.set_xlabel('Predicted Midterm Score')
        ax1.set_ylabel('Number of Students')
        ax1.set_title('Distribution of Predicted Midterm Scores')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Prediction vs Current Score
        ax2 = axes[1]
        for cluster in ['weak', 'medium', 'strong']:
            current_scores = [p['final_avg_score'] for p in predictions_data[cluster]]
            predicted_scores = [p['predicted_score'] for p in predictions_data[cluster]]
            ax2.scatter(current_scores, predicted_scores, color=colors[cluster], 
                       s=100, alpha=0.6, label=f'{cluster.capitalize()}', edgecolors='black')
        
        # Perfect prediction line
        ax2.plot([0, 100], [0, 100], 'k--', alpha=0.3, label='Perfect prediction')
        ax2.set_xlabel('Current Average Score')
        ax2.set_ylabel('Predicted Midterm Score')
        ax2.set_title('Prediction vs Current Performance')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 100])
        ax2.set_ylim([0, 100])
        
        plt.tight_layout()
        
        if save:
            filename = self.output_dir / 'midterm_predictions.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved to {filename}")
        
        plt.show()
        
        # Print summary statistics
        print(f"\n  Prediction Summary:")
        for cluster in ['weak', 'medium', 'strong']:
            scores = [p['predicted_score'] for p in predictions_data[cluster]]
            pass_rate = sum(1 for s in scores if s >= 50) / len(scores) * 100
            print(f"    {cluster.capitalize():7s}: μ={np.mean(scores):5.1f}, σ={np.std(scores):4.1f}, "
                  f"pass_rate={pass_rate:5.1f}%")
    
    def visualize_action_distribution(
        self,
        n_students: int = 30,
        n_steps: int = 40,
        save: bool = True
    ):
        """
        Analyze action distribution from trained agent
        
        Args:
            n_students: Number of students to simulate
            n_steps: Steps per student
            save: Save plot
        """
        print(f"\n📊 Analyzing action distribution ({n_students} students)...")
        
        action_counts = defaultdict(int)
        cluster_actions = defaultdict(lambda: defaultdict(int))
        
        student_id = 1
        clusters = ['weak'] * 10 + ['medium'] * 10 + ['strong'] * 10
        
        for cluster in clusters[:n_students]:
            student = Student(student_id, cluster)
            history = self.simulate_student_trajectory(student, n_steps=n_steps)
            
            for action in history['actions']:
                action_counts[action] += 1
                cluster_actions[cluster][action] += 1
            
            student_id += 1
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Action Distribution Analysis', fontsize=16, fontweight='bold')
        
        # 1. Overall action distribution
        ax1 = axes[0]
        actions = sorted(action_counts.keys(), key=lambda x: action_counts[x], reverse=True)
        counts = [action_counts[a] for a in actions]
        bars = ax1.bar(range(len(actions)), counts, color='steelblue', alpha=0.7, edgecolor='black')
        ax1.set_xticks(range(len(actions)))
        ax1.set_xticklabels(actions, rotation=45, ha='right')
        ax1.set_ylabel('Count')
        ax1.set_title('Overall Action Distribution')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add count labels
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # 2. Action distribution by cluster
        ax2 = axes[1]
        clusters_list = ['weak', 'medium', 'strong']
        actions_list = sorted(set(action_counts.keys()))
        
        x = np.arange(len(actions_list))
        width = 0.25
        
        for i, cluster in enumerate(clusters_list):
            counts = [cluster_actions[cluster].get(a, 0) for a in actions_list]
            offset = width * (i - 1)
            ax2.bar(x + offset, counts, width, label=cluster.capitalize(), alpha=0.7)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(actions_list, rotation=45, ha='right')
        ax2.set_ylabel('Count')
        ax2.set_title('Action Distribution by Cluster')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save:
            filename = self.output_dir / 'action_distribution.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved to {filename}")
        
        plt.show()


def demo_visualizer():
    """Demo các visualization"""
    print("=" * 80)
    print("TRAINING VISUALIZATION DEMO")
    print("=" * 80)
    
    viz = TrainingVisualizer(qtable_path='models/qtable.pkl')
    
    # 1. Visualize individual students
    print("\n1️⃣  Individual Student Learning:")
    for cluster in ['weak', 'medium', 'strong']:
        viz.visualize_student_learning(cluster=cluster, student_id=1, n_steps=50, save=True)
    
    # 2. Cluster comparison
    print("\n2️⃣  Cluster Comparison:")
    viz.compare_clusters(n_students_per_cluster=5, n_steps=40, save=True)
    
    # 3. Midterm predictions
    print("\n3️⃣  Midterm Score Predictions:")
    viz.visualize_midterm_predictions(n_students_per_cluster=10, n_steps=40, save=True)
    
    # 4. Action distribution
    print("\n4️⃣  Action Distribution:")
    viz.visualize_action_distribution(n_students=30, n_steps=40, save=True)
    
    print("\n" + "=" * 80)
    print("✓ Visualization complete! Check plots/training/ directory")
    print("=" * 80)


if __name__ == '__main__':
    demo_visualizer()
