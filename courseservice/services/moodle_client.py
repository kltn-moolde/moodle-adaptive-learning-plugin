#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle API Client
=================
Clean, robust Moodle API integration with error handling and logging
"""

import requests
from typing import Dict, List, Any, Optional
from config import Config
from utils.logger import setup_logger, log_execution_time
from utils.exceptions import MoodleAPIError, ValidationError

logger = setup_logger('moodle_client')


class MoodleClient:
    """Moodle API Client with clean interface"""
    
    def __init__(self):
        self.base_url = Config.MOODLE_API_BASE
        self.token = Config.MOODLE_TOKEN
        self.headers = {"Host": Config.ADDRESS_MOODLE}
        self.timeout = 30
        
        logger.info(f"Initialized Moodle client: {self.base_url}")
    
    def _make_request(self, function_name: str, params: Dict[str, Any]) -> Any:
        """
        Generic Moodle API request handler
        
        Args:
            function_name: Moodle webservice function name
            params: Additional parameters
            
        Returns:
            JSON response from Moodle
            
        Raises:
            MoodleAPIError: If request fails
        """
        request_params = {
            "wstoken": self.token,
            "wsfunction": function_name,
            "moodlewsrestformat": "json",
            **params
        }
        
        try:
            logger.debug(f"→ Calling Moodle API: {function_name}")
            logger.debug(f"  Params: {params}")
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=request_params,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for Moodle error response
            if isinstance(data, dict) and 'exception' in data:
                error_msg = data.get('message', 'Unknown Moodle error')
                logger.error(f"✗ Moodle API error: {error_msg}")
                raise MoodleAPIError(
                    f"Moodle API error: {error_msg}",
                    details={'function': function_name, 'response': data}
                )
            
            logger.debug(f"✓ Moodle API success: {function_name}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"✗ Moodle API timeout: {function_name}")
            raise MoodleAPIError(
                "Moodle API request timeout",
                details={'function': function_name, 'timeout': self.timeout}
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Moodle API request failed: {str(e)}")
            raise MoodleAPIError(
                f"Moodle API request failed: {str(e)}",
                details={'function': function_name}
            )
    
    @log_execution_time
    def get_courses(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tất cả khóa học
        
        Returns:
            List of course objects
        """
        logger.info("Fetching all courses from Moodle")
        courses = self._make_request("core_course_get_courses", {})
        logger.info(f"✓ Retrieved {len(courses)} courses")
        return courses
    
    @log_execution_time
    def get_course_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết 1 khóa học
        
        Args:
            course_id: ID của khóa học
            
        Returns:
            Course object hoặc None nếu không tìm thấy
        """
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValidationError(f"Invalid course_id: {course_id}")
        
        logger.info(f"Fetching course: {course_id}")
        
        result = self._make_request(
            "core_course_get_courses_by_field",
            {"field": "id", "value": course_id}
        )
        
        courses = result.get("courses", [])
        if not courses:
            logger.warning(f"Course not found: {course_id}")
            return None
        
        logger.info(f"✓ Retrieved course: {courses[0].get('fullname', 'N/A')}")
        return courses[0]
    
    @log_execution_time
    def get_course_contents(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Lấy nội dung (sections, modules) của khóa học
        
        Args:
            course_id: ID của khóa học
            
        Returns:
            List of section objects với modules
        """
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValidationError(f"Invalid course_id: {course_id}")
        
        logger.info(f"Fetching course contents: {course_id}")
        
        contents = self._make_request(
            "core_course_get_contents",
            {"courseid": course_id}
        )
        
        total_modules = sum(len(section.get('modules', [])) for section in contents)
        logger.info(f"✓ Retrieved {len(contents)} sections, {total_modules} modules")
        
        return contents
    
    @log_execution_time
    def get_enrolled_users(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Lấy danh sách users enrolled trong khóa học
        
        Args:
            course_id: ID của khóa học
            
        Returns:
            List of user objects
        """
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValidationError(f"Invalid course_id: {course_id}")
        
        logger.info(f"Fetching enrolled users: {course_id}")
        
        users = self._make_request(
            "core_enrol_get_enrolled_users",
            {"courseid": course_id}
        )
        
        logger.info(f"✓ Retrieved {len(users)} enrolled users")
        return users
    
    def health_check(self) -> bool:
        """
        Kiểm tra kết nối Moodle API
        
        Returns:
            True nếu kết nối thành công
        """
        try:
            logger.info("Performing Moodle health check")
            self.get_courses()
            logger.info("✓ Moodle health check passed")
            return True
        except Exception as e:
            logger.error(f"✗ Moodle health check failed: {str(e)}")
            return False


# Singleton instance
_moodle_client = None


def get_moodle_client() -> MoodleClient:
    """Get singleton Moodle client instance"""
    global _moodle_client
    if _moodle_client is None:
        _moodle_client = MoodleClient()
    return _moodle_client


# Backward compatibility functions
def get_courses_from_moodle():
    """Legacy function - use get_moodle_client().get_courses() instead"""
    return get_moodle_client().get_courses()


def get_course_contents(course_id):
    """Legacy function - use get_moodle_client().get_course_contents() instead"""
    return get_moodle_client().get_course_contents(course_id)


def get_course_by_id(course_id: int):
    """Legacy function - use get_moodle_client().get_course_by_id() instead"""
    return get_moodle_client().get_course_by_id(course_id)


def get_moodle_course_users(course_id):
    """Legacy function - use get_moodle_client().get_enrolled_users() instead"""
    return get_moodle_client().get_enrolled_users(course_id)


def get_moodle_user_detail(user_id):
    """Get user details by ID"""
    client = get_moodle_client()
    logger.info(f"Fetching user details: {user_id}")
    
    result = client._make_request(
        "core_user_get_users_by_field",
        {
            "field": "id",
            "values[0]": user_id
        }
    )
    
    if result and len(result) > 0:
        logger.info(f"✓ Retrieved user: {result[0].get('fullname', 'N/A')}")
        return result[0]
    
    logger.warning(f"User not found: {user_id}")
    return None

    hierarchy = process_sections(course_data)
    return clean_structure(hierarchy)