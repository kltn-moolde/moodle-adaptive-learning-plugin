#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests - End-to-end testing for log-to-state pipeline
==================================================================
"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.log_models import LogEvent, UserLogSummary, ActionType
from core.log_preprocessor import LogPreprocessor
from core.log_to_state_builder import LogToStateBuilder
from services.state_repository import StateRepository


class TestLogModels(unittest.TestCase):
    """Test log data models"""
    
    def test_action_type_normalization(self):
        """Test action type normalization"""
        test_cases = [
            ("quiz_attempt_started", ActionType.ATTEMPT_QUIZ),
            ("view page", ActionType.VIEW_CONTENT),
            ("forum post created", ActionType.POST_FORUM),
            ("assignment submitted", ActionType.SUBMIT_ASSIGNMENT)
        ]
        
        for raw, expected in test_cases:
            result = ActionType.normalize(raw)
            self.assertEqual(result, expected, f"Failed to normalize {raw}")
    
    def test_log_event_creation(self):
        """Test LogEvent creation from dict"""
        raw_data = {
            'user_id': 101,
            'cluster_id': 2,
            'cmid': 54,
            'eventname': 'quiz_attempt_started',
            'timecreated': 1700000000,
            'grade': 85.5
        }
        
        event = LogEvent.from_dict(raw_data)
        
        self.assertEqual(event.user_id, 101)
        self.assertEqual(event.cluster_id, 2)
        self.assertEqual(event.module_id, 54)
        self.assertEqual(event.action_type, ActionType.ATTEMPT_QUIZ)
        self.assertAlmostEqual(event.score, 0.855, places=3)
    
    def test_user_log_summary_update(self):
        """Test UserLogSummary updates"""
        summary = UserLogSummary(user_id=101, cluster_id=2, module_id=54)
        
        # Add events
        for i in range(3):
            event = LogEvent(
                user_id=101,
                cluster_id=2,
                module_id=54,
                action_type=ActionType.VIEW_CONTENT,
                timestamp=1700000000 + i * 300,
                score=0.7 + i * 0.1
            )
            summary.update_from_event(event)
        
        self.assertEqual(summary.total_actions, 3)
        self.assertAlmostEqual(summary.avg_score, 0.8, places=1)
        self.assertEqual(len(summary.recent_actions), 3)


