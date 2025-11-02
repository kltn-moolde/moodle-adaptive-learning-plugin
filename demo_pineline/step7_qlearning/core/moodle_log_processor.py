#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle Log Processor
====================
Xử lý log thô từ Moodle CSV và tạo training data cho Q-Learning

Input: Raw Moodle logs (log.csv, grade.csv)
Output: (state, action, reward, next_state) tuples
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import ast


class MoodleLogProcessor:
    """
    Processor để xử lý log thô từ Moodle
    
    Features:
    - Parse log.csv và grade.csv
    - Extract student interactions
    - Calculate state từ log history
    - Map events to actions
    - Calculate rewards
    """
    
    def __init__(
        self,
        log_csv_path: str,
        grade_csv_path: Optional[str] = None,
        course_structure_path: Optional[str] = None
    ):
        """
        Initialize log processor
        
        Args:
            log_csv_path: Path to log.csv
            grade_csv_path: Path to grade.csv (optional)
            course_structure_path: Path to course_structure.json (optional)
        """
        self.log_csv_path = log_csv_path
        self.grade_csv_path = grade_csv_path
        self.course_structure_path = course_structure_path
        
        # Load data
        print("Loading Moodle logs...")
        self.df_log = self._load_log_csv()
        self.df_grade = self._load_grade_csv() if grade_csv_path else None
        self.course_structure = self._load_course_structure() if course_structure_path else None
        
        print(f"  ✓ Loaded {len(self.df_log)} log entries")
        if self.df_grade is not None:
            print(f"  ✓ Loaded {len(self.df_grade)} grade entries")
    
    def _load_log_csv(self) -> pd.DataFrame:
        """Load and parse log.csv"""
        df = pd.read_csv(self.log_csv_path)
        
        # Parse timestamp
        if 'timecreated' in df.columns:
            # Try multiple formats
            try:
                df['timestamp'] = pd.to_datetime(df['timecreated'], unit='s')
            except:
                try:
                    df['timestamp'] = pd.to_datetime(df['timecreated'])
                except:
                    print("  ⚠ Warning: Could not parse timecreated")
        
        # Sort by user and time
        df = df.sort_values(['userid', 'timestamp'])
        
        return df
    
    def _load_grade_csv(self) -> pd.DataFrame:
        """Load and parse grade.csv"""
        if not os.path.exists(self.grade_csv_path):
            return None
        
        df = pd.read_csv(self.grade_csv_path)
        
        # Parse timestamp if exists
        if 'timecreated' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timecreated'])
            except:
                pass
        
        return df
    
    def _load_course_structure(self) -> Dict:
        """Load course structure"""
        if not os.path.exists(self.course_structure_path):
            return None
        
        with open(self.course_structure_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_student_ids(self) -> List[int]:
        """Get all unique student IDs"""
        return sorted(self.df_log['userid'].unique().tolist())
    
    def get_student_logs(
        self,
        student_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get logs for a specific student
        
        Args:
            student_id: Student ID
            start_time: Start time filter
            end_time: End time filter
        
        Returns:
            DataFrame of student logs
        """
        logs = self.df_log[self.df_log['userid'] == student_id].copy()
        
        if start_time:
            logs = logs[logs['timestamp'] >= start_time]
        if end_time:
            logs = logs[logs['timestamp'] <= end_time]
        
        return logs
    
    def extract_interactions(
        self,
        min_session_gap_minutes: int = 30
    ) -> List[Dict]:
        """
        Extract learning interactions từ logs
        
        Interaction = Student làm 1 activity (quiz, assignment, resource, etc.)
        
        Args:
            min_session_gap_minutes: Gap time to separate sessions
        
        Returns:
            List of interactions:
            [
                {
                    'student_id': 8670,
                    'timestamp': datetime,
                    'action_type': 'quiz_submit',
                    'action_id': 56,
                    'session_id': 'student_8670_session_0',
                    'time_spent': 120,  # seconds
                },
                ...
            ]
        """
        print("\nExtracting interactions from logs...")
        
        interactions = []
        
        # Process each student
        student_ids = self.get_student_ids()
        
        for i, student_id in enumerate(student_ids, 1):
            print(f"  Processing student {i}/{len(student_ids)}: {student_id}", end='\r')
            
            student_logs = self.get_student_logs(student_id)
            
            # Group into sessions
            sessions = self._group_into_sessions(student_logs, min_session_gap_minutes)
            
            # Extract interactions from each session
            for session_id, session_logs in sessions.items():
                session_interactions = self._extract_session_interactions(
                    student_id, session_id, session_logs
                )
                interactions.extend(session_interactions)
        
        print(f"\n  ✓ Extracted {len(interactions)} interactions from {len(student_ids)} students")
        
        return interactions
    
    def _group_into_sessions(
        self,
        logs: pd.DataFrame,
        gap_minutes: int
    ) -> Dict[str, pd.DataFrame]:
        """
        Group logs into sessions based on time gap
        
        Args:
            logs: Student logs
            gap_minutes: Gap to separate sessions
        
        Returns:
            Dict mapping session_id -> session_logs
        """
        if len(logs) == 0:
            return {}
        
        sessions = {}
        session_idx = 0
        
        current_session = []
        prev_time = None
        
        for _, row in logs.iterrows():
            current_time = row['timestamp']
            
            # Check if new session
            if prev_time is not None:
                gap = (current_time - prev_time).total_seconds() / 60
                if gap > gap_minutes:
                    # Save current session
                    if current_session:
                        session_id = f"student_{row['userid']}_session_{session_idx}"
                        sessions[session_id] = pd.DataFrame(current_session)
                        session_idx += 1
                    
                    # Start new session
                    current_session = []
            
            current_session.append(row)
            prev_time = current_time
        
        # Save last session
        if current_session:
            student_id = logs.iloc[0]['userid']
            session_id = f"student_{student_id}_session_{session_idx}"
            sessions[session_id] = pd.DataFrame(current_session)
        
        return sessions
    
    def _extract_session_interactions(
        self,
        student_id: int,
        session_id: str,
        session_logs: pd.DataFrame
    ) -> List[Dict]:
        """
        Extract interactions từ 1 session
        
        Identify key events:
        - Quiz: attempt_submitted
        - Assignment: assessable_submitted
        - Resource: course_module_viewed (mod_resource, mod_page, mod_hvp)
        - Forum: discussion_viewed, post_created
        """
        interactions = []
        
        # Group events by action type
        for _, row in session_logs.iterrows():
            event = row['eventname']
            action_type = row['action']
            target = row['target']
            
            interaction = None
            
            # QUIZ
            if 'mod_quiz' in event:
                if 'submitted' in action_type:
                    interaction = {
                        'type': 'quiz',
                        'action': 'submit',
                        'module': 'quiz'
                    }
                elif 'viewed' in action_type and 'attempt' in target:
                    interaction = {
                        'type': 'quiz',
                        'action': 'view',
                        'module': 'quiz'
                    }
            
            # ASSIGNMENT
            elif 'mod_assign' in event:
                if 'submitted' in action_type:
                    interaction = {
                        'type': 'assignment',
                        'action': 'submit',
                        'module': 'assign'
                    }
                elif 'viewed' in action_type and 'course_module' in target:
                    interaction = {
                        'type': 'assignment',
                        'action': 'view',
                        'module': 'assign'
                    }
            
            # RESOURCE
            elif any(mod in event for mod in ['mod_resource', 'mod_page', 'mod_hvp', 'mod_folder']):
                if 'viewed' in action_type:
                    module = event.split('\\')[1].replace('mod_', '')
                    interaction = {
                        'type': 'resource',
                        'action': 'view',
                        'module': module
                    }
            
            # FORUM
            elif 'mod_forum' in event:
                if 'viewed' in action_type:
                    interaction = {
                        'type': 'forum',
                        'action': 'view',
                        'module': 'forum'
                    }
                elif 'created' in action_type:
                    interaction = {
                        'type': 'forum',
                        'action': 'post',
                        'module': 'forum'
                    }
            
            # Add interaction
            if interaction:
                # Parse 'other' field for additional info
                other_data = {}
                if 'other' in row and pd.notna(row['other']):
                    try:
                        other_data = ast.literal_eval(row['other'])
                    except:
                        pass
                
                interaction.update({
                    'student_id': student_id,
                    'timestamp': row['timestamp'],
                    'session_id': session_id,
                    'event': event,
                    'courseid': row.get('courseid'),
                    'other': other_data
                })
                
                interactions.append(interaction)
        
        return interactions
    
    def calculate_state_features(
        self,
        student_id: int,
        before_timestamp: datetime,
        window_days: int = 30
    ) -> Dict:
        """
        Calculate student state features BEFORE timestamp
        
        Features (12 dimensions - MATCH với MoodleStateBuilder):
        
        === 1. STUDENT PERFORMANCE (3 dims) ===
        1. knowledge_level: mean grade (0-1)
        2. engagement_level: normalized total events
        3. struggle_indicator: high attempts + low feedback
        
        === 2. ACTIVITY PATTERNS (5 dims) ===
        4. submission_activity: submit events normalized
        5. review_activity: review + feedback events
        6. resource_usage: resource/page views
        7. assessment_engagement: quiz/assign events
        8. collaborative_activity: forum/comment events
        
        === 3. COMPLETION METRICS (4 dims) ===
        9. overall_progress: module count normalized
        10. module_completion_rate: completion rate
        11. activity_diversity: diversity of activity types
        12. completion_consistency: consistency across modules
        
        Args:
            student_id: Student ID
            before_timestamp: Calculate state BEFORE this time
            window_days: Look back window (days)
        
        Returns:
            Dict of features (12 keys matching state_builder.py)
        """
        # Get logs in time window
        start_time = before_timestamp - timedelta(days=window_days)
        logs = self.get_student_logs(student_id, start_time, before_timestamp)
        
        if len(logs) == 0:
            # Return default values for new student (12 dims matching state_builder.py)
            return {
                'knowledge_level': 0.5,
                'engagement_level': 0.0,
                'struggle_indicator': 0.0,
                'submission_activity': 0.0,
                'review_activity': 0.0,
                'resource_usage': 0.0,
                'assessment_engagement': 0.0,
                'collaborative_activity': 0.0,
                'overall_progress': 0.0,
                'module_completion_rate': 0.0,
                'activity_diversity': 0.0,
                'completion_consistency': 0.0
            }
        
        # Calculate features
        features = {}
        
        # Normalize factor (for scaling event counts to 0-1)
        max_events = max(len(logs), 100)  # Use 100 as baseline
        
        # === 1. STUDENT PERFORMANCE (3 dims) ===
        
        # 1.1 Knowledge level (from grades)
        features['knowledge_level'] = self._calculate_avg_grade(student_id, before_timestamp)
        
        # 1.2 Engagement level (normalized total events)
        features['engagement_level'] = min(len(logs) / max_events, 1.0)
        
        # 1.3 Struggle indicator
        quiz_attempts = len(logs[logs['eventname'].str.contains('mod_quiz.*attempt', na=False)])
        feedback_views = len(logs[logs['eventname'].str.contains('feedback_viewed', na=False)])
        attempt_norm = min(quiz_attempts / 10, 1.0)  # Normalize by 10 attempts
        feedback_norm = min(feedback_views / 5, 1.0)  # Normalize by 5 feedbacks
        struggle = attempt_norm * (1 - feedback_norm) * (1 - features['knowledge_level'])
        features['struggle_indicator'] = np.clip(struggle, 0.0, 1.0)
        
        # === 2. ACTIVITY PATTERNS (5 dims) ===
        
        # 2.1 Submission activity
        submit_events = len(logs[logs['eventname'].str.contains('submitted|assessable_submitted|submission_created', na=False)])
        features['submission_activity'] = min(submit_events / 10, 1.0)
        
        # 2.2 Review activity
        review_events = len(logs[logs['eventname'].str.contains('reviewed|feedback_viewed|attempt_reviewed', na=False)])
        features['review_activity'] = min(review_events / 10, 1.0)
        
        # 2.3 Resource usage
        resource_patterns = ['mod_resource', 'mod_page', 'mod_url', 'course_module_viewed']
        resource_events = len(logs[logs['eventname'].str.contains('|'.join(resource_patterns), na=False)])
        features['resource_usage'] = min(resource_events / 20, 1.0)
        
        # 2.4 Assessment engagement
        assessment_patterns = ['mod_quiz.*attempt', 'mod_assign.*submitted']
        assessment_events = len(logs[logs['eventname'].str.contains('|'.join(assessment_patterns), na=False)])
        features['assessment_engagement'] = min(assessment_events / 10, 1.0)
        
        # 2.5 Collaborative activity
        collab_patterns = ['mod_forum', 'comment']
        collab_events = len(logs[logs['eventname'].str.contains('|'.join(collab_patterns), na=False)])
        features['collaborative_activity'] = min(collab_events / 10, 1.0)
        
        # === 3. COMPLETION METRICS (4 dims) ===
        
        # 3.1 Overall progress (module count)
        module_views = logs['eventname'].str.contains('course_module_viewed', na=False).sum()
        features['overall_progress'] = min(module_views / 30, 1.0)  # Normalize by 30 modules
        
        # 3.2 Module completion rate
        completion_events = logs[logs['eventname'].str.contains('completion_updated', na=False)]
        completed = len(completion_events[completion_events['other'].str.contains('completionstate.*1', na=False)])
        total_modules = max(module_views, 1)
        features['module_completion_rate'] = completed / total_modules
        
        # 3.3 Activity diversity
        activity_types = ['submitted', 'viewed', 'created', 'updated', 'downloaded', 'reviewed', 'uploaded']
        active_types = sum([
            1 for activity in activity_types
            if logs['action'].str.contains(activity, na=False).sum() > 0
        ])
        features['activity_diversity'] = active_types / len(activity_types)
        
        # 3.4 Completion consistency
        # Check consistency across different modules
        unique_modules = logs['contextinstanceid'].nunique() if 'contextinstanceid' in logs.columns else 1
        events_per_module = len(logs) / max(unique_modules, 1)
        # High consistency = similar events per module (std close to mean)
        consistency = 1.0 - min(events_per_module / max_events, 1.0)
        features['completion_consistency'] = np.clip(consistency, 0.0, 1.0)
        
        return features
    
    def _calculate_avg_grade(self, student_id: int, before_timestamp: datetime) -> float:
        """Calculate average grade from grade.csv"""
        if self.df_grade is None:
            return 0.5  # Default
        
        # Filter grades for this student before timestamp
        student_grades = self.df_grade[
            (self.df_grade['userid'] == student_id) &
            (self.df_grade['timestamp'] <= before_timestamp)
        ] if 'timestamp' in self.df_grade.columns else self.df_grade[self.df_grade['userid'] == student_id]
        
        if len(student_grades) == 0:
            return 0.5
        
        # TODO: Parse grade from 'other' field or separate grade column
        # For now, return default
        return 0.5
    
    def _calculate_streak_days(self, logs: pd.DataFrame) -> int:
        """Calculate consecutive days with activity"""
        if len(logs) == 0:
            return 0
        
        # Get unique dates
        dates = logs['timestamp'].dt.date.unique()
        dates = sorted(dates)
        
        # Count consecutive days
        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i + 1] - dates[i]).days == 1:
                streak += 1
            else:
                break
        
        return streak
    
    def create_training_episodes(
        self,
        interaction_types: List[str] = ['quiz', 'assignment'],
        min_session_gap_minutes: int = 30
    ) -> List[Dict]:
        """
        Create training episodes for Q-Learning
        
        Episode = (state_before, action, reward, state_after)
        
        Args:
            interaction_types: Types of interactions to include
            min_session_gap_minutes: Session gap threshold
        
        Returns:
            List of episodes
        """
        print("\n" + "=" * 70)
        print("CREATING TRAINING EPISODES FROM MOODLE LOGS")
        print("=" * 70)
        
        # Extract interactions
        all_interactions = self.extract_interactions(min_session_gap_minutes)
        
        # Filter by type
        filtered_interactions = [
            i for i in all_interactions
            if i['type'] in interaction_types and i['action'] in ['submit', 'view']
        ]
        
        print(f"\nFiltered {len(filtered_interactions)} interactions (types: {interaction_types})")
        
        # Create episodes
        episodes = []
        
        for i, interaction in enumerate(filtered_interactions, 1):
            print(f"  Creating episode {i}/{len(filtered_interactions)}", end='\r')
            
            student_id = interaction['student_id']
            timestamp = interaction['timestamp']
            
            # State BEFORE interaction
            state_before = self.calculate_state_features(
                student_id,
                timestamp - timedelta(seconds=1)
            )
            
            # Action
            action = {
                'type': interaction['type'],
                'module': interaction['module'],
                'action': interaction['action']
            }
            
            # Reward (estimate - need actual grade data)
            reward = self._estimate_reward(interaction)
            
            # State AFTER interaction
            state_after = self.calculate_state_features(
                student_id,
                timestamp + timedelta(seconds=1)
            )
            
            episode = {
                'student_id': student_id,
                'timestamp': timestamp,
                'state_before': state_before,
                'action': action,
                'reward': reward,
                'state_after': state_after,
                'interaction': interaction
            }
            
            episodes.append(episode)
        
        print(f"\n\n✓ Created {len(episodes)} training episodes")
        
        return episodes
    
    def _estimate_reward(self, interaction: Dict) -> float:
        """
        Estimate reward for an interaction
        
        TODO: Use actual grade data from grade.csv
        
        For now:
        - Submit quiz/assignment: +1.0
        - View resource: +0.5
        - Submit late: -0.2
        """
        reward = 0.0
        
        if interaction['action'] == 'submit':
            reward = 1.0
            
            # TODO: Add score-based reward
            # if 'score' in interaction['other']:
            #     reward += interaction['other']['score'] / 100.0
        
        elif interaction['action'] == 'view':
            reward = 0.5
        
        return reward
    
    def save_episodes(self, episodes: List[Dict], output_path: str):
        """Save episodes to JSON"""
        print(f"\nSaving episodes to {output_path}...")
        
        # Convert datetime/Timestamp to string recursively
        def convert_timestamps(obj):
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_timestamps(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_timestamps(v) for v in obj]
            else:
                return obj
        
        episodes_json = [convert_timestamps(ep) for ep in episodes]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(episodes_json, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Saved {len(episodes)} episodes")


# ============================================================================
# Demo Usage
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Moodle logs to create training data')
    parser.add_argument('--log-csv', type=str, required=True, help='Path to log.csv')
    parser.add_argument('--grade-csv', type=str, default=None, help='Path to grade.csv')
    parser.add_argument('--course-structure', type=str, default=None, help='Path to course_structure.json')
    parser.add_argument('--output', type=str, default='data/training_episodes.json', help='Output path')
    parser.add_argument('--interaction-types', nargs='+', default=['quiz', 'assignment'], help='Interaction types')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = MoodleLogProcessor(
        log_csv_path=args.log_csv,
        grade_csv_path=args.grade_csv,
        course_structure_path=args.course_structure
    )
    
    # Create episodes
    episodes = processor.create_training_episodes(
        interaction_types=args.interaction_types
    )
    
    # Save
    processor.save_episodes(episodes, args.output)
    
    print("\n" + "=" * 70)
    print("✅ PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\nGenerated {len(episodes)} training episodes")
    print(f"Output: {args.output}")
    print("\nNext step: Train Q-learning model")
    print(f"  python train_qlearning_from_logs.py --data {args.output}")
