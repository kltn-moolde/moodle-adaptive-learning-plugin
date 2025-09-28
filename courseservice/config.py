import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/courseservice?retryWrites=true&w=majority&appName=Cluster0")
    MOODLE_API_BASE = os.getenv("MOODLE_API_BASE", "http://localhost:8100/webservice/rest/server.php")
    ADDRESS_MOODLE = os.getenv("ADDRESS_MOODLE", "localhost:8100")
    MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "a5187ae3fec69f55815fa924f038ccf2")