class TestLogPreprocessor(unittest.TestCase):
    """Test log preprocessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        base_path = Path(__file__).parent.parent
        self.course_structure = base_path / 'data' / 'course_structure.json'
        
        if self.course_structure.exists():
            self.preprocessor = LogPreprocessor(
                course_structure_path=str(self.course_structure),
                recent_window=10
            )
    
    def test_parse_raw_logs(self):
        """Test parsing raw logs"""
        if not hasattr(self, 'preprocessor'):
            self.skipTest("course_structure.json not found")
        
        raw_logs = [
            {'user_id': 101, 'cluster_id': 2, 'cmid': 54, 'eventname': 'course module viewed',
             'timecreated': 1700000000},
            {'user_id': 101, 'cluster_id': 2, 'cmid': 54, 'eventname': 'quiz_attempt_started',
             'timecreated': 1700000300, 'grade': 75.0}
        ]
        
        events = self.preprocessor.parse_raw_logs(raw_logs)
        
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].user_id, 101)
        self.assertEqual(events[1].action_type, ActionType.ATTEMPT_QUIZ)
    
    def test_aggregate_by_user_module(self):
        """Test aggregation by user and module"""
        if not hasattr(self, 'preprocessor'):
            self.skipTest("course_structure.json not found")
        
        raw_logs = [
            {'user_id': 101, 'cluster_id': 2, 'cmid': 54, 'eventname': 'view',
             'timecreated': 1700000000},
            {'user_id': 101, 'cluster_id': 2, 'cmid': 54, 'eventname': 'quiz attempt',
             'timecreated': 1700000300, 'grade': 80}
        ]
        
        events = self.preprocessor.parse_raw_logs(raw_logs)
        summaries = self.preprocessor.aggregate_by_user_module(events)
        
        self.assertIn((101, 54), summaries)
        summary = summaries[(101, 54)]
        self.assertEqual(summary.total_actions, 2)


class TestLogToStateBuilder(unittest.TestCase):
    """Test log-to-state builder"""
    
    def setUp(self):
        """Set up test fixtures"""
        base_path = Path(__file__).parent.parent
        self.cluster_path = base_path / 'data' / 'cluster_profiles.json'
        self.course_path = base_path / 'data' / 'course_structure.json'
        
        if self.cluster_path.exists() and self.course_path.exists():
            self.builder = LogToStateBuilder(
                cluster_profiles_path=str(self.cluster_path),
                course_structure_path=str(self.course_path),
                recent_window=10
            )
    
    def test_build_states_from_logs(self):
        """Test building states from logs"""
        if not hasattr(self, 'builder'):
            self.skipTest("Required data files not found")
        
        sample_logs = [
            {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'view content',
             'timestamp': 1700000000, 'progress': 0.3},
            {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'attempt quiz',
             'timestamp': 1700000300, 'score': 0.75, 'progress': 0.5},
        ]
        
        states = self.builder.build_states_from_logs(sample_logs)
        
        self.assertIn((101, 54), states)
        state = states[(101, 54)]
        self.assertEqual(len(state), 6)  # 6D state
        
        # Check state dimensions
        cluster_id, module_idx, progress_bin, score_bin, phase, engagement = state
        self.assertIsInstance(cluster_id, int)
        self.assertIsInstance(module_idx, int)
        self.assertIsInstance(progress_bin, float)
        self.assertIsInstance(score_bin, float)
        self.assertIn(phase, [0, 1, 2])
        self.assertIn(engagement, [0, 1, 2])
    
    def test_state_explanation(self):
        """Test state explanation"""
        if not hasattr(self, 'builder'):
            self.skipTest("Required data files not found")
        
        state = (2, 0, 0.5, 0.75, 1, 1)  # Sample 6D state
        
        explanation = self.builder.get_state_explanation(state, verbose=True)
        
        self.assertIn('state_string', explanation)
        self.assertIn('dimensions', explanation)
        self.assertIn('interpretation', explanation)
        self.assertEqual(len(explanation['dimensions']), 6)


class TestStateRepository(unittest.TestCase):
    """Test MongoDB state repository"""
    
    def setUp(self):
        """Set up test repository"""
        try:
            self.repo = StateRepository()
            self.test_user_id = 999999  # Use high ID to avoid conflicts
        except Exception as e:
            self.skipTest(f"MongoDB not available: {e}")
    
    def tearDown(self):
        """Clean up test data"""
        if hasattr(self, 'repo'):
            self.repo.delete_user_states(self.test_user_id)
            self.repo.close()
    
    def test_save_and_get_state(self):
        """Test saving and retrieving state"""
        if not hasattr(self, 'repo'):
            self.skipTest("MongoDB not available")
        
        state = (2, 0, 0.5, 0.75, 1, 1)
        
        # Save state
        result = self.repo.save_state(
            user_id=self.test_user_id,
            module_id=54,
            state=state
        )
        self.assertTrue(result)
        
        # Get state
        retrieved_state = self.repo.get_state(
            user_id=self.test_user_id,
            module_id=54
        )
        self.assertEqual(retrieved_state, state)
    
    def test_get_user_states(self):
        """Test getting all states for a user"""
        if not hasattr(self, 'repo'):
            self.skipTest("MongoDB not available")
        
        # Save multiple states
        states = {
            54: (2, 0, 0.5, 0.75, 1, 1),
            56: (2, 1, 0.25, 0.5, 0, 0)
        }
        
        for module_id, state in states.items():
            self.repo.save_state(
                user_id=self.test_user_id,
                module_id=module_id,
                state=state
            )
        
        # Get all states
        user_states = self.repo.get_user_states(self.test_user_id)
        self.assertEqual(len(user_states), 2)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("Running Integration Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestLogModels))
    suite.addTests(loader.loadTestsFromTestCase(TestLogPreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestLogToStateBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestStateRepository))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
