#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB State Repository - State persistence layer
===================================================
Lưu trữ và truy xuất 6D states từ MongoDB
"""

import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError


class Config:
    """Configuration for MongoDB connection"""
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://lockbkbang:lHkgnWyAGVSi3CrQ@cluster0.z20xcvv.mongodb.net/courseservice?retryWrites=true&w=majority&appName=Cluster0"
    )
    DATABASE_NAME = "recommendservice"
    COLLECTION_USER_STATES = "user_states"
    COLLECTION_STATE_HISTORY = "state_history"
    COLLECTION_LOG_EVENTS = "log_events"
    COLLECTION_RECOMMENDATIONS = "recommendations"


class StateRepository:
    """
    MongoDB repository for user states
    
    Collections:
    - user_states: Current state for each (user_id, module_id)
    - state_history: Historical states (time series)
    - log_events: Raw log events (optional)
    - recommendations: Generated recommendations for users
    """
    
    def __init__(
        self,
        mongo_uri: Optional[str] = None,
        database_name: Optional[str] = None
    ):
        """
        Initialize MongoDB repository
        
        Args:
            mongo_uri: MongoDB connection URI (default from Config)
            database_name: Database name (default: "recommendservice")
        """
        self.mongo_uri = mongo_uri or Config.MONGO_URI
        self.database_name = database_name or Config.DATABASE_NAME
        
        # Connect to MongoDB
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        
        # Collections
        self.user_states = self.db[Config.COLLECTION_USER_STATES]
        self.state_history = self.db[Config.COLLECTION_STATE_HISTORY]
        self.log_events = self.db[Config.COLLECTION_LOG_EVENTS]
        self.recommendations = self.db[Config.COLLECTION_RECOMMENDATIONS]
        
        # Create indexes
        self._create_indexes()
        
        print(f"✓ StateRepository connected to MongoDB:")
        print(f"  - Database: {self.database_name}")
        print(f"  - Collections: user_states, state_history, log_events, recommendations")
    
    def _create_indexes(self):
        """Create indexes for efficient queries"""
        # Drop old index if it exists (migration for multi-course support)
        try:
            self.user_states.drop_index("user_id_1_module_id_1")
            print("  ⚠️  Dropped old index (user_id, module_id) for multi-course migration")
        except:
            pass  # Index doesn't exist or already dropped
        
        # user_states: unique index on (user_id, course_id, module_id) for multi-course support
        self.user_states.create_index(
            [("user_id", ASCENDING), ("course_id", ASCENDING), ("module_id", ASCENDING)],
            unique=True,
            name="user_course_module_unique"
        )
        self.user_states.create_index([("updated_at", DESCENDING)])
        
        # state_history: index on (user_id, course_id, module_id, timestamp)
        self.state_history.create_index([
            ("user_id", ASCENDING),
            ("course_id", ASCENDING),
            ("module_id", ASCENDING),
            ("timestamp", DESCENDING)
        ])
        
        # log_events: index on (user_id, timestamp)
        self.log_events.create_index([
            ("user_id", ASCENDING),
            ("timestamp", DESCENDING)
        ])
        self.log_events.create_index([("module_id", ASCENDING)])
        
        # recommendations: unique index on (user_id, module_id)
        self.recommendations.create_index([
            ("user_id", ASCENDING),
            ("module_id", ASCENDING)
        ], unique=True)
        self.recommendations.create_index([("updated_at", DESCENDING)])
    
    def save_state(
        self,
        user_id: int,
        module_id: int,
        state: Tuple[int, int, float, float, int, int],
        metadata: Optional[Dict[str, Any]] = None,
        save_history: bool = True,
        course_id: Optional[int] = None
    ) -> bool:
        """
        Save or update user state
        
        Args:
            user_id: User ID
            module_id: Module ID
            state: 6D state tuple
            metadata: Additional metadata (e.g., summary stats)
            save_history: Also save to history collection
            course_id: Course ID (optional, for multi-course support)
            
        Returns:
            True if successful
        """
        cluster_id, module_idx, progress_bin, score_bin, phase, engagement = state
        
        # Prepare document
        doc = {
            "user_id": user_id,
            "module_id": module_id,
            "state": {
                "cluster_id": cluster_id,
                "module_idx": module_idx,
                "progress_bin": progress_bin,
                "score_bin": score_bin,
                "learning_phase": phase,
                "engagement_level": engagement
            },
            "state_tuple": list(state),  # For easy retrieval
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        # Add course_id if provided (multi-course support)
        if course_id is not None:
            doc["course_id"] = course_id
        
        # Build query filter - include course_id if provided
        query_filter = {"user_id": user_id, "module_id": module_id}
        if course_id is not None:
            query_filter["course_id"] = course_id
        
        # Upsert to user_states
        self.user_states.update_one(
            query_filter,
            {"$set": doc},
            upsert=True
        )
        
        # Save to history if requested
        if save_history:
            history_doc = {
                **doc,
                "timestamp": datetime.utcnow()
            }
            self.state_history.insert_one(history_doc)
        
        return True
    
    def get_state(
        self,
        user_id: int,
        module_id: int,
        course_id: Optional[int] = None
    ) -> Optional[Tuple[int, int, float, float, int, int]]:
        """
        Get current state for user and module
        
        Args:
            user_id: User ID
            module_id: Module ID
            course_id: Course ID (optional, for multi-course support)
            
        Returns:
            6D state tuple or None if not found
        """
        query_filter = {
            "user_id": user_id,
            "module_id": module_id
        }
        if course_id is not None:
            query_filter["course_id"] = course_id
        
        doc = self.user_states.find_one(query_filter)
        
        if doc and "state_tuple" in doc:
            return tuple(doc["state_tuple"])
        
        return None
    
    def get_user_states(
        self,
        user_id: int,
        course_id: Optional[int] = None
    ) -> Dict[int, Tuple[int, int, float, float, int, int]]:
        """
        Get all states for a user
        
        Args:
            user_id: User ID
            course_id: Course ID (optional, filter by course)
            
        Returns:
            Dictionary mapping module_id -> state tuple
        """
        query_filter = {"user_id": user_id}
        if course_id is not None:
            query_filter["course_id"] = course_id
        
        docs = self.user_states.find(query_filter)
        
        states = {}
        for doc in docs:
            module_id = doc["module_id"]
            state = tuple(doc["state_tuple"])
            states[module_id] = state
        
        return states
    
    def get_state_history(
        self,
        user_id: int,
        module_id: int,
        limit: int = 10,
        course_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get state history for user and module
        
        Args:
            user_id: User ID
            module_id: Module ID
            limit: Maximum number of historical states
            course_id: Course ID (optional, for multi-course support)
            
        Returns:
            List of state documents (newest first)
        """
        query_filter = {
            "user_id": user_id,
            "module_id": module_id
        }
        if course_id is not None:
            query_filter["course_id"] = course_id
        
        docs = self.state_history.find(query_filter).sort("timestamp", DESCENDING).limit(limit)
        
        return list(docs)
    
    def save_log_events(
        self,
        events: List[Dict[str, Any]]
    ) -> int:
        """
        Save raw log events
        
        Args:
            events: List of log event dictionaries
            
        Returns:
            Number of events saved
        """
        if not events:
            return 0
        
        # Add timestamp if not present
        for event in events:
            if "created_at" not in event:
                event["created_at"] = datetime.utcnow()
        
        result = self.log_events.insert_many(events)
        return len(result.inserted_ids)
    
    def get_log_events(
        self,
        user_id: Optional[int] = None,
        module_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query log events
        
        Args:
            user_id: Filter by user ID
            module_id: Filter by module ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of events
            
        Returns:
            List of log events
        """
        query = {}
        
        if user_id is not None:
            query["user_id"] = user_id
        if module_id is not None:
            query["module_id"] = module_id
        
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time.timestamp()
            if end_time:
                query["timestamp"]["$lte"] = end_time.timestamp()
        
        docs = self.log_events.find(query).sort("timestamp", DESCENDING).limit(limit)
        return list(docs)
    
    def delete_user_states(self, user_id: int) -> int:
        """
        Delete all states for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of states deleted
        """
        result = self.user_states.delete_many({"user_id": user_id})
        return result.deleted_count
    
    def save_recommendations(
        self,
        user_id: int,
        module_id: int,
        recommendations: List[Dict[str, Any]],
        state: Optional[Tuple] = None
    ) -> bool:
        """
        Save recommendations for a user/module
        
        Args:
            user_id: User ID
            module_id: Module ID
            recommendations: List of recommendation dictionaries
            state: Current state (optional)
            
        Returns:
            True if saved successfully
        """
        doc = {
            "user_id": user_id,
            "module_id": module_id,
            "recommendations": recommendations,
            "state": list(state) if state else None,
            "timestamp": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow()
        }
        
        # Upsert (update or insert)
        self.recommendations.update_one(
            {"user_id": user_id, "module_id": module_id},
            {"$set": doc},
            upsert=True
        )
        
        return True
    
    def get_recommendations(
        self,
        user_id: int,
        module_id: int
    ) -> Optional[Dict]:
        """
        Get recommendations for a user/module
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            Recommendations document or None if not found
        """
        doc = self.recommendations.find_one({
            "user_id": user_id,
            "module_id": module_id
        })
        
        return doc
    
    def get_statistics(self) -> Dict:
        """Get repository statistics"""
        return {
            "user_states_count": self.user_states.count_documents({}),
            "state_history_count": self.state_history.count_documents({}),
            "recommendations_count": self.recommendations.count_documents({}),
            "log_events_count": self.log_events.count_documents({}),
            "unique_users": len(self.user_states.distinct("user_id")),
            "unique_modules": len(self.user_states.distinct("module_id"))
        }
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()


def test_state_repository():
    """Test StateRepository (requires MongoDB connection)"""
    print("=" * 70)
    print("Testing StateRepository")
    print("=" * 70)
    
    try:
        # Initialize repository
        repo = StateRepository()
        
        print("\n1. Save Sample States:")
        # Sample state
        sample_state = (2, 0, 0.5, 0.75, 1, 1)  # 6D state
        
        result = repo.save_state(
            user_id=101,
            module_id=54,
            state=sample_state,
            metadata={"source": "test", "avg_score": 0.75},
            save_history=True
        )
        print(f"   Saved state for user 101, module 54: {result}")
        
        # Save another state
        result = repo.save_state(
            user_id=101,
            module_id=56,
            state=(2, 1, 0.25, 0.5, 0, 0),
            save_history=True
        )
        print(f"   Saved state for user 101, module 56: {result}")
        
        print("\n2. Get State:")
        state = repo.get_state(user_id=101, module_id=54)
        print(f"   Retrieved state: {state}")
        
        print("\n3. Get All User States:")
        user_states = repo.get_user_states(user_id=101)
        print(f"   User 101 has {len(user_states)} states:")
        for module_id, state in user_states.items():
            print(f"     Module {module_id}: {state}")
        
        print("\n4. Get State History:")
        history = repo.get_state_history(user_id=101, module_id=54, limit=5)
        print(f"   Retrieved {len(history)} historical states")
        
        print("\n5. Save Log Events:")
        sample_events = [
            {
                "user_id": 101,
                "module_id": 54,
                "action_type": "attempt_quiz",
                "timestamp": 1700000000,
                "score": 0.75
            },
            {
                "user_id": 101,
                "module_id": 54,
                "action_type": "submit_quiz",
                "timestamp": 1700000300,
                "score": 0.80
            }
        ]
        count = repo.save_log_events(sample_events)
        print(f"   Saved {count} log events")
        
        print("\n6. Get Log Events:")
        events = repo.get_log_events(user_id=101, limit=10)
        print(f"   Retrieved {len(events)} events")
        
        print("\n7. Statistics:")
        stats = repo.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n8. Cleanup (optional):")
        # Uncomment to delete test data
        # deleted = repo.delete_user_states(user_id=101)
        # print(f"   Deleted {deleted} states")
        
        repo.close()
        
        print("\n" + "=" * 70)
        print("✓ StateRepository test completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("Note: This test requires MongoDB connection")


if __name__ == '__main__':
    test_state_repository()
