#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activity Recommender - Gợi ý bài học cụ thể dựa trên LO yếu
==========================================================
Chọn activity phù hợp để cải thiện LO mastery
"""

import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import numpy as np


class ActivityRecommender:
    """
    Gợi ý activity cụ thể dựa trên:
    - Action type (view_content, attempt_quiz, etc.)
    - LO mastery (ưu tiên LO yếu)
    - Module hiện tại
    - Time context (past, current, future)
    """
    
    def __init__(
        self,
        po_lo_path: str = 'data/Po_Lo.json',
        course_structure_path: str = 'data/course_structure.json'
    ):
        """
        Initialize recommender
        
        Args:
            po_lo_path: Path to Po_Lo.json (LO -> activities mapping)
            course_structure_path: Path to course structure
        """
        # Load LO mappings
        with open(po_lo_path, 'r', encoding='utf-8') as f:
            po_lo_data = json.load(f)
        
        # Build mappings
        self.lo_to_activities: Dict[str, List[int]] = {}  # LO -> [activity_ids]
        self.activity_to_los: Dict[int, List[str]] = defaultdict(list)  # activity_id -> [LOs]
        self.lo_info: Dict[str, Dict] = {}  # LO -> {description, ...}
        
        for lo in po_lo_data['learning_outcomes']:
            lo_id = lo['id']
            activity_ids = lo.get('activity_ids', [])
            
            self.lo_to_activities[lo_id] = activity_ids
            self.lo_info[lo_id] = {
                'description': lo.get('description', ''),
                'mapped_to': lo.get('mapped_to', [])
            }
            
            for activity_id in activity_ids:
                self.activity_to_los[activity_id].append(lo_id)
        
        # Initialize activity_info (will be populated from course_structure or Po_Lo)
        self.activity_info: Dict[int, Dict] = {}
        
        # Try loading from course_structure.json first
        loaded_from_course_structure = False
        try:
            with open(course_structure_path, 'r', encoding='utf-8') as f:
                course_data = json.load(f)
            
            for module in course_data.get('modules', []):
                module_idx = module.get('module_index', 0)
                
                for section in module.get('sections', []):
                    for activity in section.get('activities', []):
                        activity_id = activity.get('id')
                        if activity_id:
                            self.activity_info[activity_id] = {
                                'id': activity_id,
                                'name': activity.get('name', f'Activity {activity_id}'),
                                'type': activity.get('type', 'unknown'),
                                'module_idx': module_idx,
                                'difficulty': self._infer_difficulty(activity.get('name', ''))
                            }
            loaded_from_course_structure = True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            pass  # Will build from Po_Lo instead
        
        # Fallback: build from Po_Lo.json
        if not loaded_from_course_structure or len(self.activity_info) == 0:
            self._build_activity_info_from_po_lo(po_lo_data)
    
    def _infer_difficulty(self, activity_name: str) -> str:
        """Infer difficulty from activity name"""
        name_lower = activity_name.lower()
        if 'easy' in name_lower:
            return 'easy'
        elif 'medium' in name_lower:
            return 'medium'
        elif 'hard' in name_lower:
            return 'hard'
        return 'medium'
    
    def _build_activity_info_from_po_lo(self, po_lo_data: Dict):
        """Build activity info from Po_Lo.json when course_structure is not available"""
        for lo in po_lo_data['learning_outcomes']:
            activity_ids = lo.get('activity_ids', [])
            related_activities = lo.get('related_activities', [])
            
            for i, activity_id in enumerate(activity_ids):
                if activity_id not in self.activity_info:
                    activity_name = related_activities[i] if i < len(related_activities) else f"Activity {activity_id}"
                    
                    # Infer module from activity ID ranges
                    module_idx = (activity_id - 54) // 8 if activity_id >= 54 else 0
                    
                    # Infer type from name
                    name_lower = activity_name.lower()
                    if 'quiz' in name_lower or 'kiểm tra' in name_lower or 'trắc nghiệm' in name_lower:
                        activity_type = 'quiz'
                    elif 'assignment' in name_lower or 'bài tập' in name_lower:
                        activity_type = 'assignment'
                    elif 'forum' in name_lower or 'diễn đàn' in name_lower or 'thảo luận' in name_lower:
                        activity_type = 'forum'
                    elif 'video' in name_lower:
                        activity_type = 'resource'
                    elif 'sgk' in name_lower:
                        activity_type = 'page'
                    else:
                        activity_type = 'resource'
                    
                    self.activity_info[activity_id] = {
                        'id': activity_id,
                        'name': activity_name,
                        'type': activity_type,
                        'module_idx': module_idx,
                        'difficulty': self._infer_difficulty(activity_name)
                    }
    
    def recommend_activity(
        self,
        action: Tuple[str, str],  # (action_type, time_context)
        module_idx: int,
        lo_mastery: Dict[str, float],
        previous_activities: List[int] = None,
        top_k: int = 3,
        cluster_id: int = 2
    ) -> Dict:
        """
        Gợi ý activity cụ thể cho action
        
        Args:
            action: (action_type, time_context)
            module_idx: Current module index
            lo_mastery: Dict of LO mastery scores
            previous_activities: List of recently done activities (to avoid repetition)
            top_k: Return top-k recommendations
            
        Returns:
            Dict with:
            - activity_id: Recommended activity ID
            - activity_name: Activity name
            - weak_los: List of weak LOs this activity targets
            - reason: Explanation for recommendation
            - alternatives: List of alternative activities
        """
        action_type, time_context = action
        
        # Find weak LOs (mastery < 0.6)
        weak_los = [(lo_id, mastery) for lo_id, mastery in lo_mastery.items() if mastery < 0.6]
        weak_los.sort(key=lambda x: x[1])  # Sort by mastery (weakest first)
        
        # If no weak LOs, target LOs with lowest mastery
        if not weak_los:
            weak_los = sorted(lo_mastery.items(), key=lambda x: x[1])[:3]
        
        # Find candidate activities
        candidates = []
        
        for lo_id, mastery in weak_los[:5]:  # Focus on 5 weakest LOs
            activity_ids = self.lo_to_activities.get(lo_id, [])
            
            for activity_id in activity_ids:
                # Filter by action type
                if not self._matches_action_type(activity_id, action_type):
                    continue
                
                # Filter by time context
                if not self._matches_time_context(activity_id, module_idx, time_context):
                    continue
                
                # Skip recent activities
                if previous_activities and activity_id in previous_activities[-5:]:
                    continue
                
                # Calculate priority score
                score = self._calculate_priority(activity_id, lo_id, mastery, module_idx)
                
                candidates.append({
                    'activity_id': activity_id,
                    'lo_id': lo_id,
                    'lo_mastery': mastery,
                    'score': score
                })
        
        # If no candidates, use fallback
        if not candidates:
            return self._fallback_recommendation(action, module_idx, lo_mastery)
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Get top recommendation
        top_candidate = candidates[0]
        activity_id = top_candidate['activity_id']
        
        # Build recommendation
        activity_info = self.activity_info.get(activity_id, {})
        activity_name = activity_info.get('name', f'Activity {activity_id}')
        
        # Find all weak LOs targeted by this activity
        targeted_los = [
            (lo_id, lo_mastery.get(lo_id, 0.0))
            for lo_id in self.activity_to_los.get(activity_id, [])
            if lo_mastery.get(lo_id, 0.0) < 0.6
        ]
        targeted_los.sort(key=lambda x: x[1])
        
        # Build reason
        reason = self._build_reason(action_type, targeted_los, activity_info)
        
        # Get alternatives
        alternatives = [
            {
                'activity_id': c['activity_id'],
                'activity_name': self.activity_info.get(c['activity_id'], {}).get('name', f"Activity {c['activity_id']}"),
                'targets_lo': c['lo_id'],
                'lo_mastery': c['lo_mastery']
            }
            for c in candidates[1:top_k]
        ]
        
        return {
            'activity_id': activity_id,
            'activity_name': activity_name,
            'weak_los': targeted_los,
            'reason': reason,
            'alternatives': alternatives,
            'difficulty': activity_info.get('difficulty', 'medium')
        }
    
    def _matches_action_type(self, activity_id: int, action_type: str) -> bool:
        """Check if activity matches action type"""
        activity_info = self.activity_info.get(activity_id, {})
        activity_type = activity_info.get('type', '').lower()
        
        # Mapping action types to activity types
        if 'quiz' in action_type:
            return 'quiz' in activity_type or 'test' in activity_type or 'trắc nghiệm' in activity_type.lower()
        elif 'assignment' in action_type:
            return 'assignment' in activity_type or 'bài tập' in activity_type.lower()
        elif 'content' in action_type or 'view' in action_type:
            return 'page' in activity_type or 'resource' in activity_type or 'sgk' in activity_type.lower() or 'video' in activity_type.lower()
        elif 'forum' in action_type:
            return 'forum' in activity_type
        
        # Default: allow all
        return True
    
    def _matches_time_context(self, activity_id: int, current_module_idx: int, time_context: str) -> bool:
        """Check if activity matches time context"""
        activity_info = self.activity_info.get(activity_id, {})
        activity_module = activity_info.get('module_idx', current_module_idx)
        
        if time_context == 'past':
            return activity_module < current_module_idx
        elif time_context == 'current':
            return activity_module == current_module_idx
        elif time_context == 'future':
            return activity_module > current_module_idx
        
        return True
    
    def _calculate_priority(
        self,
        activity_id: int,
        lo_id: str,
        lo_mastery: float,
        current_module_idx: int
    ) -> float:
        """
        Calculate priority score for activity
        
        Higher score = better recommendation
        """
        score = 0.0
        
        # Factor 1: LO weakness (lower mastery = higher priority)
        score += (1.0 - lo_mastery) * 10.0
        
        # Factor 2: Activity difficulty (prefer medium for weak students)
        activity_info = self.activity_info.get(activity_id, {})
        difficulty = activity_info.get('difficulty', 'medium')
        
        if lo_mastery < 0.4:
            # Very weak: prefer easy
            if difficulty == 'easy':
                score += 3.0
            elif difficulty == 'medium':
                score += 1.0
        elif lo_mastery < 0.6:
            # Weak: prefer medium
            if difficulty == 'medium':
                score += 3.0
            elif difficulty == 'easy':
                score += 1.5
        
        # Factor 3: Module relevance (prefer current module)
        activity_module = activity_info.get('module_idx', current_module_idx)
        if activity_module == current_module_idx:
            score += 2.0
        elif abs(activity_module - current_module_idx) == 1:
            score += 1.0
        
        # Factor 4: Number of weak LOs targeted by this activity
        n_weak_los_targeted = sum(
            1 for lo in self.activity_to_los.get(activity_id, [])
            if lo_id == lo or lo_mastery < 0.6
        )
        score += n_weak_los_targeted * 1.5
        
        return score
    
    def _build_reason(
        self,
        action_type: str,
        targeted_los: List[Tuple[str, float]],
        activity_info: Dict,
        cluster_id: int = 2,
        current_lo_mastery: Dict[str, float] = None
    ) -> str:
        """Build explanation for recommendation with LO improvement prediction"""
        if not targeted_los:
            return f"Hoạt động phù hợp với {action_type}"
        
        # Get weakest LO
        weakest_lo, weakest_mastery = targeted_los[0]
        lo_desc = self.lo_info.get(weakest_lo, {}).get('description', weakest_lo)
        lo_desc_short = lo_desc[:60] + '...' if len(lo_desc) > 60 else lo_desc
        
        difficulty = activity_info.get('difficulty', 'medium')
        difficulty_vn = {'easy': 'dễ', 'medium': 'trung bình', 'hard': 'khó'}.get(difficulty, difficulty)
        
        # Predict LO mastery improvement
        improvement_prediction = self._predict_lo_improvement(
            lo_id=weakest_lo,
            current_mastery=weakest_mastery,
            action_type=action_type,
            cluster_id=cluster_id,
            difficulty=difficulty
        )
        
        reason = f"Cải thiện {weakest_lo} (hiện tại {weakest_mastery:.1%})"
        
        if improvement_prediction:
            predicted_mastery = weakest_mastery + improvement_prediction
            improvement_pct = improvement_prediction * 100
            reason += f" → dự kiến tăng {improvement_pct:.1f}% (lên {predicted_mastery:.1%})"
        
        reason += f": {lo_desc_short}"
        
        if len(targeted_los) > 1:
            reason += f" | Đồng thời rèn luyện {len(targeted_los)-1} LO khác"
        
        reason += f" | Độ khó: {difficulty_vn}"
        
        return reason
    
    def _predict_lo_improvement(
        self,
        lo_id: str,
        current_mastery: float,
        action_type: str,
        cluster_id: int,
        difficulty: str = 'medium'
    ) -> float:
        """
        Predict LO mastery improvement after completing activity
        
        Args:
            lo_id: LO ID
            current_mastery: Current mastery (0-1)
            action_type: Action type (view_content, attempt_quiz, etc.)
            cluster_id: Student cluster ID
            difficulty: Activity difficulty
            
        Returns:
            Predicted improvement (delta mastery, 0-1)
        """
        # Determine cluster level
        cluster_level = 'medium'
        if cluster_id in [0]:
            cluster_level = 'weak'
        elif cluster_id in [2, 4]:
            cluster_level = 'strong'
        
        # Learning rate α depends on cluster (weak=0.3, medium=0.2, strong=0.15)
        alpha = {'weak': 0.3, 'medium': 0.2, 'strong': 0.15}.get(cluster_level, 0.2)
        
        # Predict target mastery based on action type and difficulty
        if 'quiz' in action_type or 'assignment' in action_type:
            # Assessment activities: higher target if successful
            if difficulty == 'easy':
                target_mastery = 0.75
            elif difficulty == 'medium':
                target_mastery = 0.70
            else:  # hard
                target_mastery = 0.65
        elif 'content' in action_type or 'view' in action_type:
            # Content viewing: moderate improvement
            target_mastery = 0.60
        elif 'forum' in action_type:
            # Forum: collaborative learning, moderate improvement
            target_mastery = 0.55
        else:
            # Default
            target_mastery = 0.60
        
        # Adjust target based on current mastery
        # If already high mastery, improvement is smaller
        if current_mastery > 0.7:
            target_mastery = min(target_mastery, current_mastery + 0.15)
        elif current_mastery < 0.3:
            # Very weak: can improve more
            target_mastery = max(target_mastery, current_mastery + 0.20)
        
        # Calculate predicted improvement using EMA formula
        # new_mastery = old + α × (target - old)
        predicted_improvement = alpha * (target_mastery - current_mastery)
        
        # Clamp to reasonable range
        predicted_improvement = max(0.05, min(0.30, predicted_improvement))
        
        return predicted_improvement
    
    def _fallback_recommendation(self, action: Tuple[str, str], module_idx: int, lo_mastery: Dict[str, float] = None) -> Dict:
        """Fallback when no specific recommendation found"""
        action_type, time_context = action
        
        # Try to find any activity with weak LOs
        if lo_mastery:
            weak_los = [(lo_id, mastery) for lo_id, mastery in lo_mastery.items() if mastery < 0.6]
            weak_los.sort(key=lambda x: x[1])  # Sort by mastery (weakest first)
            
            # Try to find activity for weakest LO
            for lo_id, mastery in weak_los[:3]:
                activity_ids = self.lo_to_activities.get(lo_id, [])
                for activity_id in activity_ids[:5]:
                    activity_info = self.activity_info.get(activity_id, {})
                    # Check if matches action type
                    if self._matches_action_type(activity_id, action_type):
                        # Found suitable activity
                        activity_name = activity_info.get('name', f'Activity {activity_id}')
                        targeted_los = [(lo_id, mastery)]
                        reason = self._build_reason(action_type, targeted_los, activity_info)
                        
                        return {
                            'activity_id': activity_id,
                            'activity_name': activity_name,
                            'weak_los': targeted_los,
                            'reason': reason,
                            'alternatives': [],
                            'difficulty': activity_info.get('difficulty', 'medium')
                        }
        
        # No suitable activity found - use simple mapping
        base_id = 54 + module_idx * 8
        
        if 'quiz' in action_type:
            activity_id = base_id + 2
        elif 'assignment' in action_type:
            activity_id = base_id + 5
        elif 'forum' in action_type:
            activity_id = base_id + 7
        else:
            activity_id = base_id
        
        activity_info = self.activity_info.get(activity_id, {})
        
        # Try to find LOs for this activity
        targeted_los = []
        if lo_mastery:
            activity_los = self.activity_to_los.get(activity_id, [])
            targeted_los = [
                (lo_id, lo_mastery.get(lo_id, 0.0))
                for lo_id in activity_los
                if lo_mastery.get(lo_id, 0.0) < 0.6
            ]
            targeted_los.sort(key=lambda x: x[1])
        
        reason = f'Hoạt động tiêu chuẩn cho module {module_idx + 1}'
        if targeted_los:
            reason = self._build_reason(action_type, targeted_los, activity_info)
        
        return {
            'activity_id': activity_id,
            'activity_name': activity_info.get('name', f'Activity {activity_id}'),
            'weak_los': targeted_los,
            'reason': reason,
            'alternatives': [],
            'difficulty': activity_info.get('difficulty', 'medium')
        }
    
    def get_weak_lo_summary(self, lo_mastery: Dict[str, float], threshold: float = 0.6) -> str:
        """
        Get summary of weak LOs
        
        Args:
            lo_mastery: Dict of LO mastery scores
            threshold: Mastery threshold for "weak"
            
        Returns:
            Summary string
        """
        weak_los = [(lo_id, mastery) for lo_id, mastery in lo_mastery.items() if mastery < threshold]
        weak_los.sort(key=lambda x: x[1])
        
        if not weak_los:
            return "✓ Tất cả LOs đều tốt (≥ 60%)"
        
        summary = f"⚠ {len(weak_los)} LOs cần cải thiện:\n"
        for lo_id, mastery in weak_los[:5]:
            lo_desc = self.lo_info.get(lo_id, {}).get('description', lo_id)
            lo_desc_short = lo_desc[:50] + '...' if len(lo_desc) > 50 else lo_desc
            summary += f"  - {lo_id} ({mastery:.1%}): {lo_desc_short}\n"
        
        if len(weak_los) > 5:
            summary += f"  ... và {len(weak_los) - 5} LOs khác"
        
        return summary.strip()
