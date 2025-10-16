#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Progress Visualization
================================
Visualize student learning progress and improvement during Q-Learning training
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, List


def load_training_data():
    """Load training history and data"""
    base_path = Path(__file__).parent
    
    # Load training history
    with open(base_path / "results/training_history.json", 'r') as f:
        history = json.load(f)
    
    # Load train data
    train_df = pd.read_csv(base_path / "data/simulated/train_data.csv")
    
    return history, train_df


def compute_reward(row):
    """Compute reward from record (same formula as in trainer)"""
    grade = row['grade']
    time_spent = row['time_spent']
    completed = row['completed']
    
    grade_reward = grade
    time_normalized = min(time_spent / 60, 1)
    time_reward = 1.0 - time_normalized
    completion_reward = 1.0 if completed else 0.0
    
    return 0.5 * grade_reward + 0.2 * time_reward + 0.3 * completion_reward


def plot_epoch_metrics(history: Dict):
    """Plot overall metrics across epochs"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Training Metrics Across Epochs', fontsize=16)
    
    epochs = range(1, len(history['episode_rewards']) + 1)
    
    # 1. Average Reward
    axes[0, 0].plot(epochs, history['episode_rewards'], marker='o', color='blue')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Avg Reward')
    axes[0, 0].set_title('Average Reward per Epoch')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Average Grade
    if 'epoch_avg_grades' in history:
        axes[0, 1].plot(epochs, history['epoch_avg_grades'], marker='o', color='green')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Avg Grade')
        axes[0, 1].set_title('Average Grade per Epoch')
        axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Completion Rate
    if 'epoch_completion_rates' in history:
        axes[0, 2].plot(epochs, history['epoch_completion_rates'], marker='o', color='orange')
        axes[0, 2].set_xlabel('Epoch')
        axes[0, 2].set_ylabel('Completion Rate')
        axes[0, 2].set_title('Completion Rate per Epoch')
        axes[0, 2].set_ylim([0, 1.1])
        axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Average Q-value
    axes[1, 0].plot(epochs, history['avg_q_values'], marker='o', color='red')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Avg Q-value')
    axes[1, 0].set_title('Average Q-value per Epoch')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Average Time Spent
    if 'epoch_avg_time_spent' in history:
        axes[1, 1].plot(epochs, history['epoch_avg_time_spent'], marker='o', color='purple')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Avg Time (min)')
        axes[1, 1].set_title('Average Time Spent per Epoch')
        axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Episode Length
    axes[1, 2].plot(epochs, history['episode_lengths'], marker='o', color='brown')
    axes[1, 2].set_xlabel('Epoch')
    axes[1, 2].set_ylabel('Episode Length')
    axes[1, 2].set_title('Average Episode Length')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/epoch_metrics.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/epoch_metrics.png")
    plt.show()


def plot_student_progress(history: Dict, n_students: int = 5):
    """Plot individual student progress across epochs"""
    if 'student_progress' not in history or not history['student_progress']:
        print("⚠ No student progress data available")
        return
    
    student_ids = list(history['student_progress'].keys())[:n_students]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(f'Individual Student Progress (Top {n_students} Students)', fontsize=16)
    
    for student_id in student_ids:
        progress = history['student_progress'][student_id]
        epochs = range(1, len(progress['epoch_avg_grades']) + 1)
        
        # Grade progress
        axes[0].plot(epochs, progress['epoch_avg_grades'], marker='o', label=f'Student {student_id}')
        
        # Reward progress
        axes[1].plot(epochs, progress['epoch_avg_rewards'], marker='o', label=f'Student {student_id}')
        
        # Completion rate progress
        axes[2].plot(epochs, progress['epoch_completion_rates'], marker='o', label=f'Student {student_id}')
    
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Avg Grade')
    axes[0].set_title('Grade Progress')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Avg Reward')
    axes[1].set_title('Reward Progress')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    axes[2].set_xlabel('Epoch')
    axes[2].set_ylabel('Completion Rate')
    axes[2].set_title('Completion Rate Progress')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/student_progress.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/student_progress.png")
    plt.show()


def plot_student_improvement_ranking(history: Dict):
    """Rank students by improvement (first epoch vs last epoch)"""
    if 'student_progress' not in history or not history['student_progress']:
        print("⚠ No student progress data available")
        return
    
    improvements = {}
    
    for student_id, progress in history['student_progress'].items():
        if len(progress['epoch_avg_grades']) >= 2:
            first_grade = progress['epoch_avg_grades'][0]
            last_grade = progress['epoch_avg_grades'][-1]
            improvement = last_grade - first_grade
            improvements[student_id] = improvement
    
    # Sort by improvement
    sorted_students = sorted(improvements.items(), key=lambda x: x[1], reverse=True)
    
    # Plot top 10 and bottom 10
    n_show = min(10, len(sorted_students) // 2)
    top_students = sorted_students[:n_show]
    bottom_students = sorted_students[-n_show:]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Student Improvement Ranking (Grade Change: First → Last Epoch)', fontsize=16)
    
    # Top improvers
    student_ids_top = [str(s[0]) for s in top_students]
    improvements_top = [s[1] for s in top_students]
    ax1.barh(student_ids_top, improvements_top, color='green')
    ax1.set_xlabel('Grade Improvement')
    ax1.set_ylabel('Student ID')
    ax1.set_title(f'Top {n_show} Most Improved Students')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Bottom improvers (or decliners)
    student_ids_bottom = [str(s[0]) for s in bottom_students]
    improvements_bottom = [s[1] for s in bottom_students]
    ax2.barh(student_ids_bottom, improvements_bottom, color='red')
    ax2.set_xlabel('Grade Improvement')
    ax2.set_ylabel('Student ID')
    ax2.set_title(f'Bottom {n_show} Students')
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('results/student_improvement_ranking.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/student_improvement_ranking.png")
    plt.show()


def plot_learning_trajectory_samples(train_df: pd.DataFrame, n_students: int = 3):
    """Plot learning trajectories for sample students"""
    train_df['reward'] = train_df.apply(compute_reward, axis=1)
    
    unique_students = train_df['student_id'].unique()[:n_students]
    
    fig, axes = plt.subplots(n_students, 3, figsize=(15, 4 * n_students))
    if n_students == 1:
        axes = axes.reshape(1, -1)
    
    fig.suptitle('Sample Student Learning Trajectories', fontsize=16)
    
    for i, student_id in enumerate(unique_students):
        student_df = train_df[train_df['student_id'] == student_id].sort_values('step')
        steps = student_df['step'].values
        
        # Grade trajectory
        axes[i, 0].plot(steps, student_df['grade'].values, marker='o', color='blue')
        axes[i, 0].set_xlabel('Step')
        axes[i, 0].set_ylabel('Grade')
        axes[i, 0].set_title(f'Student {student_id} - Grade')
        axes[i, 0].set_ylim([0, 1.1])
        axes[i, 0].grid(True, alpha=0.3)
        
        # Reward trajectory
        axes[i, 1].plot(steps, student_df['reward'].values, marker='o', color='green')
        axes[i, 1].set_xlabel('Step')
        axes[i, 1].set_ylabel('Reward')
        axes[i, 1].set_title(f'Student {student_id} - Reward')
        axes[i, 1].set_ylim([0, 1.1])
        axes[i, 1].grid(True, alpha=0.3)
        
        # Time spent trajectory
        axes[i, 2].plot(steps, student_df['time_spent'].values, marker='o', color='orange')
        axes[i, 2].set_xlabel('Step')
        axes[i, 2].set_ylabel('Time (min)')
        axes[i, 2].set_title(f'Student {student_id} - Time Spent')
        axes[i, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/learning_trajectories.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/learning_trajectories.png")
    plt.show()


def plot_grade_distribution_by_epoch(history: Dict, train_df: pd.DataFrame):
    """Plot grade distribution evolution across epochs"""
    if 'student_progress' not in history or not history['student_progress']:
        print("⚠ No student progress data available")
        return
    
    # Get number of epochs
    first_student = list(history['student_progress'].keys())[0]
    n_epochs = len(history['student_progress'][first_student]['epoch_avg_grades'])
    
    # Collect grades for each epoch
    epoch_grades = {i: [] for i in range(n_epochs)}
    
    for student_id, progress in history['student_progress'].items():
        for epoch_idx, grade in enumerate(progress['epoch_avg_grades']):
            epoch_grades[epoch_idx].append(grade)
    
    # Plot distributions
    fig, ax = plt.subplots(figsize=(12, 6))
    
    positions = []
    data_to_plot = []
    labels = []
    
    for epoch_idx in range(n_epochs):
        positions.append(epoch_idx + 1)
        data_to_plot.append(epoch_grades[epoch_idx])
        labels.append(f'Epoch {epoch_idx + 1}')
    
    bp = ax.boxplot(data_to_plot, positions=positions, labels=labels, patch_artist=True)
    
    # Color boxes
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Grade')
    ax.set_title('Grade Distribution Evolution Across Epochs')
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('results/grade_distribution_evolution.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/grade_distribution_evolution.png")
    plt.show()


def main():
    """Main visualization script"""
    print("\n" + "="*70)
    print("Student Progress Visualization")
    print("="*70)
    
    # Load data
    print("\nLoading data...")
    history, train_df = load_training_data()
    print(f"✓ Loaded training history with {len(history['episode_rewards'])} epochs")
    print(f"✓ Loaded train data with {len(train_df)} records")
    
    # Create results directory if not exists
    Path("results").mkdir(exist_ok=True)
    
    # 1. Plot epoch-level metrics
    print("\n1. Plotting epoch-level metrics...")
    plot_epoch_metrics(history)
    
    # 2. Plot individual student progress
    print("\n2. Plotting individual student progress...")
    plot_student_progress(history, n_students=5)
    
    # 3. Plot student improvement ranking
    print("\n3. Plotting student improvement ranking...")
    plot_student_improvement_ranking(history)
    
    # 4. Plot sample learning trajectories
    print("\n4. Plotting sample learning trajectories...")
    plot_learning_trajectory_samples(train_df, n_students=3)
    
    # 5. Plot grade distribution evolution
    print("\n5. Plotting grade distribution evolution...")
    plot_grade_distribution_by_epoch(history, train_df)
    
    print("\n" + "="*70)
    print("✅ Visualization completed!")
    print("="*70)


if __name__ == '__main__':
    main()
