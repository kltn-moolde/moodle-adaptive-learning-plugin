#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Space Manager
====================
Quản lý action space từ Moodle course structure
"""

from typing import Dict, List, Optional, Tuple
import json


class Action:
    """
    Action representation cho Q-Learning
    
    Attributes:
        action_id: Unique ID (resource_id)
        action_type: Loại action (study_resource, take_quiz_easy, ...)
        resource_id: Moodle resource ID
        resource_type: modname (quiz, resource, hvp, forum)
        resource_name: Tên resource
        difficulty: Độ khó (easy, medium, hard) nếu có
        section_id: ID section chứa resource
        lesson_id: ID lesson (nếu có)
        lesson_name: Tên lesson (nếu có)
        metadata: Additional info
    """
    
    def __init__(self,
                 resource_id: int,
                 resource_name: str,
                 resource_type: str,
                 action_type: str,
                 section_id: Optional[int] = None,
                 lesson_id: Optional[int] = None,
                 lesson_name: Optional[str] = None,
                 difficulty: Optional[str] = None,
                 **metadata):
        self.action_id = str(resource_id)  # Use resource_id as action_id
        self.resource_id = resource_id
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.action_type = action_type
        self.section_id = section_id
        self.lesson_id = lesson_id
        self.lesson_name = lesson_name
        self.difficulty = difficulty
        self.metadata = metadata
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'action_id': self.action_id,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'resource_type': self.resource_type,
            'action_type': self.action_type,
            'section_id': self.section_id,
            'lesson_id': self.lesson_id,
            'lesson_name': self.lesson_name,
            'difficulty': self.difficulty,
            **self.metadata
        }
    
    def __repr__(self) -> str:
        return (f"Action(id={self.action_id}, type={self.action_type}, "
                f"name='{self.resource_name}', difficulty={self.difficulty})")


class ActionSpace:
    """
    Action Space Builder từ Moodle course structure
    
    Xây dựng toàn bộ action space từ course structure JSON
    """
    
    # Mapping modname -> action_type
    ACTION_TYPE_MAP = {
        'quiz': 'take_quiz',
        'hvp': 'watch_video',
        'resource': 'study_resource',
        'page': 'read_page',
        'url': 'visit_url',
        'forum': 'participate_forum',
        'assign': 'submit_assignment',
        'book': 'read_book',
        'folder': 'explore_folder',
        'label': 'read_label'
    }
    
    def __init__(self, course_structure: Dict):
        """
        Args:
            course_structure: Dict from MongoDB course structure
        """
        self.course_structure = course_structure
        self.actions: List[Action] = []
        self.action_dict: Dict[str, Action] = {}  # action_id -> Action
        
        # Build action space
        self._build_action_space()
    
    def _build_action_space(self):
        """Xây dựng action space từ course structure"""
        # Support both 'contents' and 'sections' keys
        contents = self.course_structure.get('contents') or self.course_structure.get('sections', [])
        
        for section in contents:
            section_id = section.get('sectionid') or section.get('sectionIdOld')
            section_name = section.get('name', 'Unknown Section')
            
            # Resources trực tiếp trong section
            if 'resources' in section:
                self._process_resources(
                    section['resources'],
                    section_id=section_id,
                    section_name=section_name
                )
            
            # Lessons trong section
            if 'lessons' in section:
                for lesson in section['lessons']:
                    lesson_id = (lesson.get('sectionIdNew') or 
                                lesson.get('sectionIdOld'))
                    lesson_name = lesson.get('name', 'Unknown Lesson')
                    
                    self._process_resources(
                        lesson['resources'],
                        section_id=section_id,
                        section_name=section_name,
                        lesson_id=lesson_id,
                        lesson_name=lesson_name
                    )
    
    def _process_resources(self,
                          resources: List[Dict],
                          section_id: Optional[int] = None,
                          section_name: Optional[str] = None,
                          lesson_id: Optional[int] = None,
                          lesson_name: Optional[str] = None):
        """Process resources và tạo actions"""
        for resource in resources:
            resource_id = resource['id']
            resource_name = resource['name']
            modname = resource['modname']
            
            # Skip non-actionable resources
            if modname in ['qbank', 'lti']:
                continue
            
            # Determine action type
            base_action_type = self.ACTION_TYPE_MAP.get(modname, 'unknown_action')
            
            # Special handling cho quiz: phân loại theo difficulty
            if modname == 'quiz':
                difficulty = self._extract_difficulty(resource_name)
                action_type = f"{base_action_type}_{difficulty}"
            else:
                difficulty = None
                action_type = base_action_type
            
            # Create action
            action = Action(
                resource_id=resource_id,
                resource_name=resource_name,
                resource_type=modname,
                action_type=action_type,
                section_id=section_id,
                lesson_id=lesson_id,
                lesson_name=lesson_name,
                difficulty=difficulty,
                section_name=section_name
            )
            
            # Add to collections
            self.actions.append(action)
            self.action_dict[action.action_id] = action
    
    def _extract_difficulty(self, resource_name: str) -> str:
        """
        Trích xuất độ khó từ tên resource
        
        Args:
            resource_name: Tên resource
        
        Returns:
            'easy', 'medium', hoặc 'hard'
        """
        name_lower = resource_name.lower()
        if 'easy' in name_lower:
            return 'easy'
        elif 'medium' in name_lower:
            return 'medium'
        elif 'hard' in name_lower:
            return 'hard'
        else:
            return 'medium'  # Default
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """Lấy action theo ID"""
        return self.action_dict.get(action_id)
    
    def get_all_actions(self) -> List[Action]:
        """Lấy tất cả actions"""
        return self.actions
    
    def get_actions_by_type(self, action_type: str) -> List[Action]:
        """Lấy actions theo type"""
        return [a for a in self.actions if a.action_type == action_type]
    
    def get_actions_by_difficulty(self, difficulty: str) -> List[Action]:
        """Lấy actions theo difficulty"""
        return [a for a in self.actions if a.difficulty == difficulty]
    
    def get_actions_by_lesson(self, lesson_name: str) -> List[Action]:
        """Lấy actions theo lesson"""
        return [a for a in self.actions if a.lesson_name == lesson_name]
    
    def filter_actions(self, 
                      completed_action_ids: List[str],
                      action_types: Optional[List[str]] = None,
                      difficulties: Optional[List[str]] = None) -> List[Action]:
        """
        Lọc actions chưa hoàn thành và theo criteria
        
        Args:
            completed_action_ids: List action IDs đã hoàn thành
            action_types: Chỉ lấy các action types này (nếu có)
            difficulties: Chỉ lấy các difficulties này (nếu có)
        
        Returns:
            Filtered actions
        """
        completed_set = set(completed_action_ids)
        
        filtered = [
            a for a in self.actions 
            if a.action_id not in completed_set
        ]
        
        # Filter by action_type
        if action_types:
            filtered = [a for a in filtered if a.action_type in action_types]
        
        # Filter by difficulty
        if difficulties:
            filtered = [a for a in filtered if a.difficulty in difficulties]
        
        return filtered
    
    def get_action_space_size(self) -> int:
        """Lấy số lượng actions"""
        return len(self.actions)
    
    def get_action_type_distribution(self) -> Dict[str, int]:
        """Phân bố action types"""
        distribution = {}
        for action in self.actions:
            distribution[action.action_type] = distribution.get(action.action_type, 0) + 1
        return distribution
    
    @staticmethod
    def load_from_file(json_path: str) -> 'ActionSpace':
        """
        Load action space từ course structure JSON file
        
        Args:
            json_path: Path to course structure JSON
        
        Returns:
            ActionSpace object
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find course structure (skip metadata entries)
        course_structure = None
        if isinstance(data, list):
            for item in data:
                if 'contents' in item or 'sections' in item:
                    course_structure = item
                    break
        else:
            course_structure = data
        
        if not course_structure:
            raise ValueError("Could not find course structure in JSON")
        
        return ActionSpace(course_structure)


