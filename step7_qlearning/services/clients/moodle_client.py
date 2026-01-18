#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle API Client - Interface với Moodle REST API
==================================================
Lấy logs, user data, course structure từ Moodle
"""

import requests
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os


class MoodleAPIClient:
    """
    Moodle API Client for fetching logs and user data
    
    Required Moodle Custom APIs:
    ============================
    1. mod_adaptivelearning_get_user_logs
       - Get learning logs for a user
       - Input: user_id, course_id, start_time, end_time
       - Output: List of log events
    
    2. mod_adaptivelearning_get_user_cluster
       - Get user cluster assignment
       - Input: user_id, course_id
       - Output: cluster_id (0-6)
    
    3. mod_adaptivelearning_get_module_progress
       - Get user progress in a module
       - Input: user_id, module_id
       - Output: progress (0-1), completed_activities
    
    4. mod_adaptivelearning_get_user_scores
       - Get user scores across activities
       - Input: user_id, course_id, module_id (optional)
       - Output: List of scores with activity IDs
    
    5. mod_adaptivelearning_get_course_structure
       - Get course structure (modules, activities)
       - Input: course_id
       - Output: Full course structure JSON
    """
    
    def __init__(
        self,
        # moodle_url: str = "http://139.99.103.223:9090",
        moodle_url: str = "http://localhost:8100",
        ws_token: str = "86e86e0301d495db032da3b855180f5f",  # Custom API token (default)
        ws_token_standard: str = "eb4a1ea54118eb52574ac5ede106dbd3",  # Standard Moodle API token
        course_id: int = 5,
        timeout: int = 30
    ):
        """
        Initialize Moodle API client with dual token support
        
        Args:
            moodle_url: Base Moodle URL (e.g., https://moodle.example.com)
            ws_token: Web service token for custom APIs (local_*)
            ws_token_standard: Web service token for standard Moodle APIs (core_*)
            course_id: Course ID
            timeout: Request timeout in seconds
        """
        self.moodle_url = moodle_url.rstrip('/')
        self.ws_token_custom = ws_token  # Token for local_* APIs
        self.ws_token_standard = ws_token_standard  # Token for core_* APIs
        self.ws_token = ws_token  # Backward compatibility
        self.course_id = course_id if course_id is not None else 5  # Default to 5 if None
        self.timeout = timeout
        
        # API endpoint
        self.api_endpoint = f"{self.moodle_url}/webservice/rest/server.php"
        
        print(f"✓ MoodleAPIClient initialized:")
        print(f"  - Moodle URL: {self.moodle_url}")
        print(f"  - Course ID: {self.course_id}")
    
    def _call_api(
        self,
        function_name: str,
        params: Dict[str, Any]
    ) -> Dict:
        """
        Call Moodle web service API with automatic token selection
        
        Args:
            function_name: Moodle function name
            params: Function parameters
            
        Returns:
            API response as dictionary
        """
        # Auto-select token based on API function name
        if function_name.startswith('core_'):
            # Standard Moodle APIs use standard token
            selected_token = self.ws_token_standard
        else:
            # Custom APIs (local_*) use custom token
            selected_token = self.ws_token_custom
        
        # Add required parameters
        data = {
            'wstoken': selected_token,
            'wsfunction': function_name,
            'moodlewsrestformat': 'json',
            **params
        }
        
        # Log full API call details
        print(f"\n🌐 API Request:")
        print(f"   URL: {self.api_endpoint}")
        print(f"   Function: {function_name}")
        print(f"   Params: {params}")
        
        # Build full URL with actual token for testing
        full_url_with_token = self.api_endpoint + '?' + '&'.join([f"{k}={v}" for k, v in data.items()])
        print(f"   🔗 Full URL (for testing): {full_url_with_token}")
        
        try:
            response = requests.post(
                self.api_endpoint,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"   ✅ Response Status: {response.status_code}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error calling Moodle API: {e}")
            return {"error": str(e)}
    
    def get_user_logs(
        self,
        user_id: int,
        module_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get user learning logs
        
        Uses: local_userlog_get_logs
        
        Args:
            user_id: User ID
            module_id: Module/Section ID (required)
            start_time: Start time (default: last 7 days)
            end_time: End time (default: now)
            
        Returns:
            List of log event dictionaries
        """
        # Default time range: last 7 days
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(days=7)
        
        params = {
            'userid': user_id,
            'courseid': self.course_id,
            'moduleid': module_id,  # Required parameter
            'starttime': int(start_time.timestamp()),
            'endtime': int(end_time.timestamp())
        }
        
        function_name = 'local_userlog_get_logs'
        
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching user logs: {result['error']}")
            return []
        
        return result.get('logs', [])
    
    def get_user_cluster(
        self,
        user_id: int
    ) -> int:
        """
        Get user cluster assignment
        
        NOTE: API not available yet - using MOCKUP
        TODO: Implement API endpoint for user clustering
        
        Args:
            user_id: User ID
            
        Returns:
            Cluster ID (0-6), default 3 if not found
        """
        # MOCKUP: Return default cluster since API not available yet
        # TODO: Replace with actual API call when available
        print(f"⚠️  MOCKUP: get_user_cluster for user {user_id} - returning default cluster 2")
        return 2  # Default to medium cluster
    
    def get_module_progress(
        self,
        user_id: int,
        section_id: int
    ) -> Dict:
        """
        Get user progress in a module (completion rate)
        
        Uses: llocal_userlog_get_section_completion
        
        Args:
            user_id: User ID
            section_id: Module ID
            
        Returns:
            Progress dictionary with progress, completed_activities, total_activities, time_spent
        """
        params = {
            'userid': user_id,
            'sectionid': section_id
        }
        
        function_name = 'local_userlog_get_section_completion'
        
        print(f"\n🔍 API Call: {function_name}")
        print(f"   Params: userid={user_id}, moduleid={section_id}")
        
        result = self._call_api(function_name, params)
        
        # Lấy đúng giá trị từ response API
        # Response format: {"section_id": 38, "userid": 5, "total_activities": 5, "completed_activities": 5, "completion_rate": 100}
        completion_rate = result.get('completion_rate', 0)  # 0-100
        progress = completion_rate / 100.0 if completion_rate else 0.0  # Convert to 0.0-1.0
        
        response_data = {
            'progress': progress,
            'completed_activities': [],  # API trả về số, không có list chi tiết
            'completed_count': result.get('completed_activities', 0),  # Số lượng đã hoàn thành
            'total_activities': result.get('total_activities', 0),
            'time_spent': result.get('time_spent', 0)
        }
        
        print(f"   ✅ Processed Response: {response_data}")
        
        return response_data
    
    def get_user_scores(
        self,
        user_id: int,
        section_id: Optional[int] = None,
        course_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get user scores across activities (quizzes)
        
        Uses: local_userlog_get_score_section (per section)
        Aggregates scores from all sections if section_id not specified
        
        Args:
            user_id: User ID
            section_id: Section ID (optional - if None, get scores from all sections)
            course_id: Course ID (optional - uses self.course_id if not provided)
            
        Returns:
            List of score dictionaries with quiz scores
        """
        # Use provided course_id or fall back to instance course_id
        effective_course_id = course_id if course_id is not None else self.course_id
        
        # If specific section requested, get scores for that section only
        if section_id is not None:
            params = {
                'userid': user_id,
                'courseid': effective_course_id,
                'sectionid': section_id
            }
            
            function_name = 'local_userlog_get_score_section'
            result = self._call_api(function_name, params)
            
            if 'error' in result:
                print(f"Error fetching user scores for section {section_id}: {result['error']}")
                return []
            
            return result.get('scores', [])
        
        # Otherwise, get scores from ALL sections
        print(f"\n🔍 Getting scores for user {user_id} from all sections...")
        
        try:
            # Get course structure to find all sections
            course_structure = self.get_course_structure(course_id=effective_course_id)
            contents = course_structure.get('contents', [])
            
            if not contents:
                print("   ⚠️  No course sections found")
                return []
            
            print(f"   📚 Found {len(contents)} sections in course")
            
            # Aggregate scores from all sections
            all_scores = []
            section_count = 0
            
            for section in contents:
                section_id_current = section.get('id')
                
                # Validate section_id
                if section_id_current is None:
                    print(f"   ⚠️  Skipping section without ID: {section.get('name', 'Unknown')}")
                    continue
                
                # Ensure section_id is integer
                try:
                    section_id_current = int(section_id_current)
                except (ValueError, TypeError):
                    print(f"   ⚠️  Invalid section ID: {section_id_current}")
                    continue
                
                section_count += 1
                
                # Get scores for this section with all required params
                params = {
                    'userid': user_id,
                    'courseid': effective_course_id,
                    'sectionid': section_id_current
                }
                
                function_name = 'local_userlog_get_score_section'
                result = self._call_api(function_name, params)
                
                if 'error' not in result and 'exception' not in result:
                    section_scores = result.get('scores', [])
                    all_scores.extend(section_scores)
                    if section_scores:
                        print(f"   ✓ Section {section_id_current}: {len(section_scores)} scores")
                else:
                    error_msg = result.get('message', result.get('error', 'Unknown error'))
                    print(f"   ⚠️  Section {section_id_current}: {error_msg}")
            
            print(f"   ✅ Total: {len(all_scores)} scores from {section_count} sections")
            return all_scores
            
        except Exception as e:
            print(f"   ❌ Error getting scores from all sections: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_lesson_progression(
        self,
        user_id: int,
        course_id: Optional[int] = None
    ) -> Dict:
        """
        Get lesson progression status for a user
        
        Uses: local_adaptivelearning_get_lesson_progression
        
        Args:
            user_id: User ID
            course_id: Course ID (default: self.course_id)
            
        Returns:
            Dictionary with:
            {
                'past_lesson_ids': [14, 15],      # Lessons đã học
                'current_lesson_id': 17,          # Lesson đang học
                'future_lesson_ids': [18, 19, 20], # Lessons chưa học
                'all_lesson_ids': [14, 15, 17, 18, 19, 20]  # Tất cả lessons
            }
        """
        params = {
            'userid': user_id,
            'courseid': course_id or self.course_id
        }
        
        function_name = 'local_adaptivelearning_get_lesson_progression'
        
        print(f"\n🔍 API Call: {function_name}")
        print(f"   Params: userid={user_id}, courseid={params['courseid']}")
        
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"   ⚠️  Error fetching lesson progression: {result['error']}")
            # Return empty structure on error
            return {
                'past_lesson_ids': [],
                'current_lesson_id': None,
                'future_lesson_ids': [],
                'all_lesson_ids': []
            }
        
        # Ensure all required fields exist
        progression = {
            'past_lesson_ids': result.get('past_lesson_ids', []),
            'current_lesson_id': result.get('current_lesson_id'),
            'future_lesson_ids': result.get('future_lesson_ids', []),
            'all_lesson_ids': result.get('all_lesson_ids', [])
        }
        
        print(f"   ✅ Lesson Progression:")
        print(f"      - Past lessons: {progression['past_lesson_ids']}")
        print(f"      - Current lesson: {progression['current_lesson_id']}")
        print(f"      - Future lessons: {progression['future_lesson_ids']}")
        
        return progression
    
    def get_course_structure(self, course_id: Optional[int] = None) -> Dict:
        """
        Get course structure
        
        Custom API Required: mod_adaptivelearning_get_course_structure
        OR use standard: core_course_get_contents
        
        Expected Input Parameters:
        - courseid: int
        
        Expected Output Format:
        {
            "id": 2,
            "fullname": "Course Name",
            "contents": [
                {
                    "id": 1,
                    "name": "Topic 1",
                    "section": 1,
                    "modules": [
                        {
                            "id": 54,
                            "name": "Module 1",
                            "modname": "subsection",
                            "visible": 1,
                            "uservisible": true
                        },
                        ...
                    ]
                },
                ...
            ]
        }
        
        Args:
            course_id: Course ID (optional - uses self.course_id if not provided)
            
        Returns:
            Course structure dictionary
        """
        # Use provided course_id or fall back to instance course_id
        effective_course_id = course_id if course_id is not None else self.course_id
        
        params = {
            'courseid': effective_course_id
        }
        
        # Try custom function first, fallback to standard
        function_name = 'core_course_get_contents'
        
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching course structure: {result['error']}")
            return {'contents': []}
        
        # Wrap in expected format if using standard API
        if isinstance(result, list):
            return {'contents': result}
        
        return result
    
    # ========================================
    # Additional Helper Methods
    # ========================================
    
    def get_quiz_attempts(
        self,
        user_id: int
    ) -> int:
        """
        Get number of quiz attempts by user
        
        Uses: local_userlog_get_quiz_attempts
        
        Args:
            user_id: User ID
            
        Returns:
            Total number of quiz attempts
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_quiz_attempts'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching quiz attempts: {result['error']}")
            return 0
        
        return result.get('attempts', 0)
    
    def get_total_quiz_time(
        self,
        user_id: int
    ) -> int:
        """
        Get total time spent on quizzes (in seconds)
        
        Uses: local_userlog_get_total_quiz_time
        
        Args:
            user_id: User ID
            
        Returns:
            Total quiz time in seconds
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_total_quiz_time'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching total quiz time: {result['error']}")
            return 0
        
        return result.get('total_time', 0)
    
    def get_resource_views(
        self,
        user_id: int
    ) -> Dict:
        """
        Get number of resource views by type
        
        Uses: local_userlog_get_resource_views
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with view counts by resource type
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_resource_views'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching resource views: {result['error']}")
            return {}
        
        return result
    
    def get_learning_days(
        self,
        user_id: int
    ) -> int:
        """
        Get number of distinct learning days
        
        Uses: local_userlog_get_learning_days
        
        Args:
            user_id: User ID
            
        Returns:
            Number of learning days
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_learning_days'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching learning days: {result['error']}")
            return 0
        
        return result.get('learning_days', 0)
    
    def get_avg_quiz_score(
        self,
        user_id: int
    ) -> float:
        """
        Get average quiz score for completed quizzes
        
        Uses: local_userlog_get_avg_quiz_score
        
        Args:
            user_id: User ID
            
        Returns:
            Average score (0-1 scale)
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_avg_quiz_score'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching avg quiz score: {result['error']}")
            return 0.0
        
        return result.get('average_score', 0.0)
    
    def get_section_completion(
        self,
        user_id: int,
        section_id: int
    ) -> Dict:
        """
        Get section completion statistics
        
        Uses: local_userlog_get_section_completion
        
        Args:
            user_id: User ID
            section_id: Section ID
            
        Returns:
            Dict with total, completed, and completion rate
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id,
            'sectionid': section_id
        }
        
        function_name = 'local_userlog_get_section_completion'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching section completion: {result['error']}")
            return {
                'total': 0,
                'completed': 0,
                'rate': 0.0
            }
        
        return result
    
    def get_grade_status(
        self,
        user_id: int
    ) -> Dict:
        """
        Get grade status (pass/fail) for user
        
        Uses: local_userlog_get_grade_status
        
        Args:
            user_id: User ID
            
        Returns:
            Grade status information
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_grade_status'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching grade status: {result['error']}")
            return {'status': 'unknown'}  # MOCKUP
        
        return result
    
    def get_total_study_time(
        self,
        user_id: int
    ) -> int:
        """
        Get estimated total study time (in seconds)
        
        Uses: local_userlog_get_total_study_time
        
        Args:
            user_id: User ID
            
        Returns:
            Total study time in seconds
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_total_study_time'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching total study time: {result['error']}")
            return 0
        
        return result.get('total_time', 0)
    
    def get_user_activity_summary(
        self,
        user_id: int
    ) -> Dict:
        """
        Get comprehensive user activity summary
        
        Uses: local_userlog_get_user_object_activity_summary
        
        Args:
            user_id: User ID
            
        Returns:
            Activity summary dictionary
        """
        params = {
            'userid': user_id,
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_user_object_activity_summary'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching activity summary: {result['error']}")
            return {}
        
        return result
    
    def get_quiz_questions(
        self,
        quiz_id: int
    ) -> List[Dict]:
        """
        Get questions from a specific quiz
        
        Uses: local_userlog_get_quiz_questions
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            List of quiz questions
        """
        params = {
            'quizid': quiz_id
        }
        
        function_name = 'local_userlog_get_quiz_questions'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching quiz questions: {result['error']}")
            return []
        
        return result.get('questions', [])
    
    def get_enrolled_users(self, course_id: Optional[int] = None) -> List[Dict]:
        """
        Get list of enrolled users in a course
        
        Uses: core_enrol_get_enrolled_users (standard Moodle API)
        
        Args:
            course_id: Course ID (default: self.course_id)
            
        Returns:
            List of user dictionaries with id, username, firstname, lastname, email
        """
        params = {
            'courseid': course_id or self.course_id
        }
        
        function_name = 'core_enrol_get_enrolled_users'
        
        print(f"\n🔍 API Call: {function_name}")
        print(f"   Params: courseid={course_id or self.course_id}")
        
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"   ❌ Error fetching enrolled users: {result['error']}")
            return []
        
        # Result is array of user objects
        users = result if isinstance(result, list) else []
        print(f"   ✅ Found {len(users)} enrolled users")
        
        return users
    
    def get_grade_course(self) -> List[Dict]:
        """
        Get grade information for all users in course
        
        Uses: local_userlog_get_grade_course
        
        Returns:
            List of user grades
        """
        params = {
            'courseid': self.course_id
        }
        
        function_name = 'local_userlog_get_grade_course'
        result = self._call_api(function_name, params)
        
        if 'error' in result:
            print(f"Error fetching course grades: {result['error']}")
            return []
        
        return result.get('grades', [])
    
    def get_bulk_user_data(
        self,
        user_ids: List[int],
        module_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[int, Dict]:
        """
        Get data for multiple users (batch processing)
        
        Args:
            user_ids: List of user IDs
            module_id: Module/Section ID
            start_time: Start time for logs
            end_time: End time for logs
            
        Returns:
            Dictionary mapping user_id -> {logs, cluster, progress, scores}
        """
        user_data = {}
        
        for user_id in user_ids:
            try:
                # Get logs (requires module_id)
                logs = self.get_user_logs(user_id, module_id, start_time, end_time)
                
                # Get cluster (MOCKUP)
                cluster = self.get_user_cluster(user_id)
                
                # Get scores
                scores = self.get_user_scores(user_id)
                
                # Get progress
                progress = self.get_module_progress(user_id, module_id)
                
                user_data[user_id] = {
                    'user_id': user_id,
                    'cluster_id': cluster,  # MOCKUP
                    'logs': logs,
                    'scores': scores,
                    'progress': progress
                }
                
            except Exception as e:
                print(f"Error fetching data for user {user_id}: {e}")
                continue
        
        return user_data


def test_moodle_api_client():
    """Test Moodle API Client with actual connection"""
    print("=" * 70)
    print("Testing MoodleAPIClient")
    print("=" * 70)
    
    # Initialize with actual credentials
    client = MoodleAPIClient()
    
    print("\n1. Testing API Connection:")
    print("   Testing basic API call...")
    
    # Test with sample user ID and module ID
    test_user_id = 2
    test_module_id = 1
    test_section_id = 1
    
    try:
        # Test get_user_logs (requires module_id)
        print(f"\n2. Testing get_user_logs(user_id={test_user_id}, module_id={test_module_id})...")
        logs = client.get_user_logs(test_user_id, test_module_id)
        print(f"   ✓ Retrieved {len(logs)} logs")
        if logs:
            print(f"   Sample log: {logs[0]}")
        
        # Test get_user_scores
        print(f"\n3. Testing get_user_scores(user_id={test_user_id})...")
        scores = client.get_user_scores(test_user_id)
        print(f"   ✓ Retrieved {len(scores)} scores")
        if scores:
            print(f"   Sample score: {scores[0]}")
        
        # Test get_module_progress
        print(f"\n4. Testing get_module_progress(user_id={test_user_id}, module_id={test_module_id})...")
        progress = client.get_module_progress(test_user_id, test_module_id)
        print(f"   ✓ Progress: {progress}")
        
        # Test get_user_cluster (MOCKUP)
        print(f"\n5. Testing get_user_cluster(user_id={test_user_id})...")
        cluster = client.get_user_cluster(test_user_id)
        print(f"   ✓ Cluster: {cluster} (MOCKUP - always returns 3)")
        
        # Test additional methods
        print(f"\n6. Testing additional helper methods...")
        
        quiz_attempts = client.get_quiz_attempts(test_user_id)
        print(f"   - Quiz attempts: {quiz_attempts}")
        
        total_quiz_time = client.get_total_quiz_time(test_user_id)
        print(f"   - Total quiz time: {total_quiz_time}s")
        
        learning_days = client.get_learning_days(test_user_id)
        print(f"   - Learning days: {learning_days}")
        
        avg_score = client.get_avg_quiz_score(test_user_id)
        print(f"   - Average quiz score: {avg_score}")
        
        section_completion = client.get_section_completion(test_user_id, test_section_id)
        print(f"   - Section completion: {section_completion}")
        
    except Exception as e:
        print(f"   ✗ Error during testing: {e}")
    
    print("\n" + "=" * 70)
    print("Available API Methods:")
    print("=" * 70)
    methods = [
        ("get_user_logs", "Get user learning logs (requires module_id)", "✓"),
        ("get_user_cluster", "Get user cluster assignment", "⚠️ MOCKUP"),
        ("get_module_progress", "Get module completion rate", "✓"),
        ("get_user_scores", "Get quiz scores", "✓"),
        ("get_course_structure", "Get course structure", "✓"),
        ("get_quiz_attempts", "Get quiz attempt count", "✓"),
        ("get_total_quiz_time", "Get total quiz time", "✓"),
        ("get_resource_views", "Get resource view counts", "✓"),
        ("get_learning_days", "Get learning days count", "✓"),
        ("get_avg_quiz_score", "Get average quiz score", "✓"),
        ("get_section_completion", "Get section completion stats", "✓"),
        ("get_grade_status", "Get user grade status", "✓"),
        ("get_total_study_time", "Get total study time", "✓"),
        ("get_user_activity_summary", "Get activity summary", "✓"),
        ("get_quiz_questions", "Get quiz questions", "✓"),
        ("get_grade_course", "Get all user grades in course", "✓"),
    ]
    
    for method, desc, status in methods:
        print(f"{status} {method:<30} - {desc}")
    
    print("\n" + "=" * 70)
    print("API Configuration:")
    # Test get_enrolled_users
    print("\n" + "=" * 70)
    print("Test: get_enrolled_users()")
    print("=" * 70)
    enrolled_users = client.get_enrolled_users()
    print(f"✓ Found {len(enrolled_users)} enrolled users")
    if enrolled_users:
        print(f"  Sample user: {enrolled_users[0]}")
    
    print("=" * 70)
    print(f"Moodle URL: {client.moodle_url}")
    print(f"Course ID: {client.course_id}")
    print(f"Token: {client.ws_token[:10]}...")
    
    print("\n" + "=" * 70)
    print("MOCKUP Fields (not yet available in API):")
    print("=" * 70)
    print("⚠️  get_user_cluster() - Returns default cluster 3")
    print("⚠️  time_spent in get_module_progress() - Returns 0")
    print("=" * 70)
    print("✓ MoodleAPIClient completed and ready to use!")
    print("=" * 70)


if __name__ == '__main__':
    test_moodle_api_client()
