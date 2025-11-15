#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Action Space
=====================
Comprehensive tests for the action space design
"""

from core.action_space import ActionSpace, LearningAction


def test_action_space_initialization():
    """Test 1: Action space initialization"""
    print("=" * 70)
    print("TEST 1: Action Space Initialization")
    print("=" * 70)
    
    action_space = ActionSpace()
    
    assert action_space.get_action_count() == 15, "Should have 15 actions"
    assert len(action_space.actions) == 15, "Actions list should have 15 items"
    assert len(action_space.action_map) == 15, "Action map should have 15 entries"
    assert len(action_space.index_map) == 15, "Index map should have 15 entries"
    
    print("✓ Action space initialized with 15 actions")
    print("✓ All internal maps populated correctly")


def test_action_distribution():
    """Test 2: Action distribution by context"""
    print("\n" + "=" * 70)
    print("TEST 2: Action Distribution")
    print("=" * 70)
    
    action_space = ActionSpace()
    summary = action_space.get_action_summary()
    
    # Check context distribution
    assert summary['by_context']['past'] == 5, "Should have 5 past actions"
    assert summary['by_context']['current'] == 7, "Should have 7 current actions"
    assert summary['by_context']['future'] == 3, "Should have 3 future actions"
    
    print("\n✓ Past actions: 5")
    print("✓ Current actions: 7")
    print("✓ Future actions: 3")
    
    # Show distribution
    print("\nAction Type Distribution:")
    for action_type, count in sorted(summary['by_type'].items()):
        print(f"  {action_type:25s}: {count}")


def test_action_retrieval():
    """Test 3: Action retrieval methods"""
    print("\n" + "=" * 70)
    print("TEST 3: Action Retrieval")
    print("=" * 70)
    
    action_space = ActionSpace()
    
    # Test 3.1: Get by tuple
    action = action_space.get_action_by_tuple("attempt_quiz", "current")
    assert action is not None, "Should find attempt_quiz/current"
    assert action.action_type == "attempt_quiz"
    assert action.time_context == "current"
    print("✓ get_action_by_tuple('attempt_quiz', 'current') works")
    
    # Test 3.2: Get by index
    action = action_space.get_action_by_index(8)
    assert action is not None, "Should find action at index 8"
    assert action.index == 8
    print(f"✓ get_action_by_index(8) works: {action}")
    
    # Test 3.3: Get by type
    quiz_actions = action_space.get_actions_by_type("attempt_quiz")
    assert len(quiz_actions) == 3, "Should have 3 attempt_quiz actions"
    print(f"✓ get_actions_by_type('attempt_quiz') found {len(quiz_actions)} actions")
    
    # Test 3.4: Get by context
    current_actions = action_space.get_actions_by_context("current")
    assert len(current_actions) == 7, "Should have 7 current actions"
    print(f"✓ get_actions_by_context('current') found {len(current_actions)} actions")
    
    # Test 3.5: Get action index
    idx = action_space.get_action_index("submit_quiz", "current")
    assert idx == 9, "submit_quiz/current should be at index 9"
    print(f"✓ get_action_index('submit_quiz', 'current') = {idx}")


def test_action_validation():
    """Test 4: Action validation"""
    print("\n" + "=" * 70)
    print("TEST 4: Action Validation")
    print("=" * 70)
    
    action_space = ActionSpace()
    
    # Valid actions
    valid_actions = [
        ("attempt_quiz", "past"),
        ("submit_quiz", "current"),
        ("view_content", "future"),
        ("review_quiz", "current"),
    ]
    
    for action_type, time_context in valid_actions:
        is_valid = action_space.is_valid_action(action_type, time_context)
        assert is_valid, f"({action_type}, {time_context}) should be valid"
        print(f"✓ ({action_type:25s}, {time_context:10s}) is valid")
    
    # Invalid actions
    invalid_actions = [
        ("submit_assignment", "future"),  # No submit_assignment in future
        ("submit_quiz", "past"),  # No submit_quiz in past
        ("invalid_action", "current"),
        ("attempt_quiz", "invalid_context"),
    ]
    
    print("\nInvalid actions:")
    for action_type, time_context in invalid_actions:
        is_valid = action_space.is_valid_action(action_type, time_context)
        assert not is_valid, f"({action_type}, {time_context}) should be invalid"
        print(f"✓ ({action_type:25s}, {time_context:10s}) is invalid")


def test_action_structure():
    """Test 5: Action structure verification"""
    print("\n" + "=" * 70)
    print("TEST 5: Action Structure Verification")
    print("=" * 70)
    
    action_space = ActionSpace()
    
    # Verify expected actions exist
    expected_actions = [
        # Past
        ("view_assignment", "past", 0),
        ("view_content", "past", 1),
        ("attempt_quiz", "past", 2),
        ("review_quiz", "past", 3),
        ("post_forum", "past", 4),
        # Current
        ("view_assignment", "current", 5),
        ("view_content", "current", 6),
        ("submit_assignment", "current", 7),
        ("attempt_quiz", "current", 8),
        ("submit_quiz", "current", 9),
        ("review_quiz", "current", 10),
        ("post_forum", "current", 11),
        # Future
        ("view_content", "future", 12),
        ("attempt_quiz", "future", 13),
        ("post_forum", "future", 14),
    ]
    
    for action_type, time_context, expected_idx in expected_actions:
        action = action_space.get_action_by_tuple(action_type, time_context)
        assert action is not None, f"Action ({action_type}, {time_context}) should exist"
        assert action.index == expected_idx, f"Index mismatch for ({action_type}, {time_context})"
        print(f"✓ [{expected_idx:2d}] {action_type:25s} | {time_context:10s}")
    
    print(f"\n✓ All {len(expected_actions)} expected actions verified")


def test_action_tuple_conversion():
    """Test 6: Action tuple conversion"""
    print("\n" + "=" * 70)
    print("TEST 6: Action Tuple Conversion")
    print("=" * 70)
    
    action_space = ActionSpace()
    
    action = action_space.get_action_by_index(8)
    assert action is not None
    
    tuple_repr = action.to_tuple()
    assert tuple_repr == ("attempt_quiz", "current")
    print(f"✓ Action.to_tuple() works: {tuple_repr}")
    
    # Verify can retrieve back using tuple
    retrieved = action_space.get_action_by_tuple(*tuple_repr)
    assert retrieved.index == action.index
    print(f"✓ Can retrieve action back using tuple: {retrieved}")


def test_all_actions_unique():
    """Test 7: All actions are unique"""
    print("\n" + "=" * 70)
    print("TEST 7: Action Uniqueness")
    print("=" * 70)
    
    action_space = ActionSpace()
    
    # Check indices are unique
    indices = [action.index for action in action_space.actions]
    assert len(indices) == len(set(indices)), "All indices should be unique"
    print("✓ All action indices are unique")
    
    # Check tuples are unique
    tuples = [action.to_tuple() for action in action_space.actions]
    assert len(tuples) == len(set(tuples)), "All action tuples should be unique"
    print("✓ All action tuples are unique")
    
    # Check no gaps in indices
    assert indices == list(range(15)), "Indices should be 0-14 without gaps"
    print("✓ Action indices are sequential (0-14)")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("RUNNING ALL TESTS FOR NEW ACTION SPACE")
    print("=" * 70)
    
    tests = [
        test_action_space_initialization,
        test_action_distribution,
        test_action_retrieval,
        test_action_validation,
        test_action_structure,
        test_action_tuple_conversion,
        test_all_actions_unique,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ❌")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
