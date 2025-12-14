#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Path Simulator - Simulate toàn bộ quá trình học
=========================================================
Class để simulate quá trình học với đầy đủ thông tin về state transitions,
action selection, reward calculation, và LO mastery tracking
"""

import json
import random
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
        save_logs: bool = True,
        sim_params_path: Optional[str] = None,
        use_param_policy: bool = False
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

        # Optional parameterized simulator policy
        self.use_param_policy = use_param_policy
        self.sim_params = self._load_sim_params(sim_params_path)
        self.action_type_to_indices = self._build_action_type_index()

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
            if self.sim_params:
                print(f"  Loaded simulate params from {sim_params_path}")
                available = list(self.sim_params.keys())
                print(f"  Param keys: {available}")

    def _load_sim_params(self, sim_params_path: Optional[str]) -> Dict[str, Any]:
        """Load simulate parameters JSON if provided"""
        if sim_params_path and Path(sim_params_path).exists():
            with open(sim_params_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _build_action_type_index(self) -> Dict[str, List[int]]:
        """Map action_type to list of action indices for quick sampling"""
        mapping: Dict[str, List[int]] = defaultdict(list)
        for action in self.action_space.get_actions():
            mapping[action.action_type].append(action.index)
        return mapping

    def _normalize_distribution(self, probs: Dict[str, float]) -> Dict[str, float]:
        total = sum(probs.values())
        if total <= 0:
            return {}
        return {k: v / total for k, v in probs.items() if v > 0}

    def _sample_action_from_params(self, state: Tuple[int, int, float, float, int, int]) -> Optional[int]:
        """Sample an action index using pre-computed probability tables"""
        if not self.sim_params:
            return None

        learning_phase = state[4]
        engagement = state[5]

        probs = {}
        # Prefer learning phase distribution, then engagement distribution
        phase_key = str(learning_phase)
        engagement_key = str(engagement)
        phase_table = self.sim_params.get('action_probs_by_learning_phase', {})
        engage_table = self.sim_params.get('action_probs_by_engagement', {})

        if phase_key in phase_table:
            probs = self._normalize_distribution(phase_table[phase_key])
        elif engagement_key in engage_table:
            probs = self._normalize_distribution(engage_table[engagement_key])

        if not probs:
            return None

        # Sample action type then map to an action index (prefer current context if available)
        action_types = list(probs.keys())
        weights = list(probs.values())
        action_type = random.choices(action_types, weights=weights, k=1)[0]

        candidates = self.action_type_to_indices.get(action_type, [])
        if not candidates:
            return None

        current_pref = [idx for idx in candidates if self.action_space.get_action_by_index(idx).time_context == 'current']
        pool = current_pref if current_pref else candidates
        return random.choice(pool) if pool else None

    def _generate_students_by_mix(
        self,
        n_students: int,
        cluster_mix: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Create student configs following a cluster ratio"""
        mix = cluster_mix or {'weak': 0.2, 'medium': 0.6, 'strong': 0.2}
        mix = self._normalize_distribution(mix) or {'weak': 0.2, 'medium': 0.6, 'strong': 0.2}
        configs: List[Dict[str, Any]] = []
        cumulative = []
        total = 0.0
        for cluster, weight in mix.items():
            total += weight
            cumulative.append((total, cluster))

        for sid in range(1, n_students + 1):
            r = random.random()
            cluster = next(c for threshold, c in cumulative if r <= threshold)
            configs.append({'student_id': sid, 'cluster': cluster, 'n_steps': 30})
        return configs
    
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
            if self.use_param_policy and self.sim_params:
                action_idx = self._sample_action_from_params(state)
                # Fallback to agent if params missing
                if action_idx is None:
                    action_idx = self.agent.select_action(state)
                    is_exploration = True
                else:
                    is_exploration = False
            else:
                if use_trained_agent:
                    best_action_idx = self.agent.get_best_action(state)
                    epsilon_check = random.random()
                    action_idx = self.agent.select_action(state)
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
            # Use simplified parameters based on student state
            recommendation = self.activity_recommender.recommend_activity(
                action=action_tuple,
                course_id=670,  # Fixed course ID for now
                lesson_id=student.module_idx,  # Use module_idx as lesson_id
                lo_mastery=self.lo_tracker.get_mastery(student_id),
                previous_activities=getattr(student, 'activity_history', []),
                cluster_id=student.cluster_id
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
            midterm_score = lo_summary['midterm_prediction']['predicted_score']
            midterm_score_10 = midterm_score / 2.0
            print(f"Predicted midterm: {midterm_score:.1f}/20 ({midterm_score_10:.1f}/10) - "
                  f"{lo_summary['midterm_prediction']['predicted_percentage']:.1f}%")
        
        return result
    
    def simulate_multiple_students(
        self,
        students_config: Optional[List[Dict[str, Any]]] = None,
        output_path: Optional[str] = None,
        n_students: Optional[int] = None,
        cluster_mix: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Simulate multiple students
        
        Args:
            students_config: List of {student_id, cluster, n_steps}
            output_path: Path to save JSON output
            n_students: If provided, auto-generate configs using cluster_mix when students_config is None
            cluster_mix: Dict ratios for weak/medium/strong, defaults 0.2/0.6/0.2
        
        Returns:
            Dict với results for all students
        """
        all_results = []

        configs = students_config or []
        if not configs and n_students:
            configs = self._generate_students_by_mix(n_students, cluster_mix)
        
        for config in configs:
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
        avg_reward = sum(r['total_reward'] for r in all_results) / total_students if total_students else 0.0
        avg_midterm = sum(
            r['lo_summary']['midterm_prediction']['predicted_score']
            for r in all_results
        ) / total_students if total_students else 0.0
        avg_midterm_10 = avg_midterm / 2.0
        
        output = {
            'simulation_metadata': {
                'total_students': int(total_students),
                'students_config': configs,
                'avg_reward': float(avg_reward),
                'avg_midterm_score': float(avg_midterm),
                'avg_midterm_score_10': float(avg_midterm_10)  # Hệ 10
            },
            'students': all_results
        }
        
        # Save to JSON (convert numpy types to native Python types)
        if output_path and self.save_logs:
            import numpy as np
            import math
            
            def convert_numpy_types(obj):
                """Recursively convert numpy types and tuple keys to native Python types"""
                if isinstance(obj, (np.integer, np.int32, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float32, np.float64)):
                    # Handle NaN and Inf values
                    val = float(obj)
                    if math.isnan(val) or math.isinf(val):
                        return None
                    return val
                elif isinstance(obj, np.bool_):
                    return bool(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    # Convert tuple keys to strings for JSON serialization
                    new_dict = {}
                    for key, value in obj.items():
                        if isinstance(key, tuple):
                            new_key = str(key)
                        else:
                            new_key = key
                        new_dict[new_key] = convert_numpy_types(value)
                    return new_dict
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

