#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Builder V2
================
Redesigned state representation: [cluster_id, current_module, module_progress, avg_score, recent_action, is_stuck]
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class StateBuilderV2:
    """
    State Builder cho Q-Learning System V2
    
    State Structure (6 dimensions):
    ================================
    1. cluster_id: [0, 1, 2, 3, 4, 5] - Student cluster (removed teacher cluster)
    2. current_module: [0, 1, 2, ..., N-1] - Current learning module
    3. module_progress: [0.25, 0.5, 0.75, 1.0] - Progress quartiles
    4. avg_score: [0.25, 0.5, 0.75, 1.0] - Score quartiles  
    5. recent_action: [0-5] - Last action type performed
    6. is_stuck: [0, 1] - Whether student is stuck
    """
    
    # Action type mapping
    ACTION_TYPES = {
        'watch_video': 0,
        'do_quiz': 1,
        'mod_forum': 2,
        'review_quiz': 3,
        'read_resource': 4,
        'do_assignment': 5
    }
    
    # Reverse mapping
    ACTION_NAMES = {v: k for k, v in ACTION_TYPES.items()}
    
    # Quartile bins for continuous values
    PROGRESS_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]
    SCORE_BINS = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    def __init__(
        self, 
        cluster_profiles_path: str,
        course_structure_path: str,
        excluded_cluster: int = 3  # Teacher cluster
    ):
        """
        Initialize State Builder V2
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json
            course_structure_path: Path to course_structure.json
            excluded_cluster: Cluster to exclude - teachers (default: 3)
        """
        self.cluster_profiles_path = Path(cluster_profiles_path)
        self.course_structure_path = Path(course_structure_path)
        self.excluded_cluster = excluded_cluster
        
        # Load data
        self._load_cluster_profiles()
        self._load_course_structure()
        
        # Cluster mapping (original -> new)
        self._build_cluster_mapping()
        
        # Calculate n_clusters after exclusion
        self.n_clusters = len(self.cluster_mapping)
        
    def _load_cluster_profiles(self):
        """Load cluster profiles"""
        with open(self.cluster_profiles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.cluster_profiles = data.get('cluster_stats', {})
        self.original_n_clusters = data.get('n_clusters', 6)
        
    def _load_course_structure(self):
        """Load course structure and extract modules"""
        with open(self.course_structure_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract all learning modules (exclude subsections, labels, etc.)
        self.modules = []
        for section in data.get('contents', []):
            for module in section.get('modules', []):
                # Filter: only keep learning activities
                if module.get('modname') not in ['subsection', 'label', 'qbank']:
                    if module.get('visible', 0) == 1 and module.get('uservisible', False):
                        self.modules.append({
                            'id': module['id'],
                            'name': module['name'],
                            'type': module.get('modname', 'unknown'),
                            'section': section['name'],
                            'purpose': module.get('purpose', 'other')
                        })
        
        self.n_modules = len(self.modules)
        print(f"✓ Loaded {self.n_modules} modules from course structure")
        
        # Create module ID to index mapping
        self.module_id_to_idx = {m['id']: idx for idx, m in enumerate(self.modules)}
        
    def _build_cluster_mapping(self):
        """Build mapping from original cluster IDs to new cluster IDs"""
        # Original clusters: [0, 1, 2, 3, 4, 5]
        # Remove cluster 3 (teacher)
        # New clusters: [0, 1, 2, 3, 4]
        
        self.cluster_mapping = {}
        new_id = 0
        for orig_id in range(self.original_n_clusters):
            if orig_id == self.excluded_cluster:
                continue  # Skip teacher cluster
            self.cluster_mapping[orig_id] = new_id
            new_id += 1
        
        print(f"✓ Cluster mapping: {self.cluster_mapping}")
        print(f"✓ Excluded cluster {self.excluded_cluster} (teacher)")
        
    def map_cluster_id(self, original_cluster_id: int) -> Optional[int]:
        """
        Map original cluster ID to new cluster ID
        
        Args:
            original_cluster_id: Original cluster ID [0-5]
            
        Returns:
            New cluster ID [0-4] or None if excluded
        """
        return self.cluster_mapping.get(original_cluster_id, None)
    
    def quartile_bin(self, value: float, bins: List[float]) -> float:
        """
        Bin a continuous value into quartiles
        
        Args:
            value: Value to bin (0-1)
            bins: Bin edges
            
        Returns:
            Binned value (0.25, 0.5, 0.75, or 1.0)
        """
        value = max(0.0, min(1.0, value))  # Clip to [0, 1]
        
        for i in range(len(bins) - 1):
            if value <= bins[i + 1]:
                return bins[i + 1]
        
        return bins[-1]  # Max bin
    
    def map_action_type(self, event_name: str, component: str, action: str) -> str:
        """
        Map Moodle event to action type
        
        Args:
            event_name: Full event name from log
            component: Component (e.g., mod_quiz)
            action: Action (e.g., viewed)
            
        Returns:
            Action type string (one of ACTION_TYPES keys)
        """
        event_lower = event_name.lower()
        
        # Mapping rules
        if 'hvp' in event_lower or 'video' in component.lower():
            return 'watch_video'
        elif 'quiz' in component.lower():
            if 'attempt_started' in event_lower or 'attempt_submitted' in event_lower:
                return 'do_quiz'
            elif 'reviewed' in event_lower:
                return 'review_quiz'
            else:
                return 'do_quiz'  # Default for quiz
        elif 'forum' in component.lower():
            return 'mod_forum'
        elif 'assign' in component.lower():
            if 'feedback' in event_lower:
                return 'review_quiz'  # Treat feedback as review
            else:
                return 'do_assignment'
        elif 'resource' in component.lower() or 'page' in component.lower() or 'url' in component.lower():
            return 'read_resource'
        else:
            return 'read_resource'  # Default
    
    def detect_stuck(
        self,
        quiz_attempts: int,
        time_on_module: float,
        median_time: float,
        recent_scores: List[float]
    ) -> int:
        """
        Detect if student is stuck
        
        Args:
            quiz_attempts: Number of quiz attempts on current module
            time_on_module: Time spent on current module (minutes)
            median_time: Median time for this module across all students
            recent_scores: List of recent scores (last 3 attempts)
            
        Returns:
            1 if stuck, 0 otherwise
        """
        # Rule 1: Too many attempts
        if quiz_attempts > 3:
            return 1
        
        # Rule 2: Time significantly longer than median
        if time_on_module > 2 * median_time:
            return 1
        
        # Rule 3: Consistently low scores
        if len(recent_scores) >= 2:
            avg_recent = sum(recent_scores) / len(recent_scores)
            if avg_recent < 0.5:
                return 1
        
        return 0
    
    def build_state(
        self,
        cluster_id: int,
        current_module_id: int,
        module_progress: float,
        avg_score: float,
        recent_action_type: str,
        is_stuck: int
    ) -> Tuple[int, ...]:
        """
        Build state tuple from components
        
        Args:
            cluster_id: Original cluster ID [0-6]
            current_module_id: Module ID from course_structure
            module_progress: Progress on current module [0-1]
            avg_score: Average score [0-1]
            recent_action_type: Action type string
            is_stuck: Stuck indicator [0-1]
            
        Returns:
            State tuple: (cluster, module_idx, progress_bin, score_bin, action_id, stuck)
        """
        # Map cluster ID
        mapped_cluster = self.map_cluster_id(cluster_id)
        if mapped_cluster is None:
            raise ValueError(f"Cluster {cluster_id} is excluded (teacher cluster)")
        
        # Map module ID to index
        module_idx = self.module_id_to_idx.get(current_module_id, 0)
        
        # Bin continuous values
        progress_bin = self.quartile_bin(module_progress, self.PROGRESS_BINS)
        score_bin = self.quartile_bin(avg_score, self.SCORE_BINS)
        
        # Map action type
        action_id = self.ACTION_TYPES.get(recent_action_type, 4)  # Default to read_resource
        
        return (mapped_cluster, module_idx, progress_bin, score_bin, action_id, is_stuck)
    
    def state_to_string(self, state: Tuple[int, ...]) -> str:
        """
        Convert state tuple to readable string
        
        Args:
            state: State tuple
            
        Returns:
            Human-readable state string
        """
        cluster, module, progress, score, action, stuck = state
        action_name = self.ACTION_NAMES.get(action, 'unknown')
        stuck_str = 'STUCK' if stuck == 1 else 'OK'
        
        return (f"Cluster={cluster}, Module={module}, "
                f"Progress={progress:.2f}, Score={score:.2f}, "
                f"Action={action_name}, Status={stuck_str}")
    
    def build_state_from_log_entry(self, log_entry: Dict, student_context: Dict) -> Tuple[int, ...]:
        """
        Build state from a log entry and student context
        
        Args:
            log_entry: Single log entry from Moodle logs
                - eventname, component, action, objectid, userid, timecreated
            student_context: Current student context
                - cluster_id, current_module, progress, avg_score, quiz_attempts, 
                  time_on_module, median_time, recent_scores
                  
        Returns:
            State tuple
        """
        # Extract action type from log
        action_type = self.map_action_type(
            log_entry.get('eventname', ''),
            log_entry.get('component', ''),
            log_entry.get('action', '')
        )
        
        # Detect stuck
        is_stuck = self.detect_stuck(
            student_context.get('quiz_attempts', 0),
            student_context.get('time_on_module', 0),
            student_context.get('median_time', 30),
            student_context.get('recent_scores', [])
        )
        
        # Build state
        return self.build_state(
            cluster_id=student_context['cluster_id'],
            current_module_id=student_context['current_module'],
            module_progress=student_context.get('progress', 0.5),
            avg_score=student_context.get('avg_score', 0.5),
            recent_action_type=action_type,
            is_stuck=is_stuck
        )
    
    def get_state_space_size(self) -> int:
        """Calculate total state space size"""
        return (self.n_clusters * 
                self.n_modules * 
                len(self.PROGRESS_BINS) * 
                len(self.SCORE_BINS) * 
                len(self.ACTION_TYPES) * 
                2)  # is_stuck: 0 or 1
    
    def get_state_info(self) -> Dict:
        """Get information about state space"""
        return {
            'n_clusters': self.n_clusters,
            'n_modules': self.n_modules,
            'n_progress_bins': len(self.PROGRESS_BINS),
            'n_score_bins': len(self.SCORE_BINS),
            'n_action_types': len(self.ACTION_TYPES),
            'n_stuck_states': 2,
            'total_state_space': self.get_state_space_size(),
            'action_types': list(self.ACTION_TYPES.keys()),
            'cluster_mapping': self.cluster_mapping,
            'modules': self.modules[:5]  # Show first 5 modules
        }


def test_state_builder():
    """Test StateBuilderV2"""
    print("=" * 60)
    print("Testing StateBuilderV2")
    print("=" * 60)
    
    # Paths
    base_path = Path(__file__).parent.parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    course_path = base_path / 'data' / 'course_structure.json'
    
    # Initialize
    builder = StateBuilderV2(
        cluster_profiles_path=str(cluster_path),
        course_structure_path=str(course_path)
    )
    
    # Test 1: State space info
    print("\n1. State Space Info:")
    info = builder.get_state_info()
    for key, value in info.items():
        if key != 'modules':
            print(f"   {key}: {value}")
    
    # Test 2: Build sample states
    print("\n2. Sample States:")
    test_cases = [
        (0, 46, 0.3, 0.8, 'watch_video', 0),
        (2, 50, 0.7, 0.45, 'do_quiz', 1),
        (5, 60, 1.0, 0.95, 'read_resource', 0),
    ]
    
    for cluster, module, progress, score, action, stuck in test_cases:
        try:
            state = builder.build_state(cluster, module, progress, score, action, stuck)
            print(f"   Input: cluster={cluster}, module={module}, progress={progress:.2f}")
            print(f"   State: {state}")
            print(f"   String: {builder.state_to_string(state)}")
            print()
        except Exception as e:
            print(f"   Error: {e}\n")
    
    # Test 3: Quartile binning
    print("\n3. Quartile Binning Test:")
    test_values = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    for val in test_values:
        binned = builder.quartile_bin(val, builder.PROGRESS_BINS)
        print(f"   {val:.2f} -> {binned:.2f}")
    
    print("\n" + "=" * 60)
    print("✓ StateBuilderV2 test completed!")
    print("=" * 60)


if __name__ == '__main__':
    test_state_builder()
