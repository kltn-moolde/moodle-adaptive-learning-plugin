"""
Student Simulator V2
Simulates student learning behavior for Q-Learning training

This module generates synthetic student trajectories with realistic
behavior patterns based on cluster characteristics.
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime, timedelta
import sys
import os
import pickle

# Add parent directory to path for testing
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state_builder_v2 import StateBuilderV2
from core.reward_calculator_v2 import RewardCalculatorV2
from core.student_context import StudentContext


class StudentSimulatorV2:
    """
    Simulate student learning behavior với enhanced features
    
    NEW Features:
    - Learning curve model (logistic/exponential progress)
    - Attempt-level quiz tracking với improvement over time
    - Policy-based action selection từ Q-table
    - Learned parameters từ cluster_profiles.json
    - Realistic reward tuning
    
    Original Features:
    - Cluster-specific behavior patterns
    - Realistic action selection (ε-greedy with cluster bias)
    - Progress-based difficulty adjustment
    - Stuck state simulation
    - Time-based progression
    """
    
    def __init__(
        self,
        course_structure_path: str = "data/course_structure.json",
        cluster_profiles_path: str = "data/cluster_profiles.json",
        qtable_path: Optional[str] = None,
        use_learned_params: bool = True,
        learning_curve_type: str = 'logistic',
        seed: Optional[int] = None
    ):
        """
        Initialize simulator
        
        Args:
            course_structure_path: Path to course structure JSON
            cluster_profiles_path: Path to cluster profiles JSON
            qtable_path: Path to Q-table pickle file (for policy-based selection)
            use_learned_params: Sử dụng params học từ cluster_profiles.json
            learning_curve_type: 'logistic' hoặc 'exponential'
            seed: Random seed for reproducibility
        """
        print("=" * 60)
        print("Initializing StudentSimulatorV2 (Enhanced)...")
        print("=" * 60)
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.learning_curve_type = learning_curve_type
        self.use_learned_params = use_learned_params
        
        # Initialize components
        self.state_builder = StateBuilderV2(
            course_structure_path=course_structure_path,
            cluster_profiles_path=cluster_profiles_path
        )
        
        self.reward_calculator = RewardCalculatorV2(
            cluster_profiles_path=cluster_profiles_path
        )
        
        # Load course structure
        with open(course_structure_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        # Extract modules from nested structure
        self.modules = []
        if 'contents' in course_data:
            for section in course_data['contents']:
                if 'modules' in section:
                    self.modules.extend(section['modules'])
        elif 'modules' in course_data:
            self.modules = course_data['modules']
        
        self.n_modules = len(self.modules)
        
        # Load cluster profiles data
        with open(cluster_profiles_path, 'r', encoding='utf-8') as f:
            self.cluster_profiles = json.load(f)
        
        # Load Q-table if provided (for policy-based action selection)
        self.qtable = None
        if qtable_path and os.path.exists(qtable_path):
            print(f"\n✓ Loading Q-table from {qtable_path}...")
            with open(qtable_path, 'rb') as f:
                self.qtable = pickle.load(f)
            print(f"  Q-table size: {len(self.qtable)} states")
        
        # Cluster-specific parameters
        if use_learned_params:
            self.cluster_params = self._learn_cluster_params_from_profiles()
        else:
            self.cluster_params = self._initialize_cluster_params()
        
        # Learning curve parameters
        self.learning_curve_params = self._initialize_learning_curves()
        
        print(f"\n✓ Loaded {self.n_modules} modules")
        print(f"✓ Initialized {len(self.cluster_params)} cluster behavior profiles")
        print(f"✓ Learning curve type: {learning_curve_type}")
        print(f"✓ Using learned params: {use_learned_params}")
        print("=" * 60)
    
    def _initialize_cluster_params(self) -> Dict[int, Dict]:
        """
        Initialize cluster-specific behavior parameters
        
        Returns:
            Dictionary mapping cluster_id -> parameters
        """
        # Get cluster levels
        cluster_levels = {}
        for cluster_id in [0, 1, 2, 4, 5]:  # Original cluster IDs (excluding 3)
            mapped_id = self.state_builder.map_cluster_id(cluster_id)
            level = self.reward_calculator.get_cluster_level(mapped_id)
            cluster_levels[cluster_id] = level
        
        # Define parameters based on cluster level
        params = {}
        
        for cluster_id, level in cluster_levels.items():
            if level == 'weak':
                # Weak learners: slow, need more attempts, get stuck often
                params[cluster_id] = {
                    'level': 'weak',
                    'completion_rate': 0.8,  # ✅ FIXED: 80% complete modules (increased from 0.6)
                    'success_rate': 0.5,      # 50% success on first try
                    'stuck_probability': 0.3,  # 30% chance to get stuck
                    'retry_attempts': (2, 5),  # 2-5 retries when stuck
                    'progress_speed': 0.30,    # ✅ FIXED: Increased from 0.15 to 0.30
                    'score_range': (0.3, 0.7), # Lower scores
                    'action_exploration': 0.4,  # 40% random actions
                    'preferred_actions': ['watch_video', 'read_resource'],  # Prefer passive learning
                }
            elif level == 'medium':
                # Medium learners: moderate, balanced
                params[cluster_id] = {
                    'level': 'medium',
                    'completion_rate': 0.85,  # ✅ FIXED: 85% complete modules (increased from 0.75)
                    'success_rate': 0.7,
                    'stuck_probability': 0.15,
                    'retry_attempts': (1, 3),
                    'progress_speed': 0.40,    # ✅ FIXED: Increased from 0.25 to 0.40
                    'score_range': (0.5, 0.85),
                    'action_exploration': 0.25,
                    'preferred_actions': ['do_quiz', 'read_resource', 'watch_video'],
                }
            else:  # strong
                # Strong learners: fast, high success, rarely stuck
                params[cluster_id] = {
                    'level': 'strong',
                    'completion_rate': 0.95,  # ✅ FIXED: 95% complete modules (increased from 0.9)
                    'success_rate': 0.85,
                    'stuck_probability': 0.05,
                    'retry_attempts': (1, 2),
                    'progress_speed': 0.50,    # ✅ FIXED: Increased from 0.35 to 0.50
                    'score_range': (0.7, 1.0),
                    'action_exploration': 0.15,
                    'preferred_actions': ['do_quiz', 'do_assignment', 'review_quiz'],  # Prefer active learning
                }
        
        return params
    
    def _learn_cluster_params_from_profiles(self) -> Dict[int, Dict]:
        """
        Học parameters từ cluster_profiles.json
        """
        print("\n📊 Learning parameters from cluster profiles...")
        
        params = {}
        cluster_stats = self.cluster_profiles.get('cluster_stats', {})
        
        for cluster_id_str in ['0', '1', '2', '4', '5']:  # Skip cluster 3
            cluster_id = int(cluster_id_str)
            
            if cluster_id_str not in cluster_stats:
                continue
            
            cluster_data = cluster_stats[cluster_id_str]
            feature_means = cluster_data.get('feature_means', {})
            
            # Extract key metrics
            mean_grade = feature_means.get('mean_module_grade', 0.65)
            total_events = feature_means.get('total_events', 100)
            
            # Quiz-related events
            quiz_started = feature_means.get('\\mod_quiz\\event\\attempt_started', 0)
            quiz_submitted = feature_means.get('\\mod_quiz\\event\\attempt_submitted', 0)
            quiz_reviewed = feature_means.get('\\mod_quiz\\event\\attempt_reviewed', 0)
            
            # Assignment events
            assign_submitted = feature_means.get('\\mod_assign\\event\\assessable_submitted', 0)
            assign_viewed = feature_means.get('\\mod_assign\\event\\course_module_viewed', 0)
            
            # Completion events
            completion_updated = feature_means.get('\\core\\event\\course_module_completion_updated', 0)
            
            # Compute derived parameters
            # Success rate: based on mean_grade
            success_rate = np.clip(mean_grade / 100.0 if mean_grade > 1 else mean_grade, 0.3, 0.95)
            
            # Stuck probability: based on review/submitted ratio
            if quiz_submitted > 0:
                review_ratio = quiz_reviewed / quiz_submitted
                stuck_probability = np.clip(review_ratio * 0.5, 0.05, 0.4)
            else:
                stuck_probability = 0.15
            
            # Progress speed: based on total events (inverse)
            # More events = slower progress (more struggling)
            progress_speed = np.clip(0.5 / (1 + total_events / 100), 0.1, 0.4)
            
            # Completion rate: based on completion_updated events
            completion_rate = np.clip(0.5 + completion_updated / 2, 0.5, 0.95)
            
            # Action exploration: based on event diversity (entropy)
            # Calculate Shannon entropy of event distribution
            event_counts = []
            for key, value in feature_means.items():
                if '\\' in key and 'event' in key:
                    event_counts.append(value)
            
            if event_counts:
                event_probs = np.array(event_counts) / (np.sum(event_counts) + 1e-10)
                event_probs = event_probs[event_probs > 0]
                entropy = -np.sum(event_probs * np.log2(event_probs + 1e-10))
                max_entropy = np.log2(len(event_probs))
                action_exploration = np.clip(entropy / max_entropy, 0.1, 0.5)
            else:
                action_exploration = 0.25
            
            # Infer level
            if success_rate > 0.75 and stuck_probability < 0.15:
                level = 'strong'
            elif success_rate > 0.6 and stuck_probability < 0.25:
                level = 'medium'
            else:
                level = 'weak'
            
            # Determine preferred actions from event frequencies
            action_scores = {
                'watch_video': feature_means.get('\\mod_page\\event\\course_module_viewed', 0),
                'do_quiz': quiz_started,
                'read_resource': feature_means.get('\\mod_resource\\event\\course_module_viewed', 0),
                'do_assignment': assign_submitted,
                'review_quiz': quiz_reviewed,
                'mod_forum': feature_means.get('\\mod_forum\\event\\course_module_viewed', 0)
            }
            
            preferred_actions = sorted(action_scores.keys(), key=lambda k: action_scores[k], reverse=True)[:3]
            
            params[cluster_id] = {
                'level': level,
                'completion_rate': float(completion_rate),
                'success_rate': float(success_rate),
                'stuck_probability': float(stuck_probability),
                'retry_attempts': (1, 3) if level == 'strong' else (2, 5) if level == 'weak' else (1, 4),
                'progress_speed': float(progress_speed),
                'score_range': (
                    float(max(0.3, mean_grade - 0.15)),
                    float(min(1.0, mean_grade + 0.15))
                ),
                'action_exploration': float(action_exploration),
                'preferred_actions': preferred_actions
            }
            
            print(f"  Cluster {cluster_id} ({level}): "
                  f"success={success_rate:.2f}, stuck={stuck_probability:.2f}, "
                  f"progress={progress_speed:.3f}")
        
        return params
    
    def _initialize_learning_curves(self) -> Dict[str, Dict]:
        """
        Initialize learning curve parameters for each cluster level
        """
        if self.learning_curve_type == 'logistic':
            return {
                'weak': {
                    'L': 1.0,        # Maximum value (asymptote)
                    'k': 0.3,        # Steepness (slower learning)
                    'x0': 8.0        # Midpoint (takes more attempts to reach 50%)
                },
                'medium': {
                    'L': 1.0,
                    'k': 0.5,        # Moderate learning
                    'x0': 5.0        # Moderate attempts to 50%
                },
                'strong': {
                    'L': 1.0,
                    'k': 0.8,        # Fast learning
                    'x0': 3.0        # Few attempts to 50%
                }
            }
        else:  # exponential
            return {
                'weak': {
                    'a': 0.85,       # Initial learning rate (lower)
                    'b': 0.12        # Decay rate (slower)
                },
                'medium': {
                    'a': 0.92,
                    'b': 0.15
                },
                'strong': {
                    'a': 0.97,
                    'b': 0.20
                }
            }
    
    def _compute_learning_curve_progress(
        self,
        n_attempts: int,
        cluster_level: str,
        current_progress: float = 0.0
    ) -> float:
        """
        Compute expected progress based on learning curve
        
        Args:
            n_attempts: Number of attempts for this module
            cluster_level: Cluster level
            current_progress: Current progress
            
        Returns:
            Expected progress [0, 1]
        """
        curve_params = self.learning_curve_params.get(cluster_level, self.learning_curve_params['medium'])
        
        # ✅ FIX: Compute INCREMENT instead of absolute value
        if n_attempts == 1:
            # First attempt: no learning curve bonus yet
            return current_progress
        
        if self.learning_curve_type == 'logistic':
            # Logistic: L / (1 + exp(-k * (x - x0)))
            L = curve_params['L']
            k = curve_params['k']
            x0 = curve_params['x0']
            curr_value = L / (1 + np.exp(-k * (n_attempts - x0)))
            prev_value = L / (1 + np.exp(-k * ((n_attempts - 1) - x0)))
        else:
            # Exponential: a * (1 - exp(-b * x))
            a = curve_params['a']
            b = curve_params['b']
            curr_value = a * (1 - np.exp(-b * n_attempts))
            prev_value = a * (1 - np.exp(-b * (n_attempts - 1)))
        
        # Compute increment and add to current progress
        increment = (curr_value - prev_value) * 0.15  # 15% of curve growth as bonus
        return current_progress + increment
    
    def _compute_score_with_improvement(
        self,
        n_attempts: int,
        cluster_level: str,
        previous_score: Optional[float],
        base_score_range: Tuple[float, float]
    ) -> float:
        """
        Compute score with improvement over attempts
        
        Args:
            n_attempts: Number of attempts
            cluster_level: Cluster level
            previous_score: Previous score (None if first attempt)
            base_score_range: (min, max) score range
            
        Returns:
            New score
        """
        if previous_score is None:
            # First attempt: sample from lower part of range
            min_score, max_score = base_score_range
            return random.uniform(min_score, (min_score + max_score) / 2)
        
        # Subsequent attempts: improve based on learning curve
        curve_params = self.learning_curve_params.get(cluster_level, self.learning_curve_params['medium'])
        
        if self.learning_curve_type == 'logistic':
            L = curve_params['L']
            k = curve_params['k']
            x0 = curve_params['x0']
            mastery = L / (1 + np.exp(-k * (n_attempts - x0)))
        else:
            a = curve_params['a']
            b = curve_params['b']
            mastery = a * (1 - np.exp(-b * n_attempts))
        
        # Improvement potential
        max_score = base_score_range[1]
        learning_potential = max_score - previous_score
        
        # New score
        improvement = learning_potential * mastery * random.uniform(0.3, 0.7)
        new_score = previous_score + improvement
        
        # Add noise
        noise = random.uniform(-0.05, 0.05)
        new_score += noise
        
        # Clamp
        new_score = np.clip(new_score, base_score_range[0], base_score_range[1])
        
        return new_score
    
    def simulate_trajectory(
        self,
        student_id: int,
        cluster_id: int,
        max_steps: int = 100,
        start_time: Optional[datetime] = None,
        verbose: bool = False
    ) -> List[Dict]:
        """
        Simulate a single student's learning trajectory
        
        Args:
            student_id: Student ID
            cluster_id: Cluster ID (0-5, original IDs)
            max_steps: Maximum number of actions
            start_time: Starting timestamp
            verbose: Print simulation progress
            
        Returns:
            List of transition dicts
        """
        if verbose:
            print(f"\nSimulating student {student_id} (cluster {cluster_id})...")
        
        # Get cluster parameters
        params = self.cluster_params[cluster_id]
        
        # Initialize student context
        context = StudentContext(student_id=student_id, cluster_id=cluster_id)
        
        # Initialize trajectory
        trajectory = []
        current_time = start_time or datetime.now()
        
        # Start with first module
        current_module_idx = 0
        module_progress = 0.0
        
        # Attempt tracking per module: {module_id: {'attempts': n, 'scores': [...], 'last_score': x}}
        module_attempts = {}
        
        for step in range(max_steps):
            # Get current module
            if current_module_idx >= self.n_modules:
                break  # Completed all modules
            
            current_module = self.modules[current_module_idx]
            module_id = current_module['id']
            
            # Track attempts for this module
            if module_id not in module_attempts:
                module_attempts[module_id] = {'attempts': 0, 'scores': [], 'last_score': None}
            
            module_attempts[module_id]['attempts'] += 1
            n_attempts = module_attempts[module_id]['attempts']
            
            # Get current state for policy-based action selection
            state_dict = context.get_state_dict()
            current_state = self.state_builder.build_state(
                cluster_id=state_dict['cluster_id'],
                current_module_id=state_dict['current_module'],
                module_progress=state_dict['progress'],
                avg_score=state_dict['avg_score'],
                recent_action_type=state_dict['recent_action'],
                is_stuck=state_dict['is_stuck']
            )
            
            # Select action (policy-based or heuristic)
            action_type = self._select_action_with_policy(
                current_state=current_state,
                params=params,
                module_progress=module_progress,
                module_id=module_id
            )
            
            # Simulate action outcome with learning curve
            outcome = self._simulate_action_outcome_with_curve(
                action_type=action_type,
                module_progress=module_progress,
                n_attempts=n_attempts,
                params=params,
                context=context,
                module_attempts=module_attempts[module_id]
            )
            
            # Update progress with learning curve
            old_progress = module_progress
            
            # Expected progress from learning curve
            expected_progress = self._compute_learning_curve_progress(
                n_attempts=n_attempts,
                cluster_level=params['level'],
                current_progress=module_progress
            )
            
            # Actual progress includes action outcome
            module_progress = expected_progress + outcome['progress_delta']
            module_progress = min(1.0, module_progress)
            
            # Update context with simulated log entry
            log_entry = {
                'userid': student_id,
                'timecreated': current_time,
                'contextinstanceid': module_id,
                'eventname': self._action_to_eventname(action_type),
                'component': self._action_to_component(action_type),
                'action': 'viewed'
            }
            context.update_from_log_entry(log_entry)
            
            # Update score if applicable
            if outcome['score'] is not None:
                grade_entry = {
                    'userid': student_id,
                    'finalgrade': outcome['score'] * 100,  # Convert to 0-100 scale
                    'contextinstanceid': module_id
                }
                context.update_from_grade_entry(grade_entry)
            
            # Get current state
            state_dict = context.get_state_dict()
            
            # ✅ CRITICAL FIX: Safe module-specific avg score calculation
            module_scores = module_attempts[module_id]['scores']
            
            if module_scores:
                # Use module-specific average
                module_avg_score = sum(module_scores) / len(module_scores)
            elif context.scores:
                # Fallback 1: Use global average if available
                module_avg_score = context.avg_score
            else:
                # Fallback 2: Use cluster-based default
                cluster_level = params['level']
                default_scores = {'weak': 0.5, 'medium': 0.65, 'strong': 0.75}
                module_avg_score = default_scores.get(cluster_level, 0.6)
            
            # Ensure score is valid
            module_avg_score = np.clip(module_avg_score, 0.0, 1.0)
            
            current_state = self.state_builder.build_state(
                cluster_id=state_dict['cluster_id'],
                current_module_id=state_dict['current_module'],
                module_progress=module_progress,  # ✅ CRITICAL FIX: Use simulated progress, not context's event-based progress
                avg_score=module_avg_score,       # ✅ CRITICAL FIX: Safe module-specific average with fallbacks
                recent_action_type=state_dict['recent_action'],
                is_stuck=state_dict['is_stuck']
            )
            
            # Calculate reward
            mapped_cluster = self.state_builder.map_cluster_id(cluster_id)
            reward = self.reward_calculator.calculate_reward_simple(
                cluster_id=mapped_cluster,
                completed=outcome['completed'],
                score=outcome['score'] if outcome['score'] is not None else state_dict['avg_score'],
                previous_score=trajectory[-1]['avg_score'] if trajectory else 0.5,
                is_stuck=state_dict['is_stuck'],
                difficulty='medium'
            )
            
            # Create transition
            transition = {
                'state': current_state,
                'action': module_id,
                'action_type': action_type,
                'reward': reward,
                'next_state': None,  # Will be filled in next iteration
                'timestamp': current_time,
                'module_id': module_id,
                'module_progress': module_progress,
                'avg_score': state_dict['avg_score'],
                'is_stuck': state_dict['is_stuck'],
                'is_terminal': False,
                'completed': outcome['completed']
            }
            
            # Update next_state of previous transition
            if trajectory:
                trajectory[-1]['next_state'] = current_state
            
            trajectory.append(transition)
            
            # Check if module completed
            if module_progress >= 1.0:
                # Decide whether to complete module
                if random.random() < params['completion_rate']:
                    if verbose:
                        print(f"  Step {step}: Completed module {current_module_idx} ({module_id})")
                    current_module_idx += 1
                    module_progress = 0.0
                    
                    # ✅ FIX: Update context with new module
                    if current_module_idx < self.n_modules:
                        new_module = self.modules[current_module_idx]
                        context.current_module = new_module['id']
                else:
                    # Give up on this module
                    if verbose:
                        print(f"  Step {step}: Gave up on module {current_module_idx} ({module_id})")
                    current_module_idx += 1
                    module_progress = 0.0
                    
                    # ✅ FIX: Update context with new module
                    if current_module_idx < self.n_modules:
                        new_module = self.modules[current_module_idx]
                        context.current_module = new_module['id']
            
            # Update time (random interval between 1-30 minutes)
            time_delta = random.randint(1, 30)
            current_time += timedelta(minutes=time_delta)
        
        # Mark last transition as terminal
        if trajectory:
            trajectory[-1]['is_terminal'] = True
            # Last next_state is same as current state
            trajectory[-1]['next_state'] = trajectory[-1]['state']
        
        if verbose:
            print(f"  ✓ Generated {len(trajectory)} transitions")
            print(f"  ✓ Completed {current_module_idx}/{self.n_modules} modules")
        
        return trajectory
    
    def _select_action(self, params: Dict, module_progress: float) -> str:
        """
        Select action based on cluster parameters and current progress
        
        Args:
            params: Cluster parameters
            module_progress: Current module progress [0-1]
            
        Returns:
            Action type string
        """
        # ε-greedy with cluster-specific exploration rate
        if random.random() < params['action_exploration']:
            # Random action
            return random.choice(['watch_video', 'do_quiz', 'read_resource', 
                                'review_quiz', 'do_assignment', 'mod_forum'])
        else:
            # Preferred action based on progress
            if module_progress < 0.3:
                # Early: prefer learning actions
                preferred = [a for a in params['preferred_actions'] 
                           if a in ['watch_video', 'read_resource']]
                if not preferred:
                    preferred = ['watch_video', 'read_resource']
            elif module_progress < 0.7:
                # Middle: prefer practice actions
                preferred = [a for a in params['preferred_actions'] 
                           if a in ['do_quiz', 'do_assignment']]
                if not preferred:
                    preferred = ['do_quiz']
            else:
                # Late: prefer assessment actions
                preferred = [a for a in params['preferred_actions'] 
                           if a in ['do_quiz', 'review_quiz', 'do_assignment']]
                if not preferred:
                    preferred = ['do_quiz', 'do_assignment']
            
            return random.choice(preferred)
    
    def _simulate_action_outcome(
        self,
        action_type: str,
        module_progress: float,
        params: Dict,
        context: StudentContext
    ) -> Dict:
        """
        Simulate outcome of an action
        
        Args:
            action_type: Type of action
            module_progress: Current progress
            params: Cluster parameters
            context: Student context
            
        Returns:
            Outcome dict with progress_delta, score, completed, success
        """
        outcome = {
            'progress_delta': 0.0,
            'score': None,
            'completed': False,
            'success': True
        }
        
        # Base progress
        base_progress = params['progress_speed']
        
        # Action-specific behavior
        if action_type in ['watch_video', 'read_resource']:
            # Passive learning: steady progress, no score
            outcome['progress_delta'] = base_progress * random.uniform(0.8, 1.2)
            outcome['success'] = True
            
        elif action_type in ['do_quiz', 'do_assignment']:
            # Active learning: progress + score
            success = random.random() < params['success_rate']
            
            if success:
                outcome['progress_delta'] = base_progress * random.uniform(1.0, 1.5)
                outcome['score'] = random.uniform(*params['score_range'])
                outcome['success'] = True
            else:
                # Failed attempt
                outcome['progress_delta'] = base_progress * 0.5
                outcome['score'] = random.uniform(0.0, params['score_range'][0])
                outcome['success'] = False
                
                # Check if stuck
                if random.random() < params['stuck_probability']:
                    outcome['progress_delta'] *= 0.5  # Very slow progress when stuck
        
        elif action_type == 'review_quiz':
            # Review: small progress, possible score improvement
            outcome['progress_delta'] = base_progress * 0.7
            if context.scores:
                # Improve previous score
                prev_score = context.scores[-1]
                improvement = random.uniform(0.05, 0.15)
                outcome['score'] = min(1.0, prev_score + improvement)
            else:
                outcome['score'] = random.uniform(*params['score_range'])
        
        elif action_type == 'mod_forum':
            # Forum interaction: minimal progress
            outcome['progress_delta'] = base_progress * 0.3
        
        # Check if completed
        if module_progress + outcome['progress_delta'] >= 1.0:
            outcome['completed'] = True
        
        return outcome
    
    def _select_action_with_policy(
        self,
        current_state: Tuple,
        params: Dict,
        module_progress: float,
        module_id: int
    ) -> str:
        """
        Select action using Q-table policy (if available) or heuristic
        
        Args:
            current_state: Current state tuple
            params: Cluster parameters
            module_progress: Current progress
            module_id: Current module ID
            
        Returns:
            Action type string
        """
        # If Q-table available, use it with ε-greedy
        if self.qtable is not None:
            epsilon = params['action_exploration']
            
            if random.random() < epsilon:
                # Explore: random action
                return self._select_action(params, module_progress)
            else:
                # Exploit: use Q-table
                if current_state in self.qtable:
                    q_values = self.qtable[current_state]
                    
                    # Get best action (module_id with highest Q-value)
                    best_action_id = max(q_values.keys(), key=lambda a: q_values[a])
                    
                    # Map action ID to action type
                    # If best_action_id matches current module, do active learning
                    if best_action_id == module_id:
                        # On-module: do quiz or assignment
                        return random.choice(['do_quiz', 'do_assignment'])
                    else:
                        # Off-module: maybe review or learn
                        return random.choice(['watch_video', 'read_resource', 'review_quiz'])
                else:
                    # State not in Q-table, use heuristic
                    return self._select_action(params, module_progress)
        else:
            # No Q-table, use heuristic
            return self._select_action(params, module_progress)
    
    def _simulate_action_outcome_with_curve(
        self,
        action_type: str,
        module_progress: float,
        n_attempts: int,
        params: Dict,
        context: StudentContext,
        module_attempts: Dict
    ) -> Dict:
        """
        Simulate outcome with learning curve and attempt tracking
        
        Args:
            action_type: Type of action
            module_progress: Current progress
            n_attempts: Number of attempts for this module
            params: Cluster parameters
            context: Student context
            module_attempts: Attempt tracking dict for this module
            
        Returns:
            Outcome dict
        """
        outcome = {
            'progress_delta': 0.0,
            'score': None,
            'completed': False,
            'success': True
        }
        
        # Base progress (will be adjusted by learning curve in main loop)
        base_progress = params['progress_speed'] * 0.8  # ✅ FIXED: Increased from 0.3 to 0.8 for better coverage
        
        # Action-specific behavior
        if action_type in ['watch_video', 'read_resource']:
            # Passive learning: steady progress, no score
            outcome['progress_delta'] = base_progress * random.uniform(0.8, 1.2)
            outcome['success'] = True
            
        elif action_type in ['do_quiz', 'do_assignment']:
            # Active learning with score improvement over attempts
            success = random.random() < params['success_rate']
            
            if success:
                outcome['progress_delta'] = base_progress * random.uniform(1.0, 1.5)
                
                # ✅ FIXED: Wider score ranges based on cluster level
                cluster_level = params['level']
                if cluster_level == 'weak':
                    base_range = (0.3, 0.7)
                elif cluster_level == 'medium':
                    base_range = (0.5, 0.85)
                else:  # strong
                    base_range = (0.7, 0.95)
                
                # Score improves with attempts
                previous_score = module_attempts['last_score']
                new_score = self._compute_score_with_improvement(
                    n_attempts=n_attempts,
                    cluster_level=cluster_level,
                    previous_score=previous_score,
                    base_score_range=base_range
                )
                
                # ✅ FIXED: Add random variation (-0.1 to +0.1)
                variation = random.uniform(-0.1, 0.1)
                new_score = max(0.0, min(1.0, new_score + variation))
                
                outcome['score'] = new_score
                module_attempts['last_score'] = new_score
                module_attempts['scores'].append(new_score)
                outcome['success'] = True
            else:
                # Failed attempt
                outcome['progress_delta'] = base_progress * 0.3
                
                # ✅ FIXED: Lower failure scores (0.1-0.4 instead of 0.2-params['score_range'][0])
                failed_score = random.uniform(0.1, 0.4)
                outcome['score'] = failed_score
                module_attempts['scores'].append(failed_score)
                outcome['success'] = False
                
                # Check if stuck
                if random.random() < params['stuck_probability']:
                    outcome['progress_delta'] *= 0.3
        
        elif action_type == 'review_quiz':
            # Review: small progress, score improvement
            outcome['progress_delta'] = base_progress * 0.5
            
            if module_attempts['scores']:
                # Improve on last score
                last_score = module_attempts['scores'][-1]
                improvement = random.uniform(0.05, 0.20)  # ✅ FIXED: Increased from 0.15 to 0.20
                new_score = min(1.0, last_score + improvement)
                
                # ✅ FIXED: Add random variation
                variation = random.uniform(-0.05, 0.05)
                new_score = max(0.0, min(1.0, new_score + variation))
                
                outcome['score'] = new_score
                module_attempts['last_score'] = new_score
                module_attempts['scores'].append(new_score)
            else:
                # No previous score, start fresh with wider range
                cluster_level = params['level']
                if cluster_level == 'weak':
                    base_range = (0.3, 0.7)
                elif cluster_level == 'medium':
                    base_range = (0.5, 0.85)
                else:  # strong
                    base_range = (0.7, 0.95)
                
                new_score = random.uniform(base_range[0], base_range[1])
                # ✅ FIXED: Add variation
                variation = random.uniform(-0.1, 0.1)
                new_score = max(0.0, min(1.0, new_score + variation))
                
                outcome['score'] = new_score
                module_attempts['last_score'] = new_score
                module_attempts['scores'].append(new_score)
        
        elif action_type == 'mod_forum':
            # Forum: minimal progress
            outcome['progress_delta'] = base_progress * 0.2
        
        # Check if completed
        if module_progress + outcome['progress_delta'] >= 1.0:
            outcome['completed'] = True
        
        return outcome
    
    def _action_to_eventname(self, action_type: str) -> str:
        """Map action type to Moodle eventname"""
        mapping = {
            'watch_video': '\\mod_page\\event\\course_module_viewed',
            'do_quiz': '\\mod_quiz\\event\\attempt_started',
            'read_resource': '\\mod_resource\\event\\course_module_viewed',
            'review_quiz': '\\mod_quiz\\event\\attempt_reviewed',
            'do_assignment': '\\mod_assign\\event\\assessable_submitted',
            'mod_forum': '\\mod_forum\\event\\discussion_viewed'
        }
        return mapping.get(action_type, '\\core\\event\\course_module_viewed')
    
    def _action_to_component(self, action_type: str) -> str:
        """Map action type to Moodle component"""
        mapping = {
            'watch_video': 'mod_page',
            'do_quiz': 'mod_quiz',
            'read_resource': 'mod_resource',
            'review_quiz': 'mod_quiz',
            'do_assignment': 'mod_assign',
            'mod_forum': 'mod_forum'
        }
        return mapping.get(action_type, 'core')
    
    def simulate_batch(
        self,
        n_students_per_cluster: int = 10,
        max_steps_per_student: int = 100,
        start_date: Optional[datetime] = None,
        verbose: bool = True
    ) -> Dict[int, List[Dict]]:
        """
        Simulate multiple students across all clusters
        
        Args:
            n_students_per_cluster: Number of students to simulate per cluster
            max_steps_per_student: Maximum steps per student
            start_date: Starting date for simulations
            verbose: Print progress
            
        Returns:
            Dictionary mapping student_id -> trajectory
        """
        if verbose:
            print("\n" + "=" * 60)
            print("Batch Simulation")
            print("=" * 60)
        
        trajectories = {}
        student_id = 1000  # Start from 1000
        start_date = start_date or datetime.now()
        
        # Simulate for each cluster
        for cluster_id in sorted(self.cluster_params.keys()):
            params = self.cluster_params[cluster_id]
            
            if verbose:
                print(f"\nCluster {cluster_id} ({params['level']}):")
                print(f"  Simulating {n_students_per_cluster} students...")
            
            for i in range(n_students_per_cluster):
                # Vary start time for each student
                student_start = start_date + timedelta(days=random.randint(0, 30))
                
                # Simulate trajectory
                trajectory = self.simulate_trajectory(
                    student_id=student_id,
                    cluster_id=cluster_id,
                    max_steps=max_steps_per_student,
                    start_time=student_start,
                    verbose=False
                )
                
                if trajectory:
                    trajectories[student_id] = trajectory
                
                student_id += 1
            
            if verbose:
                cluster_trajectories = [t for sid, t in trajectories.items() 
                                      if t and t[0]['state'][0] == self.state_builder.map_cluster_id(cluster_id)]
                n_traj = len(cluster_trajectories)
                avg_len = np.mean([len(t) for t in cluster_trajectories]) if cluster_trajectories else 0
                print(f"  ✓ Generated {n_traj} trajectories")
                print(f"  ✓ Avg length: {avg_len:.1f} transitions")
        
        if verbose:
            print("\n" + "=" * 60)
            print(f"✓ Total: {len(trajectories)} trajectories generated")
            print("=" * 60)
        
        return trajectories
    
    def save_trajectories(self, trajectories: Dict[int, List[Dict]], output_path: str):
        """Save trajectories to JSON file"""
        print(f"\nSaving trajectories to: {output_path}")
        
        # Convert to serializable format
        serializable = {}
        for student_id, trajectory in trajectories.items():
            serializable[str(student_id)] = [
                {
                    'state': list(t['state']),
                    'action': int(t['action']),
                    'action_type': t['action_type'],
                    'reward': float(t['reward']),
                    'next_state': list(t['next_state']),
                    'timestamp': t['timestamp'].isoformat(),
                    'module_id': int(t['module_id']),
                    'module_progress': float(t['module_progress']),
                    'avg_score': float(t['avg_score']),
                    'is_stuck': bool(t['is_stuck']),
                    'is_terminal': bool(t['is_terminal']),
                    'completed': bool(t['completed'])
                }
                for t in trajectory
            ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(trajectories)} trajectories")


def test_simulator():
    """Test StudentSimulatorV2 Enhanced"""
    print("\n" + "=" * 60)
    print("Testing StudentSimulatorV2 (Enhanced)")
    print("=" * 60)
    
    # Initialize simulator with learned parameters
    simulator = StudentSimulatorV2(
        course_structure_path="data/course_structure.json",
        cluster_profiles_path="data/cluster_profiles.json",
        use_learned_params=True,
        learning_curve_type='logistic',
        seed=42
    )
    
    print("\n📋 Learned Cluster Parameters:")
    for cluster_id, params in simulator.cluster_params.items():
        print(f"  Cluster {cluster_id} ({params['level']}):")
        print(f"    Success rate: {params['success_rate']:.2f}")
        print(f"    Progress speed: {params['progress_speed']:.3f}")
        print(f"    Stuck probability: {params['stuck_probability']:.2f}")
        print(f"    Preferred actions: {params['preferred_actions']}")
    
    # Test single student simulation
    print("\n1. Testing single student simulation...")
    trajectory = simulator.simulate_trajectory(
        student_id=999,
        cluster_id=0,  # Weak learner
        max_steps=50,
        verbose=True
    )
    
    print(f"\n  Sample trajectory:")
    print(f"    Length: {len(trajectory)} transitions")
    if trajectory:
        t = trajectory[0]
        print(f"    First transition:")
        print(f"      State: {t['state']}")
        print(f"      Action: {t['action']} ({t['action_type']})")
        print(f"      Reward: {t['reward']:.2f}")
        print(f"      Progress: {t['module_progress']:.2f}")
        print(f"      Score: {t['avg_score']:.2f}")
    
    # Test batch simulation
    print("\n2. Testing batch simulation...")
    trajectories = simulator.simulate_batch(
        n_students_per_cluster=3,  # 3 students per cluster
        max_steps_per_student=50,
        verbose=True
    )
    
    # Statistics
    print("\n3. Trajectory statistics:")
    total_transitions = sum(len(t) for t in trajectories.values())
    avg_length = total_transitions / len(trajectories) if trajectories else 0
    
    all_rewards = [t['reward'] for traj in trajectories.values() for t in traj]
    avg_reward = np.mean(all_rewards)
    
    print(f"  Total students: {len(trajectories)}")
    print(f"  Total transitions: {total_transitions}")
    print(f"  Avg trajectory length: {avg_length:.1f}")
    print(f"  Avg reward: {avg_reward:.2f}")
    
    # Action distribution
    action_counts = {}
    for traj in trajectories.values():
        for t in traj:
            action_type = t['action_type']
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
    
    print(f"\n  Action distribution:")
    for action_type, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {action_type}: {count}")
    
    # Save test trajectories
    output_path = "data/simulated_trajectories_test.json"
    simulator.save_trajectories(trajectories, output_path)
    
    print("\n" + "=" * 60)
    print("✓ StudentSimulatorV2 test completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Chạy lệnh này để tạo đủ dữ liệu (5-10 phút):
    # python3 generate_large_simulation_data.py --preset production
    test_simulator()
