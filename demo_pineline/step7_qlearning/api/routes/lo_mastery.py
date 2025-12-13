"""
LO Mastery API endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from ..dependencies import lo_mastery_service

router = APIRouter(prefix='/api/lo-mastery', tags=['lo-mastery'])


@router.post('/sync/{course_id}')
@router.get('/sync/{course_id}')
async def sync_course_mastery(
    course_id: int,
    background_tasks: BackgroundTasks,
    user_id: Optional[int] = Query(None, description="Sync single user (optional)")
):
    """
    Sync LO mastery cho course (hoặc specific user)
    
    Supports both GET and POST methods for convenience.
    
    Args:
        course_id: Course ID
        user_id: Optional - sync single user, None = sync all students in background
        
    Returns:
        Sync result or background task confirmation
        
    Examples:
        GET  /api/lo-mastery/sync/5              - Sync all students (background)
        GET  /api/lo-mastery/sync/5?user_id=10   - Sync single student
        POST /api/lo-mastery/sync/5              - Sync all students (background)
    """
    try:
        if user_id:
            # Sync single student (foreground)
            result = lo_mastery_service.sync_student_mastery(user_id, course_id)
            return {
                'success': result.get('success', False),
                'course_id': course_id,
                'user_id': user_id,
                'result': result
            }
        else:
            # Sync all students (background task)
            background_tasks.add_task(
                lo_mastery_service.sync_all_students,
                course_id
            )
            return {
                'success': True,
                'course_id': course_id,
                'message': 'Background sync started for all students',
                'status': 'background_task_started'
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing mastery: {str(e)}"
        )


@router.get('/{user_id}/{course_id}')
def get_student_mastery(
    user_id: int,
    course_id: int,
    use_cache: bool = Query(True, description="Use cached data if available")
):
    """
    Get LO/PO mastery cho một student
    
    Args:
        user_id: User ID
        course_id: Course ID
        use_cache: Use cache (default: True)
        
    Returns:
        Student mastery data
    """
    try:
        mastery_data = lo_mastery_service.get_student_mastery(
            user_id=user_id,
            course_id=course_id,
            use_cache=use_cache
        )
        
        if not mastery_data:
            raise HTTPException(
                status_code=404,
                detail=f"No mastery data for user {user_id} in course {course_id}. Try syncing first."
            )
        
        return {
            'success': True,
            'user_id': user_id,
            'course_id': course_id,
            'data': mastery_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving mastery: {str(e)}"
        )


@router.get('/course/{course_id}/summary')
def get_course_mastery_summary(course_id: int):
    """
    Get class-level statistics
    
    Args:
        course_id: Course ID
        
    Returns:
        Course statistics including LO/PO averages
    """
    try:
        stats = lo_mastery_service.get_course_statistics(course_id)
        
        if 'error' in stats:
            raise HTTPException(
                status_code=404,
                detail=stats['error']
            )
        
        return {
            'success': True,
            'course_id': course_id,
            'statistics': stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting statistics: {str(e)}"
        )


@router.get('/course/{course_id}/weak-students')
def get_weak_students(
    course_id: int,
    lo_id: Optional[str] = Query(None, description="Specific LO ID (optional)"),
    threshold: float = Query(0.6, ge=0.0, le=1.0, description="Mastery threshold")
):
    """
    Get students với mastery thấp
    
    Args:
        course_id: Course ID
        lo_id: Specific LO ID (optional, None = all LOs)
        threshold: Mastery threshold (default: 0.6)
        
    Returns:
        List of weak students
    """
    try:
        weak_students = lo_mastery_service.get_weak_students(
            course_id=course_id,
            lo_id=lo_id,
            threshold=threshold
        )
        
        return {
            'success': True,
            'course_id': course_id,
            'lo_id': lo_id,
            'threshold': threshold,
            'count': len(weak_students),
            'weak_students': weak_students
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting weak students: {str(e)}"
        )


@router.get('/stats')
def get_service_stats():
    """
    Get service statistics (cache hits, syncs, etc.)
    
    Returns:
        Service stats
    """
    try:
        stats = lo_mastery_service.get_stats()
        return {
            'success': True,
            'stats': stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


@router.delete('/cache')
def clear_cache():
    """
    Clear service cache
    
    Returns:
        Success confirmation
    """
    try:
        lo_mastery_service.clear_cache()
        return {
            'success': True,
            'message': 'Cache cleared successfully'
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )
