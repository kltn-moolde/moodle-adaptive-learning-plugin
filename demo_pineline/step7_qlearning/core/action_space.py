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
    """Represent một learning action"""
    id: int
    name: str
    type: str  # quiz, assign, resource, video, forum, etc.
    section: str
    purpose: str  # assessment, content, collaboration
    difficulty: str = 'medium'  # easy, medium, hard
    
    def __repr__(self):
        return f"Action({self.id}, {self.type}: {self.name[:30]}...)"


class ActionSpace:
    """
    Action Space Builder cho Q-Learning
    
    Actions = Learning objects từ course structure:
    - Quiz (assessment)
    - Assignment (assessment)
    - Resource/Page/URL (content)
    - Video/H5P (interactive content)
    - Forum (collaboration)
    """
    
    def __init__(self, course_structure_path: str):
        """
        Initialize action space từ course structure
        
        Args:
            course_structure_path: Path to course_structure.json
        """
        self.course_structure_path = course_structure_path
        self.actions: List[LearningAction] = []
        self.action_map: Dict[int, LearningAction] = {}
        
        self._load_actions()
    
    def _load_actions(self):
        """Load actions từ course structure"""
        with open(self.course_structure_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        contents = data.get('contents', [])
        
        for section in contents:
            section_name = section.get('name', 'Unknown Section')
            
            for module in section.get('modules', []):
                action = self._create_action(module, section_name)
                if action:
                    self.actions.append(action)
                    self.action_map[action.id] = action
    
    def _create_action(self, module: Dict, section: str) -> Optional[LearningAction]:
        """
        Tạo action từ module data
        
        Args:
            module: Module data từ Moodle
            section: Section name
        
        Returns:
            LearningAction hoặc None nếu module không phải action hợp lệ
        """
        modname = module.get('modname', '')
        
        # Filter: chỉ lấy learning activities, bỏ qua subsection links
        if modname == 'subsection':
            return None
        
        # Map purpose
        purpose = module.get('purpose', 'other')
        
        # Detect difficulty từ tên (heuristic)
        name = module.get('name', '').lower()
        difficulty = 'medium'
        if 'easy' in name or 'dễ' in name:
            difficulty = 'easy'
        elif 'hard' in name or 'khó' in name or 'cuối kỳ' in name:
            difficulty = 'hard'
        elif 'medium' in name or 'trung bình' in name:
            difficulty = 'medium'
        
        return LearningAction(
            id=module['id'],
            name=module.get('name', 'Unnamed'),
            type=modname,
            section=section,
            purpose=purpose,
            difficulty=difficulty
        )
    
    def get_actions(self) -> List[LearningAction]:
        """Get all actions"""
        return self.actions
    
    def get_action_by_id(self, action_id: int) -> Optional[LearningAction]:
        """Get action by ID"""
        return self.action_map.get(action_id)
    
    def get_actions_by_type(self, action_type: str) -> List[LearningAction]:
        """Get actions filtered by type"""
        return [a for a in self.actions if a.type == action_type]
    
    def get_actions_by_purpose(self, purpose: str) -> List[LearningAction]:
        """Get actions filtered by purpose"""
        return [a for a in self.actions if a.purpose == purpose]
    
    def get_actions_by_difficulty(self, difficulty: str) -> List[LearningAction]:
        """Get actions filtered by difficulty"""
        return [a for a in self.actions if a.difficulty == difficulty]
    
    def get_action_count(self) -> int:
        """Get total number of actions"""
        return len(self.actions)
    
    def get_action_summary(self) -> Dict:
        """Get summary statistics"""
        types = {}
        purposes = {}
        difficulties = {}
        
        for action in self.actions:
            types[action.type] = types.get(action.type, 0) + 1
            purposes[action.purpose] = purposes.get(action.purpose, 0) + 1
            difficulties[action.difficulty] = difficulties.get(action.difficulty, 0) + 1
        
        return {
            'total_actions': len(self.actions),
            'by_type': types,
            'by_purpose': purposes,
            'by_difficulty': difficulties
        }


# Example usage
if __name__ == '__main__':
    import os
    
    # Test with course structure
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    course_path = os.path.join(data_dir, 'course_structure.json')
    
    action_space = ActionSpace(course_path)
    
    print("=" * 70)
    print("ACTION SPACE SUMMARY")
    print("=" * 70)
    
    summary = action_space.get_action_summary()
    print(f"\nTotal actions: {summary['total_actions']}")
    
    print("\nBy Type:")
    for type_name, count in summary['by_type'].items():
        print(f"  {type_name:15s}: {count}")
    
    print("\nBy Purpose:")
    for purpose, count in summary['by_purpose'].items():
        print(f"  {purpose:15s}: {count}")
    
    print("\nBy Difficulty:")
    for diff, count in summary['by_difficulty'].items():
        print(f"  {diff:15s}: {count}")
    
    print("\n" + "=" * 70)
    print("SAMPLE ACTIONS")
    print("=" * 70)
    
    # Show sample actions
    for action in action_space.get_actions()[:5]:
        print(f"\nID: {action.id}")
        print(f"  Name: {action.name}")
        print(f"  Type: {action.type}")
        print(f"  Purpose: {action.purpose}")
        print(f"  Difficulty: {action.difficulty}")
        print(f"  Section: {action.section}")
