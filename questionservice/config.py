import os

class Config:
    """Application configuration"""
    
    # MongoDB Configuration
    MONGO_URI = os.getenv(
        "MONGO_URI", 
        "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/questionservice?retryWrites=true&w=majority&appName=Cluster0"
    )
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAxNFSQyws7cC9ZnRFKT2rwRU8vT4pXWF8")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Service Configuration
    MAX_QUESTIONS_PER_REQUEST = int(os.getenv("MAX_QUESTIONS_PER_REQUEST", "100"))
    SUPPORTED_QUESTION_TYPES = ["multichoice", "truefalse", "shortanswer", "essay"]
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/questionservice")
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB default
