#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Daily Q-Table
====================
Pipeline tự động cập nhật Q-table mỗi ngày từ real logs
"""

import os
import argparse
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from core.state_builder import MoodleStateBuilder
from core.action_space import ActionSpace
from core.reward_calculator import RewardCalculator
from core.qlearning_agent import QLearningAgent


def fetch_daily_logs(date: datetime) -> List[Dict]:
    """
    Fetch logs từ Moodle cho ngày cụ thể
    
    TODO: Implement actual Moodle API integration
    
    Args:
        date: Date to fetch logs
    
    Returns:
        List of log entries
    """
    # Placeholder: trong thực tế sẽ call Moodle API
    print(f"  → Fetching logs for {date.strftime('%Y-%m-%d')}...")
    
    # Mock data structure
    logs = []
    
    return logs


def extract_features_from_logs(logs: List[Dict]) -> Dict:
    """
    Extract features từ logs
    
    TODO: Implement feature extraction pipeline
    
    Args:
        logs: Raw log entries
    
    Returns:
        Features dict compatible with state_builder
    """
    # Placeholder: trong thực tế sẽ chạy feature extraction pipeline
    features = {}
    
    return features


def update_daily_qtable(
    model_path: str = 'models/qlearning_model.pkl',
    date: Optional[datetime] = None,
    learning_rate: Optional[float] = None
):
    """
    Main pipeline: cập nhật Q-table từ logs thực tế
    
    Pipeline:
    1. Fetch logs từ Moodle (ngày hôm trước)
    2. Extract features từ logs
    3. Build states cho từng student
    4. Identify actions và outcomes
    5. Calculate rewards
    6. Update Q-table
    7. Save updated model
    8. Generate recommendations
    
    Args:
        model_path: Path to Q-learning model
        date: Date to process (default: yesterday)
        learning_rate: Override learning rate (optional)
    """
    print("=" * 70)
    print("UPDATE DAILY Q-TABLE")
    print("=" * 70)
    
    # Setup date
    if date is None:
        date = datetime.now() - timedelta(days=1)
    
    print(f"\nProcessing date: {date.strftime('%Y-%m-%d')}")
    
    # Initialize components
    print("\n[1/8] Initializing components...")
    data_dir = 'data'
    course_structure_path = os.path.join(data_dir, 'course_structure.json')
    cluster_profiles_path = os.path.join(data_dir, 'cluster_profiles.json')
    
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(course_structure_path)
    reward_calculator = RewardCalculator(cluster_profiles_path)
    
    # Load existing model
    print("\n[2/8] Loading existing Q-learning model...")
    if not os.path.exists(model_path):
        print(f"  ✗ Model not found: {model_path}")
        print("  Please train initial model first")
        return
    
    agent = QLearningAgent(n_actions=action_space.get_action_count())
    agent.load(model_path)
    
    print(f"  ✓ Model loaded")
    print(f"    - Q-table size: {len(agent.q_table)} states")
    print(f"    - Total updates: {agent.training_stats['total_updates']}")
    
    # Override learning rate if provided
    if learning_rate is not None:
        agent.learning_rate = learning_rate
        print(f"    - Learning rate overridden: {learning_rate}")
    
    # Fetch daily logs
    print("\n[3/8] Fetching daily logs from Moodle...")
    logs = fetch_daily_logs(date)
    
    if not logs:
        print("  ⚠ No logs found for this date")
        print("  Skipping update")
        return
    
    print(f"  ✓ Fetched {len(logs)} log entries")
    
    # Extract features
    print("\n[4/8] Extracting features from logs...")
    features = extract_features_from_logs(logs)
    print(f"  ✓ Extracted features for {len(features)} students")
    
    # Build states
    print("\n[5/8] Building states...")
    student_states = {}
    for student_id, student_features in features.items():
        state = state_builder.build_state(student_features)
        student_states[student_id] = state
    
    print(f"  ✓ Built {len(student_states)} student states")
    
    # Identify interactions
    print("\n[6/8] Identifying interactions and outcomes...")
    # TODO: Map logs to (state, action, reward, next_state)
    interactions = []
    print(f"  ✓ Identified {len(interactions)} interactions")
    
    # Update Q-table
    print("\n[7/8] Updating Q-table...")
    updates_count = 0
    
    for interaction in interactions:
        state = interaction['state']
        action_id = interaction['action_id']
        reward = interaction['reward']
        next_state = interaction['next_state']
        
        agent.update(state, action_id, reward, next_state)
        updates_count += 1
    
    print(f"  ✓ Applied {updates_count} Q-value updates")
    
    # Save updated model
    print("\n[8/8] Saving updated model...")
    
    # Backup old model
    backup_path = model_path.replace('.pkl', f'_backup_{date.strftime("%Y%m%d")}.pkl')
    if os.path.exists(model_path):
        import shutil
        shutil.copy(model_path, backup_path)
        print(f"  ✓ Backed up old model: {backup_path}")
    
    # Save new model
    agent.save(model_path)
    print(f"  ✓ Saved updated model: {model_path}")
    
    # Statistics
    print("\n" + "=" * 70)
    print("UPDATE COMPLETE")
    print("=" * 70)
    
    stats = agent.get_statistics()
    print(f"\nModel Statistics:")
    print(f"  Q-table size: {stats['q_table_size']} states")
    print(f"  Total updates: {stats['total_updates']}")
    print(f"  Today's updates: {updates_count}")
    print(f"  Avg actions/state: {stats['avg_actions_per_state']:.2f}")
    
    # Generate recommendations
    print("\n" + "-" * 70)
    print("GENERATING RECOMMENDATIONS")
    print("-" * 70)
    
    recommendations_dir = 'data/recommendations'
    os.makedirs(recommendations_dir, exist_ok=True)
    
    all_recommendations = {}
    
    for student_id, state in student_states.items():
        # Get available actions (filter by student progress)
        available_actions = [a.id for a in action_space.get_actions()]
        
        # Get recommendations
        recs = agent.recommend_action(state, available_actions, top_k=5)
        
        all_recommendations[student_id] = [
            {
                'action_id': action_id,
                'action_name': action_space.get_action_by_id(action_id).name,
                'q_value': float(q_val)
            }
            for action_id, q_val in recs
        ]
    
    # Save recommendations
    recommendations_file = os.path.join(
        recommendations_dir,
        f'recommendations_{date.strftime("%Y%m%d")}.json'
    )
    
    with open(recommendations_file, 'w', encoding='utf-8') as f:
        json.dump(all_recommendations, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Saved recommendations: {recommendations_file}")
    print(f"  ✓ Generated recommendations for {len(all_recommendations)} students")
    
    print("\n" + "=" * 70)
    print("✅ DAILY UPDATE SUCCESSFUL")
    print("=" * 70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update Q-table daily from real logs'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='models/qlearning_model.pkl',
        help='Path to Q-learning model'
    )
    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Date to process (YYYY-MM-DD, default: yesterday)'
    )
    parser.add_argument(
        '--lr',
        type=float,
        default=None,
        help='Override learning rate'
    )
    
    args = parser.parse_args()
    
    # Parse date
    date = None
    if args.date:
        date = datetime.strptime(args.date, '%Y-%m-%d')
    
    update_daily_qtable(
        model_path=args.model,
        date=date,
        learning_rate=args.lr
    )
