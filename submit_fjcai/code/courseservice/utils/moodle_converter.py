#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle Course Structure Converter
==================================
Chuyển đổi cấu trúc phẳng của Moodle thành deep hierarchy
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from utils.logger import setup_logger, log_execution_time

logger = setup_logger('converter')


class NodeType(Enum):
    """Loại node trong cây phân cấp"""
    COURSE = "course"
    SECTION = "section"
    SUBSECTION = "subsection"
    MODULE = "module"
    ACTIVITY = "activity"
    RESOURCE = "resource"


@dataclass
class HierarchyNode:
    """Node trong cây phân cấp"""
    id: int
    name: str
    type: NodeType
    level: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['HierarchyNode'] = field(default_factory=list)
    parent: Optional['HierarchyNode'] = None
    
    def add_child(self, child: 'HierarchyNode'):
        """Thêm node con"""
        child.parent = self
        child.level = self.level + 1
        self.children.append(child)
        
    def to_dict(self, include_parent=False) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'level': self.level,
            'metadata': self.metadata,
            'children': [child.to_dict() for child in self.children]
        }
        if include_parent and self.parent:
            result['parent_id'] = self.parent.id
        return result
    
    def get_path(self) -> List[str]:
        """Lấy đường dẫn từ root đến node hiện tại"""
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.parent
        return path
    
    def find_node_by_id(self, node_id: int) -> Optional['HierarchyNode']:
        """Tìm node theo ID (DFS)"""
        if self.id == node_id:
            return self
        for child in self.children:
            result = child.find_node_by_id(node_id)
            if result:
                return result
        return None
    
    def get_all_nodes(self, node_type: Optional[NodeType] = None) -> List['HierarchyNode']:
        """Lấy tất cả nodes (có thể filter theo type)"""
        nodes = []
        if node_type is None or self.type == node_type:
            nodes.append(self)
        for child in self.children:
            nodes.extend(child.get_all_nodes(node_type))
        return nodes


