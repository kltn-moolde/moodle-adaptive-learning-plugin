#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Table Update Service
======================
Connects log-to-state pipeline with Q-Learning agent for online learning

Flow:
1. Parse logs → 6D states (LogToStateBuilder)
2. Detect state transitions from sequential logs
3. Map actions to action_space indices
4. Calculate rewards (RewardCalculatorV2)
5. Update Q-table (QLearningAgentV2)

Usage:
    updater = QTableUpdateService(
        agent=qlearning_agent,
        reward_calculator=reward_calc,
        action_space=action_space
    )
    
    # From logs
    stats = updater.update_from_logs(logs_list)
    
    # From states (if already converted)
    stats = updater.update_from_states(states_list)
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np

# Handle imports for both module and standalone execution
try:
    from core.qlearning_agent_v2 import QLearningAgentV2
    from core.reward_calculator_v2 import RewardCalculatorV2
    from core.action_space import ActionSpace
    from core.log_to_state_builder import LogToStateBuilder
    from core.lo_mastery_tracker import LOMasteryTracker
except ImportError:
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from core.qlearning_agent_v2 import QLearningAgentV2
    from core.reward_calculator_v2 import RewardCalculatorV2
    from core.action_space import ActionSpace
    from core.log_to_state_builder import LogToStateBuilder
    from core.lo_mastery_tracker import LOMasteryTracker


