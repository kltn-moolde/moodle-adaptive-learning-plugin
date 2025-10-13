#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Course Structure Models
=======================
Định nghĩa cấu trúc khóa học: Activity, Module, CourseStructure
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx


class ActivityType(Enum):
    """Các loại activity"""
    VIDEO = "video"
    READING = "reading"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    FORUM = "forum"
    LAB = "lab"
    PROJECT = "project"
    OTHER = "other"


@dataclass
class Activity:
    """
    Activity trong khóa học
    
    Attributes:
        activity_id: ID duy nhất
        name: Tên activity
        activity_type: Loại activity
        module_id: ID của module chứa activity này
        order: Thứ tự trong module
        difficulty: Độ khó (0-1)
        estimated_minutes: Thời gian ước tính (phút)
        prerequisites: List các activity_id cần hoàn thành trước
        learning_objectives: List các mục tiêu học tập
        is_optional: Activity có bắt buộc không
        passing_grade: Điểm tối thiểu để pass (0-1)
    """
    activity_id: str
    name: str
    activity_type: ActivityType
    module_id: str
    order: int
    difficulty: float
    estimated_minutes: int
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    is_optional: bool = False
    passing_grade: float = 0.6
    
    def __post_init__(self):
        """Validate data"""
        if not 0 <= self.difficulty <= 1:
            raise ValueError(f"Difficulty must be in [0, 1], got {self.difficulty}")
        if not 0 <= self.passing_grade <= 1:
            raise ValueError(f"Passing grade must be in [0, 1], got {self.passing_grade}")
        if self.estimated_minutes <= 0:
            raise ValueError(f"Estimated minutes must be positive, got {self.estimated_minutes}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'activity_id': self.activity_id,
            'name': self.name,
            'activity_type': self.activity_type.value,
            'module_id': self.module_id,
            'order': self.order,
            'difficulty': self.difficulty,
            'estimated_minutes': self.estimated_minutes,
            'prerequisites': self.prerequisites,
            'learning_objectives': self.learning_objectives,
            'is_optional': self.is_optional,
            'passing_grade': self.passing_grade,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Activity':
        """Create from dictionary"""
        data = data.copy()
        data['activity_type'] = ActivityType(data['activity_type'])
        return cls(**data)


@dataclass
class Module:
    """
    Module trong khóa học (nhóm các activities liên quan)
    
    Attributes:
        module_id: ID duy nhất
        name: Tên module
        order: Thứ tự trong khóa học
        difficulty: Độ khó trung bình (0-1)
        estimated_hours: Thời gian ước tính (giờ)
        prerequisites: List các module_id cần hoàn thành trước
        description: Mô tả module
    """
    module_id: str
    name: str
    order: int
    difficulty: float
    estimated_hours: float
    prerequisites: List[str] = field(default_factory=list)
    description: str = ""
    
    def __post_init__(self):
        """Validate data"""
        if not 0 <= self.difficulty <= 1:
            raise ValueError(f"Difficulty must be in [0, 1], got {self.difficulty}")
        if self.estimated_hours <= 0:
            raise ValueError(f"Estimated hours must be positive, got {self.estimated_hours}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'module_id': self.module_id,
            'name': self.name,
            'order': self.order,
            'difficulty': self.difficulty,
            'estimated_hours': self.estimated_hours,
            'prerequisites': self.prerequisites,
            'description': self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Module':
        """Create from dictionary"""
        return cls(**data)


class CourseStructure:
    """
    Cấu trúc khóa học đầy đủ
    
    Quản lý modules, activities, prerequisites graph
    """
    
    def __init__(self, 
                 course_id: str,
                 course_name: str,
                 modules: List[Module],
                 activities: List[Activity],
                 metadata: Optional[Dict] = None):
        """
        Initialize course structure
        
        Args:
            course_id: ID khóa học
            course_name: Tên khóa học
            modules: List các modules
            activities: List các activities
            metadata: Thông tin bổ sung
        """
        self.course_id = course_id
        self.course_name = course_name
        self.modules = {m.module_id: m for m in modules}
        self.activities = {a.activity_id: a for a in activities}
        self.metadata = metadata or {}
        
        # Build prerequisite graph
        self._prerequisite_graph = self._build_prerequisite_graph()
        
        # Validate structure
        self._validate()
    
    def _build_prerequisite_graph(self) -> nx.DiGraph:
        """
        Xây dựng directed graph cho prerequisites
        
        Returns:
            NetworkX DiGraph
        """
        G = nx.DiGraph()
        
        # Add activity nodes
        for activity_id, activity in self.activities.items():
            G.add_node(activity_id, **activity.to_dict())
        
        # Add prerequisite edges
        for activity_id, activity in self.activities.items():
            for prereq_id in activity.prerequisites:
                if prereq_id in self.activities:
                    G.add_edge(prereq_id, activity_id)
        
        return G
    
    def _validate(self):
        """Validate course structure"""
        # Check for cycles in prerequisites
        if not nx.is_directed_acyclic_graph(self._prerequisite_graph):
            cycles = list(nx.simple_cycles(self._prerequisite_graph))
            raise ValueError(f"Prerequisite graph contains cycles: {cycles}")
        
        # Check all prerequisites exist
        for activity in self.activities.values():
            for prereq_id in activity.prerequisites:
                if prereq_id not in self.activities:
                    raise ValueError(
                        f"Activity {activity.activity_id} has non-existent "
                        f"prerequisite {prereq_id}"
                    )
        
        # Check all module prerequisites exist
        for module in self.modules.values():
            for prereq_id in module.prerequisites:
                if prereq_id not in self.modules:
                    raise ValueError(
                        f"Module {module.module_id} has non-existent "
                        f"prerequisite {prereq_id}"
                    )
    
    def get_available_activities(self, completed_activities: Set[str]) -> List[str]:
        """
        Lấy danh sách activities có thể học tiếp theo
        
        Args:
            completed_activities: Set các activity_id đã hoàn thành
        
        Returns:
            List activity_ids có thể học
        """
        available = []
        
        for activity_id, activity in self.activities.items():
            # Skip if already completed
            if activity_id in completed_activities:
                continue
            
            # Check prerequisites
            prereqs = set(activity.prerequisites)
            if prereqs.issubset(completed_activities):
                available.append(activity_id)
        
        return available
    
    def get_learning_path(self, start_activity_id: str, end_activity_id: str) -> List[str]:
        """
        Tìm learning path ngắn nhất giữa 2 activities
        
        Args:
            start_activity_id: Activity bắt đầu
            end_activity_id: Activity kết thúc
        
        Returns:
            List activity_ids trong path
        """
        try:
            path = nx.shortest_path(
                self._prerequisite_graph,
                start_activity_id,
                end_activity_id
            )
            return path
        except nx.NetworkXNoPath:
            return []
    
    def get_module_completion(self, module_id: str, 
                             completed_activities: Set[str]) -> float:
        """
        Tính % hoàn thành của module
        
        Args:
            module_id: ID của module
            completed_activities: Set các activity_id đã hoàn thành
        
        Returns:
            Completion rate (0-1)
        """
        module_activities = [
            a for a in self.activities.values()
            if a.module_id == module_id
        ]
        
        if not module_activities:
            return 0.0
        
        completed_count = sum(
            1 for a in module_activities
            if a.activity_id in completed_activities
        )
        
        return completed_count / len(module_activities)
    
    def get_overall_completion(self, completed_activities: Set[str]) -> float:
        """
        Tính % hoàn thành toàn khóa học
        
        Args:
            completed_activities: Set các activity_id đã hoàn thành
        
        Returns:
            Completion rate (0-1)
        """
        if not self.activities:
            return 0.0
        
        # Only count non-optional activities
        required_activities = [
            a for a in self.activities.values()
            if not a.is_optional
        ]
        
        completed_count = sum(
            1 for a in required_activities
            if a.activity_id in completed_activities
        )
        
        return completed_count / len(required_activities) if required_activities else 0.0
    
    def get_activity_depth(self, activity_id: str) -> int:
        """
        Tính độ sâu của activity trong prerequisite graph
        (Số bước tối thiểu từ root activities)
        
        Args:
            activity_id: ID của activity
        
        Returns:
            Depth (0 = root activity)
        """
        # Find root nodes (no prerequisites)
        roots = [
            node for node in self._prerequisite_graph.nodes()
            if self._prerequisite_graph.in_degree(node) == 0
        ]
        
        if activity_id in roots:
            return 0
        
        # Calculate shortest path from any root
        min_depth = float('inf')
        for root in roots:
            try:
                path = nx.shortest_path(self._prerequisite_graph, root, activity_id)
                min_depth = min(min_depth, len(path) - 1)
            except nx.NetworkXNoPath:
                continue
        
        return min_depth if min_depth != float('inf') else -1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'modules': [m.to_dict() for m in self.modules.values()],
            'activities': [a.to_dict() for a in self.activities.values()],
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CourseStructure':
        """Create from dictionary"""
        modules = [Module.from_dict(m) for m in data['modules']]
        activities = [Activity.from_dict(a) for a in data['activities']]
        
        return cls(
            course_id=data['course_id'],
            course_name=data['course_name'],
            modules=modules,
            activities=activities,
            metadata=data.get('metadata', {})
        )
    
    def __repr__(self) -> str:
        return (
            f"CourseStructure(course_id='{self.course_id}', "
            f"modules={len(self.modules)}, "
            f"activities={len(self.activities)})"
        )
