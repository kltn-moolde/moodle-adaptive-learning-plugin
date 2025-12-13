#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Recommendation Service - Simplified recommendation with auto-fetch
=========================================================================
Tự động lấy state và LO mastery từ DB, đơn giản hóa API
"""

from typing import Dict, Optional, Any
from datetime import datetime


class SmartRecommendationService:
    """
    Smart recommendation service with auto-fetch capabilities
    Simplifies recommendation flow by auto-loading state and mastery
    
    Features:
    - Auto-fetch current state from user_states collection
    - Auto-fetch LO mastery from student_lo_mastery collection
    - Generate recommendations with minimal input
    - Handle new users gracefully with defaults
    """
    
    def __init__(
        self,
        state_repository,
        lo_mastery_service,
        get_services_func
    ):
        """
        Initialize smart recommendation service
        
        Args:
            state_repository: StateRepository instance
            lo_mastery_service: LOMasteryService instance
            get_services_func: Function to get services for a course
        """
        self.state_repo = state_repository
        self.lo_mastery_service = lo_mastery_service
        self.get_services_func = get_services_func
        
        print("✓ SmartRecommendationService initialized")
    
    def get_recommendations_simple(
        self,
        user_id: int,
        course_id: int,
        module_id: Optional[int] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Get recommendations with auto-fetched state and mastery
        
        Args:
            user_id: User ID
            course_id: Course ID
            module_id: Optional specific module
            top_k: Number of recommendations
            
        Returns:
            Complete recommendation response with state, mastery, and recommendations
        """
        print(f"\n🔍 SmartRecommend: user={user_id}, course={course_id}, module={module_id}")
        
        # 1. Get current state from DB
        state_doc = self.state_repo.get_current_state(
            user_id, course_id, module_id
        )
        
        if not state_doc:
            print(f"   ⚠️  No state found - using default state for new user")
            state = self._create_default_state(user_id, course_id)
            actual_module_id = module_id or 0
        else:
            state = tuple(state_doc['state_tuple'])
            actual_module_id = state_doc.get('module_id', module_id or 0)
            print(f"   ✓ Found state: cluster={state[0]}, module={actual_module_id}")
        
        # 2. Get LO mastery from service (with cache)
        mastery_data = self.lo_mastery_service.get_student_mastery(
            user_id, course_id, use_cache=True
        )
        
        lo_mastery = mastery_data.get('lo_mastery', {}) if mastery_data else {}
        if not lo_mastery:
            print(f"   ⚠️  No LO mastery found - using default")
            lo_mastery = self._create_default_mastery()
        else:
            avg_mastery = sum(lo_mastery.values()) / len(lo_mastery) if lo_mastery else 0
            print(f"   ✓ Found LO mastery: {len(lo_mastery)} LOs, avg={avg_mastery:.2f}")
        
        # 3. Get recommendation service for this course
        try:
            services = self.get_services_func(course_id)
            recommendation_service = services['recommendation_service']
            print(f"   ✓ Loaded recommendation service for course {course_id}")
        except Exception as e:
            print(f"   ❌ Error loading services: {e}")
            raise
        
        # 4. Generate recommendations
        cluster_id = int(state[0])
        module_idx = int(state[1])
        
        try:
            recommendations = recommendation_service.get_recommendations(
                state=state,
                cluster_id=cluster_id,
                top_k=top_k,
                lo_mastery=lo_mastery,
                module_idx=module_idx
            )
            print(f"   ✓ Generated {len(recommendations)} recommendations")
        except Exception as e:
            print(f"   ❌ Error generating recommendations: {e}")
            raise
        
        # 5. Build response
        return {
            'success': True,
            'user_id': user_id,
            'course_id': course_id,
            'current_state': self._format_state(state, state_doc, actual_module_id),
            'lo_mastery': lo_mastery,
            'recommendations': recommendations,
            'metadata': {
                'has_saved_state': state_doc is not None,
                'has_lo_mastery': mastery_data is not None,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def _create_default_state(self, user_id: int, course_id: int) -> tuple:
        """
        Create default state for new user
        
        Default state: cluster 2 (medium), module 0, low progress/score, 
                      phase 0 (starting), engagement 2 (moderate)
        
        Returns:
            State tuple (cluster_id, module_idx, progress_bin, score_bin, phase, engagement)
        """
        return (2, 0, 0.0, 0.0, 0, 2)
    
    def _create_default_mastery(self) -> Dict[str, float]:
        """
        Create default LO mastery (all LOs at 0.4 = 40%)
        
        Returns:
            Dict mapping LO_id -> mastery score
        """
        # Generate LO1.1 to LO5.2
        lo_mastery = {}
        for i in range(1, 6):  # LO1 to LO5
            for j in range(1, 3):  # .1 to .2
                lo_id = f'LO{i}.{j}'
                lo_mastery[lo_id] = 0.4
        
        return lo_mastery
    
    def _format_state(
        self, 
        state: tuple, 
        state_doc: Optional[Dict], 
        module_id: int
    ) -> Dict[str, Any]:
        """
        Format state for API response
        
        Args:
            state: State tuple
            state_doc: Original state document from DB (or None)
            module_id: Module ID
            
        Returns:
            Formatted state dict
        """
        return {
            'cluster_id': int(state[0]),
            'module_idx': int(state[1]),
            'progress_bin': float(state[2]),
            'score_bin': float(state[3]),
            'learning_phase': int(state[4]),
            'engagement_level': int(state[5]),
            'module_id': module_id,
            'last_updated': state_doc.get('updated_at').isoformat() if state_doc and state_doc.get('updated_at') else None
        }