class QTableUpdateService:
    """
    Service to update Q-table from log events
    
    Responsibilities:
    - Convert logs to state transitions
    - Map log actions to action_space indices
    - Calculate rewards for transitions
    - Update Q-table via QLearningAgentV2.update()
    """
    
    def __init__(
        self,
        agent: QLearningAgentV2,
        reward_calculator: RewardCalculatorV2,
        action_space: ActionSpace,
        log_to_state_builder: Optional[LogToStateBuilder] = None,
        lo_mastery_tracker: Optional[LOMasteryTracker] = None,
        min_transition_gap: int = 60,  # seconds
        max_transition_gap: int = 3600,  # 1 hour
        verbose: bool = False
    ):
        """
        Initialize Q-table update service
        
        Args:
            agent: Q-Learning agent to update
            reward_calculator: Reward calculator for transitions
            action_space: Action space for mapping log actions
            log_to_state_builder: Optional builder for log→state conversion
            lo_mastery_tracker: Optional LO mastery tracker for reward bonus
            min_transition_gap: Min seconds between valid transitions
            max_transition_gap: Max seconds for valid transition sequence
            verbose: Print detailed logs
        """
        self.agent = agent
        self.reward_calculator = reward_calculator
        self.action_space = action_space
        self.log_to_state_builder = log_to_state_builder
        self.lo_mastery_tracker = lo_mastery_tracker
        self.min_transition_gap = min_transition_gap
        self.max_transition_gap = max_transition_gap
        self.verbose = verbose
        
        # Statistics
        self.stats = {
            'total_logs_processed': 0,
            'valid_transitions': 0,
            'invalid_transitions': 0,
            'q_updates': 0,
            'total_reward': 0.0,
            'action_distribution': defaultdict(int)
        }
        
        if verbose:
            print("=" * 70)
            print("Q-Table Update Service Initialized")
            print("=" * 70)
            print(f"  Agent: {agent.__class__.__name__}")
            print(f"  Reward Calculator: {reward_calculator.__class__.__name__}")
            print(f"  Action Space: {action_space.get_action_count()} actions")
            print(f"  Transition gap: {min_transition_gap}s - {max_transition_gap}s")
            print("=" * 70)
    
    def update_from_logs(
        self,
        logs: List[Dict],
        user_id: Optional[int] = None
    ) -> Dict:
        """
        Update Q-table from raw log events
        
        Args:
            logs: List of log dicts with keys:
                  - user_id, cluster_id, module_id
                  - action, timestamp, score, progress
            user_id: Optional filter for specific user
            
        Returns:
            Statistics dict
        """
        if not self.log_to_state_builder:
            raise ValueError("log_to_state_builder required for update_from_logs()")
        
        # Filter logs if user_id specified
        if user_id is not None:
            logs = [log for log in logs if log.get('user_id') == user_id]
        
        # Convert logs to states
        states_map = self.log_to_state_builder.build_states_from_logs(logs)
        
        # Build state sequence for each user
        user_sequences = self._build_state_sequences(logs, states_map)
        
        # Update Q-table from sequences
        return self._update_from_sequences(user_sequences)
    
    def _build_state_sequences(
        self,
        logs: List[Dict],
        states_map: Dict[Tuple[int, int], Tuple]
    ) -> Dict[int, List[Dict]]:
        """
        Build temporal state sequences from logs
        
        Args:
            logs: Sorted log events
            states_map: {(user_id, module_id): state_tuple}
            
        Returns:
            {user_id: [transition_dicts]}
        """
        # Sort logs by user and timestamp
        sorted_logs = sorted(logs, key=lambda x: (x['user_id'], x['timestamp']))
        
        # Group by user
        user_logs = defaultdict(list)
        for log in sorted_logs:
            user_logs[log['user_id']].append(log)
        
        # Build sequences
        sequences = {}
        for user_id, user_log_list in user_logs.items():
            sequence = []
            
            for i in range(len(user_log_list) - 1):
                current_log = user_log_list[i]
                next_log = user_log_list[i + 1]
                
                # Check time gap
                time_gap = next_log['timestamp'] - current_log['timestamp']
                if time_gap < self.min_transition_gap or time_gap > self.max_transition_gap:
                    continue
                
                # Get states
                current_key = (user_id, current_log['module_id'])
                next_key = (user_id, next_log['module_id'])
                
                if current_key not in states_map or next_key not in states_map:
                    continue
                
                current_state = states_map[current_key]
                next_state = states_map[next_key]
                
                # Use RAW log progress for context detection (not aggregated state progress)
                raw_progress = current_log.get('progress', 0.0)
                raw_learning_phase = current_log.get('learning_phase')
                
                # Determine time context from RAW log data
                time_context = self._determine_time_context(
                    module_idx=current_log['module_id'],
                    progress=raw_progress,
                    learning_phase=raw_learning_phase
                )
                
                # Map action with determined context
                action_idx = self._map_action_with_time_context(
                    action_str=current_log['action'],
                    time_context=time_context,
                    log=current_log
                )
                if action_idx is None:
                    continue
                
                # Build transition
                transition = {
                    'state': current_state,
                    'action': action_idx,
                    'next_state': next_state,
                    'timestamp': current_log['timestamp'],
                    'module_id': current_log['module_id'],
                    'score': current_log.get('score', 0.0),
                    'progress': current_log.get('progress', 0.0),
                    'time_gap': time_gap
                }
                
                sequence.append(transition)
            
            if sequence:
                sequences[user_id] = sequence
        
        return sequences
    
    def _determine_time_context(
        self,
        module_idx: int,
        progress: float,
        learning_phase: Optional[int] = None
    ) -> str:
        """
        Determine time context (past/current/future) for action
        
        Args:
            module_idx: Module index (0-5)
            progress: Module progress (0.0-1.0)
            learning_phase: Learning phase (0=pre, 1=active, 2=reflective)
            
        Returns:
            Time context: 'past', 'current', or 'future'
        """
        # If progress >= 1.0 → completed module → past
        if progress >= 1.0:
            return 'past'
        
        # If progress >= 0.75 and in reflective phase → past (reviewing)
        if progress >= 0.75 and learning_phase == 2:
            return 'past'
        
        # If progress > 0 → currently working → current
        if progress > 0:
            return 'current'
        
        # If progress = 0 → not started → future
        return 'future'
    
    def _map_action_with_time_context(
        self,
        action_str: str,
        time_context: str,
        log: Dict
    ) -> Optional[int]:
        """
        Map log action to action_space index with known time context
        
        Args:
            action_str: Action string from log
            time_context: Time context ('past', 'current', 'future')
            log: Full log dict for additional info
            
        Returns:
            Action index or None if invalid
        """
        # Normalize action string to action_type
        action_type = self._normalize_action_type(action_str)
        if not action_type:
            if self.verbose:
                print(f"  ✗ Unknown action type: '{action_str}'")
            return None
        
        # Find action in action_space with (action_type, time_context)
        action = self.action_space.get_action_by_tuple(action_type, time_context)
        
        if action:
            if self.verbose:
                print(f"  ✓ Mapped '{action_str}' → {action_type} ({time_context}) [idx={action.index}]")
            return action.index
        
        # Fallback: Try other contexts if exact match not available
        for fallback_context in ['current', 'past', 'future']:
            if fallback_context != time_context:
                action = self.action_space.get_action_by_tuple(action_type, fallback_context)
                if action:
                    if self.verbose:
                        print(f"  ⚠️  Fallback: '{action_str}' → {action_type} ({fallback_context}) [idx={action.index}]")
                    return action.index
        
        if self.verbose:
            print(f"  ✗ No valid mapping: '{action_str}' (type={action_type}, context={time_context})")
        
        return None
    
    def _map_action_with_context(
        self,
        action_str: str,
        module_idx: int,
        progress: float,
        log: Dict
    ) -> Optional[int]:
        """
        DEPRECATED: Use _map_action_with_time_context() instead
        
        Map log action to action_space index with time context
        Old method that determines context from module state
        """
        # Normalize action string
        action_str = action_str.lower().strip()
        
        # Determine time context from state
        learning_phase = log.get('learning_phase')  # If available
        time_context = self._determine_time_context(module_idx, progress, learning_phase)
        
        # Map action_str to action_type
        action_type = self._normalize_action_type(action_str)
        if not action_type:
            return None
        
        # Find action in action_space with matching (action_type, time_context)
        action = self.action_space.get_action_by_tuple(action_type, time_context)
        
        if action:
            if self.verbose:
                print(f"  ✓ Mapped '{action_str}' → {action_type} ({time_context}) [idx={action.index}]")
            return action.index
        
        # Fallback: Try other time contexts if exact match not found
        for fallback_context in ['current', 'past', 'future']:
            if fallback_context != time_context:
                action = self.action_space.get_action_by_tuple(action_type, fallback_context)
                if action:
                    if self.verbose:
                        print(f"  ⚠️  Fallback: '{action_str}' → {action_type} ({fallback_context}) [idx={action.index}]")
                    return action.index
        
        if self.verbose:
            print(f"  ✗ Could not map action: '{action_str}' (type={action_type}, context={time_context})")
        
        return None
    
    def _normalize_action_type(self, action_str: str) -> Optional[str]:
        """
        Normalize action string to action_type
        
        Args:
            action_str: Raw action string from log
            
        Returns:
            Normalized action_type or None
        """
        action_str = action_str.lower().strip()
        
        # Direct mappings
        action_mappings = {
            # View actions
            'view_content': 'view_content',
            'view': 'view_content',
            'read': 'view_content',
            'watch': 'view_content',
            'video': 'view_content',
            'resource': 'view_content',
            'page': 'view_content',
            'url': 'view_content',
            
            # Assignment actions
            'view_assignment': 'view_assignment',
            'assignment': 'view_assignment',
            'submit_assignment': 'submit_assignment',
            'upload': 'submit_assignment',
            
            # Quiz actions
            'attempt_quiz': 'attempt_quiz',
            'attempt': 'attempt_quiz',
            'start_quiz': 'attempt_quiz',
            'quiz_attempt': 'attempt_quiz',
            
            'submit_quiz': 'submit_quiz',
            'submit': 'submit_quiz',
            'finish_quiz': 'submit_quiz',
            'complete_quiz': 'submit_quiz',
            
            'review_quiz': 'review_quiz',
            'review': 'review_quiz',
            'review_errors': 'review_quiz',
            'view_quiz': 'review_quiz',
            
            # Forum actions
            'post_forum': 'post_forum',
            'forum': 'post_forum',
            'discuss': 'post_forum',
            'post': 'post_forum',
            'reply': 'post_forum',
            'forum_post': 'post_forum',
            'forum_reply': 'post_forum'
        }
        
        # Exact match
        if action_str in action_mappings:
            return action_mappings[action_str]
        
        # Partial match
        for key, mapped_type in action_mappings.items():
            if key in action_str or action_str in key:
                return mapped_type
        
        # Check if contains key action words
        if 'view' in action_str or 'read' in action_str or 'watch' in action_str:
            if 'assignment' in action_str:
                return 'view_assignment'
            return 'view_content'
        
        if 'attempt' in action_str or 'start' in action_str:
            if 'quiz' in action_str:
                return 'attempt_quiz'
        
        if 'submit' in action_str or 'finish' in action_str or 'complete' in action_str:
            if 'assignment' in action_str:
                return 'submit_assignment'
            if 'quiz' in action_str:
                return 'submit_quiz'
        
        if 'review' in action_str:
            return 'review_quiz'
        
        if 'forum' in action_str or 'discuss' in action_str or 'post' in action_str or 'reply' in action_str:
            return 'post_forum'
        
        return None
    
    def _map_action(self, action_str: str) -> Optional[int]:
        """
        DEPRECATED: Use _map_action_with_context() instead
        
        Old simple mapping without time context
        Kept for backward compatibility
        """
        # Normalize action string
        action_str = action_str.lower().strip()
        
        # Try to find matching action
        for action in self.action_space.get_actions():
            action_name = action.action_type.lower()
            
            # Check if action matches
            if action_str in action_name or action_name in action_str:
                return action.index
        
        # Try common mappings
        action_mappings = {
            'view': 'view_content',
            'read': 'view_content',
            'attempt': 'attempt_quiz',
            'start': 'attempt_quiz',
            'submit': 'submit_quiz',
            'complete': 'submit_quiz',
            'review': 'review_quiz',
            'forum': 'post_forum',
            'post': 'post_forum',
            'discuss': 'post_forum',
            'assignment': 'view_assignment'
        }
        
        for key, mapped in action_mappings.items():
            if key in action_str:
                # Find action for mapped type
                for action in self.action_space.get_actions():
                    if mapped in action.action_type.lower():
                        return action.index
        
        if self.verbose:
            print(f"⚠️  Could not map action: '{action_str}'")
        
        return None
    
    def _update_from_sequences(
        self,
        user_sequences: Dict[int, List[Dict]]
    ) -> Dict:
        """
        Update Q-table from user state sequences
        
        Args:
            user_sequences: {user_id: [transition_dicts]}
            
        Returns:
            Statistics dict
        """
        local_stats = {
            'users_processed': len(user_sequences),
            'transitions_processed': 0,
            'q_updates': 0,
            'total_reward': 0.0,
            'avg_reward': 0.0,
            'action_counts': defaultdict(int)
        }
        
        for user_id, sequence in user_sequences.items():
            if self.verbose:
                print(f"\n📊 Processing user {user_id}: {len(sequence)} transitions")
            
            for transition in sequence:
                # Calculate reward
                reward = self._calculate_reward(transition)
                
                # Determine if terminal state
                is_terminal = self._is_terminal(transition['next_state'])
                
                # Update Q-table
                self.agent.update(
                    state=transition['state'],
                    action=transition['action'],
                    reward=reward,
                    next_state=transition['next_state'],
                    is_terminal=is_terminal
                )
                
                # Update statistics
                local_stats['transitions_processed'] += 1
                local_stats['q_updates'] += 1
                local_stats['total_reward'] += reward
                local_stats['action_counts'][transition['action']] += 1
                
                self.stats['q_updates'] += 1
                self.stats['total_reward'] += reward
                self.stats['action_distribution'][transition['action']] += 1
                
                if self.verbose:
                    action = self.action_space.get_action_by_index(transition['action'])
                    action_name = action.name if action else 'Unknown'
                    print(f"  ✓ State {transition['state'][:3]}... → "
                          f"Action {action_name} → "
                          f"Reward {reward:.3f}")
        
        # Calculate averages
        if local_stats['transitions_processed'] > 0:
            local_stats['avg_reward'] = (
                local_stats['total_reward'] / local_stats['transitions_processed']
            )
        
        return local_stats
    
    def _calculate_reward(self, transition: Dict) -> float:
        """
        Calculate reward for a state transition
        
        Args:
            transition: Transition dict with state, action, next_state
            
        Returns:
            Reward value
        """
        state = transition['state']
        next_state = transition['next_state']
        action_idx = transition['action']
        
        # Get action details
        action = self.action_space.get_action_by_index(action_idx)
        if not action:
            return 0.0
        
        # Build action dict for RewardCalculatorV2
        action_dict = {
            'type': action.action_type,
            'time_context': action.time_context,
            'difficulty': 'medium',  # Default
            'expected_time': 300  # 5 minutes default
        }
        
        # Build outcome dict
        score = transition.get('score', 0.0)
        time_taken = transition.get('time_gap', 0)
        
        # Determine success based on score improvement
        score_improved = next_state[3] > state[3]  # score_bin comparison
        progress_improved = next_state[2] > state[2]  # progress_bin comparison
        
        outcome_dict = {
            'completed': progress_improved or score_improved,
            'score': score,
            'time': time_taken,
            'success': score_improved or (score >= 0.6)
        }
        
        # Use RewardCalculatorV2
        reward = self.reward_calculator.calculate_reward(
            state=state,
            action=action_dict,
            outcome=outcome_dict,
            previous_state=state  # Pass current state as previous
        )
        
        # Optional: Add LO mastery bonus
        if self.lo_mastery_tracker and 'module_id' in transition:
            try:
                lo_bonus = self._calculate_lo_bonus(
                    transition['module_id'],
                    state,
                    next_state
                )
                reward += lo_bonus
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  LO bonus calculation failed: {e}")
        
        return reward
    
    def _calculate_lo_bonus(
        self,
        module_id: int,
        state: Tuple,
        next_state: Tuple
    ) -> float:
        """
        Calculate LO mastery improvement bonus
        
        Args:
            module_id: Module ID
            state: Current state
            next_state: Next state
            
        Returns:
            Bonus reward
        """
        if not self.lo_mastery_tracker:
            return 0.0
        
        # Get cluster
        cluster_id = state[0]
        
        # Get LO mastery improvement
        # This is simplified - in production, you'd track per-user mastery
        # For now, use score improvement as proxy
        score_improvement = next_state[3] - state[3]  # score_bin delta
        
        if score_improvement > 0:
            # Get midterm weight for module's LOs
            midterm_weight = self.lo_mastery_tracker.get_avg_midterm_weight_for_module(
                module_id
            )
            
            # Cluster bonus
            cluster_bonus = {0: 1.5, 1: 1.2, 2: 1.0, 3: 0.8, 4: 0.8}.get(cluster_id, 1.0)
            
            return score_improvement * midterm_weight * cluster_bonus * 0.1
        
        return 0.0
    
    def _is_terminal(self, state: Tuple) -> bool:
        """
        Check if state is terminal (course completed)
        
        Args:
            state: State tuple
            
        Returns:
            True if terminal
        """
        # Terminal conditions:
        # 1. Progress = 1.0 (completed)
        # 2. Score = 1.0 (perfect)
        # 3. Last module + high engagement
        
        module_idx = state[1]
        progress_bin = state[2]
        score_bin = state[3]
        
        # Simple terminal check
        is_last_module = module_idx >= 5  # Module 5 is last
        is_completed = progress_bin >= 1.0
        
        return is_last_module and is_completed
    
    def get_statistics(self) -> Dict:
        """Get update statistics"""
        stats = self.stats.copy()
        stats['avg_reward'] = (
            stats['total_reward'] / stats['q_updates'] 
            if stats['q_updates'] > 0 else 0.0
        )
        return stats
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            'total_logs_processed': 0,
            'valid_transitions': 0,
            'invalid_transitions': 0,
            'q_updates': 0,
            'total_reward': 0.0,
            'action_distribution': defaultdict(int)
        }


