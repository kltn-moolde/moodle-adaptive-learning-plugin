#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-table Adapter - Convert between action indices and module IDs
===============================================================
Adapter để convert giữa action indices (0-14) và module IDs (46-83)
cho compatibility với Q-table cũ
"""

from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class QTableAdapter:
    """
    Adapter để convert giữa action indices và module IDs
    
    Q-table best model dùng module IDs (46, 47, ...) làm action keys
    Code mới dùng action indices (0-14)
    """
    
    def __init__(self, course_structure_path: str = 'data/course_structure.json'):
        """
        Initialize adapter
        
        Args:
            course_structure_path: Path to course_structure.json
        """
        self.course_structure_path = Path(course_structure_path)
        self.module_ids: List[int] = []
        self.index_to_module_id: Dict[int, int] = {}  # action_index -> module_id
        self.module_id_to_index: Dict[int, int] = {}  # module_id -> action_index
        
        self._load_mappings()
    
    def _load_mappings(self):
        """Load module ID mappings from course structure"""
        try:
            with open(self.course_structure_path, 'r', encoding='utf-8') as f:
                course = json.load(f)
            
            # Extract all module IDs
            module_ids = []
            for section in course.get('contents', []):
                for module in section.get('modules', []):
                    module_id = module.get('id')
                    if module_id and module.get('visible', 0) == 1:
                        module_ids.append(module_id)
            
            # Sort và map
            module_ids = sorted(module_ids)
            self.module_ids = module_ids
            
            # Create mappings (first 15 modules map to action indices 0-14)
            # Note: This is a simplified mapping - in reality, we need to map
            # based on action type and time context, not just module order
            for idx, module_id in enumerate(module_ids[:15]):
                self.index_to_module_id[idx] = module_id
                self.module_id_to_index[module_id] = idx
            
        except Exception as e:
            print(f"Warning: Failed to load course structure: {e}")
            # Fallback: use default mapping based on common module IDs
            default_modules = [46, 47, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
            for idx, module_id in enumerate(default_modules):
                self.index_to_module_id[idx] = module_id
                self.module_id_to_index[module_id] = idx
    
    def action_index_to_module_id(self, action_index: int) -> Optional[int]:
        """Convert action index to module ID"""
        return self.index_to_module_id.get(action_index)
    
    def module_id_to_action_index(self, module_id: int) -> Optional[int]:
        """Convert module ID to action index"""
        return self.module_id_to_index.get(module_id)
    
    def convert_available_actions(
        self,
        action_indices: List[int],
        to_module_ids: bool = True
    ) -> List[int]:
        """
        Convert list of action indices to module IDs or vice versa
        
        Args:
            action_indices: List of action indices
            to_module_ids: If True, convert to module IDs; else convert to indices
            
        Returns:
            List of converted IDs
        """
        if to_module_ids:
            return [self.index_to_module_id.get(idx, idx) for idx in action_indices]
        else:
            return [self.module_id_to_index.get(idx, idx) for idx in action_indices]
    
    def convert_recommendations(
        self,
        recommendations: List[Tuple[int, float]],
        from_module_ids: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Convert recommendations from module IDs to action indices or vice versa
        
        Args:
            recommendations: List of (id, q_value) tuples
            from_module_ids: If True, convert from module IDs to indices
            
        Returns:
            List of converted (id, q_value) tuples
        """
        converted = []
        for action_id, q_value in recommendations:
            if from_module_ids:
                # Convert module ID to action index
                action_index = self.module_id_to_action_index(action_id)
                if action_index is not None:
                    converted.append((action_index, q_value))
            else:
                # Convert action index to module ID
                module_id = self.action_index_to_module_id(action_id)
                if module_id is not None:
                    converted.append((module_id, q_value))
        
        return converted

