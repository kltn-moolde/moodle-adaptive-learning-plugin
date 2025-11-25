#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Processing Pipeline - Orchestrator for log-to-state processing
====================================================================
Main pipeline để xử lý logs từ Moodle → 6D states → MongoDB → Q-Learning
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import json
import sys


# Support both relative and absolute imports
try:
    from core.log_to_state_builder import LogToStateBuilder
    from services.state_repository import StateRepository
    from services.moodle_api_client import MoodleAPIClient
    from services.qtable_update_service import QTableUpdateService
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.log_to_state_builder import LogToStateBuilder
    from services.state_repository import StateRepository
    from services.moodle_api_client import MoodleAPIClient
    from services.qtable_update_service import QTableUpdateService


class LogProcessingPipeline:
    """
    Main pipeline for processing Moodle logs into 6D states
    
    Pipeline Flow:
    1. Fetch logs from Moodle API
    2. Preprocess logs (normalize, aggregate)
    3. Build 6D states using StateBuilderV2
    4. Save states to MongoDB
    5. Update Q-table with state transitions
    6. Optionally save logs for audit
    
    Modes:
    - Real-time: Process logs as they arrive (webhook)
    - Batch: Process logs at scheduled intervals (daily, hourly)
    - Manual: Process specific user/module on demand
    """
    
    def __init__(
        self,
        cluster_profiles_path: str,
        course_structure_path: str,
        moodle_url: Optional[str] = None,
        moodle_token: Optional[str] = None,
        course_id: Optional[int] = None,
        mongo_uri: Optional[str] = None,
        recent_window: int = 10,
        qtable_updater: Optional[QTableUpdateService] = None,
        enable_qtable_updates: bool = True
    ):
        """
        Initialize log processing pipeline
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json
            course_structure_path: Path to course_structure.json
            moodle_url: Moodle base URL (optional, for API mode)
            moodle_token: Moodle web service token (optional)
            course_id: Moodle course ID (optional)
            mongo_uri: MongoDB connection URI (optional)
            recent_window: Recent actions window size
            qtable_updater: QTableUpdateService instance (optional)
            enable_qtable_updates: Enable Q-table updates from logs
        """
        self.cluster_profiles_path = Path(cluster_profiles_path)
        self.course_structure_path = Path(course_structure_path)
        
        # Initialize MongoDB repository
        self.repository = StateRepository(mongo_uri=mongo_uri)
        
        # Initialize Moodle API client (if credentials provided)
        self.moodle_client = None
        if moodle_url and moodle_token and course_id:
            self.moodle_client = MoodleAPIClient(
                moodle_url=moodle_url,
                ws_token=moodle_token,
                course_id=course_id
            )
        
        # Initialize state builder WITH moodle_client for enrichment
        self.state_builder = LogToStateBuilder(
            cluster_profiles_path=str(cluster_profiles_path),
            course_structure_path=str(course_structure_path),
            recent_window=recent_window,
            moodle_client=self.moodle_client  # Pass moodle_client here!
        )
        
        # Initialize Q-table updater
        self.qtable_updater = qtable_updater
        self.enable_qtable_updates = enable_qtable_updates and qtable_updater is not None
        
        # Statistics
        self.stats = {
            'total_logs_processed': 0,
            'total_states_built': 0,
            'total_states_saved': 0,
            'total_qtable_updates': 0,
            'errors': 0
        }
        
        print(f"\n{'='*70}")
        print("LogProcessingPipeline Initialized")
        print(f"{'='*70}")
        print(f"  - State builder: Ready")
        print(f"  - MongoDB: Connected")
        print(f"  - Moodle API: {'Connected' if self.moodle_client else 'Not configured'}")
        print(f"  - Q-table updates: {'Enabled' if self.enable_qtable_updates else 'Disabled'}")
        print(f"{'='*70}")
    
    def process_logs_from_dict(
        self,
        raw_logs: List[Dict],
        save_to_db: bool = True,
        save_logs: bool = False
    ) -> Dict:
        """
        Process raw logs (from API or file)
        
        Args:
            raw_logs: List of raw log dictionaries
            save_to_db: Save states to MongoDB
            save_logs: Also save raw logs to MongoDB
            
        Returns:
            Processing result summary
        """
        print(f"\n{'='*70}")
        print(f"Raw: {raw_logs}")
        print(f"Processing {len(raw_logs)} logs...")
        print(f"{'='*70}")
        
        # Step 1: Build states from logs
        print("\nStep 1: Building states from logs...")
        states = self.state_builder.build_states_from_logs(
            raw_logs, 
            enrich_with_api=True  # Enable API enrichment!
        )
        print(f"  ✓ Built {len(states)} states")
        
        # Update statistics
        self.stats['total_logs_processed'] += len(raw_logs)
        self.stats['total_states_built'] += len(states)
        
        # Step 2: Save to MongoDB
        saved_count = 0
        if save_to_db:
            print("\nStep 2: Saving states to MongoDB...")
            for (user_id, course_id, lesson_id), state in states.items():
                try:
                    self.repository.save_state(
                        user_id=user_id,
                        course_id=course_id,
                        module_id=lesson_id,
                        state=state,
                        save_history=True
                    )
                    saved_count += 1
                except Exception as e:
                    print(f"  ✗ Error saving state for user {user_id}, course {course_id}, lesson {lesson_id}: {e}")
                    self.stats['errors'] += 1
            
            print(f"  ✓ Saved {saved_count} states")
            self.stats['total_states_saved'] += saved_count
        
        # Step 3: Optionally save logs
        if save_logs:
            print("\nStep 3: Saving logs to MongoDB...")
            logs_saved = self.repository.save_log_events(raw_logs)
            print(f"  ✓ Saved {logs_saved} log events")
        
        # Step 4: Update Q-table (if enabled)
        qtable_stats = None
        if self.enable_qtable_updates:
            print(f"\nStep 4: Updating Q-table from logs...")
            try:
                qtable_stats = self.qtable_updater.update_from_logs(raw_logs)
                print(f"  ✓ Q-table updates: {qtable_stats['q_updates']}")
                print(f"  ✓ Avg reward: {qtable_stats['avg_reward']:.3f}")
                self.stats['total_qtable_updates'] += qtable_stats['q_updates']
            except Exception as e:
                print(f"  ✗ Q-table update error: {e}")
                self.stats['errors'] += 1
        
        # Generate summary
        summary = {
            'logs_processed': len(raw_logs),
            'states_built': len(states),
            'states_saved': saved_count,
            'unique_users': len(set(user_id for user_id, _, _ in states.keys())),
            'unique_courses': len(set(course_id for _, course_id, _ in states.keys())),
            'unique_modules': len(set(lesson_id for _, _, lesson_id in states.keys())),
            'qtable_updates': qtable_stats['q_updates'] if qtable_stats else 0,
            'avg_reward': qtable_stats['avg_reward'] if qtable_stats else 0.0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"\n{'='*70}")
        print("Processing Complete")
        print(f"{'='*70}")
        print(f"  - Logs processed: {summary['logs_processed']}")
        print(f"  - States built: {summary['states_built']}")
        print(f"  - States saved: {summary['states_saved']}")
        print(f"  - Unique users: {summary['unique_users']}")
        print(f"  - Unique courses: {summary['unique_courses']}")
        print(f"  - Unique modules: {summary['unique_modules']}")
        if self.enable_qtable_updates:
            print(f"  - Q-table updates: {summary['qtable_updates']}")
            print(f"  - Avg reward: {summary['avg_reward']:.3f}")
        
        return summary

def test_pipeline(): 
    """Test LogProcessingPipeline"""
    print("=" * 70)
    print("Testing LogProcessingPipeline")
    print("=" * 70)
   

if __name__ == '__main__':
    test_pipeline()
