#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log-to-State Builder - UNIFIED VERSION
======================================
Gộp LogPreprocessor + StateBuilder thành 1 file duy nhất
Xử lý: raw logs → states 6D theo StateBuilderV2 + enrichment với Moodle API
"""

from typing import Dict, Tuple, List, Any, Optional
from pathlib import Path
from collections import defaultdict
import sys

# Import LogEvent, StateBuilderV2
try:
    from .log_models import LogEvent
    from .state_builder_v2 import StateBuilderV2
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.log_models import LogEvent
    from core.state_builder_v2 import StateBuilderV2


class LogToStateBuilder:
    """
    UNIFIED LogToStateBuilder
    
    Flow:
    1. Raw logs → Parse với LogEvent.from_dict() → Có lesson_id
    2. Aggregate theo (user_id, lesson_id) → Intermediate data
    3. Enrich với Moodle API (get_module_progress, get_user_scores)
    4. Convert sang 6D state tuple với StateBuilderV2
    """
    
    def __init__(
        self,
        cluster_profiles_path: str,
        course_structure_path: str,
        recent_window: int = 10,
        excluded_clusters: List[int] = None,
        moodle_client=None  # MoodleAPIClient instance for enrichment
    ):
        """
        Initialize unified state builder
        
        Args:
            cluster_profiles_path: Path to cluster profiles JSON
            course_structure_path: Path to course structure JSON
            recent_window: Number of recent actions to keep
            excluded_clusters: List of cluster IDs to exclude (default: [3] - teachers)
            moodle_client: MoodleAPIClient instance for API enrichment (optional)
        """
        self.recent_window = recent_window
        self.moodle_client = moodle_client
        
        # Initialize StateBuilderV2 for 6D state conversion
        self.state_builder = StateBuilderV2(
            cluster_profiles_path=cluster_profiles_path,
            course_structure_path=course_structure_path,
            excluded_clusters=excluded_clusters,
            recent_window=recent_window
        )
    
    def build_states_from_logs(
        self,
        raw_logs: List[Dict],
        enrich_with_api: bool = True
    ) -> Dict[Tuple[int, int, int], Tuple[int, int, float, float, int, int]]:
        """
        Build 6D states from raw logs - MAIN FUNCTION
        
        Args:
            raw_logs: List of raw log dictionaries from Moodle
            enrich_with_api: Whether to enrich states with Moodle API data
            
        Returns:
            Dictionary mapping (user_id, course_id, lesson_id) -> 6D state tuple
            State tuple: (cluster_id, lesson_id, progress_bin, score_bin, learning_phase, engagement_level)
        """
        # Step 1: Build intermediate data from logs
        intermediate_data = self._build_intermediate_data(raw_logs)
        
        # Step 2: Enrich with Moodle API (if available)
        if enrich_with_api and self.moodle_client:
            intermediate_data = self._enrich_states_with_api(intermediate_data)
        
        # Step 3: Convert to 6D states using StateBuilderV2
        states_6d = self._convert_to_6d_states(intermediate_data)
        
        # Step 4: Print final summary
        print(f"\n{'='*70}")
        print(f"📊 FINAL STATE SUMMARY - {len(states_6d)} states built")
        print(f"{'='*70}")
        for i, ((uid, cid, lid), state_tuple) in enumerate(list(states_6d.items())[:10]):
            state_str = self.state_builder.state_to_string(state_tuple)
            print(f"  {i+1}. User {uid}, Course {cid}, Lesson {lid}:")
            print(f"      Vector: {state_tuple}")
            print(f"      Readable: {state_str}")
        if len(states_6d) > 10:
            print(f"  ... and {len(states_6d) - 10} more states")
        print(f"{'='*70}\n")
        
        return states_6d
    
    def _build_intermediate_data(
        self,
        raw_logs: List[Dict]
    ) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """
        Step 1: Parse logs and aggregate by (user_id, course_id, lesson_id)
        
        Returns:
            Dictionary mapping (user_id, course_id, lesson_id) -> intermediate data dict
        """
        intermediate = {}
        
        for i, log in enumerate(raw_logs):
            
            # Parse log → LogEvent (has lesson_id, lesson_name)
            event = LogEvent.from_dict(log)
            if not event:
                continue  # Course-level event or invalid
            if event.lesson_id is None:
                continue  # Cannot determine lesson
            
            # Use (user_id, course_id, lesson_id) as key for multi-course support
            key = (event.user_id, event.course_id, event.lesson_id)
            
            # Initialize intermediate data if not exists
            if key not in intermediate:
                intermediate[key] = {
                    'user_id': event.user_id,
                    'course_id': event.course_id,
                    'lesson_id': event.lesson_id,
                    'lesson_name': event.lesson_name or "Unknown Lesson",
                    'cluster_id': event.cluster_id if event.cluster_id not in [3] else 2,  # Default to cluster 2 if excluded
                    'total_actions': 0,
                    'recent_actions': [],
                    'action_timestamps': [],
                    'scores': [],
                    'quiz_attempts': 0,
                    'quiz_success': 0,
                    'total_time_spent': 0.0,
                    'first_timestamp': event.timestamp,
                    'last_timestamp': event.timestamp,
                    'avg_score': 0.0,
                    # Will be enriched by API
                    'progress': 0.0,
                    'completed_activities': [],
                    'total_activities': 0
                }
            
            # Update intermediate data with event
            data = intermediate[key]
            data['total_actions'] += 1
            data['recent_actions'].append(event.action_type)
            data['action_timestamps'].append(event.timestamp)
            data['last_timestamp'] = event.timestamp
            
            if event.score is not None:
                data['scores'].append(event.score)
                data['avg_score'] = sum(data['scores']) / len(data['scores'])
            
            if 'quiz' in event.action_type:
                data['quiz_attempts'] += 1
                if event.score is not None and event.score >= 0.6:
                    data['quiz_success'] += 1
            
            if event.time_spent:
                data['total_time_spent'] += event.time_spent
            
            # Trim recent actions window
            if len(data['recent_actions']) > self.recent_window:
                data['recent_actions'] = data['recent_actions'][-self.recent_window:]
                data['action_timestamps'] = data['action_timestamps'][-self.recent_window:]
        
        return intermediate
    
    def _enrich_states_with_api(
        self,
        intermediate_data: Dict[Tuple[int, int, int], Dict[str, Any]]
    ) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """
        Step 2: Enrich intermediate data with Moodle API
        
        For each (user_id, course_id, lesson_id):
        1. Call get_module_progress() → progress, completed_activities
        2. Call get_user_scores() → quiz scores
        3. Call get_user_cluster() → cluster assignment
        
        Args:
            intermediate_data: Intermediate data from logs
            
        Returns:
            Enriched intermediate data with API data
        """
        enriched_count = 0
        total_states = len(intermediate_data)
        
        for (user_id, course_id, lesson_id), data in intermediate_data.items():
            try:
                # 1. Get module progress (completion rate)
                progress_data = self.moodle_client.get_module_progress(user_id, lesson_id)
                
                data['progress'] = progress_data.get('progress', 0.0)
                data['completed_activities'] = progress_data.get('completed_activities', [])
                data['total_activities'] = progress_data.get('total_activities', 0)
                completed_count = progress_data.get('completed_count', 0)
                
                # Add API time_spent to logged time
                api_time = progress_data.get('time_spent', 0)
                if api_time > 0:
                    data['total_time_spent'] = max(data['total_time_spent'], api_time)
                
                # 2. Get user scores (quiz grades)
                scores_data = self.moodle_client.get_user_scores(user_id, section_id=lesson_id)
                
                if scores_data and len(scores_data) > 0:
                    api_scores = []
                    for s in scores_data:
                        score_val = s.get('score')
                        if score_val is not None:
                            api_scores.append(float(score_val))
                    
                    if api_scores:
                        all_scores = data['scores'] + api_scores
                        data['scores'] = all_scores
                        data['avg_score'] = sum(all_scores) / len(all_scores)
                
                # 3. Get user cluster (if not already set or if excluded cluster)
                if data['cluster_id'] == 2:  # Default cluster, try to get real cluster
                    cluster_id = self.moodle_client.get_user_cluster(user_id)
                    if cluster_id not in [3]:
                        data['cluster_id'] = cluster_id
                
                enriched_count += 1
                
            except Exception as e:
                # Chỉ log error, không log chi tiết
                print(f"   ⚠️  API enrichment failed for user {user_id}, lesson {lesson_id}: {e}")
                # Keep default values on error
                if data['progress'] == 0.0:
                    data['progress'] = 0.1  # Small default to avoid zero state
                continue
        return intermediate_data
    
    def _convert_to_6d_states(
        self,
        intermediate_data: Dict[Tuple[int, int, int], Dict[str, Any]]
    ) -> Dict[Tuple[int, int, int], Tuple[int, int, float, float, int, int]]:
        """
        Step 3: Convert intermediate data to 6D state tuples using StateBuilderV2
        
        Args:
            intermediate_data: Enriched intermediate data
            
        Returns:
            Dictionary mapping (user_id, course_id, lesson_id) -> 6D state tuple
        """
        states_6d = {}
        failed_states = []
        
        print(f"\n{'='*70}")
        print(f"🔧 CONVERTING TO 6D STATES - {len(intermediate_data)} intermediate states")
        print(f"{'='*70}")
        
        for (user_id, course_id, lesson_id), data in intermediate_data.items():
            try:
                # Use StateBuilderV2 to build 6D state with lesson_id
                state_tuple = self.state_builder.build_state(
                    cluster_id=data['cluster_id'],
                    current_module_id=lesson_id,
                    module_progress=data['progress'],
                    avg_score=data['avg_score'],
                    recent_actions=data['recent_actions'],
                    time_on_task=data['total_time_spent'],
                    action_timestamps=data['action_timestamps']
                )
                
                states_6d[(user_id, course_id, lesson_id)] = state_tuple
                
            except Exception as e:
                print(f"   ❌ FAILED: {type(e).__name__}: {e}")
                failed_states.append({
                    'user': user_id,
                    'course': course_id,
                    'lesson': lesson_id,
                    'cluster': data.get('cluster_id', 'unknown'),
                    'error': str(e)
                })
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ CONVERSION COMPLETE: {len(states_6d)}/{len(intermediate_data)} states built")
        if failed_states:
            print(f"\n❌ FAILED CONVERSIONS ({len(failed_states)}):")
            for f in failed_states:
                print(f"   - User {f['user']}, Course {f['course']}, Lesson {f['lesson']}, Cluster {f['cluster']}: {f['error']}")
        print(f"{'='*70}")
        
        return states_6d
    
    def get_statistics(self) -> Dict:
        """Get pipeline statistics"""
        return {
            'recent_window': self.recent_window,
            'moodle_api': 'connected' if self.moodle_client else 'not available',
            'state_space_size': self.state_builder.calculate_state_space_size(),
            'n_clusters': self.state_builder.n_clusters,
            'n_modules': self.state_builder.n_modules
        }


# ===================================================================
# TEST
# ===================================================================
def test_log_to_state_builder():
    """Test unified LogToStateBuilder with 6D states"""
    import sys
    from pathlib import Path
    
    print("=" * 70)
    print("Test LogToStateBuilder (unified version with 6D states)")
    print("=" * 70)
    
    # Paths to required files
    base_path = Path(__file__).parent.parent
    cluster_profiles_path = base_path / "data" / "cluster_profiles.json"
    course_structure_path = base_path / "data" / "course_structure.json"
    
    # Sample logs
    sample_logs = [
        {'userid': 5, 'courseid': 5, 'contextinstanceid': 78, 'eventname': '\\mod_quiz\\event\\attempt_submitted', 'grade': 85, 'timecreated': 1763803848},
        {'userid': 5, 'courseid': 5, 'contextinstanceid': 79, 'eventname': '\\mod_page\\event\\course_module_viewed', 'timecreated': 1763804000},
        {'userid': 6, 'courseid': 5, 'contextinstanceid': 78, 'eventname': '\\mod_quiz\\event\\attempt_started', 'timecreated': 1763805000},
    ]
    
    # Test without API
    print("\n1. Test without Moodle API (6D states):")
    builder = LogToStateBuilder(
        cluster_profiles_path=str(cluster_profiles_path),
        course_structure_path=str(course_structure_path),
        recent_window=10,
        moodle_client=None
    )
    states = builder.build_states_from_logs(sample_logs, enrich_with_api=False)
    
    print(f"\nBuilt {len(states)} 6D states:")
    for (user_id, course_id, lesson_id), state_tuple in states.items():
        state_str = builder.state_builder.state_to_string(state_tuple)
        print(f"  User {user_id} | Course {course_id} | Lesson {lesson_id}: {state_str}")
    
    # Test with API (if available)
    try:
        sys.path.insert(0, str(base_path / "services"))
        from moodle_api_client import MoodleAPIClient
        
        print("\n2. Test with Moodle API (6D states enriched):")
        api_client = MoodleAPIClient()
        builder_with_api = LogToStateBuilder(
            cluster_profiles_path=str(cluster_profiles_path),
            course_structure_path=str(course_structure_path),
            recent_window=10,
            moodle_client=api_client
        )
        states_enriched = builder_with_api.build_states_from_logs(sample_logs, enrich_with_api=True)
        
        print(f"\nEnriched {len(states_enriched)} 6D states:")
        for (user_id, course_id, lesson_id), state_tuple in states_enriched.items():
            state_str = builder_with_api.state_builder.state_to_string(state_tuple)
            print(f"  User {user_id} | Course {course_id} | Lesson {lesson_id}: {state_str}")
    except Exception as e:
        print(f"\n⚠️  Cannot test with API: {e}")
    
    print("\n" + "=" * 70)
    print("✓ LogToStateBuilder (unified with 6D states) test completed!")
    print("=" * 70)


if __name__ == '__main__':
    test_log_to_state_builder()

