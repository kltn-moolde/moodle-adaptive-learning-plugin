#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick AI Example
================
Quick example of AI question generation
"""

import requests
import json
import time

BASE_URL = "http://localhost:5003"

def quick_generate():
    """Quick AI generation example"""
    
    print("🤖 AI Question Generator - Quick Example\n")
    print("="*60)
    
    # Example 1: Generate 3 easy questions
    print("\n📝 Example 1: Generate 3 Easy Questions")
    print("-"*60)
    
    data = {
        "topic": "Python - Biến và Kiểu dữ liệu cơ bản",
        "num_questions": 3,
        "difficulty": "easy",
        "language": "vi",
        "save_to_db": False  # Preview only
    }
    
    print(f"Topic: {data['topic']}")
    print(f"Questions: {data['num_questions']}")
    print(f"Generating...")
    
    response = requests.post(
        f"{BASE_URL}/api/ai/generate",
        json=data,
        timeout=60
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ {result['message']}\n")
        
        # Show first question
        q = result['questions'][0]
        print(f"First Question:")
        print(f"  Name: {q['name']}")
        print(f"  Difficulty: {q['difficulty']}")
        print(f"  Answers: {len(q['answers'])}")
    else:
        print(f"✗ Error: {response.status_code}")
        return
    
    # Example 2: Generate and save
    time.sleep(2)
    print("\n" + "="*60)
    print("\n📝 Example 2: Generate & Save to Database")
    print("-"*60)
    
    data2 = {
        "topic": "Python - List và Tuple",
        "num_questions": 2,
        "difficulty": "medium",
        "language": "vi",
        "save_to_db": True  # Save to DB
    }
    
    print(f"Topic: {data2['topic']}")
    print(f"Questions: {data2['num_questions']}")
    print(f"Save to DB: Yes")
    print(f"Generating...")
    
    response = requests.post(
        f"{BASE_URL}/api/ai/generate",
        json=data2,
        timeout=60
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ {result['message']}")
        
        if 'saved_ids' in result:
            print(f"\nSaved IDs:")
            for qid in result['saved_ids']:
                print(f"  - {qid}")
            
            # Export to XML
            print("\n📦 Exporting to XML...")
            export_response = requests.post(
                f"{BASE_URL}/api/questions/export/xml",
                json={
                    "question_ids": result['saved_ids'],
                    "filename": "quick_example.xml"
                }
            )
            
            if export_response.status_code == 200:
                with open("quick_example.xml", "wb") as f:
                    f.write(export_response.content)
                print("✓ Exported to: quick_example.xml")
    else:
        print(f"✗ Error: {response.status_code}")
    
    print("\n" + "="*60)
    print("✓ Done! Check the output above.")
    print("="*60)


if __name__ == "__main__":
    try:
        quick_generate()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Service not running!")
        print("Start the service first: python app.py")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
