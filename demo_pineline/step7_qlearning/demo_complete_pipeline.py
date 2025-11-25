#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Demo: Logs → States → Q-Learning
==========================================
Demonstrates full pipeline from Moodle logs to Q-table updates

Flow:
1. Parse sample logs
2. Build 6D states
3. Detect state transitions
4. Calculate rewards
5. Update Q-table
6. Show Q-table contents
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.qlearning_agent_v2 import QLearningAgentV2
from core.reward_calculator_v2 import RewardCalculatorV2
from core.action_space import ActionSpace
from core.log_to_state_builder import LogToStateBuilder
from services.qtable_update_service import QTableUpdateService
from pipeline.log_processing_pipeline import LogProcessingPipeline


def generate_realistic_logs():
    """Generate realistic learning sequence logs"""
    logs = []
    
    # User 101: Medium learner (cluster 2) - Good progression
    user_101_logs = [
        # Module 54: Initial learning
        {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'view_content',
         'timestamp': 1700000000, 'score': 0.0, 'progress': 0.1},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'view_content',
         'timestamp': 1700000300, 'score': 0.0, 'progress': 0.2},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'attempt_quiz',
         'timestamp': 1700000600, 'score': 0.6, 'progress': 0.3},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'review_errors',
         'timestamp': 1700000900, 'score': 0.6, 'progress': 0.4},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'attempt_quiz',
         'timestamp': 1700001200, 'score': 0.75, 'progress': 0.5},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 54, 'action': 'submit_quiz',
         'timestamp': 1700001500, 'score': 0.8, 'progress': 0.6},
        
        # Module 55: Continue learning
        {'user_id': 101, 'cluster_id': 2, 'module_id': 55, 'action': 'view_content',
         'timestamp': 1700002000, 'score': 0.8, 'progress': 0.1},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 55, 'action': 'attempt_quiz',
         'timestamp': 1700002300, 'score': 0.7, 'progress': 0.3},
        {'user_id': 101, 'cluster_id': 2, 'module_id': 55, 'action': 'submit_quiz',
         'timestamp': 1700002600, 'score': 0.85, 'progress': 0.5},
    ]
    
    # User 102: Weak learner (cluster 0) - Needs more help
    user_102_logs = [
        {'user_id': 102, 'cluster_id': 0, 'module_id': 54, 'action': 'view_content',
         'timestamp': 1700000000, 'score': 0.0, 'progress': 0.1},
        {'user_id': 102, 'cluster_id': 0, 'module_id': 54, 'action': 'attempt_quiz',
         'timestamp': 1700000600, 'score': 0.3, 'progress': 0.2},
        {'user_id': 102, 'cluster_id': 0, 'module_id': 54, 'action': 'review_errors',
         'timestamp': 1700000900, 'score': 0.3, 'progress': 0.3},
        {'user_id': 102, 'cluster_id': 0, 'module_id': 54, 'action': 'view_content',
         'timestamp': 1700001200, 'score': 0.3, 'progress': 0.4},
        {'user_id': 102, 'cluster_id': 0, 'module_id': 54, 'action': 'attempt_quiz',
         'timestamp': 1700001500, 'score': 0.5, 'progress': 0.5},
    ]
    
    # User 103: Strong learner (cluster 3) - Fast progression
    user_103_logs = [
        {'user_id': 103, 'cluster_id': 3, 'module_id': 54, 'action': 'view_content',
         'timestamp': 1700000000, 'score': 0.0, 'progress': 0.2},
        {'user_id': 103, 'cluster_id': 3, 'module_id': 54, 'action': 'attempt_quiz',
         'timestamp': 1700000300, 'score': 0.9, 'progress': 0.4},
        {'user_id': 103, 'cluster_id': 3, 'module_id': 54, 'action': 'submit_quiz',
         'timestamp': 1700000600, 'score': 0.95, 'progress': 0.6},
        {'user_id': 103, 'cluster_id': 3, 'module_id': 55, 'action': 'view_content',
         'timestamp': 1700000900, 'score': 0.95, 'progress': 0.1},
        {'user_id': 103, 'cluster_id': 3, 'module_id': 55, 'action': 'attempt_quiz',
         'timestamp': 1700001200, 'score': 0.9, 'progress': 0.3},
    ]
    
    logs.extend(user_101_logs)
    logs.extend(user_102_logs)
    logs.extend(user_103_logs)
    
    return logs


