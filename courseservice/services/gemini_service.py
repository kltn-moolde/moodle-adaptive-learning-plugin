import requests
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class GeminiService:
    """Simple Gemini AI service for learning path explanations"""
    
    def __init__(self):
        self.api_key = getattr(Config, 'GEMINI_API_KEY', None)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    def generate_explanation(self, prompt: str) -> dict:
        """Generate explanation using Gemini AI"""
        try:
            if not self.api_key:
                logger.warning("Gemini API key not found")
                return self._get_fallback_explanation()
            
            headers = {
                'x-goog-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Shorter, more focused prompt to avoid MAX_TOKENS
            focused_prompt = f"""Tạo gợi ý học tập ngắn gọn. Trả lời JSON format:
{{
  "explanation": "Giải thích ngắn gọn tại sao gợi ý này phù hợp",
  "reasoning": "Lý do chính", 
  "benefits": ["Lợi ích 1", "Lợi ích 2"],
  "next_steps": ["Bước tiếp theo 1", "Bước tiếp theo 2"]
}}

Context: {prompt[:200]}..."""
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": focused_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                    "candidateCount": 1
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    
                    # Check finish reason
                    finish_reason = candidate.get('finishReason', '')
                    if finish_reason == 'MAX_TOKENS':
                        logger.warning("Response was truncated due to MAX_TOKENS")
                    
                    # Extract text with better error handling
                    generated_text = None
                    if 'content' in candidate:
                        content = candidate['content']
                        if 'parts' in content and len(content['parts']) > 0:
                            generated_text = content['parts'][0].get('text', '')
                    
                    if not generated_text:
                        logger.error("No text found in Gemini response")
                        return self._get_fallback_explanation()
                    
                    # Extract JSON from response
                    try:
                        json_start = generated_text.find('{')
                        json_end = generated_text.rfind('}') + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_str = generated_text[json_start:json_end]
                            explanation_data = json.loads(json_str)
                            return explanation_data
                        else:
                            # If no JSON found, create structured response
                            return {
                                "explanation": generated_text,
                                "reasoning": "AI đã phân tích tình trạng học tập của bạn",
                                "benefits": ["Phù hợp với năng lực hiện tại", "Tối ưu hóa quá trình học tập"],
                                "next_steps": ["Thực hiện theo gợi ý", "Theo dõi tiến độ"]
                            }
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON from Gemini: {e}")
                        # Return text as explanation if JSON parsing fails
                        return {
                            "explanation": generated_text,
                            "reasoning": "AI đã phân tích và đưa ra gợi ý phù hợp",
                            "benefits": ["Cải thiện hiệu quả học tập"],
                            "next_steps": ["Làm theo hướng dẫn"]
                        }
                else:
                    logger.error("No candidates in Gemini response")
                    return self._get_fallback_explanation()
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._get_fallback_explanation()
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._get_fallback_explanation()
    
    def _get_fallback_explanation(self) -> dict:
        """Fallback explanation when AI is not available"""
        return {
            "explanation": "Hệ thống AI tạm thời không khả dụng. Gợi ý này dựa trên phân tích dữ liệu học tập của bạn.",
            "reasoning": "Dựa trên tiến độ học tập và kết quả đánh giá, hệ thống đề xuất bạn nên tiếp tục với hoạt động phù hợp.",
            "benefits": [
                "Duy trì momentum học tập",
                "Củng cố kiến thức đã học",
                "Chuẩn bị tốt cho các bước tiếp theo"
            ],
            "next_steps": [
                "Hoàn thành các bài tập được giao",
                "Ôn tập kiến thức cơ bản",
                "Tham gia thảo luận với giáo viên"
            ]
        }

# Singleton instance
gemini_service = GeminiService()