def test_qtable_update_service():
    """Test Q-table update service with sample data"""
    print("=" * 70)
    print("Testing Q-Table Update Service")
    print("=" * 70)
    
    # Paths
    base_path = Path(__file__).parent.parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    course_path = base_path / 'data' / 'course_structure.json'
    
    # Initialize components
    print("\n1. Initializing components...")
    
    # Action space
    action_space = ActionSpace()
    
    # Q-Learning agent
    agent = QLearningAgentV2(
        n_actions=action_space.get_action_count(),
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.1
    )
    
    # Reward calculator
    reward_calc = RewardCalculatorV2(
        cluster_profiles_path=str(cluster_path)
    )
    
    # Log-to-state builder
    builder = LogToStateBuilder(
        cluster_profiles_path=str(cluster_path),
        course_structure_path=str(course_path)
    )
    
    # Update service
    updater = QTableUpdateService(
        agent=agent,
        reward_calculator=reward_calc,
        action_space=action_space,
        log_to_state_builder=builder,
        verbose=True
    )
    
    # Sample logs (simulating learning sequence)
    print("\n2. Creating sample logs...")
    sample_logs = [
        {
            'user_id': 101,
            'cluster_id': 2,
            'module_id': 54,
            'action': 'view_content',
            'timestamp': 1700000000,
            'score': 0.0,
            'progress': 0.2
        },
        {
            'user_id': 101,
            'cluster_id': 2,
            'module_id': 54,
            'action': 'attempt_quiz',
            'timestamp': 1700000300,  # 5 min later
            'score': 0.65,
            'progress': 0.4
        },
        {
            'user_id': 101,
            'cluster_id': 2,
            'module_id': 54,
            'action': 'submit_quiz',
            'timestamp': 1700000600,  # 5 min later
            'score': 0.75,
            'progress': 0.6
        },
        {
            'user_id': 101,
            'cluster_id': 2,
            'module_id': 55,  # Next module
            'action': 'view_content',
            'timestamp': 1700001200,  # 10 min later
            'score': 0.75,
            'progress': 0.7
        }
    ]
    
    print(f"   Created {len(sample_logs)} sample logs")
    
    # Update Q-table
    print("\n3. Updating Q-table from logs...")
    stats = updater.update_from_logs(sample_logs)
    
    # Print results
    print("\n4. Update Statistics:")
    print(f"   Users processed: {stats['users_processed']}")
    print(f"   Transitions: {stats['transitions_processed']}")
    print(f"   Q-updates: {stats['q_updates']}")
    print(f"   Total reward: {stats['total_reward']:.3f}")
    print(f"   Avg reward: {stats['avg_reward']:.3f}")
    
    print("\n   Action distribution:")
    for action_idx, count in stats['action_counts'].items():
        action = action_space.get_action_by_index(action_idx)
        action_name = action.name if action else 'Unknown'
        print(f"     {action_name}: {count}")
    
    # Check Q-table
    print("\n5. Q-Table Status:")
    print(f"   Total states in Q-table: {len(agent.q_table)}")
    print(f"   Total updates: {agent.stats['total_updates']}")
    
    print("\n" + "=" * 70)
    print("✅ Test completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    test_qtable_update_service()
