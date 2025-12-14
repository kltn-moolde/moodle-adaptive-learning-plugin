"""
Moodle API Service
Handles communication with Moodle Web Services API
"""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.models.user_log import UserLog
from loguru import logger


class MoodleService:
    """Service for interacting with Moodle Web Services API"""
    
    def __init__(self):
        self.api_url = settings.MOODLE_API_URL
        self.api_token = settings.MOODLE_API_TOKEN
        
    async def _make_request(self, function: str, **params) -> Dict[str, Any]:
        """
        Make a request to Moodle Web Services API
        """
        request_params = {
            "wstoken": self.api_token,
            "wsfunction": function,
            "moodlewsrestformat": "json",
            **params
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, data=request_params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making request to Moodle API: {e}")
            raise
    
    async def get_user_logs(self, course_id: str, user_id: Optional[str] = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user activity logs from Moodle
        """
        try:
            # Use core_report_get_course_participants or similar function
            # This is a simplified implementation - adjust based on your Moodle setup
            
            # For demo purposes, return mock data
            mock_logs = [
                {
                    "id": 1,
                    "user_id": user_id or "1",
                    "course_id": course_id,
                    "action": "view",
                    "target": "course_module",
                    "object_table": "course_modules",
                    "object_id": "123",
                    "crud": "r",
                    "event_name": "\\mod_page\\event\\course_module_viewed",
                    "component": "mod_page",
                    "time_created": datetime.utcnow().isoformat(),
                    "ip": "192.168.1.100",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                {
                    "id": 2,
                    "user_id": user_id or "1",
                    "course_id": course_id,
                    "action": "submit",
                    "target": "assessable",
                    "object_table": "assign_submission",
                    "object_id": "456",
                    "crud": "c",
                    "event_name": "\\mod_assign\\event\\assessable_submitted",
                    "component": "mod_assign",
                    "time_created": datetime.utcnow().isoformat(),
                    "ip": "192.168.1.100",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                {
                    "id": 3,
                    "user_id": user_id or "1",
                    "course_id": course_id,
                    "action": "view",
                    "target": "user_profile",
                    "object_table": "user",
                    "object_id": user_id or "1",
                    "crud": "r",
                    "event_name": "\\core\\event\\user_profile_viewed",
                    "component": "core",
                    "time_created": datetime.utcnow().isoformat(),
                    "ip": "192.168.1.100",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            ]
            
            return mock_logs
            
        except Exception as e:
            logger.error(f"Error getting user logs: {e}")
            # Return empty list on error for now
            return []
    
    async def get_course_info(self, course_id: str) -> Dict[str, Any]:
        """
        Get course information from Moodle
        """
        try:
            result = await self._make_request(
                "core_course_get_courses_by_field",
                field="id",
                value=course_id
            )
            
            if result and "courses" in result and len(result["courses"]) > 0:
                return result["courses"][0]
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting course info: {e}")
            return {}
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information from Moodle
        """
        try:
            result = await self._make_request(
                "core_user_get_users_by_field",
                field="id",
                values=[user_id]
            )
            
            if result and len(result) > 0:
                return result[0]
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    async def get_course_participants(self, course_id: str) -> List[Dict[str, Any]]:
        """
        Get course participants from Moodle
        """
        try:
            result = await self._make_request(
                "core_enrol_get_enrolled_users",
                courseid=course_id
            )
            
            return result if result else []
            
        except Exception as e:
            logger.error(f"Error getting course participants: {e}")
            return []


# Global service instance
moodle_service = MoodleService()
