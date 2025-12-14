#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Script - Demo log-to-state pipeline
================================================
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.log_processing.state_builder import LogToStateBuilder
from services.repository.state_repository import StateRepository
from pipeline.log_processing_pipeline import LogProcessingPipeline


def generate_sample_logs():
    """Generate sample logs for testing"""
    base_time = datetime.now().timestamp()
    
    logs = []
    
    # User 101: Medium learner, good progress
    user_101_actions = [
        ('view_content', 0, 0.1),
        ('view_content', 300, 0.2),
        ('attempt_quiz', 600, 0.3, 0.70),
        ('submit_quiz', 1200, 0.4, 0.75),
        ('review_quiz', 1500, 0.5, 0.75),
        ('view_content', 1800, 0.6),
        ('attempt_quiz', 2100, 0.7, 0.80),
        ('submit_quiz', 2700, 0.8, 0.85),
    ]
    
    for action, offset, progress, *score in user_101_actions:
        log = {
            'user_id': 101,
            'cluster_id': 2,  # Medium learner
            'module_id': 54,  # First subsection
            'action': action,
            'timestamp': base_time + offset,
            'progress': progress,
        }
        if score:
            log['score'] = score[0]
        logs.append(log)
    
    # User 102: Weak learner, struggling
    user_102_actions = [
        ('view_content', 0, 0.1),
        ('view_content', 300, 0.1),  # Repeated viewing
        ('view_content', 600, 0.2),
        ('attempt_quiz', 900, 0.3, 0.45),
        ('attempt_quiz', 1500, 0.3, 0.50),  # Second attempt
        ('view_content', 1800, 0.4),
    ]
    
    for action, offset, progress, *score in user_102_actions:
        log = {
            'user_id': 102,
            'cluster_id': 0,  # Weak learner
            'module_id': 56,  # Second subsection
            'action': action,
            'timestamp': base_time + offset,
            'progress': progress,
        }
        if score:
            log['score'] = score[0]
        logs.append(log)
    
    # User 103: Strong learner, fast progress
    user_103_actions = [
        ('view_content', 0, 0.2),
        ('attempt_quiz', 300, 0.5, 0.90),
        ('submit_quiz', 600, 0.7, 0.92),
        ('view_content', 900, 0.8),
        ('submit_assignment', 1200, 0.9, 0.95),
        ('post_forum', 1500, 1.0),
    ]
    
    for action, offset, progress, *score in user_103_actions:
        log = {
            'user_id': 103,
            'cluster_id': 4,  # Strong learner
            'module_id': 58,  # Third subsection
            'action': action,
            'timestamp': base_time + offset,
            'progress': progress,
        }
        if score:
            log['score'] = score[0]
        logs.append(log)
    
    return logs


def demo_standalone_state_builder():
    """Demo 1: Standalone state builder (no MongoDB)"""
    print("\n" + "=" * 70)
    print("DEMO 1: Standalone State Builder")
    print("=" * 70)
    
    # Paths
    base_path = Path(__file__).parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    course_path = base_path / 'data' / 'course_structure.json'
    
    if not cluster_path.exists() or not course_path.exists():
        print("❌ Required data files not found!")
        print(f"   Looking for:")
        print(f"   - {cluster_path}")
        print(f"   - {course_path}")
        return
    
    # Initialize builder
    print("\n1. Initialize LogToStateBuilder...")
    builder = LogToStateBuilder(
        cluster_profiles_path=str(cluster_path),
        course_structure_path=str(course_path),
        recent_window=10
    )
    
    # Generate sample logs
    print("\n2. Generate sample logs...")
    sample_logs = generate_sample_logs()
    print(f"   Generated {len(sample_logs)} log events for 3 users")
    
    # Build states
    print("\n3. Build states from logs...")
    states = builder.build_states_from_logs(sample_logs)
    print(f"   Built {len(states)} states")
    
    # Display states
    print("\n4. State Details:")
    for (user_id, module_id), state in states.items():
        print(f"\n   User {user_id}, Module {module_id}:")
        print(f"   State tuple: {state}")
        print(f"   {builder.state_builder.state_to_string(state)}")
        
        # Get explanation
        explanation = builder.get_state_explanation(state, verbose=True)
        print(f"\n   📊 Interpretation:")
        for line in explanation['interpretation'].split('\n'):
            print(f"      {line}")
    
    print("\n" + "=" * 70)


