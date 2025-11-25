#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Path Simulator - Simulate toàn bộ quá trình học
=========================================================
Class để simulate quá trình học với đầy đủ thông tin về state transitions,
action selection, reward calculation, và LO mastery tracking
"""

import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from collections import defaultdict

from core.simulation.student import Student
from core.rl.agent import QLearningAgentV2
from core.rl.action_space import ActionSpace
from core.rl.reward_calculator import RewardCalculatorV2
from core.activity_recommender import ActivityRecommender
from core.lo_mastery_tracker import LOMasteryTracker
from core.simulation.logger import StateTransitionLogger


class LearningPathSimulator:
    """
    Simulate quá trình học với đầy đủ logging và tracking
    
    Features:
    - Simulate state transitions chi tiết
    - Track action selection (exploration vs exploitation)
    - Log reward calculation breakdown
    - Track LO filtering và recommendations
    - Predict midterm scores
    - Export to JSON
    """
    
    def __init__(
        self,
        qtable_path: Optional[str] = None,
        verbose: bool = True,
        save_logs: bool = True
    ):
        """
        Initialize simulator
        
        Args:
            qtable_path: Path to trained Q-table (optional, will create new if None)
            verbose: Print detailed logs
            save_logs: Save logs to JSON
        """
        self.verbose = verbose
        self.save_logs = save_logs
        
        # Initialize components
        self.action_space = ActionSpace()
        self.reward_calc = RewardCalculatorV2(
            cluster_profiles_path='data/cluster_profiles.json',
            po_lo_path='data/Po_Lo.json',
            midterm_weights_path='data/midterm_lo_weights.json'
        )
        self.activity_recommender = ActivityRecommender(
            po_lo_path='data/Po_Lo.json',
            course_structure_path='data/course_structure.json'
        )
        self.lo_tracker = LOMasteryTracker(
            midterm_weights_path='data/midterm_lo_weights.json',
            po_lo_path='data/Po_Lo.json'
        )
        self.logger = StateTransitionLogger(verbose=verbose)
        
        # Initialize Q-Learning agent
        n_actions = self.action_space.get_action_count()
        self.agent = QLearningAgentV2(
            n_actions=n_actions,
            learning_rate=0.1,
            discount_factor=0.95,
            epsilon=0.1,
            epsilon_decay=0.995,
            epsilon_min=0.01
        )
        
        # Load Q-table if provided
        if qtable_path and Path(qtable_path).exists():
            self.agent.load(qtable_path)
            if verbose:
                print(f"✓ Loaded Q-table from {qtable_path}")
                stats = self.agent.get_statistics()
                print(f"  Q-table size: {stats['q_table_size']} states")
        
        # Load LO mappings
        with open('data/Po_Lo.json', 'r', encoding='utf-8') as f:
            po_lo_data = json.load(f)
        
        self.lo_mappings = defaultdict(list)
        for lo in po_lo_data['learning_outcomes']:
            for activity_id in lo.get('activity_ids', []):
                self.lo_mappings[activity_id].append(lo['id'])
        
        if verbose:
            print(f"✓ Initialized LearningPathSimulator")
            print(f"  Actions: {n_actions}")
            print(f"  LO mappings: {len(self.lo_mappings)} activities")
    
    def simulate_student(
        self,
        student_id: int,
        cluster: str,
        n_steps: int = 30,
        use_trained_agent: bool = True
    ) -> Dict[str, Any]:
        """
        Simulate learning path cho một học sinh
        
        Args:
            student_id: Student ID
            cluster: 'weak', 'medium', or 'strong'
            n_steps: Number of learning steps
            use_trained_agent: Use trained Q-table or random
            
        Returns:
            Dict với simulation results
        """
        # Create student
        student = Student(student_id, cluster)
        self.lo_tracker.initialize_student(student_id)
        
        # Initialize tracking
        prev_state = None
        prev_action_type = None
        total_reward = 0.0
        
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Simulating Student {student_id} ({cluster.upper()})")
            print(f"{'='*80}")
        
        # Simulation loop
        for step in range(n_steps):
            if student.is_finished:
                break
            
            # Get current state
            state = student.get_state()
            
            # Select action
            import random
            if use_trained_agent:
                # Store best action to compare
                best_action_idx = self.agent.get_best_action(state)
                
                # Select action (may explore or exploit)
                # Check epsilon to determine if exploration happened
                epsilon_check = random.random()
                action_idx = self.agent.select_action(state)
                
                # Determine if this was exploration
                # If epsilon > random value, it was exploration (unless it happened to pick best)
                is_exploration = (epsilon_check < self.agent.epsilon) and \
                    (self.agent.epsilon > 0) and \
                    (action_idx != best_action_idx)
            else:
                action_idx = self.agent.select_action(state)
                is_exploration = True
            
            action = self.action_space.get_action_by_index(action_idx)
            if action is None:
                # Fallback to first action if index invalid
                action = self.action_space.get_action_by_index(0)
            action_tuple = action.to_tuple()
            
            # Get Q-values
            q_value = self.agent.get_q_value(state, action_idx)
            
            # Get weak LOs for filtering
            weak_los = self.lo_tracker.get_weak_los(student_id, threshold=0.6)
            
            # Get activity recommendation (LO-based filtering)
            recommendation = self.activity_recommender.recommend_activity(
                action=action_tuple,
                module_idx=student.module_idx,
                lo_mastery=self.lo_tracker.get_mastery(student_id),
                previous_activities=getattr(student, 'activity_history', [])
            )
            activity_id = recommendation['activity_id']
            activity_name = recommendation['activity_name']
            
            # Execute action
            result = student.do_action(action_tuple, activity_id, self.lo_mappings)
            outcome = result['outcome']
            old_mastery = result['old_mastery']
            
            # Update LO mastery in tracker
            if activity_id in self.lo_mappings:
                for lo_id in self.lo_mappings[activity_id]:
                    # Get new mastery from student
                    new_mastery = student.lo_mastery.get(lo_id, 0.4)
                    self.lo_tracker.update_mastery(
                        student_id=student_id,
                        lo_id=lo_id,
                        new_mastery=new_mastery,
                        activity_id=activity_id,
                        timestamp=step
                    )
            
            # Calculate reward with breakdown
            reward, reward_breakdown = self.reward_calc.calculate_reward_with_breakdown(
                state=state,
                action={'type': action_tuple[0], 'difficulty': 'medium'},
                outcome=outcome,
                previous_state=prev_state,
                previous_action_type=prev_action_type,
                student_id=student_id,
                activity_id=activity_id
            )
            
            # Get LO deltas
            lo_deltas = {}
            current_mastery = self.lo_tracker.get_mastery(student_id)
            for lo_id in self.lo_mappings.get(activity_id, []):
                old_val = old_mastery.get(lo_id, 0.4)
                new_val = current_mastery.get(lo_id, 0.4)
                lo_deltas[lo_id] = new_val - old_val
            
            # Get next state
            next_state = student.get_state()
            max_next_q = self.agent.get_max_q_value(next_state)
            
            # Predict midterm score
            midterm_prediction = self.lo_tracker.predict_midterm_score(student_id)
            
            # Log transition
            self.logger.log_transition(
                step=step + 1,
                student_id=student_id,
                cluster_id=student.cluster_id,
                state=state,
                action_idx=action_idx,
                action_type=action_tuple[0],
                activity_id=activity_id,
                activity_name=activity_name,
                reward=reward,
                reward_breakdown=reward_breakdown,
                next_state=next_state,
                q_value=q_value,
                max_q_value=max_next_q,
                is_exploration=is_exploration,
                weak_los=weak_los,
                lo_deltas=lo_deltas,
                midterm_prediction=midterm_prediction,
                timestamp=step + 1
            )
            
            # Update Q-table (if training)
            if use_trained_agent:
                self.agent.update(
                    state=state,
                    action=action_idx,
                    reward=reward,
                    next_state=next_state,
                    is_terminal=student.is_finished
                )
            
            # Update tracking
            total_reward += reward
            prev_state = state
            prev_action_type = action_tuple[0]
        
        # Get final statistics
        final_stats = student.get_statistics()
        lo_summary = self.lo_tracker.get_summary(student_id)
        comparison = self.lo_tracker.compare_los(student_id)
        
        result = {
            'student_id': student_id,
            'cluster': cluster,
            'total_steps': step + 1,
            'total_reward': float(total_reward),
            'final_state': {
                'module_idx': final_stats['module_idx'],
                'progress': float(final_stats['progress']),
                'score': float(final_stats['score']),
                'avg_lo_mastery': float(final_stats['avg_lo_mastery'])
            },
            'lo_summary': lo_summary,
            'lo_comparison': comparison,
            'transitions': self.logger.get_transitions()[-n_steps:],  # Last n_steps transitions
            'statistics': self.logger.get_statistics()
        }
        
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Simulation Complete for Student {student_id}")
            print(f"{'='*80}")
            print(f"Total steps: {result['total_steps']}")
            print(f"Total reward: {result['total_reward']:.2f}")
            print(f"Final progress: {result['final_state']['progress']:.2f}")
            print(f"Final score: {result['final_state']['score']:.2f}")
            print(f"Avg LO mastery: {result['final_state']['avg_lo_mastery']:.2f}")
            print(f"Predicted midterm: {lo_summary['midterm_prediction']['predicted_score']:.1f}/20 "
                  f"({lo_summary['midterm_prediction']['predicted_percentage']:.1f}%)")
        
        return result
    
    def simulate_multiple_students(
        self,
        students_config: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate multiple students
        
        Args:
            students_config: List of {student_id, cluster, n_steps}
            output_path: Path to save JSON output
            
        Returns:
            Dict với results for all students
        """
        all_results = []
        
        for config in students_config:
            student_id = config['student_id']
            cluster = config['cluster']
            n_steps = config.get('n_steps', 30)
            
            result = self.simulate_student(
                student_id=student_id,
                cluster=cluster,
                n_steps=n_steps,
                use_trained_agent=True
            )
            
            all_results.append(result)
            
            # Reset logger for next student
            self.logger.reset()
        
        # Aggregate statistics
        total_students = len(all_results)
        avg_reward = sum(r['total_reward'] for r in all_results) / total_students
        avg_midterm = sum(
            r['lo_summary']['midterm_prediction']['predicted_score']
            for r in all_results
        ) / total_students
        
        output = {
            'simulation_metadata': {
                'total_students': int(total_students),
                'students_config': students_config,
                'avg_reward': float(avg_reward),
                'avg_midterm_score': float(avg_midterm)
            },
            'students': all_results
        }
        
        # Save to JSON (convert numpy types to native Python types)
        if output_path and self.save_logs:
            import numpy as np
            def convert_numpy_types(obj):
                """Recursively convert numpy types to native Python types"""
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_numpy_types(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
                elif isinstance(obj, tuple):
                    return tuple(convert_numpy_types(item) for item in obj)
                return obj
            
            output_converted = convert_numpy_types(output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_converted, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"\n✓ Saved simulation results to {output_path}")
        
        return output
    
    def get_action_selection_details(
        self,
        state: Tuple,
        action_idx: int
    ) -> Dict[str, Any]:
        """
        Get detailed information about action selection
        
        Args:
            state: Current state
            action_idx: Selected action index
            
        Returns:
            Dict với action selection details
        """
        action = self.action_space.get_action_by_index(action_idx)
        q_value = self.agent.get_q_value(state, action_idx)
        max_q = self.agent.get_max_q_value(state)
        best_action_idx = self.agent.get_best_action(state)
        
        return {
            'selected_action': {
                'index': action_idx,
                'type': action.to_tuple()[0],
                'name': action.name,
                'q_value': float(q_value)
            },
            'best_action': {
                'index': best_action_idx,
                'q_value': float(max_q)
            },
            'is_best': action_idx == best_action_idx,
            'epsilon': float(self.agent.epsilon),
            'all_q_values': {
                i: float(self.agent.get_q_value(state, i))
                for i in range(self.agent.n_actions)
            }
        }

