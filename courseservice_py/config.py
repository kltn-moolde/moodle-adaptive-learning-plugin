import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/courseservice?retryWrites=true&w=majority&appName=Cluster0")
    MOODLE_API_BASE = os.getenv("MOODLE_API_BASE", "http://127.0.0.1:8100/webservice/rest/server.php")
    MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "f53989bc6999e2418fddece85cf3470e")