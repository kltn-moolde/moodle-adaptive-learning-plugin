#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Course Routes - Restructured
=============================
Clean API endpoints for course operations
"""

from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from database import mongo
from services.moodle_client import get_moodle_client
from utils.moodle_converter import MoodleStructureConverter
from utils.logger import setup_logger, log_request
from utils.exceptions import (
    CourseServiceError, 
    MoodleAPIError, 
    DatabaseError,
    NotFoundError,
    ValidationError
)

logger = setup_logger('course_routes')
course_bp = Blueprint("course", __name__)


def error_response(error: Exception, status_code: int = 500):
    """Standardized error response"""
    if isinstance(error, CourseServiceError):
        return jsonify(error.to_dict()), status_code
    
    return jsonify({
        'error': 'InternalServerError',
        'message': str(error)
    }), status_code


@course_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        # Check MongoDB
        mongo.db.command("ping")
        
        # Check Moodle API
        client = get_moodle_client()
        moodle_ok = client.health_check()
        
        if not moodle_ok:
            return jsonify({
                "status": "DEGRADED",
                "mongodb": "UP",
                "moodle": "DOWN"
            }), 200
        
        return jsonify({
            "status": "UP",
            "mongodb": "UP",
            "moodle": "UP"
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "DOWN",
            "error": str(e)
        }), 500


# ==================== MongoDB CRUD ====================

@course_bp.route("/courses", methods=["GET"])
@log_request
def get_courses():
    """Lấy tất cả courses từ MongoDB"""
    try:
        courses = list(mongo.db.courses.find())
        for c in courses:
            c["_id"] = str(c["_id"])
        
        logger.info(f"Retrieved {len(courses)} courses from database")
        return jsonify(courses), 200
        
    except Exception as e:
        logger.error(f"Failed to get courses: {str(e)}")
        return error_response(DatabaseError(str(e)), 500)


@course_bp.route("/courses", methods=["POST"])
@log_request
def create_course():
    """Tạo course mới trong MongoDB"""
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data or "name" not in data:
            raise ValidationError("Missing required field: name")
        
        new_course = {
            "moodle_id": data.get("moodle_id"),
            "name": data["name"],
            "description": data.get("description", "")
        }
        
        inserted = mongo.db.courses.insert_one(new_course)
        logger.info(f"Created course: {new_course['name']} (ID: {inserted.inserted_id})")
        
        return jsonify({
            "message": "Course created successfully",
            "id": str(inserted.inserted_id),
            "course": new_course
        }), 201
        
    except ValidationError as e:
        return error_response(e, 400)
    except Exception as e:
        logger.error(f"Failed to create course: {str(e)}")
        return error_response(DatabaseError(str(e)), 500)


@course_bp.route("/courses/<id>", methods=["GET"])
@log_request
def get_course(id):
    """Lấy 1 course từ MongoDB"""
    try:
        course = mongo.db.courses.find_one({"_id": ObjectId(id)})
        
        if not course:
            raise NotFoundError(f"Course not found: {id}")
        
        course["_id"] = str(course["_id"])
        logger.info(f"Retrieved course: {course.get('name', 'N/A')}")
        
        return jsonify(course), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except Exception as e:
        logger.error(f"Failed to get course: {str(e)}")
        return error_response(DatabaseError(str(e)), 500)


@course_bp.route("/courses/<id>", methods=["PUT"])
@log_request
def update_course(id):
    """Cập nhật course trong MongoDB"""
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data:
            raise ValidationError("No data provided")
        
        update_data = {k: v for k, v in data.items() if v is not None}
        
        result = mongo.db.courses.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise NotFoundError(f"Course not found: {id}")
        
        logger.info(f"Updated course: {id}")
        return jsonify({"message": "Course updated successfully"}), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except ValidationError as e:
        return error_response(e, 400)
    except Exception as e:
        logger.error(f"Failed to update course: {str(e)}")
        return error_response(DatabaseError(str(e)), 500)


@course_bp.route("/courses/<id>", methods=["DELETE"])
@log_request
def delete_course(id):
    """Xóa course từ MongoDB"""
    try:
        result = mongo.db.courses.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count == 0:
            raise NotFoundError(f"Course not found: {id}")
        
        logger.info(f"Deleted course: {id}")
        return jsonify({"message": "Course deleted successfully"}), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except Exception as e:
        logger.error(f"Failed to delete course: {str(e)}")
        return error_response(DatabaseError(str(e)), 500)


# ==================== Moodle Integration ====================

@course_bp.route("/moodle/courses", methods=["GET"])
@log_request
def get_moodle_courses():
    """Lấy danh sách courses từ Moodle"""
    try:
        client = get_moodle_client()
        courses = client.get_courses()
        
        return jsonify({
            "message": "Retrieved courses from Moodle",
            "total": len(courses),
            "courses": courses
        }), 200
        
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to get Moodle courses: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)


@course_bp.route("/moodle/courses/<int:course_id>", methods=["GET"])
@log_request
def get_moodle_course_detail(course_id):
    """Lấy chi tiết 1 course từ Moodle"""
    try:
        client = get_moodle_client()
        course = client.get_course_by_id(course_id)
        
        if not course:
            raise NotFoundError(f"Course not found in Moodle: {course_id}")
        
        return jsonify({
            "message": "Retrieved course from Moodle",
            "course": course
        }), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to get Moodle course: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)


@course_bp.route("/moodle/courses/<int:course_id>/contents", methods=["GET"])
@log_request
def get_moodle_course_contents(course_id):
    """Lấy nội dung course từ Moodle (raw structure)"""
    try:
        client = get_moodle_client()
        contents = client.get_course_contents(course_id)
        
        return jsonify({
            "message": "Retrieved course contents from Moodle",
            "course_id": course_id,
            "total_sections": len(contents),
            "contents": contents
        }), 200
        
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to get course contents: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)


@course_bp.route("/moodle/courses/<int:course_id>/hierarchy", methods=["GET"])
@log_request
def get_course_hierarchy(course_id):
    """
    Lấy cấu trúc phân cấp của course (NEW - recommended)
    Sử dụng MoodleStructureConverter để chuyển đổi sang deep hierarchy
    """
    try:
        # Get course info
        client = get_moodle_client()
        course = client.get_course_by_id(course_id)
        
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")
        
        # Get contents
        contents = client.get_course_contents(course_id)
        
        # Convert to hierarchy
        course_name = course.get('fullname', 'Unknown Course')
        converter = MoodleStructureConverter(course_name=course_name)
        converter.convert(contents)
        
        # Get analysis
        analysis = converter.analyze_structure()
        
        return jsonify({
            "message": "Course hierarchy generated successfully",
            "course_id": course_id,
            "course_name": course_name,
            "analysis": analysis,
            "hierarchy": converter.to_dict()
        }), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to generate hierarchy: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)


@course_bp.route("/moodle/courses/<int:course_id>/users", methods=["GET"])
@log_request
def get_course_users(course_id):
    """Lấy danh sách users enrolled trong course"""
    try:
        client = get_moodle_client()
        users = client.get_enrolled_users(course_id)
        
        return jsonify({
            "message": "Retrieved enrolled users",
            "course_id": course_id,
            "total": len(users),
            "users": users
        }), 200
        
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to get course users: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)


# ==================== Analysis Endpoints ====================

@course_bp.route("/moodle/courses/<int:course_id>/analysis", methods=["GET"])
@log_request
def analyze_course_structure(course_id):
    """Phân tích cấu trúc course (activities, resources, completion rate, etc.)"""
    try:
        client = get_moodle_client()
        course = client.get_course_by_id(course_id)
        
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")
        
        contents = client.get_course_contents(course_id)
        
        # Convert and analyze
        converter = MoodleStructureConverter(course.get('fullname', 'Unknown'))
        converter.convert(contents)
        analysis = converter.analyze_structure()
        
        # Additional stats
        activities = converter.get_all_activities()
        resources = converter.get_all_resources()
        
        return jsonify({
            "message": "Course analysis completed",
            "course_id": course_id,
            "course_name": course.get('fullname'),
            "analysis": analysis,
            "breakdown": {
                "activities": len(activities),
                "resources": len(resources),
                "sections": len(converter.root.children) if converter.root else 0
            }
        }), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to analyze course: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)


@course_bp.route("/moodle/courses/<int:course_id>/learning-path/<int:node_id>", methods=["GET"])
@log_request
def get_learning_path(course_id, node_id):
    """Lấy learning path từ root đến một node cụ thể"""
    try:
        client = get_moodle_client()
        course = client.get_course_by_id(course_id)
        
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")
        
        contents = client.get_course_contents(course_id)
        
        # Convert
        converter = MoodleStructureConverter(course.get('fullname'))
        converter.convert(contents)
        
        # Get path
        path = converter.get_learning_path(node_id)
        
        if not path:
            raise NotFoundError(f"Node not found: {node_id}")
        
        return jsonify({
            "message": "Learning path retrieved",
            "course_id": course_id,
            "node_id": node_id,
            "path": path,
            "depth": len(path) - 1  # Exclude root
        }), 200
        
    except NotFoundError as e:
        return error_response(e, 404)
    except MoodleAPIError as e:
        return error_response(e, 502)
    except Exception as e:
        logger.error(f"Failed to get learning path: {str(e)}")
        return error_response(CourseServiceError(str(e)), 500)
