#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Cluster History Model
===========================
MongoDB model for tracking user cluster transitions over time
"""

from datetime import datetime
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class UserClusterHistoryModel:
    """Model for user_cluster_history collection"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize model
        
        Args:
            db: MongoDB database instance
        """
        self.collection = db.user_cluster_history
        
    async def create_indexes(self):
        """Create indexes for efficient queries"""
        await self.collection.create_index([("user_id", 1), ("course_id", 1)])
        await self.collection.create_index("course_id")
        await self.collection.create_index("user_id")
        logger.info("Created indexes for user_cluster_history collection")
    
    async def add_cluster_assignment(
        self,
        user_id: int,
        course_id: int,
        cluster_id: int,
        transition_type: str = "initial"
    ) -> None:
        """
        Add or update cluster assignment for a user
        
        Args:
            user_id: Moodle user ID
            course_id: Moodle course ID
            cluster_id: Assigned cluster ID
            transition_type: Type of transition ("initial", "moved", "stable")
        """
        # Get existing history
        existing = await self.collection.find_one({
            "user_id": user_id,
            "course_id": course_id
        })
        
        timestamp = datetime.utcnow()
        
        if existing:
            # Get previous cluster
            previous_cluster = existing['history'][-1]['cluster_id'] if existing['history'] else None
            
            # Determine transition type
            if previous_cluster is None:
                transition_type = "initial"
            elif previous_cluster == cluster_id:
                transition_type = "stable"
            else:
                transition_type = "moved"
            
            # Append to history
            new_entry = {
                "timestamp": timestamp,
                "cluster_id": cluster_id,
                "transition_type": transition_type,
                "previous_cluster_id": previous_cluster
            }
            
            await self.collection.update_one(
                {"user_id": user_id, "course_id": course_id},
                {
                    "$push": {"history": new_entry},
                    "$set": {"last_updated": timestamp}
                }
            )
            
            logger.debug(f"Updated cluster history for user {user_id}: {transition_type}")
            
        else:
            # Create new document
            document = {
                "user_id": user_id,
                "course_id": course_id,
                "history": [
                    {
                        "timestamp": timestamp,
                        "cluster_id": cluster_id,
                        "transition_type": "initial",
                        "previous_cluster_id": None
                    }
                ],
                "last_updated": timestamp
            }
            
            await self.collection.insert_one(document)
            
            logger.debug(f"Created cluster history for user {user_id}")
    
    async def get_user_history(self, user_id: int, course_id: int) -> Optional[Dict]:
        """
        Get cluster history for a user in a course
        
        Args:
            user_id: Moodle user ID
            course_id: Moodle course ID
            
        Returns:
            User history document or None
        """
        result = await self.collection.find_one({
            "user_id": user_id,
            "course_id": course_id
        })
        
        if result:
            result['_id'] = str(result['_id'])
        
        return result
    
    async def get_course_transitions(self, course_id: int) -> List[Dict]:
        """
        Get all cluster transitions for a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of user history documents
        """
        cursor = self.collection.find({"course_id": course_id})
        results = await cursor.to_list(length=10000)
        
        for result in results:
            result['_id'] = str(result['_id'])
        
        return results
    
    async def get_transition_statistics(self, course_id: int) -> Dict:
        """
        Get statistics about cluster transitions for a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            Dictionary with transition statistics
        """
        pipeline = [
            {"$match": {"course_id": course_id}},
            {"$unwind": "$history"},
            {"$group": {
                "_id": "$history.transition_type",
                "count": {"$sum": 1}
            }}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=100)
        
        stats = {
            "total_transitions": sum(r['count'] for r in results),
            "by_type": {r['_id']: r['count'] for r in results}
        }
        
        return stats
    
    async def bulk_add_assignments(
        self,
        course_id: int,
        user_cluster_map: Dict[int, int]
    ) -> int:
        """
        Bulk add/update cluster assignments for multiple users
        
        Args:
            course_id: Moodle course ID
            user_cluster_map: Dictionary mapping user_id to cluster_id
            
        Returns:
            Number of users updated
        """
        count = 0
        
        for user_id, cluster_id in user_cluster_map.items():
            await self.add_cluster_assignment(user_id, course_id, cluster_id)
            count += 1
        
        logger.info(f"Bulk updated {count} user cluster assignments for course {course_id}")
        
        return count
