"""
LTI Router
Handles LTI 1.3 authentication and launch endpoints
"""

from fastapi import APIRouter, Request, Form, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import urllib.parse

from app.database import get_db
from app.services.lti_service import lti_service
from app.services.moodle_service import moodle_service
from app.config import settings
from loguru import logger

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/login")
async def lti_login(
    request: Request,
    login_hint: str = Form(...),
    target_link_uri: str = Form(...),
    lti_message_hint: Optional[str] = Form(None)
):
    """
    LTI 1.3 Login Initiation Endpoint
    """
    try:
        logger.info("=== LOGIN METHOD CALLED ===")
        logger.info(f"login_hint: {login_hint}")
        logger.info(f"target_link_uri: {target_link_uri}")
        logger.info(f"lti_message_hint: {lti_message_hint}")
        
        # Generate authorization URL
        auth_url = lti_service.initiate_login(
            login_hint=login_hint,
            target_link_uri=target_link_uri,
            lti_message_hint=lti_message_hint
        )
        
        # Redirect to authorization URL
        return RedirectResponse(url=auth_url, status_code=302)
        
    except Exception as e:
        logger.error(f"ERROR in login method: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/launch")
async def lti_launch(
    request: Request,
    db: Session = Depends(get_db),
    id_token: str = Form(...),
    state: Optional[str] = Form(None)
):
    """
    Handle LTI 1.3 launch request and redirect to Frontend
    """
    try:
        # Validate JWT token
        is_valid = lti_service.validate_token(id_token)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid LTI token")
        
        # Decode launch data from token
        launch_data = lti_service.decode_token(id_token)
        
        # Extract user and course information
        user_id = launch_data.get("sub")  # User ID
        course_id = launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context", {}).get("id")
        resource_link_id = launch_data.get("https://purl.imsglobal.org/spec/lti/claim/resource_link", {}).get("id")
        
        # Save launch data to database
        lti_launch = LTILaunch(
            user_id=user_id,
            course_id=course_id,
            resource_link_id=resource_link_id,
            context_id=course_id,
            deployment_id=launch_data.get("https://purl.imsglobal.org/spec/lti/claim/deployment_id"),
            launch_data=json.dumps(launch_data)
        )
        db.add(lti_launch)
        db.commit()
        
        # Create session token for Frontend
        session_token = lti_service.create_session_token({
            "user_id": user_id,
            "course_id": course_id,
            "launch_id": lti_launch.id,
            "role": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])
        })
        
        # Option 1: Redirect to Frontend with token in URL parameters
        frontend_url = f"{settings.FRONTEND_URL}/lti-dashboard"
        redirect_url = f"{frontend_url}?token={session_token}&user_id={user_id}&course_id={course_id}"
        
        logger.info(f"LTI launch successful for user {user_id}, redirecting to Frontend")
        return RedirectResponse(url=redirect_url, status_code=302)
        
        # Option 2: Alternative - Redirect with POST data (more secure)
        # return templates.TemplateResponse("redirect_to_frontend.html", {
        #     "request": request,
        #     "frontend_url": frontend_url,
        #     "session_token": session_token,
        #     "user_id": user_id,
        #     "course_id": course_id
        # })
        
    except Exception as e:
        logger.error(f"LTI launch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Launch failed: {str(e)}")

@router.get("/dashboard", response_class=HTMLResponse)
async def lti_dashboard(
    request: Request,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    LTI Dashboard Page
    """
    try:
        # Validate token
        if not lti_service.validate_token(token):
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Invalid or expired token"}
            )
        
        logger.info(f"Token validated successfully: {token}")
        
        # Extract user and course information
        user_id = lti_service.get_user_id_from_token(token)
        course_id = lti_service.get_course_id_from_token(token)
        
        logger.info(f"User ID: {user_id}")
        logger.info(f"Course ID: {course_id}")
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user_id": user_id,
                "course_id": course_id,
                "token": token,
                "title": "LTI Dashboard"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Dashboard error: {str(e)}"}
        )


@router.get("/logs", response_class=HTMLResponse)
async def user_logs_page(
    request: Request,
    token: str = Query(...),
    course_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    User Logs Page
    """
    try:
        # Validate token
        if not lti_service.validate_token(token):
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Invalid or expired token"}
            )
        
        user_id = lti_service.get_user_id_from_token(token)
        
        # Use course_id from query parameter or extract from token
        if not course_id:
            course_id = lti_service.get_course_id_from_token(token)
        
        # Get user logs from Moodle
        logs = await moodle_service.get_user_logs(course_id, user_id)
        
        return templates.TemplateResponse(
            "user-logs.html",
            {
                "request": request,
                "logs": logs,
                "user_id": user_id,
                "course_id": course_id,
                "token": token,
                "title": "User Activity Logs"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in user logs page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Logs error: {str(e)}"}
        )


@router.get("/api/logs")
async def get_logs_api(
    token: str = Query(...),
    course_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    API endpoint to get logs as JSON
    """
    try:
        # Validate token
        if not lti_service.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = lti_service.get_user_id_from_token(token)
        logs = await moodle_service.get_user_logs(course_id, user_id)
        
        return {"logs": logs, "user_id": user_id, "course_id": course_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logs API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")


@router.get("/config")
async def get_tool_configuration():
    """
    Tool Configuration Endpoint for Moodle
    """
    config = {
        "title": settings.TOOL_TITLE,
        "description": settings.TOOL_DESCRIPTION,
        "target_link_uri": settings.TOOL_TARGET_LINK_URI,
        "oidc_initiation_url": settings.TOOL_OIDC_INITIATION_URL,
        "public_jwk_url": settings.TOOL_PUBLIC_JWK_URL,
        "privacy_level": "public"
    }
    
    return config


@router.get("/jwks")
async def get_jwks():
    """
    JWKS Endpoint (JSON Web Key Set)
    In production, you should implement proper key management
    """
    # Simplified JWKS response - implement proper key management in production
    jwks = {
        "keys": []
    }
    
    return jwks