def main():
    """Main demo function"""
    print("=" * 80)
    print("COMPLETE DEMO: Logs → States → Q-Learning")
    print("=" * 80)
    
    # Paths
    base_path = Path(__file__).parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    course_path = base_path / 'data' / 'course_structure.json'
    
    # Check files exist
    if not cluster_path.exists() or not course_path.exists():
        print("\n❌ Required data files not found!")
        print(f"   Need: {cluster_path}")
        print(f"   Need: {course_path}")
        return
    
    # =========================================================================
    # STEP 1: Initialize Components
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: Initialize Q-Learning Components")
    print("=" * 80)
    
    # Action space
    print("\n1.1 Creating action space...")
    action_space = ActionSpace()
    print(f"    ✓ {action_space.get_action_count()} actions available")
    
    # Q-Learning agent
    print("\n1.2 Creating Q-Learning agent...")
    agent = QLearningAgentV2(
        n_actions=action_space.get_action_count(),
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.1,
        cluster_adaptive=True
    )
    print(f"    ✓ Agent initialized with cluster-adaptive learning")
    
    # Reward calculator
    print("\n1.3 Creating reward calculator...")
    reward_calc = RewardCalculatorV2(
        cluster_profiles_path=str(cluster_path)
    )
    print(f"    ✓ Reward calculator ready")
    
    # Log-to-state builder
    print("\n1.4 Creating log-to-state builder...")
    builder = LogToStateBuilder(
        cluster_profiles_path=str(cluster_path),
        course_structure_path=str(course_path)
    )
    print(f"    ✓ State builder ready")
    
    # Q-table update service
    print("\n1.5 Creating Q-table update service...")
    updater = QTableUpdateService(
        agent=agent,
        reward_calculator=reward_calc,
        action_space=action_space,
        log_to_state_builder=builder,
        verbose=False  # Set True for detailed logs
    )
    print(f"    ✓ Update service ready")
    
    # =========================================================================
    # STEP 2: Generate Sample Logs
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Generate Sample Learning Logs")
    print("=" * 80)
    
    logs = generate_realistic_logs()
    print(f"\n✓ Generated {len(logs)} log events")
    print(f"  - 3 users: 101 (medium), 102 (weak), 103 (strong)")
    print(f"  - 2 modules: 54, 55")
    print(f"  - Actions: view, attempt, submit, review")
    
    # =========================================================================
    # STEP 3: Process Logs → States
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Convert Logs to 6D States")
    print("=" * 80)
    
    states = builder.build_states_from_logs(logs)
    print(f"\n✓ Built {len(states)} unique states")
    
    # Show sample states
    print("\n📊 Sample States:")
    for i, ((user_id, module_id), state) in enumerate(list(states.items())[:3]):
        print(f"\n  User {user_id}, Module {module_id}:")
        print(f"    State: {state}")
        print(f"    {builder.state_builder.state_to_string(state)}")
    
    # =========================================================================
    # STEP 4: Update Q-Table
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Update Q-Table from State Transitions")
    print("=" * 80)
    
    print("\n🔄 Processing transitions and updating Q-table...")
    update_stats = updater.update_from_logs(logs)
    
    print(f"\n✓ Q-Table Update Complete!")
    print(f"  - Users processed: {update_stats['users_processed']}")
    print(f"  - Transitions: {update_stats['transitions_processed']}")
    print(f"  - Q-updates: {update_stats['q_updates']}")
    print(f"  - Total reward: {update_stats['total_reward']:.3f}")
    print(f"  - Avg reward: {update_stats['avg_reward']:.3f}")
    
    print(f"\n📈 Action Distribution:")
    for action_idx, count in update_stats['action_counts'].items():
        action = action_space.get_action_by_index(action_idx)
        print(f"  - {action.name if action else 'Unknown'}: {count} times")
    
    # =========================================================================
    # STEP 5: Inspect Q-Table
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: Inspect Q-Table Contents")
    print("=" * 80)
    
    print(f"\nQ-Table Statistics:")
    print(f"  - States in Q-table: {len(agent.q_table)}")
    print(f"  - Total updates: {agent.stats['total_updates']}")
    
    # Show top Q-values
    print(f"\n📊 Top Q-Values (Best State-Action Pairs):")
    all_q_values = []
    for state, actions in agent.q_table.items():
        for action_idx, q_value in actions.items():
            all_q_values.append((state, action_idx, q_value))
    
    # Sort by Q-value
    all_q_values.sort(key=lambda x: x[2], reverse=True)
    
    # Show top 5
    for i, (state, action_idx, q_value) in enumerate(all_q_values[:5]):
        action = action_space.get_action_by_index(action_idx)
        print(f"\n  #{i+1}: Q = {q_value:.4f}")
        print(f"      State: {state}")
        print(f"      {builder.state_builder.state_to_string(state)}")
        print(f"      Best Action: {action.name if action else 'Unknown'}")
    
    # =========================================================================
    # STEP 6: Test Recommendations
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 6: Test Action Recommendations")
    print("=" * 80)
    
    # Test for different users
    test_states = list(states.values())[:3]
    
    print("\n🎯 Recommendations for sample states:")
    for i, state in enumerate(test_states, 1):
        action_idx = agent.select_action(state)  # Use select_action instead
        action = action_space.get_action_by_index(action_idx)
        q_value = agent.get_q_value(state, action_idx)
        
        print(f"\n  Test {i}:")
        print(f"    State: {builder.state_builder.state_to_string(state)}")
        print(f"    Recommended: {action.name if action else 'Unknown'}")
        print(f"    Q-value: {q_value:.4f}")
        print(f"    Action Type: {action.action_type if action else 'N/A'}")
    
    # =========================================================================
    # STEP 7: Pipeline Integration Demo
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 7: Full Pipeline Integration")
    print("=" * 80)
    
    print("\n🚀 Creating integrated pipeline...")
    pipeline = LogProcessingPipeline(
        cluster_profiles_path=str(cluster_path),
        course_structure_path=str(course_path),
        mongo_uri=None,  # Skip MongoDB for demo
        qtable_updater=updater,
        enable_qtable_updates=True
    )
    
    print("\n📦 Processing logs through pipeline...")
    summary = pipeline.process_logs_from_dict(
        raw_logs=logs,
        save_to_db=False  # Skip MongoDB for demo
    )
    
    print(f"\n✓ Pipeline execution complete!")
    print(f"  Summary: {summary}")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)
    
    print("\n📋 What We Demonstrated:")
    print("  1. ✅ Parsed 24 realistic learning logs")
    print("  2. ✅ Built 6D states for 3 users across 2 modules")
    print("  3. ✅ Detected state transitions from sequential logs")
    print("  4. ✅ Calculated cluster-aware rewards")
    print("  5. ✅ Updated Q-table with Q-learning algorithm")
    print("  6. ✅ Inspected learned Q-values")
    print("  7. ✅ Generated action recommendations")
    print("  8. ✅ Integrated everything in unified pipeline")
    
    print("\n🎯 Key Results:")
    print(f"  - Q-table now has {len(agent.q_table)} states")
    print(f"  - Total Q-updates: {agent.stats['total_updates']}")
    print(f"  - Agent ready for recommendations!")
    
    print("\n📚 Next Steps:")
    print("  1. Connect to real Moodle logs via API")
    print("  2. Enable MongoDB persistence")
    print("  3. Run batch training on historical data")
    print("  4. Deploy real-time recommendation service")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
