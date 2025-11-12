#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test AI Generation
==================
Test AI-powered question generation
"""

import requests
import json

BASE_URL = "http://localhost:5003"

def test_ai_generate():
    """Test AI question generation"""
    print("\n" + "="*70)
    print("TEST: AI Generate Questions")
    print("="*70)
    
    data = {
        "topic": "Python Programming - Biến và Kiểu dữ liệu",
        "num_questions": 3,
        "difficulty": "easy",
        "language": "vi",
        "save_to_db": True
    }
    
    print(f"\nTopic: {data['topic']}")
    print(f"Questions: {data['num_questions']}")
    print(f"Difficulty: {data['difficulty']}")
    print(f"Language: {data['language']}")
    print(f"Save to DB: {data['save_to_db']}")
    print("\nGenerating... (this may take 10-20 seconds)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            json=data,
            timeout=60
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✓ {result['message']}")
            
            # Show questions
            questions = result['questions']
            print(f"\nGenerated {len(questions)} questions:")
            print("-" * 70)
            
            for idx, q in enumerate(questions, 1):
                print(f"\n{idx}. {q['name']}")
                print(f"   Difficulty: {q['difficulty']}")
                print(f"   Answers: {len(q['answers'])}")
                correct = sum(1 for a in q['answers'] if a['fraction'] == 100)
                print(f"   Correct: {correct}")
            
            # Show saved IDs
            if 'saved_ids' in result:
                print(f"\n✓ Saved to database with IDs:")
                for qid in result['saved_ids']:
                    print(f"   - {qid}")
                    
                return result['saved_ids']
        else:
            print(f"\n✗ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timeout (AI is taking too long)")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    return []


def test_ai_batch():
    """Test batch generation"""
    print("\n" + "="*70)
    print("TEST: AI Generate Batch")
    print("="*70)
    
    data = {
        "topic": "Python - Vòng lặp và Điều kiện",
        "total_questions": 6,  # Will split into 2 batches of 3
        "difficulty": "medium",
        "language": "vi",
        "save_to_db": False
    }
    
    print(f"\nTopic: {data['topic']}")
    print(f"Total Questions: {data['total_questions']}")
    print(f"Difficulty: {data['difficulty']}")
    print("\nGenerating batch... (this may take 30-60 seconds)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-batch",
            json=data,
            timeout=120
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✓ {result['message']}")
            print(f"   Generated {len(result['questions'])} questions total")
        else:
            print(f"\n✗ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timeout")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def test_export_ai_questions(question_ids):
    """Test exporting AI-generated questions"""
    if not question_ids:
        print("\n⚠ No questions to export")
        return
    
    print("\n" + "="*70)
    print("TEST: Export AI Generated Questions to XML")
    print("="*70)
    
    data = {
        "question_ids": question_ids,
        "filename": "ai_generated_quiz.xml"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/questions/export/xml",
            json=data
        )
        
        if response.status_code == 200:
            with open("ai_generated_quiz.xml", "wb") as f:
                f.write(response.content)
            print(f"\n✓ XML exported: ai_generated_quiz.xml")
        else:
            print(f"\n✗ Error: {response.text}")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def main():
    """Run AI tests"""
    print("\n" + "="*70)
    print("QUESTION SERVICE - AI Generation Tests")
    print("="*70)
    print("\nNote: Each test may take 10-60 seconds due to AI processing")
    
    try:
        # Test single generation
        question_ids = test_ai_generate()
        
        # Small delay between tests
        import time
        time.sleep(2)
        
        # Test batch generation
        test_ai_batch()
        
        # Export generated questions
        if question_ids:
            time.sleep(2)
            test_export_ai_questions(question_ids)
        
        print("\n" + "="*70)
        print("All AI tests completed!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the service.")
        print("Make sure the service is running on http://localhost:5003")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    main()
