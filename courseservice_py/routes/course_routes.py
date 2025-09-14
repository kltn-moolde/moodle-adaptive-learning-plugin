from itertools import count
from flask import Blueprint, request, jsonify
from database import mongo
from services.moodle_client import get_course_contents, get_courses_from_moodle
from bson.objectid import ObjectId
import requests

course_bp = Blueprint("course", __name__)

# GET all
@course_bp.route("/courses", methods=["GET"])
def get_courses():
    courses = list(mongo.db.courses.find())
    for c in courses:
        c["_id"] = str(c["_id"])
    return jsonify(courses)

# POST
@course_bp.route("/courses", methods=["POST"])
def create_course():
    data = request.json
    new_course = {
        "moodle_id": data.get("moodle_id"),
        "name": data["name"],
        "description": data.get("description", "")
    }
    inserted = mongo.db.courses.insert_one(new_course)
    return jsonify({"message": "Course created", "id": str(inserted.inserted_id)})

# PUT
@course_bp.route("/courses/<id>", methods=["PUT"])
def update_course(id):
    data = request.json
    update_data = {k: v for k, v in data.items() if v is not None}
    mongo.db.courses.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return jsonify({"message": "Course updated"})

# DELETE
@course_bp.route("/courses/<id>", methods=["DELETE"])
def delete_course(id):
    mongo.db.courses.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Course deleted"})

# # SYNC với Moodle
# @course_bp.route("/sync/moodle", methods=["POST"])
# def sync_courses():
#     moodle_courses = get_courses_from_moodle()
#     count = 0
#     for mc in moodle_courses:
#         existing = mongo.db.courses.find_one({"moodle_id": mc["id"]})
#         if existing:
#             mongo.db.courses.update_one(
#                 {"moodle_id": mc["id"]},
#                 {"$set": {"name": mc["fullname"], "description": mc.get("summary", "")}}
#             )
#         else:
#             mongo.db.courses.insert_one({
#                 "moodle_id": mc["id"],
#                 "name": mc["fullname"],
#                 "description": mc.get("summary", "")
#             })
#         count += 1
#     return jsonify({"message": "Synced with Moodle", "count": count})

# get danh sách khóa học từ Moodle
@course_bp.route("/moodle/courses", methods=["GET"])
def get_moodle_courses():
    moodle_courses = get_courses_from_moodle()
    return jsonify({"message": "Retrieved courses from Moodle", "courses": moodle_courses})


# get nội dung khóa học từ Moodle
@course_bp.route("/moodle/courses/<course_id>/contents", methods=["GET"])
def get_moodle_course_contents(course_id):
    course_contents = get_course_contents(course_id)
    return jsonify({"message": "Retrieved course contents from Moodle", "contents": course_contents})


@course_bp.route("/test/external", methods=["GET"])
def test_external_call():
    try:
        # Gọi một trang bên ngoài, ví dụ Google
        response = requests.get("https://www.google.com", timeout=5)
        return jsonify({
            "message": "External call successful",
            "status_code": response.status_code,
            "content_snippet": response.text[:200]  # chỉ lấy 200 ký tự đầu
        })
    except requests.RequestException as e:
        return jsonify({
            "message": "External call failed",
            "error": str(e)
        }), 500