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
import re
import time
from typing import Dict, List, Tuple
from xml.etree import ElementTree as ET
from utils.logger import setup_logger
from utils.exceptions import MoodleAPIError, MoodleConnectionError, MoodleImportError

logger = setup_logger('moodle_service')


class MoodleAPIClient:
    """Client for Moodle Web Services REST API"""
    
    MAX_XML_SIZE = 300 * 1024  # 300KB - ngưỡng tối đa cho 1 request
    MAX_QUESTIONS_PER_BATCH = 5  # Số câu hỏi tối đa mỗi batch
    
    def __init__(self, moodle_url: str, token: str):
        """Initialize Moodle API client"""
        if not moodle_url:
            raise MoodleConnectionError("Moodle URL is required")
        if not token:
            raise MoodleConnectionError("Moodle token is required")
        
        self.moodle_url = moodle_url.rstrip('/')
        self.token = token
        self.ws_url = f"{self.moodle_url}/webservice/rest/server.php"
    
    def _measure_xml_content(self, xml_content: bytes) -> Dict:
        """Đo độ dài XML content"""
        size_bytes = len(xml_content)
        size_kb = size_bytes / 1024
        xml_string = xml_content.decode('utf-8')
        question_count = xml_string.count('<question type=')
        
        logger.info(f"XML Analysis - Size: {size_kb:.2f}KB, Questions: {question_count}")
        
        return {
            'size_bytes': size_bytes,
            'size_kb': size_kb,
            'question_count': question_count,
            'needs_splitting': size_bytes > self.MAX_XML_SIZE or question_count > self.MAX_QUESTIONS_PER_BATCH
        }

    def _split_xml_content(self, xml_content: bytes) -> List[bytes]:
        """Chia XML thành các batch nhỏ hơn"""
        xml_string = xml_content.decode('utf-8')
        
        try:
            # Parse XML để lấy các question elements
            root = ET.fromstring(xml_string)
            questions = root.findall('.//question')
            
            if len(questions) <= self.MAX_QUESTIONS_PER_BATCH:
                return [xml_content]
            
            # Chia thành các batch
            batches = []
            for i in range(0, len(questions), self.MAX_QUESTIONS_PER_BATCH):
                batch_questions = questions[i:i + self.MAX_QUESTIONS_PER_BATCH]
                
                # Tạo XML mới cho batch
                new_root = ET.Element('quiz')
                for question in batch_questions:
                    new_root.append(question)
                
                # Convert về string
                batch_xml_str = ET.tostring(new_root, encoding='unicode', xml_declaration=True)
                batch_xml_str = batch_xml_str.replace(
                    "<?xml version='1.0' encoding='unicode'?>",
                    "<?xml version='1.0' encoding='UTF-8'?>"
                )
                batches.append(batch_xml_str.encode('utf-8'))
            
            logger.info(f"Split XML into {len(batches)} batches")
            return batches
            
        except ET.ParseError:
            # Fallback: split bằng regex
            return self._split_xml_by_pattern(xml_string)

    def _split_xml_by_pattern(self, xml_string: str) -> List[bytes]:
        """Chia XML bằng cách sử dụng regex pattern (fallback method)"""
        question_pattern = r'(<question[^>]*>.*?</question>)'
        questions = re.findall(question_pattern, xml_string, re.DOTALL)
        
        if len(questions) <= self.MAX_QUESTIONS_PER_BATCH:
            return [xml_string.encode('utf-8')]
        
        batches = []
        
        for i in range(0, len(questions), self.MAX_QUESTIONS_PER_BATCH):
            batch_questions = questions[i:i + self.MAX_QUESTIONS_PER_BATCH]
            
            batch_xml = "<?xml version='1.0' encoding='UTF-8'?>\n<quiz>\n"
            for question in batch_questions:
                batch_xml += f"  {question}\n"
            batch_xml += "</quiz>"
            
            batches.append(batch_xml.encode('utf-8'))
        
        logger.info(f"Split XML into {len(batches)} batches using pattern matching")
        return batches

    def _import_single_batch(self, xml_batch: bytes, course_id: int, batch_number: int, total_batches: int) -> Dict:
        """Import một batch XML"""
        xml_string = xml_batch.decode('utf-8')
        
        # Build request parameters
        params = {
            'wstoken': self.token,
            'moodlewsrestformat': 'json',
            'wsfunction': 'local_userlog_import_questions_from_xml',
            'courseid': course_id,
            'xmlcontent': xml_string
        }
        
        try:
            logger.info(f"Importing batch {batch_number}/{total_batches}")
            
            # Make POST request
            response = requests.post(self.ws_url, data=params, timeout=30)
            response.raise_for_status()
            
            # Extract JSON from response
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
            
            logger.info(f"Batch {batch_number}/{total_batches} imported successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to import batch {batch_number}: {e}")
            raise MoodleImportError(f"Failed to import batch {batch_number}: {e}")

    def import_questions_xml_simple(
        self,
        xml_content: bytes,
        course_id: int
    ) -> Dict:
        """
        Import questions using custom Moodle API với support cho XML dài
        
        Args:
            xml_content: XML content as bytes
            course_id: Target course ID
            
        Returns:
            Response dictionary from Moodle API (aggregated from all batches)
        """
        logger.info("======================================================================")
        logger.info("STARTING MOODLE XML IMPORT WITH ENHANCED PROCESSING")
        logger.info("======================================================================")
        
        # Bước 1: Đo độ dài và phân tích XML
        xml_analysis = self._measure_xml_content(xml_content)
        
        # Bước 2: Xử lý theo kích thước
        if not xml_analysis['needs_splitting']:
            # XML nhỏ, import trực tiếp
            logger.info("XML size is acceptable, importing directly...")
            return self._import_single_batch(xml_content, course_id, 1, 1)
        
        # Bước 3: XML lớn, chia thành batches
        logger.info("XML is too large, splitting into batches...")
        xml_batches = self._split_xml_content(xml_content)
        
        # Bước 4: Import từng batch và gộp kết quả
        total_imported = 0
        all_warnings = []
        first_result = None
        
        for i, batch in enumerate(xml_batches, 1):
            try:
                result = self._import_single_batch(batch, course_id, i, len(xml_batches))
                
                # Lưu kết quả đầu tiên làm template
                if first_result is None:
                    first_result = result.copy()
                
                # Gộp kết quả
                if isinstance(result, dict):
                    imported_count = result.get('importedcount', 0)
                    total_imported += imported_count
                    
                    warnings = result.get('warnings', [])
                    all_warnings.extend(warnings)
                    
                    logger.info(f"Batch {i} result: {imported_count} questions imported")
                
            except Exception as e:
                logger.error(f"Failed to import batch {i}: {e}")
                # Có thể tiếp tục với các batch khác hoặc stop tùy yêu cầu
                # Ở đây chúng ta tiếp tục để import tối đa có thể
                continue
        
        # Bước 5: Tạo kết quả tổng hợp (giữ nguyên format như yêu cầu)
        if first_result is None:
            # Nếu không có batch nào thành công
            return {
                "success": False,
                "importedcount": 0,
                "categoryid": None,
                "instanceid": None,
                "warnings": ["All batches failed to import"]
            }
        
        # Cập nhật kết quả tổng hợp
        aggregated_result = {
            "success": True,
            "importedcount": total_imported,
            "categoryid": first_result.get('categoryid'),
            "instanceid": first_result.get('instanceid'),
            "warnings": all_warnings
        }
        
        logger.info("======================================================================")
        logger.info("MOODLE IMPORT COMPLETED")
        logger.info(f"Total imported: {total_imported} questions across {len(xml_batches)} batches")
        logger.info("======================================================================")
        
        return aggregated_result
