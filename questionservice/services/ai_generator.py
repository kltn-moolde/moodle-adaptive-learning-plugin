#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Generator Service
====================
Generate questions using Google Gemini AI
"""

import google.generativeai as genai
import json
from typing import List, Dict, Optional
from utils.logger import setup_logger
from utils.exceptions import AIGenerationError

logger = setup_logger('ai_generator')


class AIQuestionGenerator:
    """Generate questions using Gemini AI"""
    
    # Free tier limits: ~15 requests/minute, 1 million tokens/day
    MAX_QUESTIONS_PER_REQUEST = 5
    
    def __init__(self, api_key: str):
        """Initialize Gemini AI"""
        if not api_key:
            raise AIGenerationError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("✓ Gemini AI initialized")
    
    def generate_questions(
        self,
        topic: str,
        num_questions: int = 3,
        difficulty: str = "medium",
        language: str = "vi"
    ) -> List[Dict]:
        """
        Generate multiple choice questions
        
        Args:
            topic: Question topic/subject
            num_questions: Number of questions (max 5 for free tier)
            difficulty: easy|medium|hard
            language: vi|en
            
        Returns:
            List of question dictionaries
        """
        # Limit for free tier
        if num_questions > self.MAX_QUESTIONS_PER_REQUEST:
            logger.warning(f"Requested {num_questions}, limiting to {self.MAX_QUESTIONS_PER_REQUEST}")
            num_questions = self.MAX_QUESTIONS_PER_REQUEST
        
        logger.info(f"Generating {num_questions} questions about: {topic}")
        
        try:
            # Create prompt
            prompt = self._create_prompt(topic, num_questions, difficulty, language)
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            # Parse response
            questions = self._parse_response(response.text)
            
            logger.info(f"✓ Generated {len(questions)} questions successfully")
            return questions
            
        except Exception as e:
            logger.error(f"✗ Failed to generate questions: {str(e)}")
            raise AIGenerationError(f"Generation failed: {str(e)}")
    
    def _create_prompt(
        self,
        topic: str,
        num_questions: int,
        difficulty: str,
        language: str
    ) -> str:
        """Create prompt for Gemini"""
        
        lang_instruction = "in Vietnamese (Tiếng Việt)" if language == "vi" else "in English"
        
        prompt = f"""Generate {num_questions} multiple choice questions about "{topic}" {lang_instruction}.

Requirements:
- Difficulty level: {difficulty}
- Each question must have exactly 4 answer options
- Only ONE correct answer (fraction: 100)
- Three wrong answers (fraction: 0)
- Include brief feedback for each answer
- Questions should be clear and educational

Output ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "questions": [
    {{
      "name": "Short question title",
      "question_type": "multichoice",
      "question_text": "<p>Question content here?</p>",
      "difficulty": "{difficulty}",
      "category": "{topic}",
      "tags": ["tag1", "tag2"],
      "answers": [
        {{
          "text": "Correct answer",
          "fraction": 100,
          "feedback": "Correct! Explanation..."
        }},
        {{
          "text": "Wrong answer 1",
          "fraction": 0,
          "feedback": "Incorrect. Explanation..."
        }},
        {{
          "text": "Wrong answer 2",
          "fraction": 0,
          "feedback": "Incorrect. Explanation..."
        }},
        {{
          "text": "Wrong answer 3",
          "fraction": 0,
          "feedback": "Incorrect. Explanation..."
        }}
      ]
    }}
  ]
}}

Generate now:"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> List[Dict]:
        """Parse AI response to extract questions"""
        try:
            # Clean response (remove markdown if present)
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned.startswith('```'):
                # Find first { and last }
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                if start != -1 and end > start:
                    cleaned = cleaned[start:end]
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Validate structure
            if 'questions' not in data:
                raise ValueError("Invalid response format: missing 'questions' key")
            
            questions = data['questions']
            
            # Validate each question
            for q in questions:
                self._validate_question(q)
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")
            raise AIGenerationError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            raise AIGenerationError(f"Parse error: {str(e)}")
    
    def _validate_question(self, question: Dict) -> None:
        """Validate question structure"""
        required_fields = ['name', 'question_type', 'question_text', 'difficulty', 'answers']
        
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate answers
        if not question['answers'] or len(question['answers']) < 2:
            raise ValueError("Question must have at least 2 answers")
        
        # Check for correct answer
        correct_answers = [a for a in question['answers'] if a.get('fraction') == 100]
        if not correct_answers:
            raise ValueError("Question must have at least one correct answer")
    
    def generate_batch(
        self,
        topic: str,
        total_questions: int = 10,
        difficulty: str = "medium",
        language: str = "vi"
    ) -> List[Dict]:
        """
        Generate large batch by splitting into multiple requests
        Good for free tier limits
        
        Args:
            topic: Question topic
            total_questions: Total questions needed
            difficulty: Difficulty level
            language: Language code
            
        Returns:
            List of all generated questions
        """
        all_questions = []
        remaining = total_questions
        batch_num = 1
        
        while remaining > 0:
            # Calculate questions for this batch
            batch_size = min(remaining, self.MAX_QUESTIONS_PER_REQUEST)
            
            logger.info(f"Batch {batch_num}: Generating {batch_size} questions")
            
            try:
                # Generate batch
                questions = self.generate_questions(
                    topic=topic,
                    num_questions=batch_size,
                    difficulty=difficulty,
                    language=language
                )
                
                all_questions.extend(questions)
                remaining -= len(questions)
                batch_num += 1
                
                logger.info(f"Progress: {len(all_questions)}/{total_questions} questions")
                
            except AIGenerationError as e:
                logger.error(f"Batch {batch_num} failed: {str(e)}")
                # Continue with what we have
                break
        
        logger.info(f"✓ Generated total {len(all_questions)} questions")
        return all_questions
