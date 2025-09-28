from itertools import count
from flask import Blueprint, request, jsonify
from database import mongo
from services.moodle_client import *
from bson.objectid import ObjectId
import requests
import json

course_bp = Blueprint("course", __name__)


def health():
    try:
        # 1. Kiểm tra kết nối MongoDB
        mongo.db.command("ping")
        if not mongo:
            return jsonify({
                "status": "DOWN",
                "reason": "MongoDB connection failed"
            }), 500

        # 2. Thử gọi Moodle API
        moodle_courses = get_courses_from_moodle()
        if not moodle_courses:
            return jsonify({
                "status": "DOWN",
                "reason": "Moodle API did not return data"
            }), 500

        return jsonify({"status": "UP"}), 200

    except Exception as e:
        return jsonify({
            "status": "DOWN",
            "error": str(e)
        }), 500

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


@course_bp.route("/moodle/courses/<course_id>/contents/structure", methods=["GET"])
def get_course_structure_json(course_id):
    """
    Lấy dữ liệu course từ Moodle, chuyển đổi sang cấu trúc phân cấp
    và trả về JSON string.
    """
    raw_data = get_course_contents(course_id)   # đã có sẵn trong service của bạn
    transformed_data = convert_course_structure(raw_data)  # dữ liệu đã chuẩn hóa

    return json.dumps(transformed_data, indent=2, ensure_ascii=False)


# Lấy chi tiết 1 khóa học trong Moodle
@course_bp.route("/moodle/courses/<course_id>", methods=["GET"])
def get_moodle_course_detail(course_id):
    try:
        # get_course_by_id trả về JSON từ Moodle (thường chứa key "courses")
        course_detail = get_course_by_id(course_id)
        return jsonify({"message": "Retrieved course detail from Moodle", "course": course_detail})
    except requests.RequestException as e:
        return jsonify({"message": "Failed to retrieve course detail", "error": str(e)}), 500


# Lấy danh sách học viên (người dùng) của một khóa học từ Moodle
@course_bp.route("/moodle/courses/<course_id>/users", methods=["GET"])
def get_moodle_course_users_route(course_id):
    try:
        users = get_moodle_course_users(course_id)
        return jsonify({"message": "Retrieved enrolled users from Moodle", "users": users})
    except requests.RequestException as e:
        return jsonify({"message": "Failed to retrieve enrolled users", "error": str(e)}), 500


# Lấy chi tiết 1 user từ Moodle
@course_bp.route("/moodle/users/<user_id>", methods=["GET"])
def get_moodle_user_detail_route(user_id):
    try:
        user_detail = get_moodle_user_detail(user_id)
        return jsonify({"message": "Retrieved user detail from Moodle", "user": user_detail})
    except requests.RequestException as e:
        return jsonify({"message": "Failed to retrieve user detail", "error": str(e)}), 500


@course_bp.route("/moodle/courses/<course_id>/contents/sync", methods=["POST"])
def sync_course_to_db(course_id):
    """
    Lấy dữ liệu course từ Moodle, chuyển đổi sang cấu trúc phân cấp,
    lưu (insert/update) vào MongoDB, và trả về dữ liệu đã lưu.
    """
    try:
        # 1. Lấy dữ liệu thô từ Moodle
        raw_data = get_course_contents(course_id)

        # 2. Convert sang cấu trúc phân cấp
        transformed_data = convert_course_structure(raw_data)

        # 3. Lưu hoặc cập nhật vào MongoDB
        course_doc = {
            "course_id": course_id,
            "contents": transformed_data
        }

        result = mongo.db.courses.update_one(
            {"course_id": course_id},         # tìm course theo course_id
            {"$set": course_doc},             # update dữ liệu
            upsert=True                       # nếu chưa có thì insert
        )

        # 4. Xác định là update hay insert
        if result.matched_count > 0:
            action = "updated"
        else:
            action = "inserted"

        return jsonify({
            "status": "success",
            "action": action,
            "course_id": course_id,
            "contents": transformed_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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