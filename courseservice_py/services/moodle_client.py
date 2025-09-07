import requests
from config import Config

def get_courses_from_moodle():
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_course_get_courses",
        "moodlewsrestformat": "json"
    }
    response = requests.get(Config.MOODLE_API_BASE, params=params)
    response.raise_for_status()
    return response.json()

def get_course_contents(course_id):
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_course_get_contents",
        "moodlewsrestformat": "json",
        "courseid": course_id
    }
    response = requests.get(Config.MOODLE_API_BASE, params=params)
    response.raise_for_status()
    return response.json()