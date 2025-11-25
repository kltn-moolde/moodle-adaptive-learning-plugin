#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Space Builder
====================
Extract và xây dựng action space từ course structure
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LearningAction:
    """Represent một learning action (action_type, time_context)"""
    action_type: str  # view_assignment, view_content, attempt_quiz, etc.
    time_context: str  # past, current, future
    index: int  # Index trong action space (0-based)
    
    def __repr__(self):
        return f"Action({self.index}: {self.action_type}, {self.time_context})"
    
    def to_tuple(self):
        """Convert to tuple representation"""
        return (self.action_type, self.time_context)
    
    @property
    def name(self):
        """Get human-readable name"""
        return f"{self.action_type} ({self.time_context})"


class ActionSpace:
    """
    Action Space Builder cho Q-Learning
    
    New Action Space Design:
    - Actions = (action_type, time_context) tuples
    - Total: 17 actions (5 past + 7 current + 3 future + 2 special)
    
    Action Types:
    - view_assignment: Xem yêu cầu assignment
    - view_content: Xem nội dung (video, tài liệu)
    - attempt_quiz: Bắt đầu làm quiz
    - submit_quiz: Nộp quiz
    - review_quiz: Xem lại kết quả quiz
    - post_forum: Tham gia thảo luận forum
    - submit_assignment: Nộp assignment
    
    Time Context:
    - past: Module đã học (completed)
    - current: Module đang học
    - future: Module sắp học
    """
    
    # Static action space definition
    ACTION_SPACE = [
        # --- Past actions (5) ---
        ("view_assignment", "past"),
        ("view_content", "past"),
        ("attempt_quiz", "past"),
        ("review_quiz", "past"),
        ("post_forum", "past"),

        # --- Current actions (7) ---
        ("view_assignment", "current"),
        ("view_content", "current"),
        ("submit_assignment", "current"),
        ("attempt_quiz", "current"),
        ("submit_quiz", "current"),
        ("review_quiz", "current"),
        ("post_forum", "current"),

        # --- Future actions (3) ---
        ("view_content", "future"),
        ("attempt_quiz", "future"),
        ("post_forum", "future"),
    ]
    
    def __init__(self, course_structure_path: Optional[str] = None):
        """
        Initialize action space
        
        Args:
            course_structure_path: Path to course_structure.json (not used in new design)
        """
        self.actions: List[LearningAction] = []
        self.action_map: Dict[tuple, LearningAction] = {}  # (action_type, time_context) -> LearningAction
        self.index_map: Dict[int, LearningAction] = {}  # index -> LearningAction
        
        self._build_actions()
    
    def _build_actions(self):
        """Build action space from static definition"""
        for idx, (action_type, time_context) in enumerate(self.ACTION_SPACE):
            action = LearningAction(
                action_type=action_type,
                time_context=time_context,
                index=idx
            )
            self.actions.append(action)
            self.action_map[(action_type, time_context)] = action
            self.index_map[idx] = action
    
    def get_actions(self) -> List[LearningAction]:
        """Get all actions"""
        return self.actions
    
    def get_action_by_tuple(self, action_type: str, time_context: str) -> Optional[LearningAction]:
        """Get action by (action_type, time_context) tuple"""
        return self.action_map.get((action_type, time_context))
    
    def get_action_by_index(self, index: int) -> Optional[LearningAction]:
        """Get action by index in action list (0-based)"""
        return self.index_map.get(index)
    
    def get_actions_by_type(self, action_type: str) -> List[LearningAction]:
        """Get actions filtered by action type"""
        return [a for a in self.actions if a.action_type == action_type]
    
    def get_actions_by_context(self, time_context: str) -> List[LearningAction]:
        """Get actions filtered by time context"""
        return [a for a in self.actions if a.time_context == time_context]
    
    def get_action_count(self) -> int:
        """Get total number of actions"""
        return len(self.actions)
    
    def get_action_index(self, action_type: str, time_context: str) -> int:
        """Get index of action by (action_type, time_context)"""
        action = self.get_action_by_tuple(action_type, time_context)
        return action.index if action else -1
    
    def get_action_summary(self) -> Dict:
        """Get summary statistics"""
        types = {}
        contexts = {}
        
        for action in self.actions:
            types[action.action_type] = types.get(action.action_type, 0) + 1
            contexts[action.time_context] = contexts.get(action.time_context, 0) + 1
        
        return {
            'total_actions': len(self.actions),
            'by_type': types,
            'by_context': contexts
        }
    
    def is_valid_action(self, action_type: str, time_context: str) -> bool:
        """Check if action is valid"""
        return (action_type, time_context) in self.action_map


# Example usage
if __name__ == '__main__':
    # Test action space
    action_space = ActionSpace()
    
    print("=" * 70)
    print("NEW ACTION SPACE SUMMARY")
    print("=" * 70)
    
    summary = action_space.get_action_summary()
    print(f"\nTotal actions: {summary['total_actions']}")
    
    print("\nBy Action Type:")
    for action_type, count in sorted(summary['by_type'].items()):
        print(f"  {action_type:25s}: {count}")
    
    print("\nBy Time Context:")
    for context, count in sorted(summary['by_context'].items()):
        print(f"  {context:15s}: {count}")
    
    print("\n" + "=" * 70)
    print("ALL ACTIONS")
    print("=" * 70)
    
    # Show all actions
    for action in action_space.get_actions():
        print(f"[{action.index:2d}] {action.action_type:25s} | {action.time_context:10s}")
    
    print("\n" + "=" * 70)
    print("EXAMPLE QUERIES")
    print("=" * 70)
    
    # Test queries
    print("\n1. Get action by tuple:")
    action = action_space.get_action_by_tuple("attempt_quiz", "current")
    if action:
        print(f"   Found: {action}")
    
    print("\n2. Get action by index:")
    action = action_space.get_action_by_index(8)
    if action:
        print(f"   Index 8: {action}")
    
    print("\n3. Get all 'current' actions:")
    current_actions = action_space.get_actions_by_context("current")
    print(f"   Found {len(current_actions)} current actions")
    for action in current_actions[:3]:
        print(f"   - {action}")
    
    print("\n4. Get all 'attempt_quiz' actions:")
    quiz_actions = action_space.get_actions_by_type("attempt_quiz")
    print(f"   Found {len(quiz_actions)} attempt_quiz actions")
    for action in quiz_actions:
        print(f"   - {action}")
    
    print("\n5. Check valid action:")
    is_valid = action_space.is_valid_action("submit_assignment", "current")
    print(f"   ('submit_assignment', 'current') is valid: {is_valid}")
    
    is_valid = action_space.is_valid_action("submit_assignment", "future")
    print(f"   ('submit_assignment', 'future') is valid: {is_valid}")

