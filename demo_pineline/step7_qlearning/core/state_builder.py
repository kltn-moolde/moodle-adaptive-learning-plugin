#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle State Builder
====================
State representation từ Moodle behavioral logs và student metrics
"""

import numpy as np
from typing import Dict, List, Optional
import json


class MoodleStateBuilder:
    """
    State Builder cho Moodle Q-Learning system
    
    State Structure (12 dimensions):
    ================================
    1. Student Performance (3 dims):
       - knowledge_level: mean_module_grade (0-1)
       - engagement_level: aggregated from events (0-1)
       - struggle_indicator: high attempts + low feedback (0-1)
    
    2. Activity Patterns (5 dims):
       - submission_activity: submitted events normalized
       - review_activity: reviewed + feedback_viewed
       - resource_usage: resource/page/url viewed
       - assessment_engagement: quiz/assign events
       - collaborative_activity: forum/comment events
    
    3. Completion Metrics (4 dims):
       - overall_progress: module_count normalized
       - module_completion_rate: course_module_completion
       - activity_diversity: number of activity types tried
       - completion_consistency: std dev of completion across modules
    """
    
    def __init__(self):
        """Initialize state builder"""
        # Define feature mappings từ Moodle logs
        self.submission_keys = [
            'submitted', 'assessable_submitted', 'submission_created'
        ]
        self.review_keys = [
            'reviewed', 'feedback_viewed', 'attempt_reviewed'
        ]
        self.resource_keys = [
            'course_module_viewed', 'viewed', 
            '\\mod_resource\\event\\course_module_viewed',
            '\\mod_page\\event\\course_module_viewed',
            '\\mod_url\\event\\course_module_viewed'
        ]
        self.assessment_keys = [
            'attempt', 'attempt_started', 'attempt_submitted',
            '\\mod_quiz\\event\\attempt_started',
            '\\mod_assign\\event\\assessable_submitted'
        ]
        self.collaborative_keys = [
            'comment', '\\mod_forum\\event\\course_module_viewed'
        ]
    
    def build_state_from_api_features(self, features: Dict[str, float]) -> np.ndarray:
        """
        Build state from API-friendly features (used by API endpoint)
        
        Args:
            features: Dict with structure matching state_description:
                {
                    'performance': {
                        'knowledge_level': float,
                        'engagement_level': float,
                        'struggle_indicator': float
                    },
                    'activity_patterns': {
                        'submission_activity': float,
                        'review_activity': float,
                        'resource_usage': float,
                        'assessment_engagement': float,
                        'collaborative_activity': float
                    },
                    'completion_metrics': {
                        'overall_progress': float,
                        'module_completion_rate': float,
                        'activity_diversity': float,
                        'completion_consistency': float
                    }
                }
                OR flat dict with direct key names (backward compatible)
        
        Returns:
            State vector (12 dims) directly without Moodle key mapping
        """
        # Check if features is nested (new format) or flat (old format)
        if 'performance' in features:
            # New nested format - extract values in correct order
            perf = features.get('performance', {})
            activity = features.get('activity_patterns', {})
            completion = features.get('completion_metrics', {})
            
            state = [
                # Performance (3 dims)
                perf.get('knowledge_level', 0.5),
                perf.get('engagement_level', 0.5),
                perf.get('struggle_indicator', 0.0),
                
                # Activity patterns (5 dims)
                activity.get('submission_activity', 0.0),
                activity.get('review_activity', 0.5),
                activity.get('resource_usage', 0.5),
                activity.get('assessment_engagement', 0.5),
                activity.get('collaborative_activity', 0.0),
                
                # Completion metrics (4 dims)
                completion.get('overall_progress', 0.5),
                completion.get('module_completion_rate', 0.5),
                completion.get('activity_diversity', 0.25),
                completion.get('completion_consistency', 0.5)
            ]
        else:
            # Old flat format - backward compatible
            state = [
                # Performance (3 dims)
                features.get('knowledge_level', 0.5),
                features.get('engagement_level', features.get('engagement_score', 0.5)),  # backward compat
                features.get('struggle_indicator', 0.0),
                
                # Activity patterns (5 dims)
                features.get('submission_activity', 0.0),
                features.get('review_activity', 0.5),
                features.get('resource_usage', 0.5),
                features.get('assessment_engagement', features.get('assessment_performance', 0.5)),  # backward compat
                features.get('collaborative_activity', 0.0),
                
                # Completion metrics (4 dims)
                features.get('overall_progress', features.get('progress_rate', 0.5)),  # backward compat
                features.get('module_completion_rate', features.get('completion_rate', 0.5)),  # backward compat
                features.get('activity_diversity', features.get('resource_diversity', 0.25)),  # backward compat
                features.get('completion_consistency', features.get('time_spent_avg', 0.5))  # backward compat
            ]
        
        return np.array(state, dtype=np.float32)
    
    def build_state(self, student_data: Dict) -> np.ndarray:
        """
        Xây dựng state từ Moodle student data
        
        Args:
            student_data: Dict from features_scaled_report.json
        
        Returns:
            State vector (12 dims)
        """
        state = []
        
        # === 1. STUDENT PERFORMANCE (3 dims) ===
        
        # 1.1 Knowledge level
        knowledge_level = student_data.get('mean_module_grade', 0.5)
        state.append(knowledge_level)
        
        # 1.2 Engagement level
        engagement = np.mean([
            student_data.get('total_events', 0.0),
            student_data.get('course_module', 0.0),
            student_data.get('viewed', 0.0)
        ])
        state.append(engagement)
        
        # 1.3 Struggle indicator
        attempt_norm = student_data.get('attempt', 0.0)
        feedback_norm = student_data.get('feedback_viewed', 0.0)
        struggle = attempt_norm * (1 - feedback_norm) * (1 - knowledge_level)
        struggle = np.clip(struggle, 0.0, 1.0)
        state.append(struggle)
        
        # === 2. ACTIVITY PATTERNS (5 dims) ===
        
        # 2.1 Submission activity
        submission_activity = self._aggregate_features(
            student_data, self.submission_keys
        )
        state.append(submission_activity)
        
        # 2.2 Review activity
        review_activity = self._aggregate_features(
            student_data, self.review_keys
        )
        state.append(review_activity)
        
        # 2.3 Resource usage
        resource_usage = self._aggregate_features(
            student_data, self.resource_keys
        )
        state.append(resource_usage)
        
        # 2.4 Assessment engagement
        assessment_engagement = self._aggregate_features(
            student_data, self.assessment_keys
        )
        state.append(assessment_engagement)
        
        # 2.5 Collaborative activity
        collaborative_activity = self._aggregate_features(
            student_data, self.collaborative_keys
        )
        state.append(collaborative_activity)
        
        # === 3. COMPLETION METRICS (4 dims) ===
        
        # 3.1 Overall progress
        overall_progress = student_data.get('module_count', 0.0)
        state.append(overall_progress)
        
        # 3.2 Module completion rate
        module_completion = student_data.get('course_module_completion', 0.0)
        state.append(module_completion)
        
        # 3.3 Activity diversity
        activity_types = [
            'submitted', 'viewed', 'created', 'updated', 
            'downloaded', 'reviewed', 'uploaded'
        ]
        active_types = sum([
            1 for k in activity_types 
            if student_data.get(k, 0.0) > 0.1
        ])
        activity_diversity = active_types / len(activity_types)
        state.append(activity_diversity)
        
        # 3.4 Completion consistency
        module_metrics = [
            student_data.get('course_module_completion', 0.0),
            student_data.get('module_count', 0.0),
            student_data.get('course_module', 0.0)
        ]
        completion_consistency = 1 - np.std(module_metrics)
        completion_consistency = np.clip(completion_consistency, 0.0, 1.0)
        state.append(completion_consistency)
        
        return np.array(state, dtype=np.float32)
    
    def _aggregate_features(self, data: Dict, keys: List[str]) -> float:
        """
        Aggregate multiple features thành 1 giá trị
        
        Args:
            data: Student data dict
            keys: List of feature keys
        
        Returns:
            Aggregated value (0-1)
        """
        values = []
        for key in keys:
            if key in data:
                values.append(data[key])
        
        if not values:
            return 0.0
        
        return np.mean(values)
    
    def get_state_dimension(self) -> int:
        """Get state dimension"""
        return 12
    
    def hash_state(self, state: np.ndarray, decimals: int = 1, bins: Optional[List[float]] = None) -> tuple:
        """
        Hash state vector thành tuple (key cho Q-table)
        
        Supports two strategies:
        1. Decimal rounding: decimals=1 → 11 bins (0.0, 0.1, ..., 1.0)
        2. Custom bins: bins=[0, 0.25, 0.5, 0.75, 1.0] → 4 bins (Quartile)
        
        Args:
            state: State vector (12 dims)
            decimals: Số chữ số thập phân (used if bins=None)
            bins: Custom bin edges (e.g., [0, 0.25, 0.5, 0.75, 1.0] for quartile)
        
        Returns:
            Tuple (hashable)
        """
        if bins is not None:
            # Custom binning strategy
            discretized = []
            for val in state:
                # Find which bin this value falls into
                bin_value = bins[0]  # Default to first bin
                for i in range(len(bins) - 1):
                    if bins[i] <= val < bins[i+1]:
                        bin_value = bins[i]
                        break
                    elif val >= bins[-1]:
                        bin_value = bins[-2]  # Last interval
                        break
                discretized.append(bin_value)
            return tuple(discretized)
        else:
            # Decimal rounding strategy (original)
            return tuple(np.round(state, decimals=decimals))
    
    def extract_batch(self, json_path: str) -> Dict[int, np.ndarray]:
        """
        Trích xuất states cho tất cả students trong file
        
        Args:
            json_path: Path to features_scaled_report.json
        
        Returns:
            Dict {userid: state_vector}
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        states = {}
        for student_data in data:
            userid = student_data['userid']
            state = self.build_state(student_data)
            states[userid] = state
        
        return states
    
    def get_state_description(self, state: np.ndarray) -> Dict:
        """
        Mô tả chi tiết state (for debugging)
        
        Args:
            state: State vector
        
        Returns:
            Dict with labeled values
        """
        return {
            'performance': {
                'knowledge_level': float(state[0]),
                'engagement_level': float(state[1]),
                'struggle_indicator': float(state[2])
            },
            'activity_patterns': {
                'submission_activity': float(state[3]),
                'review_activity': float(state[4]),
                'resource_usage': float(state[5]),
                'assessment_engagement': float(state[6]),
                'collaborative_activity': float(state[7])
            },
            'completion_metrics': {
                'overall_progress': float(state[8]),
                'module_completion_rate': float(state[9]),
                'activity_diversity': float(state[10]),
                'completion_consistency': float(state[11])
            }
        }


# Example usage
if __name__ == '__main__':
    builder = MoodleStateBuilder()
    
    # Example student data
    sample_data = {
        'userid': 8609,
        'mean_module_grade': 0.75,
        'total_events': 0.6,
        'course_module': 0.5,
        'viewed': 0.7,
        'attempt': 0.8,
        'feedback_viewed': 0.3,
        'submitted': 0.6,
        'reviewed': 0.4,
        'course_module_viewed': 0.5,
        'module_count': 0.5,
        'course_module_completion': 0.6,
        'created': 0.2,
        'updated': 0.1,
        'downloaded': 0.3
    }
    
    state = builder.build_state(sample_data)
    print("State vector:", state)
    print("\nState dimension:", builder.get_state_dimension())
    print("\nState description:")
    description = builder.get_state_description(state)
    for category, values in description.items():
        print(f"\n{category.upper()}:")
        for key, val in values.items():
            print(f"  {key}: {val:.3f}")
