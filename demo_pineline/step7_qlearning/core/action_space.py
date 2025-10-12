#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Space
============
Quản lý không gian hành động (available activities)
"""

from typing import List, Set
from models.course_structure import CourseStructure
from models.student_profile import StudentProfile


class ActionSpace:
    """
    Action Space = Tập hợp activities có thể recommend
    
    Quản lý:
    - Available activities (dựa trên prerequisites)
    - Filtering rules (không recommend quá xa, etc.)
    """
    
    def __init__(self, 
                 course_structure: CourseStructure,
                 max_look_ahead: float = 0.2):
        """
        Args:
            course_structure: CourseStructure object
            max_look_ahead: Maximum "jump ahead" ratio (0-1)
                           Ví dụ: 0.2 = chỉ recommend activities trong 20% tiến độ tiếp theo
        """
        self.course_structure = course_structure
        self.max_look_ahead = max_look_ahead
    
    def get_available_actions(self, student_profile: StudentProfile) -> List[str]:
        """
        Lấy danh sách actions (activity_ids) có thể recommend
        
        Args:
            student_profile: StudentProfile object
        
        Returns:
            List of activity_ids
        """
        completed = student_profile.get_completed_activities()
        
        # Get activities với prerequisites đã hoàn thành
        available = self.course_structure.get_available_activities(completed)
        
        # Apply filtering rules
        filtered = self._apply_filters(available, student_profile)
        
        return filtered
    
    def _apply_filters(self,
                      available_activities: List[str],
                      student_profile: StudentProfile) -> List[str]:
        """
        Áp dụng filtering rules
        
        Rules:
        1. Không recommend quá xa (max_look_ahead)
        2. Ưu tiên non-optional activities
        3. Không recommend activities quá khó (nếu student yếu)
        """
        if not available_activities:
            return []
        
        filtered = []
        
        total_activities = len(self.course_structure.activities)
        completed_count = len(student_profile.get_completed_activities())
        current_progress = completed_count / max(total_activities, 1)
        
        student_level = student_profile.get_average_grade()
        
        for activity_id in available_activities:
            activity = self.course_structure.activities[activity_id]
            
            # Rule 1: Max look ahead
            activity_position = activity.order / max(total_activities, 1)
            if activity_position > current_progress + self.max_look_ahead:
                continue  # Too far ahead
            
            # Rule 2: Ưu tiên non-optional (nhưng không loại bỏ hoàn toàn)
            # → Just add, prioritization happens in Q-values
            
            # Rule 3: Difficulty matching
            if activity.difficulty > student_level + 0.4:
                continue  # Too hard
            
            filtered.append(activity_id)
        
        # Fallback: If empty after filtering, return original
        return filtered if filtered else available_activities
    
    def is_terminal_state(self, student_profile: StudentProfile) -> bool:
        """
        Kiểm tra xem có phải terminal state không
        (Đã hoàn thành tất cả required activities)
        
        Args:
            student_profile: StudentProfile object
        
        Returns:
            True if terminal
        """
        available = self.get_available_actions(student_profile)
        return len(available) == 0
    
    def get_action_count(self) -> int:
        """
        Lấy tổng số actions có thể (= số activities)
        
        Returns:
            Count
        """
        return len(self.course_structure.activities)
