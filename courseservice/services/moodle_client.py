import requests
from config import Config

HEADERS = {"Host": Config.ADDRESS_MOODLE} 
TIMEOUT = 30  # giây

def get_courses_from_moodle():
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_course_get_courses",
        "moodlewsrestformat": "json"
    }
    response = requests.get(
        Config.MOODLE_API_BASE,
        headers=HEADERS,
        params=params,
        timeout=TIMEOUT,
        allow_redirects=True
    )
    response.raise_for_status()
    return response.json()

def get_course_contents(course_id):
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_course_get_contents",
        "moodlewsrestformat": "json",
        "courseid": course_id
    }
    response = requests.get(
        Config.MOODLE_API_BASE,
        headers=HEADERS,
        params=params,
        timeout=TIMEOUT,
        allow_redirects=True
    )
    response.raise_for_status()
    return response.json()

def get_course_by_id(course_id: int):
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_course_get_courses_by_field",
        "moodlewsrestformat": "json",
        "field": "id",
        "value": course_id
    }
    response = requests.get(
        Config.MOODLE_API_BASE,
        headers=HEADERS,
        params=params,
        timeout=TIMEOUT,
        allow_redirects=True
    )
    response.raise_for_status()
    return response.json()

def get_moodle_course_users(course_id):
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_enrol_get_enrolled_users",
        "moodlewsrestformat": "json",
        "courseid": course_id
    }
    response = requests.get(
        Config.MOODLE_API_BASE,
        headers=HEADERS,
        params=params,
        timeout=TIMEOUT,
        allow_redirects=True
    )
    response.raise_for_status()
    return response.json()

def get_moodle_user_detail(user_id):
    params = {
        "wstoken": Config.MOODLE_TOKEN,
        "wsfunction": "core_user_get_users_by_field",
        "moodlewsrestformat": "json",
        "field": "id",
        "values[0]": user_id
    }
    response = requests.get(
        Config.MOODLE_API_BASE,
        headers=HEADERS,
        params=params,
        timeout=TIMEOUT,
        allow_redirects=True
    )
    response.raise_for_status()
    return response.json()


# --- Hàm chuyển đổi dữ liệu ---
def convert_course_structure(course_data: list):
    """
    Chuyển đổi dữ liệu thô từ Moodle sang cấu trúc mong muốn.
    """

    def process_modules(modules):
        return [
            {"id": m.get("id"), "name": m.get("name"), "modname": m.get("modname")}
            for m in modules
        ]

    def process_sections(sections):
        hierarchy = []
        for sec in sections:
            sec_dict = {
                "sectionid": sec.get("id"),
                "name": sec.get("name"),
                "lessons": []
            }
            for mod in sec.get("modules", []):
                if mod.get("modname") == "subsection":  # lesson
                    lesson_dict = {
                        "sectionid": mod.get("id"),
                        "name": mod.get("name"),
                        "resources": process_modules(mod.get("modules", []))
                    }
                    sec_dict["lessons"].append(lesson_dict)
                else:  # resource trực tiếp trong section
                    sec_dict.setdefault("resources", []).append({
                        "id": mod.get("id"),
                        "name": mod.get("name"),
                        "modname": mod.get("modname")
                    })
            hierarchy.append(sec_dict)
        return hierarchy

    def clean_structure(hierarchy):
        resources_map = {}
        for section in hierarchy:
            if section.get("resources"):
                resources_map[section["name"]] = {
                    "sectionIdNew": section["sectionid"],
                    "resources": section["resources"]
                }

        new_structure = []

        for idx, section in enumerate(hierarchy):
            if idx == 0:
                # Giữ nguyên General
                new_structure.append(section)
                continue

            if section.get("lessons"):  # section có lessons => chủ đề
                new_section = {
                    "sectionIdOld": section["sectionid"],
                    "name": section["name"],
                    "lessons": []
                }

                for lesson in section["lessons"]:
                    res_info = resources_map.get(
                        lesson["name"],
                        {"sectionIdNew": lesson["sectionid"], "resources": []}
                    )
                    new_section["lessons"].append({
                        "sectionIdOld": lesson["sectionid"],
                        "sectionIdNew": res_info["sectionIdNew"],
                        "name": lesson["name"],
                        "resources": res_info["resources"]
                    })

                new_structure.append(new_section)

        return new_structure

    hierarchy = process_sections(course_data)
    return clean_structure(hierarchy)