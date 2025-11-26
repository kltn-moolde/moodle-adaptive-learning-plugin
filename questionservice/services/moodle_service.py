#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle Service
==============
Service for interacting with Moodle Web Services API
"""

import requests
import urllib.parse
import json
from typing import Dict
from utils.logger import setup_logger
from utils.exceptions import MoodleAPIError, MoodleConnectionError, MoodleImportError

logger = setup_logger('moodle_service')


class MoodleAPIClient:
    """Client for Moodle Web Services REST API"""
    
    def __init__(self, moodle_url: str, token: str):
        """Initialize Moodle API client"""
        if not moodle_url:
            raise MoodleConnectionError("Moodle URL is required")
        if not token:
            raise MoodleConnectionError("Moodle token is required")
        
        self.moodle_url = moodle_url.rstrip('/')
        self.token = token
        self.ws_url = f"{self.moodle_url}/webservice/rest/server.php"
    
    def import_questions_xml_simple(
        self,
        xml_content: bytes,
        course_id: int
    ) -> Dict:
        """
        Import questions using custom Moodle API: local_userlog_import_questions_from_xml
        
        Args:
            xml_content: XML content as bytes
            course_id: Target course ID
            
        Returns:
            Response dictionary from Moodle API
        """
        # Decode XML bytes to string
        xml_string = xml_content.decode('utf-8')
        
        # Build request parameters (form data)
        # xmlcontent cần được URL encode (giống --data-urlencode trong curl)
        params = {
            'wstoken': self.token,
            'moodlewsrestformat': 'json',
            'wsfunction': 'local_userlog_import_questions_from_xml',
            'courseid': course_id,
            'xmlcontent': xml_string  # requests sẽ tự encode khi dùng data=
        }
        
        # Make POST request với form data (giống curl -d)
        response = requests.post(self.ws_url, data=params, timeout=30)
        response.raise_for_status()
        
        # Extract JSON from response (có thể có HTML ở đầu)
        response_text = response.text
        
        # Tìm JSON object cuối cùng trong response
        json_start = -1
        for i in range(len(response_text) - 1, -1, -1):
            if response_text[i] == '{':
                json_start = i
                break
        
        if json_start >= 0:
            json_text = response_text[json_start:]
            result = json.loads(json_text)
        else:
            raise MoodleAPIError("No JSON found in response")
        
        # Check for errors
        if isinstance(result, dict) and ('exception' in result or 'error' in result):
            error_msg = result.get('message', result.get('error', 'Unknown error'))
            raise MoodleImportError(f"Import error: {error_msg}")
        
        return result
