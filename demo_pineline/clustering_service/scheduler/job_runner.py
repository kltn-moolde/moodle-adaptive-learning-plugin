#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Runner
==========
APScheduler setup for automated clustering jobs
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

from moodle_api import MoodleCustomAPIClient
from models import CourseClusterModel, UserClusterHistoryModel
from scheduler.clustering_job import ClusteringJob
import config

logger = logging.getLogger(__name__)


class JobRunner:
    """Manages scheduled clustering jobs"""
    
    def __init__(self):
        """Initialize job runner"""
        self.scheduler = AsyncIOScheduler()
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.jobs_running = set()
        
        logger.info("Initialized JobRunner")
    
    async def initialize(self):
        """Initialize MongoDB connection and models"""
        logger.info("Connecting to MongoDB...")
        
        self.mongo_client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.mongo_client[config.DATABASE_NAME]
        
        # Initialize models
        self.course_cluster_model = CourseClusterModel(self.db)
        self.user_history_model = UserClusterHistoryModel(self.db)
        
        # Create indexes
        await self.course_cluster_model.create_indexes()
        await self.user_history_model.create_indexes()
        
        logger.info("✓ MongoDB initialized")
    
    async def run_clustering_for_course(self, course_id: int, retry_attempt: int = 0):
        """
        Run clustering job for a specific course with retry logic
        
        Args:
            course_id: Moodle course ID
            retry_attempt: Current retry attempt (0-indexed)
        """
        job_key = f"course_{course_id}"
        
        # Prevent duplicate runs
        if job_key in self.jobs_running:
            logger.warning(f"Job already running for course {course_id}, skipping")
            return
        
        self.jobs_running.add(job_key)
        
        try:
            logger.info(f"Starting clustering job for course {course_id} (attempt {retry_attempt + 1})")
            
            # Initialize Moodle client
            moodle_client = MoodleCustomAPIClient(
                base_url=config.MOODLE_URL,
                token=config.MOODLE_CUSTOM_TOKEN
            )
            
            # Initialize clustering job
            clustering_job = ClusteringJob(
                moodle_client=moodle_client,
                course_cluster_model=self.course_cluster_model,
                user_history_model=self.user_history_model
            )
            
            # Run job
            result = await clustering_job.run(course_id)
            
            if result['status'] == 'success':
                logger.info(f"✓ Successfully completed clustering for course {course_id}")
            elif result['status'] in ['no_data', 'insufficient_data']:
                logger.warning(f"⚠ Skipped course {course_id}: {result['message']}")
            else:
                raise Exception(f"Job failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Error in clustering job for course {course_id}: {str(e)}")
            
            # Retry logic
            if retry_attempt < config.CLUSTER_JOB_RETRY_ATTEMPTS - 1:
                delay = config.RETRY_BACKOFF_DELAYS[retry_attempt]
                logger.info(f"Will retry in {delay} seconds...")
                
                # Schedule retry
                self.scheduler.add_job(
                    func=self.run_clustering_for_course,
                    args=[course_id, retry_attempt + 1],
                    trigger='date',
                    run_date=None,  # Run immediately after delay
                    id=f'retry_{course_id}_{retry_attempt + 1}',
                    replace_existing=True
                )
            else:
                logger.error(f"✗ Failed after {config.CLUSTER_JOB_RETRY_ATTEMPTS} attempts for course {course_id}")
        
        finally:
            self.jobs_running.discard(job_key)
    
    async def run_clustering_for_all_courses(self):
        """Run clustering for all target courses"""
        logger.info("=" * 80)
        logger.info("Running scheduled clustering for all courses")
        logger.info("=" * 80)
        
        # Get target courses
        if config.CLUSTER_TARGET_COURSES:
            course_ids = [int(cid.strip()) for cid in config.CLUSTER_TARGET_COURSES.split(',')]
            logger.info(f"Target courses: {course_ids}")
        else:
            # If no specific courses, you could fetch from Moodle or use a default
            logger.warning("No target courses specified in config, using default: [5]")
            course_ids = [5]
        
        # Run clustering for each course
        for course_id in course_ids:
            await self.run_clustering_for_course(course_id)
    
    def start(self):
        """Start the scheduler"""
        if not config.CLUSTER_JOB_ENABLED:
            logger.warning("Cluster job scheduler is DISABLED in config")
            return
        
        logger.info("Starting scheduler...")
        
        # Parse cron schedule
        try:
            # Cron format: minute hour day month day_of_week
            parts = config.CLUSTER_JOB_SCHEDULE.split()
            if len(parts) != 5:
                raise ValueError("Invalid cron format")
            
            minute, hour, day, month, day_of_week = parts
            
            # Add scheduled job
            self.scheduler.add_job(
                func=self.run_clustering_for_all_courses,
                trigger=CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week
                ),
                id='scheduled_clustering',
                replace_existing=True
            )
            
            logger.info(f"✓ Scheduled clustering job: {config.CLUSTER_JOB_SCHEDULE}")
            
        except Exception as e:
            logger.error(f"Failed to parse cron schedule: {e}")
            logger.warning("Falling back to daily schedule at 2AM")
            
            self.scheduler.add_job(
                func=self.run_clustering_for_all_courses,
                trigger=CronTrigger(hour=2, minute=0),
                id='scheduled_clustering',
                replace_existing=True
            )
        
        # Start scheduler
        self.scheduler.start()
        logger.info("✓ Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
