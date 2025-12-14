"""
API Router
General API endpoints for the LTI service
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.services.lti_service import lti_service
from app.services.moodle_service import moodle_service
from app.models.lti_launch import LTILaunch
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """API Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/launches")
async def get_launches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get LTI launches with pagination
    """
    try:
        launches = db.query(LTILaunch).offset(skip).limit(limit).all()
        return {
            "launches": [launch.to_dict() for launch in launches],
            "count": len(launches),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving launches: {str(e)}")


@router.get("/launches/{launch_id}")
async def get_launch(launch_id: int, db: Session = Depends(get_db)):
    """
    Get specific LTI launch by ID
    """
    try:
        launch = db.query(LTILaunch).filter(LTILaunch.id == launch_id).first()
        if not launch:
            raise HTTPException(status_code=404, detail="Launch not found")
        return launch.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving launch: {str(e)}")


@router.get("/user/{user_id}/launches")
async def get_user_launches(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get LTI launches for a specific user
    """
    try:
        launches = (
            db.query(LTILaunch)
            .filter(LTILaunch.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return {
            "launches": [launch.to_dict() for launch in launches],
            "user_id": user_id,
            "count": len(launches),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user launches: {str(e)}")


@router.get("/course/{course_id}/participants")
async def get_course_participants(course_id: str):
    """
    Get course participants from Moodle
    """
    try:
        participants = await moodle_service.get_course_participants(course_id)
        return {
            "participants": participants,
            "course_id": course_id,
            "count": len(participants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving participants: {str(e)}")


@router.get("/course/{course_id}/info")
async def get_course_info(course_id: str):
    """
    Get course information from Moodle
    """
    try:
        course_info = await moodle_service.get_course_info(course_id)
        return {
            "course": course_info,
            "course_id": course_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving course info: {str(e)}")


@router.get("/user/{user_id}/info")
async def get_user_info(user_id: str):
    """
    Get user information from Moodle
    """
    try:
        user_info = await moodle_service.get_user_info(user_id)
        return {
            "user": user_info,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user info: {str(e)}")


@router.post("/validate-token")
async def validate_token(token: str):
    """
    Validate JWT session token
    """
    try:
        is_valid = lti_service.validate_token(token)
        result = {"valid": is_valid}
        
        if is_valid:
            user_id = lti_service.get_user_id_from_token(token)
            course_id = lti_service.get_course_id_from_token(token)
            result.update({
                "user_id": user_id,
                "course_id": course_id
            })
        
        return result
    except Exception as e:
        return {"valid": False, "error": str(e)}
