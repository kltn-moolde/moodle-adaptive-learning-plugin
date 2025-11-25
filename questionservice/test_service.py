#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Question Service
=====================
Test script for question service functionality
"""

import requests
import json

BASE_URL = "http://localhost:5003/api/questions"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get("http://localhost:5003/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_question():
    """Test creating a single question"""
    print("\n=== Testing Create Question ===")
    
    question_data = {
        "name": "Test Question 1",
        "question_type": "multichoice",
        "question_text": "<p>Đây là câu hỏi test?</p>",
        "difficulty": "easy",
        "category": "Test Category",
        "answers": [
            {
                "text": "Đáp án đúng",
                "fraction": 100,
                "feedback": "Chính xác!"
            },
            {
                "text": "Đáp án sai 1",
                "fraction": 0,
                "feedback": "Sai rồi"
            },
            {
                "text": "Đáp án sai 2",
                "fraction": 0,
                "feedback": "Không đúng"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/create", json=question_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['question']['id']
    return None

def test_create_batch():
    """Test creating multiple questions"""
    print("\n=== Testing Create Batch ===")
    
    batch_data = {
        "questions": [
            {
                "name": "Batch Question 1",
                "question_type": "multichoice",
                "question_text": "<p>Câu hỏi batch 1?</p>",
                "difficulty": "easy",
                "answers": [
                    {"text": "Đúng", "fraction": 100, "feedback": "Đúng rồi"},
                    {"text": "Sai", "fraction": 0, "feedback": "Sai rồi"}
                ]
            },
            {
                "name": "Batch Question 2",
                "question_type": "multichoice",
                "question_text": "<p>Câu hỏi batch 2?</p>",
                "difficulty": "medium",
                "answers": [
                    {"text": "Đúng", "fraction": 100, "feedback": "Đúng rồi"},
                    {"text": "Sai", "fraction": 0, "feedback": "Sai rồi"}
                ]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/create-batch", json=batch_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return [q['id'] for q in response.json()['questions']]
    return []

def test_get_questions():
    """Test getting questions with filters"""
    print("\n=== Testing Get Questions ===")
    
    response = requests.get(f"{BASE_URL}/?difficulty=easy&page=1&limit=10")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_question(question_id):
    """Test getting a single question"""
    print(f"\n=== Testing Get Question {question_id} ===")
    
    response = requests.get(f"{BASE_URL}/{question_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_update_question(question_id):
    """Test updating a question"""
    print(f"\n=== Testing Update Question {question_id} ===")
    
    update_data = {
        "difficulty": "hard",
        "question_text": "<p>Câu hỏi đã được cập nhật</p>"
    }
    
    response = requests.put(f"{BASE_URL}/{question_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_export_xml(question_ids):
    """Test exporting questions to XML"""
    print("\n=== Testing Export XML ===")
    
    export_data = {
        "question_ids": question_ids,
        "filename": "test_quiz.xml"
    }
    
    response = requests.post(f"{BASE_URL}/export/xml", json=export_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        with open("test_quiz.xml", "wb") as f:
            f.write(response.content)
        print("✓ XML file saved as test_quiz.xml")
    else:
        print(f"Error: {response.text}")

def test_statistics():
    """Test getting statistics"""
    print("\n=== Testing Statistics ===")
    
    response = requests.get(f"{BASE_URL}/statistics")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_delete_question(question_id):
    """Test deleting a question"""
    print(f"\n=== Testing Delete Question {question_id} ===")
    
    response = requests.delete(f"{BASE_URL}/{question_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("="*70)
    print("QUESTION SERVICE - Test Suite")
    print("="*70)
    
    try:
        # Test health check
        test_health_check()
        
        # Test create question
        question_id = test_create_question()
        
        # Test create batch
        batch_ids = test_create_batch()
        
        # Combine IDs
        all_ids = [question_id] + batch_ids if question_id else batch_ids
        
        # Test get questions
        test_get_questions()
        
        # Test get single question
        if question_id:
            test_get_question(question_id)
        
        # Test update question
        if question_id:
            test_update_question(question_id)
        
        # Test export XML
        if all_ids:
            test_export_xml(all_ids)
        
        # Test statistics
        test_statistics()
        
        # Test delete (optional - comment out if you want to keep the data)
        # if question_id:
        #     test_delete_question(question_id)
        
        print("\n" + "="*70)
        print("All tests completed!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the service.")
        print("Make sure the service is running on http://localhost:5003")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    main()
