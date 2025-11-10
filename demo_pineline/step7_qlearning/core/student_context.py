#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Context Tracker
========================
Track student learning context for state building
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime


class StudentContext:
    """
    Track student learning context
    
    Maintains:
    - Current module and progress
    - Score history and average
    - Recent actions
    - Quiz attempts per module
    - Time spent per module
    - Stuck indicators
    """
    
    def __init__(
        self,
        student_id: int,
        cluster_id: int,
        recent_action_window: int = 5
    ):
        """
        Initialize student context
        
        Args:
            student_id: Student ID
            cluster_id: Cluster ID (original 0-6)
            recent_action_window: Window size for recent actions
        """
        self.student_id = student_id
        self.cluster_id = cluster_id
        self.recent_action_window = recent_action_window
        
        # Current state
        self.current_module = None
        self.module_start_time = None
        
        # Progress tracking (per module)
        self.module_progress = defaultdict(lambda: 0.0)  # module_id -> progress [0-1]
        self.module_events = defaultdict(lambda: {'total': 0, 'completed': 0})
        
        # Score tracking
        self.scores = []  # List of (module_id, score, timestamp)
        self.module_scores = defaultdict(list)  # module_id -> [scores]
        
        # Action tracking
        self.recent_actions = deque(maxlen=recent_action_window)  # Recent action types
        self.action_history = []  # Full history: (timestamp, module_id, action_type)
        
        # Quiz attempts
        self.quiz_attempts = defaultdict(int)  # module_id -> attempts
        
        # Time tracking
        self.module_start_times = {}  # module_id -> start timestamp
        self.module_durations = defaultdict(list)  # module_id -> [durations]
        
        # Statistics
        self.total_events = 0
        self.completed_modules = set()
    
    def update_from_log_entry(self, log_entry: Dict) -> Optional[str]:
        """
        Update context from a Moodle log entry
        
        Args:
            log_entry: Log entry dict with keys:
                - eventname, component, action, objectid
                - contextinstanceid (module_id)
                - timecreated
                
        Returns:
            Action type string or None
        """
        module_id = log_entry.get('contextinstanceid')
        timestamp = log_entry.get('timecreated', 0)
        eventname = log_entry.get('eventname', '')
        component = log_entry.get('component', '')
        action = log_entry.get('action', '')
        
        # Ignore if no module
        if not module_id:
            return None
        
        self.total_events += 1
        
        # Update current module
        if self.current_module != module_id:
            self.current_module = module_id
            if module_id not in self.module_start_times:
                self.module_start_times[module_id] = timestamp
        
        # Map to action type
        action_type = self._map_action_type(eventname, component, action)
        
        # Update recent actions
        if action_type:
            self.recent_actions.append(action_type)
            self.action_history.append((timestamp, module_id, action_type))
        
        # Update module events
        self.module_events[module_id]['total'] += 1
        
        # Track quiz attempts
        if 'quiz' in component.lower():
            if 'attempt_started' in eventname.lower():
                self.quiz_attempts[module_id] += 1
            elif 'attempt_submitted' in eventname.lower():
                self.module_events[module_id]['completed'] += 1
        
        # Track completion
        if 'completion' in eventname.lower() or 'submitted' in action.lower():
            self.module_events[module_id]['completed'] += 1
            if self._calculate_module_progress(module_id) >= 1.0:
                self.completed_modules.add(module_id)
        
        return action_type
    
    def update_from_grade_entry(self, grade_entry: Dict):
        """
        Update context from a grade entry
        
        Args:
            grade_entry: Grade entry dict with keys:
                - itemid (module_id)
                - finalgrade (score)
                - timecreated
        """
        module_id = grade_entry.get('itemid')
        score = grade_entry.get('finalgrade', 0.0)
        timestamp = grade_entry.get('timecreated', 0)
        
        if module_id and score is not None:
            # Normalize score to 0-1
            normalized_score = max(0.0, min(1.0, float(score) / 100.0))
            
            self.scores.append((module_id, normalized_score, timestamp))
            self.module_scores[module_id].append(normalized_score)
    
    def _map_action_type(self, eventname: str, component: str, action: str) -> Optional[str]:
        """Map Moodle event to action type"""
        event_lower = eventname.lower()
        comp_lower = component.lower()
        
        # Mapping rules (same as StateBuilderV2)
        if 'hvp' in event_lower or 'video' in comp_lower:
            return 'watch_video'
        elif 'quiz' in comp_lower:
            if 'attempt_started' in event_lower or 'attempt_submitted' in event_lower:
                return 'do_quiz'
            elif 'reviewed' in event_lower:
                return 'review_quiz'
            return 'do_quiz'
        elif 'forum' in comp_lower:
            return 'mod_forum'
        elif 'assign' in comp_lower:
            if 'feedback' in event_lower:
                return 'review_quiz'
            return 'do_assignment'
        elif 'resource' in comp_lower or 'page' in comp_lower or 'url' in comp_lower:
            return 'read_resource'
        
        return 'read_resource'  # Default
    
    def _calculate_module_progress(self, module_id: int) -> float:
        """Calculate progress for a module"""
        events = self.module_events[module_id]
        if events['total'] == 0:
            return 0.0
        
        # Simple progress: completed / total events
        progress = events['completed'] / max(events['total'], 1)
        return min(1.0, progress)
    
    def get_module_progress(self, module_id: Optional[int] = None) -> float:
        """
        Get progress for module
        
        Args:
            module_id: Module ID (if None, use current_module)
            
        Returns:
            Progress [0-1]
        """
        if module_id is None:
            module_id = self.current_module
        
        if module_id is None:
            return 0.0
        
        return self._calculate_module_progress(module_id)
    
    def get_avg_score(self, last_n: Optional[int] = None) -> float:
        """
        Get average score
        
        Args:
            last_n: If provided, average of last N scores only
            
        Returns:
            Average score [0-1]
        """
        if not self.scores:
            return 0.5  # Default
        
        if last_n:
            recent_scores = [s[1] for s in self.scores[-last_n:]]
        else:
            recent_scores = [s[1] for s in self.scores]
        
        return sum(recent_scores) / len(recent_scores) if recent_scores else 0.5
    
    def get_recent_action(self) -> str:
        """Get most recent action type"""
        if self.recent_actions:
            return self.recent_actions[-1]
        return 'read_resource'  # Default
    
    def get_recent_scores(self, n: int = 3) -> List[float]:
        """Get last N scores"""
        if not self.scores:
            return []
        return [s[1] for s in self.scores[-n:]]
    
    def get_quiz_attempts(self, module_id: Optional[int] = None) -> int:
        """Get quiz attempts for module"""
        if module_id is None:
            module_id = self.current_module
        
        if module_id is None:
            return 0
        
        return self.quiz_attempts[module_id]
    
    def get_time_on_module(self, module_id: Optional[int] = None) -> float:
        """
        Get time spent on module (minutes)
        
        Args:
            module_id: Module ID (if None, use current_module)
            
        Returns:
            Time in minutes
        """
        if module_id is None:
            module_id = self.current_module
        
        if module_id is None or module_id not in self.module_start_times:
            return 0.0
        
        # Get all actions on this module
        module_actions = [
            (ts, act) for ts, mod, act in self.action_history 
            if mod == module_id
        ]
        
        if len(module_actions) < 2:
            return 0.0
        
        # Time = last action - first action (in minutes)
        first_ts = module_actions[0][0]
        last_ts = module_actions[-1][0]
        
        duration = last_ts - first_ts
        
        # Handle both datetime and numeric timestamps
        if hasattr(duration, 'total_seconds'):
            # pandas Timedelta object
            return duration.total_seconds() / 60.0
        else:
            # Numeric timestamp (assume seconds)
            return duration / 60.0
    
    def is_stuck(self, median_time: float = 30.0) -> bool:
        """
        Check if student is stuck
        
        Args:
            median_time: Median time for current module (minutes)
            
        Returns:
            True if stuck
        """
        if self.current_module is None:
            return False
        
        # Rule 1: Too many quiz attempts
        if self.quiz_attempts[self.current_module] > 3:
            return True
        
        # Rule 2: Time significantly longer than median
        time_spent = self.get_time_on_module()
        if time_spent > 2 * median_time:
            return True
        
        # Rule 3: Consistently low scores
        recent_scores = self.get_recent_scores(n=2)
        if len(recent_scores) >= 2:
            avg_recent = sum(recent_scores) / len(recent_scores)
            if avg_recent < 0.5:
                return True
        
        return False
    
    def get_state_dict(self, median_time: float = 30.0) -> Dict:
        """
        Get current state as dict
        
        Args:
            median_time: Median time for current module
            
        Returns:
            Dict with all state components
        """
        return {
            'cluster_id': self.cluster_id,
            'current_module': self.current_module,
            'progress': self.get_module_progress(),
            'avg_score': self.get_avg_score(),
            'recent_action': self.get_recent_action(),
            'quiz_attempts': self.get_quiz_attempts(),
            'time_on_module': self.get_time_on_module(),
            'median_time': median_time,
            'recent_scores': self.get_recent_scores(),
            'is_stuck': self.is_stuck(median_time)
        }
    
    def get_statistics(self) -> Dict:
        """Get statistics about student"""
        return {
            'student_id': self.student_id,
            'cluster_id': self.cluster_id,
            'total_events': self.total_events,
            'total_scores': len(self.scores),
            'avg_score': self.get_avg_score(),
            'completed_modules': len(self.completed_modules),
            'current_module': self.current_module,
            'current_progress': self.get_module_progress(),
            'total_quiz_attempts': sum(self.quiz_attempts.values()),
            'is_stuck': self.is_stuck()
        }


