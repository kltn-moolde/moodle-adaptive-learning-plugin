import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/courseservice?retryWrites=true&w=majority&appName=Cluster0")
    MOODLE_API_BASE = os.getenv("MOODLE_API_BASE", "http://139.99.103.223:9090/webservice/rest/server.php")
    ADDRESS_MOODLE = os.getenv("ADDRESS_MOODLE", "139.99.103.223:9090")
    MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "becf3b3a2a6f06858f2f16505719f5ef")
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAxNFSQyws7cC9ZnRFKT2rwRU8vT4pXWF8")