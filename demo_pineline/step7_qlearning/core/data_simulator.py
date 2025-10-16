#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Simulator for Q-Learning Training
=======================================
Simulate student profiles và learning trajectories dựa trên cluster statistics
"""

import numpy as np
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class StudentDataSimulator:
    """
    Simulator để tạo dữ liệu học sinh giả lập
    
    Features:
    - Sinh student profiles dựa trên cluster statistics
    - Sinh learning trajectories (completed resources over time)
    - Chia train/test set
    - Tạo learning outcomes (grades, completion, engagement)
    """
    
    def __init__(self, 
                 cluster_stats_path: str,
                 course_structure_path: str,
                 real_features_path: Optional[str] = None):
        """
        Args:
            cluster_stats_path: Path to cluster_full_statistics.json
            course_structure_path: Path to course_structure.json
            real_features_path: Path to features_scaled_report.json (optional)
        """
        self.cluster_stats = self._load_json(cluster_stats_path)
        self.course_structure = self._load_json(course_structure_path)
        self.real_features = None
        
        if real_features_path and Path(real_features_path).exists():
            self.real_features = self._load_json(real_features_path)
        
        # Extract resources từ course structure
        self.all_resources = self._extract_all_resources()
        
        logger.info(f"Simulator initialized:")
        logger.info(f"  Clusters: {len(self.cluster_stats)}")
        logger.info(f"  Total resources: {len(self.all_resources)}")
    
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_all_resources(self) -> List[Dict]:
        """Extract all resources from course structure"""
        resources = []
        
        # Tìm course object có sections
        course_data = None
        for item in self.course_structure:
            if isinstance(item, dict) and 'sections' in item:
                course_data = item
                break
        
        if not course_data:
            logger.warning("No course structure found with sections")
            return resources
        
        for section in course_data.get('sections', []):
            section_name = section.get('name', 'Unknown')
            
            # Resources trực tiếp trong section
            for resource in section.get('resources', []):
                resources.append({
                    'id': resource['id'],
                    'name': resource['name'],
                    'type': resource['modname'],
                    'section': section_name,
                    'lesson': None
                })
            
            # Resources trong lessons
            for lesson in section.get('lessons', []):
                lesson_name = lesson.get('name', 'Unknown')
                for resource in lesson.get('resources', []):
                    resources.append({
                        'id': resource['id'],
                        'name': resource['name'],
                        'type': resource['modname'],
                        'section': section_name,
                        'lesson': lesson_name
                    })
        
        return resources
    
    def simulate_student_profile(self, cluster_id: str, noise_level: float = 0.1) -> Dict:
        """
        Simulate student profile dựa trên cluster statistics
        
        Args:
            cluster_id: ID của cluster (e.g., 'cluster_0', 'cluster_1')
            noise_level: Mức độ nhiễu (0-1) để tạo variation
        
        Returns:
            Dict of student features (15 dimensions)
        """
        cluster_data = self.cluster_stats.get(cluster_id, {})
        feature_stats = cluster_data.get('feature_statistics', {})
        
        profile = {}
        
        # Core features cần thiết cho Q-Learning
        required_features = [
            'mean_module_grade', 'total_events', 'course_module',
            'viewed', 'attempt', 'feedback_viewed', 'submitted', 'reviewed',
            'course_module_viewed', 'module_count', 'course_module_completion',
            'created', 'updated', 'downloaded'
        ]
        
        # Map some features nếu không có trực tiếp
        feature_mapping = {
            'course_module': '\\core\\event\\course_module_completion_updated',
            'viewed': '\\mod_resource\\event\\course_module_viewed',
            'attempt': '\\mod_quiz\\event\\attempt_started',
            'feedback_viewed': '\\mod_assign\\event\\feedback_viewed',
            'submitted': '\\mod_quiz\\event\\attempt_submitted',
            'reviewed': '\\mod_quiz\\event\\attempt_reviewed',
            'course_module_viewed': '\\mod_resource\\event\\course_module_viewed',
            'module_count': 'mean_module_grade',  # Use as proxy
            'course_module_completion': '\\core\\event\\course_module_completion_updated',
            'created': '\\mod_data\\event\\record_created',
            'updated': '\\assignsubmission_file\\event\\submission_updated',
            'downloaded': '\\mod_folder\\event\\all_files_downloaded'
        }
        
        for feature in required_features:
            # Try direct feature name first
            feature_key = feature
            if feature not in feature_stats:
                # Try mapped feature
                feature_key = feature_mapping.get(feature, feature)
            
            if feature_key in feature_stats:
                stats = feature_stats[feature_key]
                mean = stats['mean']
                std = stats['std']
                
                # Generate value với Gaussian noise
                value = np.random.normal(mean, std * noise_level)
                # Clip to [0, 1]
                value = np.clip(value, 0, 1)
                
                profile[feature] = float(value)
            else:
                # Default value nếu không tìm thấy
                logger.warning(f"Feature {feature} not found, using default 0.5")
                profile[feature] = 0.5
        
        # Add userid
        profile['userid'] = np.random.randint(10000, 99999)
        
        return profile
    
    def simulate_learning_trajectory(self, 
                                    student_profile: Dict,
                                    n_steps: int = 10,
                                    completion_bias: float = 0.7) -> List[Dict]:
        """
        Simulate learning trajectory (sequence of completed resources)
        
        Args:
            student_profile: Student feature dict
            n_steps: Number of learning steps
            completion_bias: Probability bias dựa trên student performance
        
        Returns:
            List of trajectory steps, each containing:
            - step: Step number
            - resource_id: Completed resource ID
            - grade: Grade achieved (0-1)
            - time_spent: Time spent (minutes)
        """
        trajectory = []
        completed_ids = set()
        
        # Difficulty-aware completion probability
        student_grade = student_profile.get('mean_module_grade', 0.5)
        
        available_resources = [r for r in self.all_resources if r['type'] in ['quiz', 'resource', 'hvp']]
        
        for step in range(n_steps):
            if len(completed_ids) >= len(available_resources):
                break
            
            # Select resource (chưa hoàn thành)
            available = [r for r in available_resources if r['id'] not in completed_ids]
            if not available:
                break
            
            # Prefer easier resources first for low-performing students
            if student_grade < 0.5:
                # Prefer non-quiz resources
                non_quiz = [r for r in available if r['type'] != 'quiz']
                if non_quiz:
                    resource = np.random.choice(non_quiz)
                else:
                    resource = np.random.choice(available)
            else:
                resource = np.random.choice(available)
            
            # Simulate completion
            resource_id = resource['id']
            resource_type = resource['type']
            
            # Grade dựa trên student ability và resource difficulty
            if resource_type == 'quiz':
                # Quiz có grade
                base_grade = student_grade
                noise = np.random.normal(0, 0.1)
                grade = np.clip(base_grade + noise, 0, 1)
            else:
                # Non-quiz: completion = 1.0 or 0.0
                grade = 1.0 if np.random.rand() < completion_bias else 0.0
            
            # Time spent (minutes)
            if resource_type == 'quiz':
                time_spent = np.random.randint(10, 30)
            elif resource_type == 'hvp':  # video
                time_spent = np.random.randint(5, 20)
            else:  # resource (PDF, etc.)
                time_spent = np.random.randint(3, 15)
            
            trajectory.append({
                'step': step,
                'resource_id': resource_id,
                'resource_name': resource['name'],
                'resource_type': resource_type,
                'grade': float(grade),
                'time_spent': int(time_spent),
                'completed': grade > 0.5
            })
            
            completed_ids.add(resource_id)
        
        return trajectory
    
    def generate_dataset(self, 
                        n_students: int = 100,
                        train_ratio: float = 0.8,
                        n_steps_per_student: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate complete dataset with train/test split
        
        Args:
            n_students: Total number of students to simulate
            train_ratio: Ratio of training data (0-1)
            n_steps_per_student: Number of learning steps per student
        
        Returns:
            (train_df, test_df): Training and test dataframes
        """
        logger.info(f"Generating dataset for {n_students} students...")
        
        data = []
        
        # Distribute students across clusters based on percentage
        cluster_ids = list(self.cluster_stats.keys())
        cluster_percentages = [self.cluster_stats[cid]['percentage'] / 100.0 for cid in cluster_ids]
        
        # Assign students to clusters
        cluster_assignments = np.random.choice(
            cluster_ids, 
            size=n_students, 
            p=cluster_percentages
        )
        
        for i, cluster_id in enumerate(cluster_assignments):
            # Simulate student profile
            profile = self.simulate_student_profile(cluster_id)
            
            # Simulate learning trajectory
            trajectory = self.simulate_learning_trajectory(
                profile, 
                n_steps=n_steps_per_student
            )
            
            # Create records
            for traj_step in trajectory:
                record = {
                    'student_id': profile['userid'],
                    'cluster': cluster_id,
                    **profile,  # All features
                    **traj_step  # Trajectory step data
                }
                data.append(record)
            
            if (i + 1) % 10 == 0:
                logger.info(f"  Generated {i + 1}/{n_students} students")
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Train/test split by student
        unique_students = df['student_id'].unique()
        n_train = int(len(unique_students) * train_ratio)
        
        train_students = np.random.choice(unique_students, size=n_train, replace=False)
        
        train_df = df[df['student_id'].isin(train_students)].copy()
        test_df = df[~df['student_id'].isin(train_students)].copy()
        
        logger.info(f"✓ Dataset generated:")
        logger.info(f"  Total records: {len(df)}")
        logger.info(f"  Train: {len(train_df)} records ({len(train_students)} students)")
        logger.info(f"  Test: {len(test_df)} records ({len(unique_students) - len(train_students)} students)")
        
        return train_df, test_df
    
    def save_dataset(self, train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: str):
        """Save datasets to CSV files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        train_path = output_path / 'train_data.csv'
        test_path = output_path / 'test_data.csv'
        
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        
        logger.info(f"✓ Datasets saved:")
        logger.info(f"  Train: {train_path}")
        logger.info(f"  Test: {test_path}")
        
        # Save summary statistics
        summary = {
            'train': {
                'n_students': int(train_df['student_id'].nunique()),
                'n_records': int(len(train_df)),
                'avg_grade': float(train_df['grade'].mean()),
                'completion_rate': float((train_df['grade'] > 0.5).mean())
            },
            'test': {
                'n_students': int(test_df['student_id'].nunique()),
                'n_records': int(len(test_df)),
                'avg_grade': float(test_df['grade'].mean()),
                'completion_rate': float((test_df['grade'] > 0.5).mean())
            }
        }
        
        summary_path = output_path / 'dataset_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  Summary: {summary_path}")


def test_simulator():
    """Test data simulator"""
    print("\n" + "="*70)
    print("TEST: Data Simulator")
    print("="*70)
    
    # Paths
    base_path = Path(__file__).parent.parent
    
    simulator = StudentDataSimulator(
        cluster_stats_path=str(base_path.parent.parent / "data/processed/cluster_full_statistics.json"),
        course_structure_path=str(base_path / "data/course_structure.json"),
        real_features_path=str(base_path / "data/features_scaled_report.json")
    )
    
    # Test 1: Simulate single student
    print("\n" + "-"*70)
    print("Test 1: Simulate single student profile")
    print("-"*70)
    
    profile = simulator.simulate_student_profile('cluster_0')
    print(f"\nStudent profile (cluster_0):")
    for key in ['userid', 'mean_module_grade', 'total_events', 'viewed', 'attempt']:
        print(f"  {key}: {profile.get(key, 'N/A')}")
    
    # Test 2: Simulate learning trajectory
    print("\n" + "-"*70)
    print("Test 2: Simulate learning trajectory")
    print("-"*70)
    
    trajectory = simulator.simulate_learning_trajectory(profile, n_steps=5)
    print(f"\nTrajectory ({len(trajectory)} steps):")
    for step in trajectory[:3]:
        print(f"  Step {step['step']}: {step['resource_name']} "
              f"({step['resource_type']}) - Grade: {step['grade']:.2f}")
    
    # Test 3: Generate small dataset
    print("\n" + "-"*70)
    print("Test 3: Generate dataset")
    print("-"*70)
    
    train_df, test_df = simulator.generate_dataset(
        n_students=20,
        train_ratio=0.8,
        n_steps_per_student=5
    )
    
    print(f"\nTrain set shape: {train_df.shape}")
    print(f"Test set shape: {test_df.shape}")
    print(f"\nTrain columns: {list(train_df.columns)[:10]}...")
    
    # Save dataset
    output_dir = base_path / "data/simulated"
    simulator.save_dataset(train_df, test_df, str(output_dir))
    
    print("\n" + "="*70)
    print("✅ Test completed!")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_simulator()
