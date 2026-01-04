#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clustering Service API
======================
FastAPI service for automated clustering with scheduled jobs
"""

import sys
from pathlib import Path

# Add current directory to path to ensure local config is imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

import logging
import math
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Any

from scheduler.job_runner import JobRunner
from moodle_api import MoodleCustomAPIClient
from models import CourseClusterModel, UserClusterHistoryModel
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)

logger = logging.getLogger(__name__)

# Global job runner
job_runner: JobRunner = None


def clean_nan_values(obj: Any) -> Any:
    """Recursively clean NaN, Infinity values from dict/list for JSON serialization"""
    if isinstance(obj, dict):
        return {key: clean_nan_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    return obj


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global job_runner
    
    logger.info("=" * 80)
    logger.info("Starting Clustering Service")
    logger.info("=" * 80)
    
    # Initialize job runner
    job_runner = JobRunner()
    await job_runner.initialize()
    
    # Start scheduler
    job_runner.start()
    
    logger.info("✓ Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down service...")
    job_runner.stop()
    logger.info("✓ Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Clustering Service",
    description="Automated student clustering service for Moodle courses",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Clustering Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler_running": job_runner.scheduler.running if job_runner else False
    }


@app.post("/api/clustering/courses/{course_id}/run")
async def trigger_clustering(course_id: int):
    """
    Manually trigger clustering for a specific course
    
    Args:
        course_id: Moodle course ID
        
    Returns:
        Clustering result
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(f"Manual trigger: Running clustering for course {course_id}")
    
    try:
        await job_runner.run_clustering_for_course(course_id)
        
        return {
            "status": "success",
            "message": f"Clustering triggered for course {course_id}",
            "course_id": course_id
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger clustering: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/results")
async def get_latest_result(course_id: int):
    """
    Get latest clustering result for a course
    
    Args:
        course_id: Moodle course ID
        
    Returns:
        Latest clustering result
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await job_runner.course_cluster_model.get_latest_result(course_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No clustering results found for course {course_id}"
            )
        
        return clean_nan_values(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/results/history")
async def get_result_history(course_id: int, limit: int = 10):
    """
    Get clustering result history for a course
    
    Args:
        course_id: Moodle course ID
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        List of clustering results
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = await job_runner.course_cluster_model.get_all_results(course_id, limit=limit)
        
        return clean_nan_values({
            "course_id": course_id,
            "count": len(results),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Failed to get result history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/users/{user_id}/history")
async def get_user_cluster_history(course_id: int, user_id: int):
    """
    Get cluster history for a specific user in a course
    
    Args:
        course_id: Moodle course ID
        user_id: Moodle user ID
        
    Returns:
        User's cluster transition history
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        history = await job_runner.user_history_model.get_user_history(user_id, course_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No history found for user {user_id} in course {course_id}"
            )
        
        return clean_nan_values(history)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/transitions")
async def get_course_transitions(course_id: int):
    """
    Get all cluster transitions for a course
    
    Args:
        course_id: Moodle course ID
        
    Returns:
        Transition statistics and user transitions
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get all transitions
        transitions = await job_runner.user_history_model.get_course_transitions(course_id)
        
        # Get statistics
        stats = await job_runner.user_history_model.get_transition_statistics(course_id)
        
        return clean_nan_values({
            "course_id": course_id,
            "statistics": stats,
            "total_users": len(transitions),
            "transitions": transitions
        })
        
    except Exception as e:
        logger.error(f"Failed to get transitions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/jobs")
async def get_scheduler_status():
    """
    Get scheduler status and scheduled jobs
    
    Returns:
        Scheduler information
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        jobs = []
        for job in job_runner.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": job_runner.scheduler.running,
            "jobs_count": len(jobs),
            "jobs": jobs,
            "jobs_running": list(job_runner.jobs_running)
        }
        
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clustering/run-all")
async def trigger_all_courses():
    """
    Manually trigger clustering for all configured courses
    
    Returns:
        Status message
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info("Manual trigger: Running clustering for all courses")
    
    try:
        await job_runner.run_clustering_for_all_courses()
        
        return {
            "status": "success",
            "message": "Clustering triggered for all configured courses"
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger clustering for all courses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses")
async def get_clustered_courses():
    """
    Get list of all courses that have clustering results
    
    Returns:
        List of courses with latest clustering info
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Aggregate to get distinct course_ids with latest result
        pipeline = [
            {
                "$sort": {"run_timestamp": -1}
            },
            {
                "$group": {
                    "_id": "$course_id",
                    "course_id": {"$first": "$course_id"},
                    "last_run": {"$first": "$run_timestamp"},
                    "optimal_k": {"$first": "$optimal_k"},
                    "total_students": {"$first": "$metadata.total_students"}
                }
            },
            {
                "$sort": {"course_id": 1}
            }
        ]
        
        cursor = job_runner.course_cluster_model.collection.aggregate(pipeline)
        courses = await cursor.to_list(length=None)
        
        return clean_nan_values({
            "total_courses": len(courses),
            "courses": courses
        })
        
    except Exception as e:
        logger.error(f"Failed to get courses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/clusters/{cluster_id}")
async def get_cluster_details(course_id: int, cluster_id: int):
    """
    Get detailed information about a specific cluster
    
    Args:
        course_id: Moodle course ID
        cluster_id: Cluster ID (0-based index)
        
    Returns:
        Cluster details including users and statistics
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get latest result
        result = await job_runner.course_cluster_model.get_latest_result(course_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No clustering results found for course {course_id}"
            )
        
        # Find the specific cluster
        cluster = None
        for c in result.get('clusters', []):
            if c.get('cluster_id') == cluster_id:
                cluster = c
                break
        
        if not cluster:
            raise HTTPException(
                status_code=404,
                detail=f"Cluster {cluster_id} not found in course {course_id}"
            )
        
        return clean_nan_values({
            "course_id": course_id,
            "cluster_id": cluster_id,
            "run_timestamp": result.get('run_timestamp'),
            "cluster": cluster
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cluster details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/students")
async def get_students_clusters(course_id: int):
    """
    Get all students with their current cluster assignments
    
    Args:
        course_id: Moodle course ID
        
    Returns:
        List of students with cluster info
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get latest result
        result = await job_runner.course_cluster_model.get_latest_result(course_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No clustering results found for course {course_id}"
            )
        
        # Build student list with cluster info
        students = []
        for cluster in result.get('clusters', []):
            cluster_id = cluster.get('cluster_id')
            cluster_name = cluster.get('name', f'Cluster {cluster_id}')
            
            for user_id in cluster.get('user_ids', []):
                students.append({
                    "user_id": user_id,
                    "cluster_id": cluster_id,
                    "cluster_name": cluster_name,
                    "cluster_description": cluster.get('description', ''),
                    "cluster_characteristics": cluster.get('characteristics', []),
                    "cluster_recommendations": cluster.get('recommendations', [])
                })
        
        return clean_nan_values({
            "course_id": course_id,
            "run_timestamp": result.get('run_timestamp'),
            "total_students": len(students),
            "students": students
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get students: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/overview")
async def get_course_overview(course_id: int):
    """
    Báo cáo tiến độ tổng quan - Overview của toàn bộ lớp học
    
    Args:
        course_id: Moodle course ID
        
    Returns:
        Tổng quan về phân bố clusters, engagement metrics, và xu hướng lớp
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get latest result
        result = await job_runner.course_cluster_model.get_latest_result(course_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No clustering results found for course {course_id}"
            )
        
        # Build overview statistics
        clusters = result.get('clusters', [])
        metadata = result.get('metadata', {})
        
        # Cluster distribution
        cluster_distribution = [
            {
                "cluster_id": c.get('cluster_id'),
                "cluster_name": c.get('name', f"Cluster {c.get('cluster_id')}"),
                "student_count": c.get('size', 0),
                "percentage": c.get('percentage', 0)
            }
            for c in clusters
        ]
        
        # Overall metrics from metadata
        overall_metrics = {
            "total_students": metadata.get('total_students', 0),
            "total_logs": metadata.get('total_logs', 0),
            "features_analyzed": metadata.get('features_selected', 0),
            "optimal_clusters": result.get('optimal_k', 0),
            "clustering_quality": {
                "silhouette_score": metadata.get('clustering_metrics', {}).get('silhouette'),
                "davies_bouldin_index": metadata.get('clustering_metrics', {}).get('davies_bouldin')
            }
        }
        
        # Identify cluster trends
        cluster_summaries = [
            {
                "cluster_id": c.get('cluster_id'),
                "name": c.get('name'),
                "description": c.get('description'),
                "student_count": c.get('size'),
                "key_characteristics": c.get('characteristics', [])[:3]  # Top 3
            }
            for c in clusters
        ]
        
        return clean_nan_values({
            "course_id": course_id,
            "run_timestamp": result.get('run_timestamp'),
            "overview": {
                "overall_metrics": overall_metrics,
                "cluster_distribution": cluster_distribution,
                "cluster_summaries": cluster_summaries
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/courses/{course_id}/at-risk-students")
async def get_at_risk_students(course_id: int):
    """
    Hệ thống cảnh báo sớm - Phát hiện học sinh có nguy cơ tụt hậu
    
    Args:
        course_id: Moodle course ID
        
    Returns:
        Danh sách học sinh cần hỗ trợ với mức độ ưu tiên
    """
    if not job_runner:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get latest result
        result = await job_runner.course_cluster_model.get_latest_result(course_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No clustering results found for course {course_id}"
            )
        
        clusters = result.get('clusters', [])
        at_risk_students = []
        
        # Define at-risk keywords to identify problematic clusters
        at_risk_keywords = [
            'thấp', 'kém', 'yếu', 'ít', 'không', 'thiếu', 
            'tụt', 'nguy cơ', 'cần hỗ trợ', 'định hướng',
            'low', 'poor', 'weak', 'inactive', 'struggling'
        ]
        
        for cluster in clusters:
            cluster_id = cluster.get('cluster_id')
            cluster_name = cluster.get('name', '').lower()
            cluster_desc = cluster.get('description', '').lower()
            characteristics = cluster.get('characteristics', [])
            
            # Check if cluster indicates at-risk behavior
            is_at_risk = any(
                keyword in cluster_name or keyword in cluster_desc
                for keyword in at_risk_keywords
            )
            
            # Calculate risk level based on characteristics
            risk_indicators = []
            for char in characteristics:
                char_lower = char.lower()
                if any(keyword in char_lower for keyword in at_risk_keywords):
                    risk_indicators.append(char)
            
            if is_at_risk or len(risk_indicators) >= 2:
                # Determine priority (high/medium/low)
                if len(risk_indicators) >= 3 or 'nguy cơ' in cluster_desc:
                    priority = "high"
                elif len(risk_indicators) >= 2:
                    priority = "medium"
                else:
                    priority = "low"
                
                # Add all students in this cluster to at-risk list
                for user_id in cluster.get('user_ids', []):
                    at_risk_students.append({
                        "user_id": user_id,
                        "cluster_id": cluster_id,
                        "cluster_name": cluster.get('name'),
                        "priority": priority,
                        "risk_indicators": risk_indicators,
                        "recommendations": cluster.get('recommendations', [])
                    })
        
        # Sort by priority (high → medium → low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        at_risk_students.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return clean_nan_values({
            "course_id": course_id,
            "run_timestamp": result.get('run_timestamp'),
            "total_at_risk": len(at_risk_students),
            "priority_breakdown": {
                "high": sum(1 for s in at_risk_students if s['priority'] == 'high'),
                "medium": sum(1 for s in at_risk_students if s['priority'] == 'medium'),
                "low": sum(1 for s in at_risk_students if s['priority'] == 'low')
            },
            "at_risk_students": at_risk_students
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get at-risk students: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # For reload to work, need to pass app as string
    if config.API_RELOAD:
        uvicorn.run(
            "main:app",
            host=config.API_HOST,
            port=config.API_PORT,
            reload=True
        )
    else:
        uvicorn.run(
            app,
            host=config.API_HOST,
            port=config.API_PORT,
            reload=False
        )