def test_student_context():
    """Test StudentContext"""
    print("=" * 60)
    print("Testing StudentContext")
    print("=" * 60)
    
    # Initialize
    ctx = StudentContext(student_id=101, cluster_id=0)
    
    # Simulate log entries
    print("\n1. Simulating log entries...")
    
    logs = [
        {'eventname': '\\mod_resource\\event\\course_module_viewed', 
         'component': 'mod_resource', 'action': 'viewed',
         'contextinstanceid': 60, 'timecreated': 1000},
        
        {'eventname': '\\mod_quiz\\event\\attempt_started',
         'component': 'mod_quiz', 'action': 'started',
         'contextinstanceid': 67, 'timecreated': 1100},
        
        {'eventname': '\\mod_quiz\\event\\attempt_submitted',
         'component': 'mod_quiz', 'action': 'submitted',
         'contextinstanceid': 67, 'timecreated': 1300},
        
        {'eventname': '\\mod_quiz\\event\\attempt_reviewed',
         'component': 'mod_quiz', 'action': 'reviewed',
         'contextinstanceid': 67, 'timecreated': 1400},
    ]
    
    for log in logs:
        action_type = ctx.update_from_log_entry(log)
        print(f"   Module {log['contextinstanceid']}: {action_type}")
    
    # Simulate grade entries
    print("\n2. Simulating grade entries...")
    
    grades = [
        {'itemid': 67, 'finalgrade': 85.0, 'timecreated': 1350},
        {'itemid': 67, 'finalgrade': 90.0, 'timecreated': 1500},
    ]
    
    for grade in grades:
        ctx.update_from_grade_entry(grade)
        print(f"   Module {grade['itemid']}: score={grade['finalgrade']}")
    
    # Get state
    print("\n3. Current state:")
    state_dict = ctx.get_state_dict()
    for key, value in state_dict.items():
        print(f"   {key}: {value}")
    
    # Get statistics
    print("\n4. Statistics:")
    stats = ctx.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ StudentContext test completed!")
    print("=" * 60)


if __name__ == '__main__':
    test_student_context()
