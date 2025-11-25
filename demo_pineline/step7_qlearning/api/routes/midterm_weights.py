"""
Midterm weights management endpoints
"""
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from ..dependencies import midterm_weights_service

router = APIRouter(prefix='/api/midterm-weights', tags=['midterm-weights'])


@router.get('/courses')
def list_midterm_weights_courses():
    """
    List tất cả courses có midterm weights file
    """
    try:
        courses = midterm_weights_service.list_available_courses()
        return {
            'success': True,
            'courses': courses,
            'count': len(courses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing courses: {str(e)}")


@router.get('')
def get_midterm_weights_default():
    """
    Lấy midterm weights data mặc định (không có course_id)
    """
    try:
        data = midterm_weights_service.get_weights(course_id=None)
        return {
            'success': True,
            'course_id': None,
            'data': data
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading midterm weights: {str(e)}")


@router.get('/{course_id}')
def get_midterm_weights(course_id: int):
    """
    Lấy midterm weights data cho course cụ thể
    """
    try:
        data = midterm_weights_service.get_weights(course_id=course_id)
        return {
            'success': True,
            'course_id': course_id,
            'data': data
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading midterm weights: {str(e)}")


@router.put('/{course_id}')
def save_midterm_weights(course_id: int, data: Dict[str, Any]):
    """
    Lưu midterm weights data cho course
    """
    try:
        midterm_weights_service.save_weights(course_id=course_id, data=data)
        return {
            'success': True,
            'course_id': course_id,
            'message': f'Midterm weights saved for course {course_id}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving midterm weights: {str(e)}")