# Example usage
if __name__ == '__main__':
    # Sample course structure
    sample_course = {
        "course_id": "5",
        "contents": [
            {
                "sectionIdOld": 34,
                "name": "Chủ đề 1: MÁY TÍNH VÀ XÃ HỘI TRI THỨC",
                "lessons": [
                    {
                        "sectionIdNew": 38,
                        "name": "Bài 1: Làm quen với Trí tuệ nhân tạo",
                        "resources": [
                            {
                                "id": 62,
                                "name": "SGK_CS_Bai1",
                                "modname": "resource"
                            },
                            {
                                "id": 63,
                                "name": "Video bài giảng bài 1",
                                "modname": "hvp"
                            },
                            {
                                "id": 61,
                                "name": "bài kiểm tra bài 1 - easy",
                                "modname": "quiz"
                            },
                            {
                                "id": 106,
                                "name": "bài kiểm tra bài 1 - medium",
                                "modname": "quiz"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Build action space
    action_space = ActionSpace(sample_course)
    
    print(f"Total actions: {action_space.get_action_space_size()}")
    print("\nAction type distribution:")
    for action_type, count in action_space.get_action_type_distribution().items():
        print(f"  {action_type}: {count}")
    
    print("\nAll actions:")
    for action in action_space.get_all_actions():
        print(f"  {action}")
    
    print("\nQuizzes only:")
    quizzes = action_space.get_actions_by_type('take_quiz_easy')
    for quiz in quizzes:
        print(f"  {quiz}")