def demo_pipeline_with_mongodb():
    """Demo 2: Full pipeline with MongoDB"""
    print("\n" + "=" * 70)
    print("DEMO 2: Full Pipeline with MongoDB")
    print("=" * 70)
    
    # Paths
    base_path = Path(__file__).parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    course_path = base_path / 'data' / 'course_structure.json'
    
    if not cluster_path.exists() or not course_path.exists():
        print("❌ Required data files not found!")
        return
    
    try:
        # Initialize pipeline
        print("\n1. Initialize Pipeline...")
        pipeline = LogProcessingPipeline(
            cluster_profiles_path=str(cluster_path),
            course_structure_path=str(course_path),
            recent_window=10
        )
        
        # Generate sample logs
        print("\n2. Generate sample logs...")
        sample_logs = generate_sample_logs()
        
        # Process logs
        print("\n3. Process logs (build states + save to MongoDB)...")
        result = pipeline.process_logs_from_dict(
            sample_logs,
            save_to_db=True,
            save_logs=True
        )
        
        # Get states from DB
        print("\n4. Retrieve states from MongoDB:")
        for user_id in [101, 102, 103]:
            user_states = pipeline.repository.get_user_states(user_id)
            print(f"\n   User {user_id}: {len(user_states)} states")
            
            for module_id, state in user_states.items():
                print(f"      Module {module_id}: {state}")
                
                # Get explanation
                explanation = pipeline.get_state_with_explanation(user_id, module_id)
                if explanation:
                    print(f"      {explanation['state_string']}")
        
        # Statistics
        print("\n5. Pipeline Statistics:")
        stats = pipeline.get_pipeline_statistics()
        print(f"   Pipeline stats: {stats['pipeline']}")
        print(f"   Repository stats: {stats['repository']}")
        
        print("\n✅ Demo completed successfully!")
        print("\nNote: Test data saved to MongoDB (recommendservice database)")
        print("      You can clean up by deleting test users (101, 102, 103)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: This demo requires MongoDB connection.")
        print("      Set MONGO_URI environment variable or check services/state_repository.py")
    
    print("\n" + "=" * 70)


def demo_batch_processing():
    """Demo 3: Batch processing simulation"""
    print("\n" + "=" * 70)
    print("DEMO 3: Batch Processing Simulation")
    print("=" * 70)
    
    base_path = Path(__file__).parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    course_path = base_path / 'data' / 'course_structure.json'
    
    if not cluster_path.exists() or not course_path.exists():
        print("❌ Required data files not found!")
        return
    
    try:
        # Initialize pipeline
        print("\n1. Initialize Pipeline...")
        pipeline = LogProcessingPipeline(
            cluster_profiles_path=str(cluster_path),
            course_structure_path=str(course_path)
        )
        
        # Simulate batch logs from multiple users
        print("\n2. Simulate batch logs (last 24 hours)...")
        all_logs = []
        
        for user_id in range(101, 110):  # 9 users
            cluster_id = user_id % 5  # Distribute across clusters
            module_id = 54 + (user_id % 3) * 2  # Different modules
            
            # Generate random activity sequence
            base_time = datetime.now().timestamp() - 86400  # 24 hours ago
            
            user_logs = [
                {
                    'user_id': user_id,
                    'cluster_id': cluster_id,
                    'module_id': module_id,
                    'action': 'view_content',
                    'timestamp': base_time + i * 1800,  # Every 30 min
                    'progress': min(1.0, i * 0.2),
                    'score': 0.6 + i * 0.05
                }
                for i in range(5)
            ]
            all_logs.extend(user_logs)
        
        print(f"   Generated {len(all_logs)} logs for {9} users")
        
        # Process batch
        print("\n3. Process batch...")
        result = pipeline.process_logs_from_dict(all_logs, save_to_db=True)
        
        print(f"\n4. Batch Processing Results:")
        print(f"   Logs processed: {result['logs_processed']}")
        print(f"   States built: {result['states_built']}")
        print(f"   States saved: {result['states_saved']}")
        print(f"   Unique users: {result['unique_users']}")
        print(f"   Unique modules: {result['unique_modules']}")
        
        print("\n✅ Batch processing completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 70)


def main():
    """Main menu"""
    print("\n" + "=" * 70)
    print("Log-to-State Pipeline - Quick Start Demo")
    print("=" * 70)
    print("\nAvailable Demos:")
    print("  1. Standalone State Builder (no MongoDB)")
    print("  2. Full Pipeline with MongoDB")
    print("  3. Batch Processing Simulation")
    print("  4. Run All Demos")
    print("  0. Exit")
    
    choice = input("\nSelect demo (0-4): ").strip()
    
    if choice == '1':
        demo_standalone_state_builder()
    elif choice == '2':
        demo_pipeline_with_mongodb()
    elif choice == '3':
        demo_batch_processing()
    elif choice == '4':
        demo_standalone_state_builder()
        demo_pipeline_with_mongodb()
        demo_batch_processing()
    elif choice == '0':
        print("\nExiting...")
        return
    else:
        print("\n❌ Invalid choice!")
        return
    
    print("\n" + "=" * 70)
    print("Demo completed! Check LOG_TO_STATE_GUIDE.md for more details.")
    print("=" * 70)


if __name__ == '__main__':
    main()