class MoodleStructureConverter:
    """Chuyển đổi cấu trúc Moodle thành deep hierarchy"""
    
    # Mapping modname -> NodeType (có thể mở rộng)
    MODULE_TYPE_MAPPING = {
        'subsection': NodeType.SUBSECTION,
        'quiz': NodeType.ACTIVITY,
        'assign': NodeType.ACTIVITY,
        'forum': NodeType.ACTIVITY,
        'resource': NodeType.RESOURCE,
        'url': NodeType.RESOURCE,
        'page': NodeType.RESOURCE,
        'book': NodeType.RESOURCE,
        'hvp': NodeType.ACTIVITY,
        'lti': NodeType.ACTIVITY,  # LTI = External Tool (activity)
        'qbank': NodeType.ACTIVITY,  # Question Bank (activity)
        'folder': NodeType.RESOURCE,
        'label': NodeType.RESOURCE,
        'workshop': NodeType.ACTIVITY,
        'wiki': NodeType.ACTIVITY,
        'glossary': NodeType.ACTIVITY,
        'chat': NodeType.ACTIVITY,
        'choice': NodeType.ACTIVITY,
        'feedback': NodeType.ACTIVITY,
        'survey': NodeType.ACTIVITY,
        'lesson': NodeType.ACTIVITY,
        'scorm': NodeType.ACTIVITY,
        'h5pactivity': NodeType.ACTIVITY,
        'bigbluebuttonbn': NodeType.ACTIVITY,
    }
    
    def __init__(self, course_name: str = "Moodle Course"):
        self.course_name = course_name
        self.root: Optional[HierarchyNode] = None
        
    @log_execution_time
    def convert(self, moodle_data: List[Dict]) -> HierarchyNode:
        """
        Chuyển đổi dữ liệu Moodle thành cây phân cấp
        
        Args:
            moodle_data: List of sections từ Moodle API
            
        Returns:
            Root node của cây phân cấp
        """
        logger.info(f"Converting Moodle structure: {len(moodle_data)} sections")
        
        # Tạo root node (Course)
        self.root = HierarchyNode(
            id=0,
            name=self.course_name,
            type=NodeType.COURSE,
            level=0,
            metadata={'total_sections': len(moodle_data)}
        )
        
        # Mapping section_id -> node
        section_map: Dict[int, HierarchyNode] = {}
        
        # Pass 1: Tạo tất cả section nodes
        for section_data in moodle_data:
            section_node = self._create_section_node(section_data)
            section_map[section_data['id']] = section_node
            
            if section_data.get('component') is None:
                self.root.add_child(section_node)
        
        # Pass 2: Xử lý modules và subsections
        for section_data in moodle_data:
            section_node = section_map[section_data['id']]
            
            for module_data in section_data.get('modules', []):
                if module_data.get('modname') == 'subsection':
                    subsection_id = self._extract_subsection_id(module_data)
                    if subsection_id and subsection_id in section_map:
                        subsection_node = section_map[subsection_id]
                        
                        # Remove from root if it was added there
                        if subsection_node in self.root.children:
                            self.root.children.remove(subsection_node)
                        
                        # Update level and add to parent section
                        subsection_node.level = section_node.level + 1
                        subsection_node.type = NodeType.SUBSECTION  # Update type
                        section_node.add_child(subsection_node)
                else:
                    module_node = self._create_module_node(module_data, section_node.level + 1)
                    section_node.add_child(module_node)
        
        stats = self._get_stats()
        logger.info(f"✓ Conversion completed: {stats}")
        
        return self.root
    
    def _create_section_node(self, section_data: Dict) -> HierarchyNode:
        """Tạo section node"""
        return HierarchyNode(
            id=section_data['id'],
            name=section_data['name'] or f"Section {section_data['section']}",
            type=NodeType.SECTION,
            level=1,
            metadata={
                'section': section_data['section'],
                'visible': section_data.get('visible', 1),
                'summary': section_data.get('summary', ''),
                'component': section_data.get('component'),
                'itemid': section_data.get('itemid'),
                'hiddenbynumsections': section_data.get('hiddenbynumsections', 0)
            }
        )
    
    def _create_module_node(self, module_data: Dict, parent_level: int = 1) -> HierarchyNode:
        """Tạo module node"""
        modname = module_data.get('modname', 'unknown')
        node_type = self.MODULE_TYPE_MAPPING.get(modname, NodeType.MODULE)
        
        return HierarchyNode(
            id=module_data['id'],
            name=module_data['name'],
            type=node_type,
            level=parent_level + 1,
            metadata={
                'modname': modname,
                'instance': module_data.get('instance'),
                'url': module_data.get('url'),
                'visible': module_data.get('visible', 1),
                'purpose': module_data.get('purpose'),
                'completion': module_data.get('completion', 0),
                'availability': module_data.get('availability'),
                'indent': module_data.get('indent', 0),
                'contextid': module_data.get('contextid'),
                'contents': module_data.get('contents', []),
                'completiondata': module_data.get('completiondata', {})
            }
        )
    
    def _extract_subsection_id(self, module_data: Dict) -> Optional[int]:
        """Extract subsection ID từ customdata"""
        try:
            customdata = module_data.get('customdata', '{}')
            if isinstance(customdata, str):
                customdata = json.loads(customdata)
            section_id = customdata.get('sectionid')
            return int(section_id) if section_id else None
        except Exception as e:
            logger.warning(f"Failed to extract subsection ID: {e}")
            return None
    
    def _get_stats(self) -> str:
        """Lấy thống kê cây"""
        if not self.root:
            return "Empty tree"
        
        stats = {}
        for node_type in NodeType:
            count = len(self.root.get_all_nodes(node_type))
            if count > 0:
                stats[node_type.value] = count
        
        max_depth = self._get_max_depth(self.root)
        return f"{stats}, max_depth={max_depth}"
    
    def _get_max_depth(self, node: HierarchyNode) -> int:
        """Tính độ sâu tối đa"""
        if not node.children:
            return node.level
        return max(self._get_max_depth(child) for child in node.children)
    
    def get_learning_path(self, node_id: int) -> Optional[List[str]]:
        """Lấy learning path từ root đến một node cụ thể"""
        if not self.root:
            return None
        
        node = self.root.find_node_by_id(node_id)
        if not node:
            return None
        
        return node.get_path()
    
    def get_all_activities(self) -> List[HierarchyNode]:
        """Lấy tất cả activities"""
        if not self.root:
            return []
        return self.root.get_all_nodes(NodeType.ACTIVITY)
    
    def get_all_resources(self) -> List[HierarchyNode]:
        """Lấy tất cả resources"""
        if not self.root:
            return []
        return self.root.get_all_nodes(NodeType.RESOURCE)
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Phân tích cấu trúc khóa học"""
        if not self.root:
            return {}
        
        all_nodes = self.root.get_all_nodes()
        
        # Thống kê theo type
        type_counts = {}
        for node_type in NodeType:
            type_counts[node_type.value] = len(
                [n for n in all_nodes if n.type == node_type]
            )
        
        # Phân tích activities
        activities = self.get_all_activities()
        activity_types = {}
        for activity in activities:
            modname = activity.metadata.get('modname', 'unknown')
            activity_types[modname] = activity_types.get(modname, 0) + 1
        
        # Phân tích completion
        activities_with_completion = len([
            a for a in activities 
            if a.metadata.get('completion', 0) > 0
        ])
        
        return {
            'total_nodes': len(all_nodes),
            'max_depth': self._get_max_depth(self.root),
            'node_type_counts': type_counts,
            'activity_types': activity_types,
            'activities_with_completion': activities_with_completion,
            'completion_rate': (
                activities_with_completion / len(activities) * 100 
                if activities else 0
            )
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export cây phân cấp thành dictionary"""
        if not self.root:
            return {}
        return self.root.to_dict()
    
    def to_json(self, indent: int = 2) -> str:
        """Export cây phân cấp thành JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# Convenience function
def convert_moodle_structure(moodle_data: List[Dict], course_name: str = "Moodle Course") -> Dict[str, Any]:
    """
    Quick function to convert Moodle structure
    
    Args:
        moodle_data: Raw Moodle course contents
        course_name: Name of the course
        
    Returns:
        Hierarchical structure as dictionary
    """
    converter = MoodleStructureConverter(course_name=course_name)
    converter.convert(moodle_data)
    return converter.to_dict()
