#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PO/LO Service - Quản lý PO/LO mappings từ JSON files
====================================================
Hỗ trợ multi-course với file riêng cho mỗi course
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import glob


class POLOService:
    """
    Service để đọc/ghi PO/LO mappings từ JSON files
    
    File naming:
    - data/Po_Lo_{course_id}.json - Cho course cụ thể
    - data/Po_Lo.json - Default/fallback
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize PO/LO Service
        
        Args:
            data_dir: Directory chứa JSON files (default: "data")
        """
        self.data_dir = Path(data_dir)
        self.default_file = self.data_dir / "Po_Lo.json"
    
    def _get_file_path(self, course_id: Optional[int] = None) -> Path:
        """
        Get file path cho course_id
        
        Args:
            course_id: Course ID (None = default)
            
        Returns:
            Path to JSON file
        """
        if course_id is not None:
            course_file = self.data_dir / f"Po_Lo_{course_id}.json"
            if course_file.exists():
                return course_file
        
        # Fallback to default
        return self.default_file
    
    def get_po_lo(self, course_id: Optional[int] = None) -> Dict:
        """
        Lấy PO/LO data cho course
        
        Args:
            course_id: Course ID (None = default)
            
        Returns:
            Dict với PO/LO data
            
        Raises:
            FileNotFoundError: Nếu không tìm thấy file
        """
        file_path = self._get_file_path(course_id)
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"PO/LO file not found: {file_path}. "
                f"Tried course_id={course_id}, fallback={self.default_file}"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_po_lo(self, course_id: int, data: Dict) -> bool:
        """
        Lưu PO/LO data cho course
        
        Args:
            course_id: Course ID
            data: PO/LO data dict
            
        Returns:
            True nếu thành công
        """
        file_path = self.data_dir / f"Po_Lo_{course_id}.json"
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def list_available_courses(self) -> List[int]:
        """
        List tất cả courses có PO/LO file
        
        Returns:
            List of course IDs
        """
        pattern = str(self.data_dir / "Po_Lo_*.json")
        files = glob.glob(pattern)
        
        course_ids = []
        for file_path in files:
            # Extract course_id from filename: Po_Lo_{course_id}.json
            filename = Path(file_path).stem  # "Po_Lo_5"
            try:
                course_id = int(filename.split('_')[-1])
                course_ids.append(course_id)
            except (ValueError, IndexError):
                continue
        
        return sorted(course_ids)
    
    def file_exists(self, course_id: Optional[int] = None) -> bool:
        """
        Check xem file có tồn tại không
        
        Args:
            course_id: Course ID (None = check default)
            
        Returns:
            True nếu file tồn tại
        """
        file_path = self._get_file_path(course_id)
        return file_path.exists()

