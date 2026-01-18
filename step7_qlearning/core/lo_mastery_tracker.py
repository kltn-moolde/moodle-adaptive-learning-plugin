#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LO Mastery Tracker - Track và dự đoán điểm midterm
===================================================
Class để track LO mastery của học sinh và dự đoán điểm midterm
"""

import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import defaultdict
import numpy as np


class LOMasteryTracker:
    """
    Track LO mastery và dự đoán điểm midterm
    
    Features:
    - Track mastery cho từng LO của từng học sinh
    - Dự đoán điểm midterm dựa trên LO mastery và weights
    - So sánh các LO với nhau
    - Tính điểm tăng dự kiến khi học LO
    """
    
    def __init__(
        self,
        midterm_weights_path: str = 'data/midterm_lo_weights.json',
        po_lo_path: str = 'data/Po_Lo.json',
        course_id: Optional[int] = None
    ):
        """
        Initialize LO Mastery Tracker
        
        Args:
            midterm_weights_path: Path to midterm_lo_weights.json (deprecated - use course_id instead)
            po_lo_path: Path to Po_Lo.json (deprecated - use course_id instead)
            course_id: Course ID để load PO/LO và weights từ file course-specific (optional)
        """
        # Load midterm weights - support both old way and new way
        if course_id is not None:
            # Use services
            from services.business.po_lo import POLOService
            from services.business.midterm_weights import MidtermWeightsService
            from pathlib import Path
            
            data_dir = Path(po_lo_path).parent if Path(po_lo_path).is_absolute() else Path('data')
            po_lo_service = POLOService(data_dir=str(data_dir))
            midterm_weights_service = MidtermWeightsService(data_dir=str(data_dir))
            
            try:
                midterm_data = midterm_weights_service.get_weights(course_id=course_id)
                po_lo_data = po_lo_service.get_po_lo(course_id=course_id)
            except FileNotFoundError:
                # Fallback to default files
                with open(midterm_weights_path, 'r', encoding='utf-8') as f:
                    midterm_data = json.load(f)
                with open(po_lo_path, 'r', encoding='utf-8') as f:
                    po_lo_data = json.load(f)
        else:
            # Old way: use file paths
            with open(midterm_weights_path, 'r', encoding='utf-8') as f:
                midterm_data = json.load(f)
            with open(po_lo_path, 'r', encoding='utf-8') as f:
                po_lo_data = json.load(f)
        
        self.midterm_weights = midterm_data['lo_weights']
        self.total_marks = midterm_data.get('total_marks', 20)
        self.midterm_quiz_id = midterm_data.get('midterm_quiz_id', 107)
        
        # Load LO info
        self.lo_info = {}
        for lo in po_lo_data['learning_outcomes']:
            self.lo_info[lo['id']] = {
                'description': lo.get('description', ''),
                'activity_ids': lo.get('activity_ids', [])
            }
        
        # Track mastery per student: {student_id: {lo_id: mastery}}
        self.mastery_cache: Dict[int, Dict[str, float]] = defaultdict(dict)
        
        # Track history: {student_id: [(lo_id, old_mastery, new_mastery, activity_id, timestamp)]}
        self.mastery_history: Dict[int, List[Dict]] = defaultdict(list)
        
        # Initialize all LOs with default mastery (0.4 = 40%)
        self.default_mastery = 0.4
    
    def initialize_student(self, student_id: int):
        """Initialize LO mastery for a new student"""
        if student_id not in self.mastery_cache:
            self.mastery_cache[student_id] = {
                lo_id: self.default_mastery 
                for lo_id in self.midterm_weights.keys()
            }
    
    def update_mastery(
        self,
        student_id: int,
        lo_id: str,
        new_mastery: float,
        activity_id: Optional[int] = None,
        timestamp: Optional[int] = None
    ):
        """
        Update LO mastery for a student
        
        Args:
            student_id: Student ID
            lo_id: Learning Outcome ID
            new_mastery: New mastery value (0-1)
            activity_id: Activity ID that caused the update
            timestamp: Step/timestamp of update
        """
        self.initialize_student(student_id)
        
        old_mastery = self.mastery_cache[student_id].get(lo_id, self.default_mastery)
        new_mastery = np.clip(new_mastery, 0.0, 1.0)
        
        # Update cache
        self.mastery_cache[student_id][lo_id] = new_mastery
        
        # Record history
        self.mastery_history[student_id].append({
            'lo_id': lo_id,
            'old_mastery': float(old_mastery),
            'new_mastery': float(new_mastery),
            'delta': float(new_mastery - old_mastery),
            'activity_id': activity_id,
            'timestamp': timestamp
        })
    
    def get_mastery(self, student_id: int, lo_id: Optional[str] = None) -> Dict[str, float]:
        """
        Get LO mastery for a student
        
        Args:
            student_id: Student ID
            lo_id: Specific LO ID (optional)
            
        Returns:
            Dict of {lo_id: mastery} or single mastery value
        """
        self.initialize_student(student_id)
        
        if lo_id:
            return {lo_id: self.mastery_cache[student_id].get(lo_id, self.default_mastery)}
        else:
            return dict(self.mastery_cache[student_id])
    
    def get_weak_los(
        self,
        student_id: int,
        threshold: float = 0.6
    ) -> List[Tuple[str, float, float]]:
        """
        Get weak LOs (mastery < threshold) sorted by priority
        
        Args:
            student_id: Student ID
            threshold: Mastery threshold (default: 0.6)
            
        Returns:
            List of (lo_id, mastery, midterm_weight) sorted by priority
        """
        mastery = self.get_mastery(student_id)
        
        weak_los = []
        for lo_id, mastery_value in mastery.items():
            if mastery_value < threshold:
                weight = self.midterm_weights.get(lo_id, 0.0)
                # Priority = (1 - mastery) * weight (higher is better)
                priority = (1.0 - mastery_value) * weight
                weak_los.append((lo_id, mastery_value, weight, priority))
        
        # Sort by priority (descending)
        weak_los.sort(key=lambda x: x[3], reverse=True)
        
        return [(lo_id, mastery, weight) for lo_id, mastery, weight, _ in weak_los]
    
    def predict_midterm_score(
        self,
        student_id: int,
        use_current_mastery: bool = True
    ) -> Dict[str, any]:
        """
        Dự đoán điểm midterm dựa trên LO mastery
        
        Args:
            student_id: Student ID
            use_current_mastery: Use current mastery or assume all LOs at 1.0
            
        Returns:
            Dict với predicted score, breakdown by LO, và expected improvement
        """
        if use_current_mastery:
            mastery = self.get_mastery(student_id)
        else:
            # Assume all LOs mastered
            mastery = {lo_id: 1.0 for lo_id in self.midterm_weights.keys()}
        
        # Calculate score per LO
        lo_scores = {}
        total_score = 0.0
        
        for lo_id, weight in self.midterm_weights.items():
            lo_mastery = mastery.get(lo_id, self.default_mastery)
            # Score = mastery * weight * total_marks
            lo_score = lo_mastery * weight * self.total_marks
            lo_scores[lo_id] = {
                'mastery': float(lo_mastery),
                'weight': weight,
                'score': float(lo_score),
                'description': self.lo_info.get(lo_id, {}).get('description', '')
            }
            total_score += lo_score
        
        # Calculate expected improvement if all weak LOs improved to threshold
        weak_los = self.get_weak_los(student_id, threshold=0.6)
        potential_improvement = 0.0
        
        for lo_id, current_mastery, weight in weak_los:
            # Assume improvement to 0.8 (good level)
            target_mastery = 0.8
            improvement = (target_mastery - current_mastery) * weight * self.total_marks
            potential_improvement += improvement
        
        return {
            'predicted_score': float(total_score),
            'predicted_percentage': float(total_score / self.total_marks * 100),
            'total_marks': self.total_marks,
            'lo_breakdown': lo_scores,
            'weak_los_count': len(weak_los),
            'potential_improvement': float(potential_improvement),
            'potential_score': float(total_score + potential_improvement),
            'potential_percentage': float((total_score + potential_improvement) / self.total_marks * 100)
        }
    
    def calculate_expected_score_increase(
        self,
        student_id: int,
        lo_id: str,
        target_mastery: float = 0.8
    ) -> Dict[str, float]:
        """
        Tính điểm tăng dự kiến khi học một LO đến target mastery
        
        Args:
            student_id: Student ID
            lo_id: Learning Outcome ID
            target_mastery: Target mastery level (default: 0.8)
            
        Returns:
            Dict với expected score increase và breakdown
        """
        current_mastery = self.get_mastery(student_id, lo_id)[lo_id]
        weight = self.midterm_weights.get(lo_id, 0.0)
        
        # Current contribution
        current_contribution = current_mastery * weight * self.total_marks
        
        # Target contribution
        target_contribution = target_mastery * weight * self.total_marks
        
        # Expected increase
        score_increase = target_contribution - current_contribution
        
        return {
            'lo_id': lo_id,
            'current_mastery': float(current_mastery),
            'target_mastery': float(target_mastery),
            'weight': weight,
            'current_contribution': float(current_contribution),
            'target_contribution': float(target_contribution),
            'expected_increase': float(score_increase),
            'description': self.lo_info.get(lo_id, {}).get('description', '')
        }
    
    def compare_los(self, student_id: int) -> Dict[str, any]:
        """
        So sánh các LO với nhau về mastery và importance
        
        Args:
            student_id: Student ID
            
        Returns:
            Dict với comparison data
        """
        mastery = self.get_mastery(student_id)
        
        # Group by mastery level
        mastery_groups = {
            'excellent': [],  # >= 0.8
            'good': [],       # 0.6-0.8
            'weak': [],       # 0.4-0.6
            'very_weak': []   # < 0.4
        }
        
        for lo_id, mastery_value in mastery.items():
            weight = self.midterm_weights.get(lo_id, 0.0)
            priority = (1.0 - mastery_value) * weight
            
            lo_data = {
                'lo_id': lo_id,
                'mastery': float(mastery_value),
                'weight': weight,
                'priority': float(priority),
                'description': self.lo_info.get(lo_id, {}).get('description', '')
            }
            
            if mastery_value >= 0.8:
                mastery_groups['excellent'].append(lo_data)
            elif mastery_value >= 0.6:
                mastery_groups['good'].append(lo_data)
            elif mastery_value >= 0.4:
                mastery_groups['weak'].append(lo_data)
            else:
                mastery_groups['very_weak'].append(lo_data)
        
        # Sort each group by priority
        for group in mastery_groups.values():
            group.sort(key=lambda x: x['priority'], reverse=True)
        
        # Calculate statistics
        all_masteries = list(mastery.values())
        
        return {
            'student_id': student_id,
            'mastery_groups': mastery_groups,
            'statistics': {
                'total_los': len(mastery),
                'avg_mastery': float(np.mean(all_masteries)),
                'min_mastery': float(np.min(all_masteries)),
                'max_mastery': float(np.max(all_masteries)),
                'std_mastery': float(np.std(all_masteries)),
                'excellent_count': len(mastery_groups['excellent']),
                'good_count': len(mastery_groups['good']),
                'weak_count': len(mastery_groups['weak']),
                'very_weak_count': len(mastery_groups['very_weak'])
            }
        }
    
    def get_mastery_history(self, student_id: int) -> List[Dict]:
        """Get mastery history for a student"""
        return self.mastery_history.get(student_id, [])
    
    def get_summary(self, student_id: int) -> Dict[str, any]:
        """
        Get comprehensive summary for a student
        
        Returns:
            Dict với tất cả thông tin về LO mastery
        """
        mastery = self.get_mastery(student_id)
        weak_los = self.get_weak_los(student_id)
        midterm_prediction = self.predict_midterm_score(student_id)
        comparison = self.compare_los(student_id)
        
        return {
            'student_id': student_id,
            'current_mastery': mastery,
            'weak_los': [
                {
                    'lo_id': lo_id,
                    'mastery': float(mastery_value),
                    'weight': float(weight),
                    'description': self.lo_info.get(lo_id, {}).get('description', '')
                }
                for lo_id, mastery_value, weight in weak_los
            ],
            'midterm_prediction': midterm_prediction,
            'comparison': comparison,
            'history_count': len(self.mastery_history.get(student_id, []))
        }

