#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LO Mastery Service - Calculate and track LO/PO mastery from Moodle data
=========================================================================
Service to calculate LO mastery from Moodle API grades and persist to MongoDB
"""

import time
from typing import Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np

from services.clients.moodle_client import MoodleAPIClient
from services.business.po_lo import POLOService
from services.repository.state_repository import StateRepository


class LOMasteryService:
    """
    Service to calculate and track LO/PO mastery from real Moodle data
    
    Features:
    - Calculate mastery from Moodle grades
    - Sync single student or entire course
    - Cache mastery data with TTL
    - Query weak students by LO/PO
    - Generate class statistics
    """
    
    def __init__(
        self,
        moodle_client: MoodleAPIClient,
        po_lo_service: POLOService,
        repository: StateRepository,
        cache_ttl: int = 300,  # 5 minutes
        default_mastery: float = 0.4
    ):
        """
        Initialize LOMasteryService
        
        Args:
            moodle_client: MoodleAPIClient instance
            po_lo_service: POLOService instance
            repository: StateRepository instance
            cache_ttl: Cache TTL in seconds (default: 300)
            default_mastery: Default mastery for unassessed LOs (default: 0.4)
        """
        self.moodle_client = moodle_client
        self.po_lo_service = po_lo_service
        self.repository = repository
        self.cache_ttl = cache_ttl
        self.default_mastery = default_mastery
        
        # In-memory cache: {(user_id, course_id): (data, timestamp)}
        self.cache: Dict[tuple, tuple] = {}
        
        # Statistics
        self.stats = {
            'total_syncs': 0,
            'failed_syncs': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def calculate_lo_mastery_from_grades(
        self,
        user_id: int,
        course_id: int
    ) -> Dict[str, Any]:
        """
        Calculate LO mastery from Moodle grades
        
        Args:
            user_id: User ID
            course_id: Course ID
            
        Returns:
            Dict with:
            - lo_mastery: {LO_id: mastery_value}
            - po_progress: {PO_id: progress_value}
            - metadata: Additional stats
        """
        try:
            # 1. Get user scores from Moodle
            scores_data = self.moodle_client.get_user_scores(user_id, section_id=None)
            
            # 2. Load Po_Lo.json for this course
            po_lo_data = self.po_lo_service.get_po_lo(course_id)
            
            # 3. Build activity_id -> [LO_ids] mapping
            activity_to_los = {}
            for lo in po_lo_data['learning_outcomes']:
                for activity_id in lo.get('activity_ids', []):
                    if activity_id not in activity_to_los:
                        activity_to_los[activity_id] = []
                    activity_to_los[activity_id].append(lo['id'])
            
            # 4. Calculate mastery per LO
            lo_scores = defaultdict(list)
            print(f"\n🔍 Processing {len(scores_data)} score entries for user {user_id}")
            print(f"   Activity-to-LO mapping has {len(activity_to_los)} activities")
            
            for score_entry in scores_data:
                # Use moduleid (cmid) to match with Po_Lo.json activity_ids
                module_id = score_entry.get('moduleid')
                score = score_entry.get('score', 0.0)  # Already normalized 0-1
                
                if module_id in activity_to_los:
                    for lo_id in activity_to_los[module_id]:
                        lo_scores[lo_id].append(score)
                        print(f"   ✓ Module {module_id} → {lo_id}: score={score}")
                else:
                    print(f"   ⚠️  Module {module_id} not in mapping (score={score})")
            
            # 5. Aggregate scores per LO
            lo_mastery = {}
            for lo_id, scores in lo_scores.items():
                if scores:
                    # Use average score (mean of all attempts)
                    lo_mastery[lo_id] = float(np.mean(scores))
                else:
                    lo_mastery[lo_id] = self.default_mastery
            
            # 6. Fill missing LOs with default
            all_lo_ids = [lo['id'] for lo in po_lo_data['learning_outcomes']]
            for lo_id in all_lo_ids:
                if lo_id not in lo_mastery:
                    lo_mastery[lo_id] = self.default_mastery
            
            # 7. Calculate PO progress
            po_progress = {}
            lo_to_pos = {}  # Build reverse mapping
            for lo in po_lo_data['learning_outcomes']:
                lo_to_pos[lo['id']] = lo.get('mapped_to', [])
            
            for po in po_lo_data['programme_outcomes']:
                po_id = po['id']
                # Get all LOs mapped to this PO
                relevant_los = [
                    lo_id for lo_id, pos in lo_to_pos.items()
                    if po_id in pos
                ]
                if relevant_los:
                    po_progress[po_id] = float(np.mean([
                        lo_mastery.get(lo_id, self.default_mastery)
                        for lo_id in relevant_los
                    ]))
                else:
                    po_progress[po_id] = self.default_mastery
            
            # 8. Build metadata
            metadata = {
                'total_activities_completed': len(scores_data),
                'total_quizzes_taken': len([s for s in scores_data if s.get('activitytype') == 'quiz']),
                'avg_quiz_score': float(np.mean([s['score'] for s in scores_data])) if scores_data else 0.0,
                'activities_by_lo': {
                    lo_id: [aid for aid, los in activity_to_los.items() if lo_id in los]
                    for lo_id in all_lo_ids
                }
            }
            
            return {
                'lo_mastery': lo_mastery,
                'po_progress': po_progress,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Error calculating LO mastery for user {user_id}: {e}")
            return None
    
    def sync_student_mastery(
        self,
        user_id: int,
        course_id: int,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Sync LO mastery for a single student
        
        Args:
            user_id: User ID
            course_id: Course ID
            force: Force sync even if cache is fresh
            
        Returns:
            Dict with sync result
        """
        try:
            start_time = time.time()
            
            # Calculate mastery from Moodle
            mastery_data = self.calculate_lo_mastery_from_grades(user_id, course_id)
            
            if not mastery_data:
                self.stats['failed_syncs'] += 1
                return {
                    'success': False,
                    'error': 'Failed to calculate mastery'
                }
            
            # Save to MongoDB
            saved = self.repository.save_lo_mastery(
                user_id=user_id,
                course_id=course_id,
                lo_mastery=mastery_data['lo_mastery'],
                po_progress=mastery_data['po_progress'],
                metadata=mastery_data['metadata']
            )
            
            # Invalidate cache
            self.invalidate_cache(user_id, course_id)
            
            # Update stats
            self.stats['total_syncs'] += 1
            elapsed_time = time.time() - start_time
            
            return {
                'success': True,
                'user_id': user_id,
                'course_id': course_id,
                'elapsed_time': elapsed_time,
                'lo_count': len(mastery_data['lo_mastery']),
                'po_count': len(mastery_data['po_progress']),
                'avg_lo_mastery': float(np.mean(list(mastery_data['lo_mastery'].values())))
            }
            
        except Exception as e:
            self.stats['failed_syncs'] += 1
            print(f"Error syncing student {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_all_students(
        self,
        course_id: int,
        max_students: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sync LO mastery for all students in a course
        
        Args:
            course_id: Course ID
            max_students: Max students to sync (for testing)
            
        Returns:
            Dict with sync summary
        """
        try:
            start_time = time.time()
            
            # Get enrolled users
            enrolled_users = self.moodle_client.get_enrolled_users(course_id)
            
            if max_students:
                enrolled_users = enrolled_users[:max_students]
            
            # Sync each student
            results = []
            for user in enrolled_users:
                user_id = user.get('id')
                if user_id:
                    result = self.sync_student_mastery(user_id, course_id)
                    results.append(result)
            
            # Calculate summary
            successful = len([r for r in results if r.get('success')])
            failed = len([r for r in results if not r.get('success')])
            elapsed_time = time.time() - start_time
            
            return {
                'success': True,
                'course_id': course_id,
                'total_students': len(enrolled_users),
                'successful_syncs': successful,
                'failed_syncs': failed,
                'elapsed_time': elapsed_time,
                'avg_time_per_student': elapsed_time / len(enrolled_users) if enrolled_users else 0
            }
            
        except Exception as e:
            print(f"Error syncing all students for course {course_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_student_mastery(
        self,
        user_id: int,
        course_id: int,
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Get LO mastery for a student (with caching)
        
        Args:
            user_id: User ID
            course_id: Course ID
            use_cache: Use cache if available
            
        Returns:
            Dict with mastery data or None
        """
        cache_key = (user_id, course_id)
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()
            
            if age < self.cache_ttl:
                self.stats['cache_hits'] += 1
                return data
        
        # Cache miss - fetch from MongoDB
        self.stats['cache_misses'] += 1
        data = self.repository.get_lo_mastery(user_id, course_id)
        
        if data:
            # Update cache
            self.cache[cache_key] = (data, datetime.now())
        
        return data
    
    def get_course_statistics(
        self,
        course_id: int
    ) -> Dict[str, Any]:
        """
        Get class-level statistics
        
        Args:
            course_id: Course ID
            
        Returns:
            Dict with course statistics
        """
        try:
            all_students = self.repository.get_all_students_mastery(course_id)
            
            if not all_students:
                return {
                    'course_id': course_id,
                    'total_students': 0,
                    'error': 'No mastery data available'
                }
            
            # Calculate statistics per LO
            lo_stats = defaultdict(list)
            po_stats = defaultdict(list)
            
            for student in all_students:
                for lo_id, mastery in student.get('lo_mastery', {}).items():
                    lo_stats[lo_id].append(mastery)
                for po_id, progress in student.get('po_progress', {}).items():
                    po_stats[po_id].append(progress)
            
            # Aggregate
            lo_summary = {
                lo_id: {
                    'avg': float(np.mean(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'std': float(np.std(values))
                }
                for lo_id, values in lo_stats.items()
            }
            
            po_summary = {
                po_id: {
                    'avg': float(np.mean(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'std': float(np.std(values))
                }
                for po_id, values in po_stats.items()
            }
            
            return {
                'course_id': course_id,
                'total_students': len(all_students),
                'lo_statistics': lo_summary,
                'po_statistics': po_summary,
                'overall_avg_mastery': float(np.mean([
                    np.mean(list(s.get('lo_mastery', {}).values()))
                    for s in all_students
                ]))
            }
            
        except Exception as e:
            print(f"Error getting course statistics: {e}")
            return {
                'course_id': course_id,
                'error': str(e)
            }
    
    def get_weak_students(
        self,
        course_id: int,
        lo_id: Optional[str] = None,
        threshold: float = 0.6
    ) -> List[Dict]:
        """
        Get students with low mastery
        
        Args:
            course_id: Course ID
            lo_id: Specific LO ID (optional)
            threshold: Mastery threshold
            
        Returns:
            List of weak students
        """
        return self.repository.get_weak_students_by_lo(
            course_id=course_id,
            lo_id=lo_id,
            threshold=threshold
        )
    
    def invalidate_cache(self, user_id: int, course_id: int):
        """Invalidate cache for a specific student"""
        cache_key = (user_id, course_id)
        if cache_key in self.cache:
            del self.cache[cache_key]
    
    def clear_cache(self):
        """Clear entire cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return {
            **self.stats,
            'cache_size': len(self.cache)
        }


def test_lo_mastery_service():
    """Test LOMasteryService"""
    print("=" * 70)
    print("Testing LOMasteryService")
    print("=" * 70)
    
    try:
        # Initialize components
        moodle_client = MoodleAPIClient(course_id=5)
        po_lo_service = POLOService(data_dir='data')
        repository = StateRepository()
        
        service = LOMasteryService(
            moodle_client=moodle_client,
            po_lo_service=po_lo_service,
            repository=repository
        )
        
        print("\n1. Test sync single student:")
        result = service.sync_student_mastery(user_id=5, course_id=5)
        print(f"   Result: {result}")
        
        print("\n2. Test get student mastery:")
        mastery = service.get_student_mastery(user_id=5, course_id=5)
        if mastery:
            print(f"   LOs: {len(mastery.get('lo_mastery', {}))}")
            print(f"   POs: {len(mastery.get('po_progress', {}))}")
            print(f"   Last sync: {mastery.get('last_sync')}")
        
        print("\n3. Test get weak students:")
        weak = service.get_weak_students(course_id=5, threshold=0.6)
        print(f"   Found {len(weak)} weak students")
        
        print("\n4. Test course statistics:")
        stats = service.get_course_statistics(course_id=5)
        print(f"   Total students: {stats.get('total_students')}")
        print(f"   Overall avg: {stats.get('overall_avg_mastery', 0):.2f}")
        
        print("\n5. Service stats:")
        service_stats = service.get_stats()
        for key, value in service_stats.items():
            print(f"   {key}: {value}")
        
        repository.close()
        
        print("\n" + "=" * 70)
        print("✓ LOMasteryService test completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_lo_mastery_service()
