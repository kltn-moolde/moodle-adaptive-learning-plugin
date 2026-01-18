"""
PO/LO management endpoints
"""
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from ..dependencies import po_lo_service

router = APIRouter(prefix='/api/po-lo', tags=['po-lo'])


@router.get('/courses')
def list_po_lo_courses():
    """
    List tất cả courses có PO/LO file
    """
    try:
        courses = po_lo_service.list_available_courses()
        return {
            'success': True,
            'courses': courses,
            'count': len(courses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing courses: {str(e)}")


@router.get('')
def get_po_lo_default():
    """
    Lấy PO/LO data mặc định (không có course_id)
    """
    try:
        data = po_lo_service.get_po_lo(course_id=None)
        return {
            'success': True,
            'course_id': None,
            'data': data
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PO/LO: {str(e)}")


@router.get('/{course_id}')
def get_po_lo(course_id: int):
    """
    Lấy PO/LO data cho course cụ thể
    """
    try:
        data = po_lo_service.get_po_lo(course_id=course_id)
        return {
            'success': True,
            'course_id': course_id,
            'data': data
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PO/LO: {str(e)}")


@router.put('/{course_id}')
def save_po_lo(course_id: int, data: Dict[str, Any]):
    """
    Lưu PO/LO data cho course
    """
    try:
        po_lo_service.save_po_lo(course_id=course_id, data=data)
        return {
            'success': True,
            'course_id': course_id,
            'message': f'PO/LO data saved for course {course_id}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving PO/LO: {str(e)}")

