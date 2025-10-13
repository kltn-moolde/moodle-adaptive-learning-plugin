import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API directly"""
    
    # Get API key from environment
    api_key = 'AIzaSyAxNFSQyws7cC9ZnRFKT2rwRU8vT4pXWF8'
    
    if not api_key:
        print("❌ GEMINI_API_KEY không tìm thấy trong environment variables")
        print("Hãy set: export GEMINI_API_KEY='your_api_key_here'")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # API endpoint
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    # Headers
    headers = {
        'x-goog-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Test prompt - Shorter to avoid MAX_TOKENS
    prompt = """Giải thích tại sao học sinh nên làm quiz cùng độ khó. Trả lời JSON:
{
  "explanation": "Giải thích ngắn gọn",
  "reasoning": "Lý do", 
  "benefits": ["Lợi ích 1", "Lợi ích 2"],
  "next_steps": ["Bước 1", "Bước 2"]
}"""
    
    # Payload
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
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
    
    print("🔄 Sending request to Gemini API...")
    print(f"URL: {api_url}")
    print(f"Headers: {headers}")
    print("Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("-" * 50)
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Full Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 50)
            
            # Check finish reason first
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print("📝 Candidate structure:")
                print(json.dumps(candidate, indent=2, ensure_ascii=False))
                
                # Check finish reason
                finish_reason = candidate.get('finishReason', '')
                print(f"🔍 Finish Reason: {finish_reason}")
                
                if finish_reason == 'MAX_TOKENS':
                    print("⚠️ Response was truncated due to MAX_TOKENS!")
                    print("💡 Try shorter prompt or increase maxOutputTokens")
                
                # Try to extract text
                if 'content' in candidate:
                    content = candidate['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        generated_text = content['parts'][0].get('text', '')
                        print(f"📄 Generated Text:\n{generated_text}")
                        print("-" * 50)
                        
                        # Try to parse JSON
                        try:
                            json_start = generated_text.find('{')
                            json_end = generated_text.rfind('}') + 1
                            
                            if json_start >= 0 and json_end > json_start:
                                json_str = generated_text[json_start:json_end]
                                explanation_data = json.loads(json_str)
                                print("✅ Successfully parsed JSON:")
                                print(json.dumps(explanation_data, indent=2, ensure_ascii=False))
                            else:
                                print("⚠️ No JSON found in response")
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON parsing error: {e}")
                    else:
                        print("❌ No parts in content or empty parts")
                        print(f"Content keys: {list(content.keys())}")
                else:
                    print("❌ No content in candidate")
            else:
                print("❌ No candidates in response")
                
        else:
            print(f"❌ Error Response:")
            print(f"Status: {response.status_code}")
            print(f"Text: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Gemini API...")
    test_gemini_api()