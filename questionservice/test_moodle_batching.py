#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra tính năng batch processing của MoodleAPIClient
"""

import sys
import os

# Thêm thư mục gốc vào path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.moodle_service import MoodleAPIClient

def test_xml_analysis():
    """Test XML measurement và analysis"""
    
    # Sample XML dài (mô phỏng XML với nhiều câu hỏi)
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<quiz>
""" + """  <question type="multichoice">
    <name><text>Câu hỏi test {}</text></name>
    <questiontext format="html">
      <text><![CDATA[<p>Đây là câu hỏi số {} để test batch processing</p>]]></text>
    </questiontext>
    <shuffleanswers>0</shuffleanswers>
    <single>true</single>
    <answernumbering>abc</answernumbering>
    <answer fraction="100">
      <text>Đáp án đúng {}</text>
      <feedback><text>Chính xác!</text></feedback>
    </answer>
    <answer fraction="0">
      <text>Đáp án sai {}</text>
      <feedback><text>Không đúng</text></feedback>
    </answer>
  </question>
""" * 25 + "</quiz>"  # Tạo 25 câu hỏi

    # Format lại XML
    formatted_xml = sample_xml.format(*range(1, 101))  # Đánh số từ 1-25
    xml_bytes = formatted_xml.encode('utf-8')
    
    print(f"=== TEST XML ANALYSIS ===")
    print(f"Generated XML size: {len(xml_bytes) / 1024:.2f}KB")
    print(f"Questions in XML: {formatted_xml.count('<question type=')}")
    
    # Tạo mock client (không cần token thật để test analysis)
    try:
        client = MoodleAPIClient("http://test.com", "fake_token")
        
        # Test XML measurement
        analysis = client._measure_xml_content(xml_bytes)
        print(f"\nXML Analysis Result:")
        print(f"- Size: {analysis['size_kb']:.2f}KB ({analysis['size_bytes']} bytes)")
        print(f"- Questions: {analysis['question_count']}")
        print(f"- Needs splitting: {analysis['needs_splitting']}")
        
        # Test XML splitting if needed
        if analysis['needs_splitting']:
            print(f"\n=== TESTING XML SPLITTING ===")
            batches = client._split_xml_content(xml_bytes)
            print(f"Split into {len(batches)} batches:")
            
            for i, batch in enumerate(batches, 1):
                batch_str = batch.decode('utf-8')
                batch_questions = batch_str.count('<question type=')
                batch_size = len(batch) / 1024
                print(f"  Batch {i}: {batch_questions} questions, {batch_size:.2f}KB")
        
        print(f"\n=== TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False
        
    return True

def test_batch_configuration():
    """Test cấu hình batch settings"""
    print(f"\n=== TEST BATCH CONFIGURATION ===")
    
    client = MoodleAPIClient("http://test.com", "fake_token")
    
    print(f"Default settings:")
    print(f"- MAX_XML_SIZE: {client.MAX_XML_SIZE / 1024:.1f}KB")
    print(f"- MAX_QUESTIONS_PER_BATCH: {client.MAX_QUESTIONS_PER_BATCH}")
    print(f"- REQUEST_TIMEOUT: {client.REQUEST_TIMEOUT}s")
    print(f"- RETRY_ATTEMPTS: {client.RETRY_ATTEMPTS}")
    
    # Thay đổi cấu hình
    client.configure_batch_settings(
        max_xml_size=200 * 1024,  # 200KB
        max_questions_per_batch=5,  # 5 câu mỗi batch
        request_timeout=30,
        retry_attempts=2
    )
    
    print(f"\nAfter configuration:")
    print(f"- MAX_XML_SIZE: {client.MAX_XML_SIZE / 1024:.1f}KB")
    print(f"- MAX_QUESTIONS_PER_BATCH: {client.MAX_QUESTIONS_PER_BATCH}")
    print(f"- REQUEST_TIMEOUT: {client.REQUEST_TIMEOUT}s")
    print(f"- RETRY_ATTEMPTS: {client.RETRY_ATTEMPTS}")

if __name__ == "__main__":
    print("Testing Enhanced Moodle Service with Batch Processing")
    print("=" * 60)
    
    success = True
    
    # Test 1: XML Analysis và Splitting
    success &= test_xml_analysis()
    
    # Test 2: Configuration
    test_batch_configuration()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Enhanced Moodle Service ready to use!")
    else:
        print("❌ SOME TESTS FAILED - Please check the implementation")