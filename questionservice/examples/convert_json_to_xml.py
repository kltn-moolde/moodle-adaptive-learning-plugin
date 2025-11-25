#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert JSON to XML Script
===========================
Standalone script to convert JSON questions to Moodle XML format
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.xml_converter import XMLConverter
from models.question import Question


def convert_json_to_xml(json_file: str, output_file: str = None):
    """
    Convert JSON file to Moodle XML
    
    Args:
        json_file: Path to JSON file
        output_file: Path to output XML file (optional)
    """
    print(f"Reading JSON file: {json_file}")
    
    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create Question objects
    questions = []
    for q_data in data['questions']:
        question = Question.from_dict(q_data)
        questions.append(question)
    
    print(f"Loaded {len(questions)} questions")
    
    # Generate XML
    if output_file is None:
        # Generate output filename
        input_path = Path(json_file)
        output_file = input_path.parent / f"{input_path.stem}_moodle.xml"
    
    xml_content = XMLConverter.create_moodle_xml(questions, str(output_file))
    
    # Save to file
    XMLConverter.save_xml_to_file(xml_content, str(output_file))
    
    print(f"✓ XML file saved: {output_file}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_json_to_xml.py <json_file> [output_file]")
        print("\nExample:")
        print("  python convert_json_to_xml.py examples/sample_questions.json")
        print("  python convert_json_to_xml.py examples/sample_questions.json output.xml")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        convert_json_to_xml(json_file, output_file)
    except FileNotFoundError:
        print(f"✗ Error: File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON file: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
