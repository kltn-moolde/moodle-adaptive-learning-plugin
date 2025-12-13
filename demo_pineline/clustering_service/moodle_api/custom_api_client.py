#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle Custom API Client
=========================
Client for local_* endpoints using custom token
"""

import requests
import logging
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class MoodleCustomAPIClient:
    """Client for Moodle custom API endpoints (local_*)"""
    
    def __init__(self, base_url: str, token: str, endpoint: str = "/webservice/rest/server.php"):
        """
        Initialize Moodle Custom API client
        
        Args:
            base_url: Moodle base URL (e.g., http://localhost:8100)
            token: Custom API token for local_* endpoints
            endpoint: Web service endpoint path
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.endpoint = f"{self.base_url}{endpoint}"
        self.timeout = 60
        
        logger.info(f"Initialized MoodleCustomAPIClient for {self.base_url}")
    
    def _make_request(self, wsfunction: str, params: Optional[Dict] = None) -> Dict:
        """
        Make request to Moodle web service
        
        Args:
            wsfunction: Web service function name
            params: Additional parameters
            
        Returns:
            Response data as dictionary
        """
        request_params = {
            'wstoken': self.token,
            'wsfunction': wsfunction,
            'moodlewsrestformat': 'json'
        }
        
        if params:
            request_params.update(params)
        
        try:
            logger.debug(f"Calling {wsfunction} with params: {params}")
            response = requests.get(self.endpoint, params=request_params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for Moodle error responses
            if isinstance(data, dict) and 'exception' in data:
                error_msg = data.get('message', 'Unknown Moodle error')
                logger.error(f"Moodle API error: {error_msg}")
                raise Exception(f"Moodle API error: {error_msg}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {wsfunction}: {str(e)}")
            raise
    
    def get_logs_course(self, course_id: int, limit: int = 1000000) -> pd.DataFrame:
        """
        Fetch user logs for a course
        
        Args:
            course_id: Moodle course ID
            limit: Maximum number of log entries to fetch
            
        Returns:
            DataFrame with log entries (event_name and action columns)
        """
        logger.info(f"Fetching logs for course {course_id} (limit: {limit})")
        
        params = {
            'courseid': course_id,
            'limit': limit
        }
        
        data = self._make_request('local_userlog_get_logs_course', params)
        
        if not data or not isinstance(data, list):
            logger.warning(f"No logs found for course {course_id}")
            return pd.DataFrame(columns=['userid', 'event_name', 'action', 'timecreated'])
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        logger.info(f"Retrieved {len(df)} log entries for course {course_id}")
        logger.debug(f"Columns in response: {df.columns.tolist()}")
        
        # Ensure required columns exist
        required_columns = ['userid', 'eventname', 'action', 'timecreated']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
            for col in missing_columns:
                df[col] = None
        
        # Focus on eventname and action as per user requirement
        return df[required_columns]
    
    def get_enrolled_students(self, course_id: int) -> List[int]:
        """
        Get list of student user IDs enrolled in a course
        Note: This uses the custom API - may need to be implemented in Moodle plugin
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of student user IDs
        """
        logger.info(f"Fetching enrolled students for course {course_id}")
        
        try:
            # Try custom endpoint first
            params = {'courseid': course_id}
            data = self._make_request('local_userlog_get_enrolled_students', params)
            
            if isinstance(data, list):
                user_ids = [item['userid'] for item in data if 'userid' in item]
                logger.info(f"Found {len(user_ids)} students in course {course_id}")
                return user_ids
            
        except Exception as e:
            logger.warning(f"Failed to get students via custom API: {str(e)}")
        
        # Fallback: Extract unique user IDs from logs
        logs_df = self.get_logs_course(course_id, limit=100000)
        if not logs_df.empty and 'userid' in logs_df.columns:
            user_ids = logs_df['userid'].dropna().unique().astype(int).tolist()
            logger.info(f"Extracted {len(user_ids)} unique users from logs")
            return user_ids
        
        logger.warning(f"No students found for course {course_id}")
        return []
