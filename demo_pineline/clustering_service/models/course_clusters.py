#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Course Clusters Model
=====================
MongoDB model for storing course clustering results
"""

from datetime import datetime
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
import math

logger = logging.getLogger(__name__)


class CourseClusterModel:
    """Model for course_clusters collection"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize model
        
        Args:
            db: MongoDB database instance
        """
        self.collection = db.course_clusters
        
    async def create_indexes(self):
        """Create indexes for efficient queries"""
        await self.collection.create_index([("course_id", 1), ("run_timestamp", -1)])
        await self.collection.create_index("course_id")
        logger.info("Created indexes for course_clusters collection")
    
    async def save_clustering_result(
        self,
        course_id: int,
        optimal_k: int,
        clusters: List[Dict],
        features_used: List[str],
        metadata: Dict
    ) -> str:
        """
        Save clustering results for a course
        
        Args:
            course_id: Moodle course ID
            optimal_k: Optimal number of clusters found
            clusters: List of cluster data with user_ids, statistics, and LLM analysis
            features_used: List of feature names used for clustering
            metadata: Additional metadata (total_students, execution_time, etc.)
            
        Returns:
            Inserted document ID as string
        """
        document = {
            "course_id": course_id,
            "run_timestamp": datetime.utcnow(),
            "optimal_k": optimal_k,
            "clusters": clusters,
            "features_used": features_used,
            "metadata": metadata
        }
        
        result = await self.collection.insert_one(document)
        
        logger.info(f"Saved clustering result for course {course_id} with {optimal_k} clusters")
        
        return str(result.inserted_id)
    
    async def get_latest_result(self, course_id: int) -> Optional[Dict]:
        """
        Get latest clustering result for a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            Latest clustering result document or None
        """
        result = await self.collection.find_one(
            {"course_id": course_id},
            sort=[("run_timestamp", -1)]
        )
        
        if result:
            result['_id'] = str(result['_id'])
            # Clean NaN values for JSON serialization
            result = self._clean_nan_values(result)
        
        return result
    
    async def get_all_results(self, course_id: int, limit: int = 10) -> List[Dict]:
        """
        Get all clustering results for a course
        
        Args:
            course_id: Moodle course ID
            limit: Maximum number of results to return
            
        Returns:
            List of clustering result documents
        """
        cursor = self.collection.find(
            {"course_id": course_id}
        ).sort("run_timestamp", -1).limit(limit)
        
        results = await cursor.to_list(length=limit)
        
        for result in results:
            result['_id'] = str(result['_id'])
            # Clean NaN values for JSON serialization
            result = self._clean_nan_values(result)
        
        return results
    
    def _clean_nan_values(self, obj):
        """
        Recursively clean NaN and Infinity values from nested dict/list structures
        
        Args:
            obj: Object to clean (dict, list, or value)
            
        Returns:
            Cleaned object with NaN/Inf converted to None
        """
        if isinstance(obj, dict):
            return {k: self._clean_nan_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_nan_values(item) for item in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        else:
            return obj
    
    async def delete_old_results(self, course_id: int, keep_latest: int = 30):
        """
        Delete old clustering results, keeping only the latest N
        
        Args:
            course_id: Moodle course ID
            keep_latest: Number of latest results to keep
        """
        # Get timestamps of results to delete
        cursor = self.collection.find(
            {"course_id": course_id},
            {"run_timestamp": 1}
        ).sort("run_timestamp", -1).skip(keep_latest)
        
        old_results = await cursor.to_list(length=1000)
        
        if old_results:
            ids_to_delete = [doc['_id'] for doc in old_results]
            result = await self.collection.delete_many({"_id": {"$in": ids_to_delete}})
            logger.info(f"Deleted {result.deleted_count} old results for course {course_id}")
