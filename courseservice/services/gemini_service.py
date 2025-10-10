import requests
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class GeminiService:
    """Simple Gemini AI service for learning path explanations"""
    
    def __init__(self):
        self.api_key = getattr(Config, 'GEMINI_API_KEY', None)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def generate_explanation(self, prompt: str) -> dict:
        """Generate explanation using Gemini AI"""
        try:
            if not self.api_key:
                logger.warning("Gemini API key not found")
                return None
            
            headers = {'Content-Type': 'application/json'}
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.6,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1000,
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Extract JSON from response
                    try:
                        json_start = generated_text.find('{')
                        json_end = generated_text.rfind('}') + 1
                        json_str = generated_text[json_start:json_end]
                        
                        explanation_data = json.loads(json_str)
                        return explanation_data
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON from Gemini: {e}")
                        return None
                else:
                    logger.error("No candidates in Gemini response")
                    return None
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

# Singleton instance
gemini_service = GeminiService()