#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML Converter Service
=====================
Convert questions from JSON to Moodle XML format
"""

from lxml import etree as ET
from typing import List, Union
from models.question import Question
from utils.logger import setup_logger

logger = setup_logger('xml_converter')


class XMLConverter:
    """Service for converting questions to Moodle XML format"""
    
    @staticmethod
    def create_moodle_xml(questions: List[Question], filename: str = "moodle_quiz.xml") -> bytes:
        """
        Create Moodle XML from list of Question objects
        
        Args:
            questions: List of Question objects
            filename: Output filename (for logging only)
            
        Returns:
            XML content as bytes
        """
        logger.info(f"Creating Moodle XML for {len(questions)} questions")
        
        quiz = ET.Element("quiz")
        
        for idx, question in enumerate(questions, start=1):
            # Add comment
            quiz.append(ET.Comment(f"Câu {idx}"))
            
            # Create question element
            question_elem = ET.SubElement(quiz, "question", type=question.question_type)
            
            # Add name
            name = ET.SubElement(question_elem, "name")
            ET.SubElement(name, "text").text = question.name
            
            # Add question text
            questiontext = ET.SubElement(question_elem, "questiontext", format="html")
            qt_text = ET.SubElement(questiontext, "text")
            qt_text.text = ET.CDATA(question.question_text)
            
            # Add configuration for multiple choice
            if question.question_type == "multichoice":
                ET.SubElement(question_elem, "shuffleanswers").text = "1" if question.shuffle_answers else "0"
                ET.SubElement(question_elem, "single").text = "true" if question.single_answer else "false"
                ET.SubElement(question_elem, "answernumbering").text = question.answer_numbering
                
                # Add answers
                for answer in question.answers:
                    answer_elem = ET.SubElement(question_elem, "answer", fraction=str(answer.fraction))
                    ET.SubElement(answer_elem, "text").text = answer.text
                    
                    feedback_elem = ET.SubElement(answer_elem, "feedback")
                    ET.SubElement(feedback_elem, "text").text = answer.feedback
            
            # Add tags
            tags = ET.SubElement(question_elem, "tags")
            
            # Add difficulty tag
            tag = ET.SubElement(tags, "tag")
            ET.SubElement(tag, "text").text = question.difficulty
            
            # Add custom tags
            for tag_text in question.tags:
                tag = ET.SubElement(tags, "tag")
                ET.SubElement(tag, "text").text = tag_text
            
            # Add category tag if exists
            if question.category:
                tag = ET.SubElement(tags, "tag")
                ET.SubElement(tag, "text").text = question.category
        
        # Convert to bytes
        tree = ET.ElementTree(quiz)
        xml_bytes = ET.tostring(
            tree,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )
        
        logger.info(f"✓ Successfully created XML with {len(questions)} questions")
        return xml_bytes
    
    @staticmethod
    def save_xml_to_file(xml_content: bytes, filepath: str) -> None:
        """
        Save XML content to file
        
        Args:
            xml_content: XML content as bytes
            filepath: Output file path
        """
        try:
            with open(filepath, 'wb') as f:
                f.write(xml_content)
            logger.info(f"✓ XML saved to {filepath}")
        except Exception as e:
            logger.error(f"✗ Failed to save XML: {str(e)}")
            raise
    
    @staticmethod
    def validate_xml(xml_content: bytes) -> tuple[bool, str]:
        """
        Validate XML content
        
        Args:
            xml_content: XML content to validate
            
        Returns:
            (is_valid, message)
        """
        try:
            ET.fromstring(xml_content)
            return True, "XML is valid"
        except ET.XMLSyntaxError as e:
            return False, f"Invalid XML: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
