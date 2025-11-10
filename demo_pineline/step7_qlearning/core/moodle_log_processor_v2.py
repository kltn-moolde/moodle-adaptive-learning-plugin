"""
Moodle Log Processor V2
Processes Moodle logs into Q-Learning trajectories using StudentContext

This module reads log.csv and grade.csv, tracks student learning context,
and generates (state, action, reward, next_state) tuples for training.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple
import json
import sys
import os

# Add parent directory to path for testing
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.student_context import StudentContext
from core.state_builder_v2 import StateBuilderV2
from core.reward_calculator_v2 import RewardCalculatorV2


class MoodleLogProcessorV2:
    """
    Process Moodle logs into Q-Learning trajectories
    
    Workflow:
    1. Load log.csv and grade.csv
    2. Group logs by student_id
    3. For each student:
       - Initialize StudentContext
       - Process logs chronologically
       - Build (state, action, reward, next_state) tuples
    4. Return trajectories
    """
    
    def __init__(
        self, 
        log_csv_path: str = "data/log/log.csv",
        grade_csv_path: str = "data/log/grade.csv",
        cluster_profiles_path: str = "data/cluster_profiles.json",
        course_structure_path: str = "data/course_structure.json"
    ):
        """
        Initialize log processor
        
        Args:
            log_csv_path: Path to Moodle log CSV file
            grade_csv_path: Path to grade CSV file
            cluster_profiles_path: Path to cluster profiles JSON
            course_structure_path: Path to course structure JSON
        """
        print("=" * 60)
        print("Initializing MoodleLogProcessorV2...")
        print("=" * 60)
        
        # Load data
        print(f"\n1. Loading logs from: {log_csv_path}")
        self.logs_df = pd.read_csv(log_csv_path)
        print(f"   ✓ Loaded {len(self.logs_df)} log entries")
        
        print(f"\n2. Loading grades from: {grade_csv_path}")
        self.grades_df = pd.read_csv(grade_csv_path)
        print(f"   ✓ Loaded {len(self.grades_df)} grade entries")
        
        # Load cluster assignments (assuming cluster_id is in logs or grades)
        # For now, we'll extract from the data
        print("\n3. Loading cluster assignments...")
        self.student_clusters = self._load_student_clusters(cluster_profiles_path)
        print(f"   ✓ Loaded cluster assignments for {len(self.student_clusters)} students")
        
        # Initialize state builder and reward calculator
        print("\n4. Initializing StateBuilderV2...")
        self.state_builder = StateBuilderV2(
            course_structure_path=course_structure_path,
            cluster_profiles_path=cluster_profiles_path
        )
        
        print("\n5. Initializing RewardCalculatorV2...")
        self.reward_calculator = RewardCalculatorV2(
            cluster_profiles_path=cluster_profiles_path
        )
        
        # Convert time columns to datetime
        if 'timecreated' in self.logs_df.columns:
            self.logs_df['timecreated'] = pd.to_datetime(self.logs_df['timecreated'], unit='s')
        
        print("\n✓ MoodleLogProcessorV2 initialized!")
        print("=" * 60)
    
    def _load_student_clusters(self, cluster_profiles_path: str) -> Dict[int, int]:
        """
        Load student cluster assignments
        
        In a real scenario, this would come from a separate file.
        For now, we'll create a mapping from available data.
        
        Args:
            cluster_profiles_path: Path to cluster profiles JSON
            
        Returns:
            Dictionary mapping student_id -> cluster_id
        """
        # Check if logs have cluster_id column
        if 'cluster_id' in self.logs_df.columns:
            student_clusters = self.logs_df.groupby('userid')['cluster_id'].first().to_dict()
            return student_clusters
        
        # Check if grades have cluster_id column
        if 'cluster_id' in self.grades_df.columns:
            student_clusters = self.grades_df.groupby('userid')['cluster_id'].first().to_dict()
            return student_clusters
        
        # If no cluster assignments, assign randomly for testing
        # In production, this should be loaded from a proper source
        print("   ⚠ Warning: No cluster assignments found in data")
        print("   ⚠ Creating dummy cluster assignments for testing")
        
        unique_students = list(set(self.logs_df['userid'].unique()) | 
                             set(self.grades_df['userid'].unique() if 'userid' in self.grades_df.columns else set()))
        
        # Load cluster profiles to get valid cluster IDs
        with open(cluster_profiles_path, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)
        
        # Extract cluster IDs from cluster_stats
        cluster_stats = cluster_data.get('cluster_stats', {})
        valid_clusters = [int(cluster_id) for cluster_id in cluster_stats.keys() if int(cluster_id) != 3]  # Exclude teacher cluster
        
        # Assign students to clusters evenly
        student_clusters = {}
        for i, student_id in enumerate(unique_students):
            student_clusters[student_id] = valid_clusters[i % len(valid_clusters)]
        
        return student_clusters
    
    def process_logs(
        self, 
        student_ids: List[int] = None,
        min_trajectory_length: int = 5,
        verbose: bool = True
    ) -> Dict[int, List[Dict]]:
        """
        Process logs into Q-Learning trajectories
        
        Args:
            student_ids: List of student IDs to process (None = all students)
            min_trajectory_length: Minimum number of transitions per trajectory
            verbose: Print progress
            
        Returns:
            Dictionary mapping student_id -> trajectory
            Each trajectory is a list of transition dicts:
            {
                'state': state_tuple,
                'action': action_id,
                'reward': reward_value,
                'next_state': next_state_tuple,
                'timestamp': timestamp,
                'module_id': module_id,
                'is_terminal': bool
            }
        """
        if verbose:
            print("\n" + "=" * 60)
            print("Processing logs into trajectories...")
            print("=" * 60)
        
        # Get student list
        if student_ids is None:
            student_ids = [sid for sid in self.student_clusters.keys() 
                          if sid in self.logs_df['userid'].values]
        
        if verbose:
            print(f"\nProcessing {len(student_ids)} students...")
        
        # Process each student
        trajectories = {}
        students_processed = 0
        students_skipped = 0
        
        for student_id in student_ids:
            trajectory = self._process_student(student_id, verbose=False)
            
            if len(trajectory) >= min_trajectory_length:
                trajectories[student_id] = trajectory
                students_processed += 1
            else:
                students_skipped += 1
        
        if verbose:
            print(f"\n✓ Processed {students_processed} students")
            print(f"  Skipped {students_skipped} students (trajectory too short)")
            
            # Statistics
            total_transitions = sum(len(t) for t in trajectories.values())
            avg_transitions = total_transitions / len(trajectories) if trajectories else 0
            print(f"\n  Total transitions: {total_transitions}")
            print(f"  Avg transitions per student: {avg_transitions:.1f}")
            
            print("=" * 60)
        
        return trajectories
    
    def _process_student(self, student_id: int, verbose: bool = False) -> List[Dict]:
        """
        Process logs for a single student
        
        Args:
            student_id: Student ID to process
            verbose: Print debug info
            
        Returns:
            List of transition dicts
        """
        # Get student's cluster
        cluster_id = self.student_clusters.get(student_id)
        if cluster_id is None:
            if verbose:
                print(f"  ⚠ Student {student_id}: No cluster assignment")
            return []
        
        # Initialize student context
        context = StudentContext(student_id=student_id, cluster_id=cluster_id)
        
        # Get student's logs (sorted by time)
        student_logs = self.logs_df[self.logs_df['userid'] == student_id].copy()
        student_logs = student_logs.sort_values('timecreated')
        
        # Get student's grades
        if 'userid' in self.grades_df.columns:
            student_grades = self.grades_df[self.grades_df['userid'] == student_id].copy()
        else:
            student_grades = pd.DataFrame()
        
        # Build trajectory
        trajectory = []
        prev_state = None
        
        for idx, log_row in student_logs.iterrows():
            # Update context from log
            context.update_from_log_entry(log_row.to_dict())
            
            # Check if there's a grade for this module at this time
            module_id = log_row.get('contextinstanceid', 0)
            if not student_grades.empty and 'finalgrade' in student_grades.columns:
                # Find grades for this module (if grade columns exist)
                try:
                    if 'iteminstance' in student_grades.columns:
                        module_grades = student_grades[student_grades['iteminstance'] == module_id]
                    elif 'contextinstanceid' in student_grades.columns:
                        module_grades = student_grades[student_grades['contextinstanceid'] == module_id]
                    else:
                        module_grades = pd.DataFrame()
                    
                    for _, grade_row in module_grades.iterrows():
                        context.update_from_grade_entry(grade_row.to_dict())
                except Exception:
                    # Skip grade processing if columns don't match
                    pass
            
            # Get current state
            state_dict = context.get_state_dict()
            current_state = self.state_builder.build_state(
                cluster_id=state_dict['cluster_id'],
                current_module_id=state_dict['current_module'],
                module_progress=state_dict['progress'],
                avg_score=state_dict['avg_score'],
                recent_action_type=state_dict['recent_action'],
                is_stuck=state_dict['is_stuck']
            )
            
            # If we have a previous state, create transition
            if prev_state is not None:
                # Get action from log
                action_type = context._map_action_type(
                    eventname=log_row.get('eventname', ''),
                    component=log_row.get('component', ''),
                    action=log_row.get('action', '')
                )
                action_id = log_row.get('contextinstanceid', 0)  # Use module as action ID
                
                # Calculate reward (using simplified version)
                prev_score = trajectory[-1]['avg_score'] if trajectory else 0.0
                current_score = state_dict['avg_score']
                completed = state_dict['progress'] > (trajectory[-1]['progress'] if trajectory else 0.0)
                
                reward = self.reward_calculator.calculate_reward_simple(
                    cluster_id=cluster_id,
                    completed=completed,
                    score=current_score,
                    previous_score=prev_score,
                    is_stuck=state_dict['is_stuck']
                )
                
                # Create transition
                transition = {
                    'state': prev_state,
                    'action': action_id,
                    'reward': reward,
                    'next_state': current_state,
                    'timestamp': log_row['timecreated'],
                    'module_id': module_id,
                    'is_terminal': False,
                    'progress': state_dict['progress'],
                    'avg_score': state_dict['avg_score'],
                    'action_type': action_type
                }
                
                trajectory.append(transition)
            
            # Update previous state
            prev_state = current_state
        
        # Mark last transition as terminal
        if trajectory:
            trajectory[-1]['is_terminal'] = True
        
        if verbose and trajectory:
            print(f"  ✓ Student {student_id}: {len(trajectory)} transitions")
        
        return trajectory
    
    def save_trajectories(self, trajectories: Dict[int, List[Dict]], output_path: str):
        """
        Save trajectories to JSON file
        
        Args:
            trajectories: Dictionary of trajectories
            output_path: Path to save JSON file
        """
        print(f"\nSaving trajectories to: {output_path}")
        
        # Convert to serializable format
        serializable_trajectories = {}
        for student_id, trajectory in trajectories.items():
            serializable_trajectories[str(student_id)] = [
                {
                    'state': list(t['state']),  # Convert tuple to list
                    'action': int(t['action']),
                    'reward': float(t['reward']),
                    'next_state': list(t['next_state']),
                    'timestamp': str(t['timestamp']),
                    'module_id': int(t['module_id']),
                    'is_terminal': bool(t['is_terminal']),
                    'progress': float(t['progress']),
                    'avg_score': float(t['avg_score']),
                    'action_type': t['action_type']
                }
                for t in trajectory
            ]
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_trajectories, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(trajectories)} trajectories")
    
    def load_trajectories(self, input_path: str) -> Dict[int, List[Dict]]:
        """
        Load trajectories from JSON file
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            Dictionary of trajectories
        """
        print(f"\nLoading trajectories from: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            serializable_trajectories = json.load(f)
        
        # Convert back to proper format
        trajectories = {}
        for student_id_str, trajectory in serializable_trajectories.items():
            student_id = int(student_id_str)
            trajectories[student_id] = [
                {
                    'state': tuple(t['state']),  # Convert list back to tuple
                    'action': t['action'],
                    'reward': t['reward'],
                    'next_state': tuple(t['next_state']),
                    'timestamp': pd.to_datetime(t['timestamp']),
                    'module_id': t['module_id'],
                    'is_terminal': t['is_terminal'],
                    'progress': t['progress'],
                    'avg_score': t['avg_score'],
                    'action_type': t['action_type']
                }
                for t in trajectory
            ]
        
        print(f"✓ Loaded {len(trajectories)} trajectories")
        return trajectories
    
    def get_statistics(self, trajectories: Dict[int, List[Dict]]) -> Dict:
        """
        Get statistics about trajectories
        
        Args:
            trajectories: Dictionary of trajectories
            
        Returns:
            Dictionary of statistics
        """
        total_students = len(trajectories)
        total_transitions = sum(len(t) for t in trajectories.values())
        
        # Trajectory lengths
        lengths = [len(t) for t in trajectories.values()]
        avg_length = np.mean(lengths)
        min_length = np.min(lengths)
        max_length = np.max(lengths)
        
        # Rewards
        all_rewards = [t['reward'] for traj in trajectories.values() for t in traj]
        avg_reward = np.mean(all_rewards)
        min_reward = np.min(all_rewards)
        max_reward = np.max(all_rewards)
        
        # Progress
        final_progress = [traj[-1]['progress'] for traj in trajectories.values()]
        avg_final_progress = np.mean(final_progress)
        
        # Scores
        final_scores = [traj[-1]['avg_score'] for traj in trajectories.values()]
        avg_final_score = np.mean(final_scores)
        
        # Action types
        action_types = [t['action_type'] for traj in trajectories.values() for t in traj]
        action_type_counts = pd.Series(action_types).value_counts().to_dict()
        
        return {
            'total_students': total_students,
            'total_transitions': total_transitions,
            'avg_trajectory_length': avg_length,
            'min_trajectory_length': min_length,
            'max_trajectory_length': max_length,
            'avg_reward': avg_reward,
            'min_reward': min_reward,
            'max_reward': max_reward,
            'avg_final_progress': avg_final_progress,
            'avg_final_score': avg_final_score,
            'action_type_distribution': action_type_counts
        }


def test_moodle_log_processor():
    """Test MoodleLogProcessorV2 with sample data"""
    print("\n" + "=" * 60)
    print("Testing MoodleLogProcessorV2")
    print("=" * 60)
    
    # Initialize processor
    processor = MoodleLogProcessorV2(
        log_csv_path="data/log/log.csv",
        grade_csv_path="data/log/grade.csv",
        cluster_profiles_path="data/cluster_profiles.json",
        course_structure_path="data/course_structure.json"
    )
    
    # Process logs for a subset of students
    print("\nProcessing first 10 students...")
    student_ids = list(processor.student_clusters.keys())[:10]
    trajectories = processor.process_logs(
        student_ids=student_ids,
        min_trajectory_length=3,
        verbose=True
    )
    
    # Print sample trajectory
    if trajectories:
        sample_student_id = list(trajectories.keys())[0]
        sample_trajectory = trajectories[sample_student_id]
        
        print(f"\nSample trajectory for student {sample_student_id}:")
        print(f"  Length: {len(sample_trajectory)} transitions")
        print(f"  First transition:")
        first_t = sample_trajectory[0]
        print(f"    State: {first_t['state']}")
        print(f"    Action: {first_t['action']} ({first_t['action_type']})")
        print(f"    Reward: {first_t['reward']:.2f}")
        print(f"    Next state: {first_t['next_state']}")
        print(f"    Progress: {first_t['progress']:.2f}")
        print(f"    Avg score: {first_t['avg_score']:.2f}")
    
    # Get statistics
    print("\nTrajectory statistics:")
    stats = processor.get_statistics(trajectories)
    for key, value in stats.items():
        if key == 'action_type_distribution':
            print(f"  {key}:")
            for action_type, count in value.items():
                print(f"    {action_type}: {count}")
        else:
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    
    # Save trajectories
    output_path = "data/trajectories_sample.json"
    processor.save_trajectories(trajectories, output_path)
    
    # Load trajectories
    loaded_trajectories = processor.load_trajectories(output_path)
    print(f"\n✓ Verified save/load: {len(loaded_trajectories)} trajectories")
    
    print("\n" + "=" * 60)
    print("✓ MoodleLogProcessorV2 test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_moodle_log_processor()
