#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reward Calculator V2
====================
Cluster-specific reward design for adaptive learning
"""

import json
from typing import Dict, Optional, Tuple
from pathlib import Path


class RewardCalculatorV2:
    """
    Reward Calculator V2 với cluster-specific rewards
    
    Reward Strategy:
    ================
    - Weak clusters: High completion rewards, encourage any progress
    - Medium clusters: Balanced rewards, focus on score improvement
    - Strong clusters: Challenge bonuses, time efficiency rewards
    
    All clusters ultimately aim for high scores, but different paths to mastery.
    """
    
    # Action type mapping (same as StateBuilderV2)
    ACTION_TYPES = {
        'watch_video': 0,
        'quiz': 1,           # do_quiz
        'forum': 2,          # mod_forum
        'review_quiz': 3,
        'read_resource': 4,
        'assignment': 5      # do_assignment
    }
    
    # Beneficial action sequences (previous → current → bonus)
    BENEFICIAL_SEQUENCES = {
        (4, 1): 2.0,  # read_resource → quiz: good preparation
        (0, 1): 1.5,  # watch_video → quiz: learned then tested
        (1, 3): 1.0,  # quiz → review_quiz: reflection
        (4, 5): 1.5,  # read_resource → assignment: applied knowledge
        (0, 5): 1.5,  # watch_video → assignment: applied knowledge
        (2, 1): 1.0,  # forum discussion → quiz: collaborative learning
    }
    
    def __init__(self, cluster_profiles_path: str):
        """
        Initialize reward calculator
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json
        """
        self.cluster_profiles_path = Path(cluster_profiles_path)
        self.cluster_profiles = {}
        self.n_clusters = 0
        self.cluster_levels = {}  # cluster_id -> 'weak'/'medium'/'strong'
        
        self._load_profiles()
        self._classify_clusters()
    
    def _load_profiles(self):
        """Load cluster profiles"""
        with open(self.cluster_profiles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.n_clusters = data.get('n_clusters', 7)
        self.cluster_profiles = data.get('cluster_stats', {})
    
    def _classify_clusters(self):
        """
        Tự động phân loại clusters thành weak/medium/strong
        dựa trên mean_module_grade
        """
        # Extract grades for all clusters (exclude teacher cluster 3)
        grade_data = []
        for cluster_id in range(self.n_clusters):
            if cluster_id == 3:  # Skip teacher cluster
                continue
            
            profile = self.cluster_profiles.get(str(cluster_id), {})
            mean_grade = profile.get('feature_means', {}).get('mean_module_grade', 0.5)
            profile_name = profile.get('ai_profile', {}).get('name', 'Unknown')
            grade_data.append((cluster_id, mean_grade, profile_name))
        
        # Sort by grade
        grade_data.sort(key=lambda x: x[1])
        
        # Split into 3 groups (weak, medium, strong)
        n = len(grade_data)
        weak_threshold = n // 3
        strong_threshold = 2 * n // 3
        
        print("\n=== CLUSTER CLASSIFICATION ===")
        for i, (cluster_id, grade, name) in enumerate(grade_data):
            if i < weak_threshold:
                level = 'weak'
            elif i < strong_threshold:
                level = 'medium'
            else:
                level = 'strong'
            
            self.cluster_levels[cluster_id] = level
            
            print(f"  Cluster {cluster_id}: grade={grade:.3f} → {level:8s} | {name}")
        print("=" * 50)
    
    def get_cluster_level(self, cluster_id: int) -> str:
        """
        Get performance level of a cluster
        
        Args:
            cluster_id: ID của cluster (already mapped, 0-5)
            
        Returns:
            'weak', 'medium', or 'strong'
        """
        return self.cluster_levels.get(cluster_id, 'medium')
    
    def _map_action_to_type(self, action_type_str: str) -> int:
        """
        Map action type string to action type ID
        
        Args:
            action_type_str: Action type string (e.g., 'quiz', 'forum')
            
        Returns:
            Action type ID (0-5)
        """
        # Normalize action type string
        action_type_str = action_type_str.lower()
        
        # Direct mapping
        if action_type_str in self.ACTION_TYPES:
            return self.ACTION_TYPES[action_type_str]
        
        # Fuzzy matching for common variations
        if 'quiz' in action_type_str:
            return self.ACTION_TYPES['quiz']
        elif 'video' in action_type_str:
            return self.ACTION_TYPES['watch_video']
        elif 'forum' in action_type_str or 'discussion' in action_type_str:
            return self.ACTION_TYPES['forum']
        elif 'resource' in action_type_str or 'page' in action_type_str or 'url' in action_type_str:
            return self.ACTION_TYPES['read_resource']
        elif 'assignment' in action_type_str or 'assign' in action_type_str:
            return self.ACTION_TYPES['assignment']
        
        # Default to read_resource
        return self.ACTION_TYPES['read_resource']
    
    def calculate_reward(
        self,
        cluster_id: int,
        state: Tuple[int, ...],
        action: Dict,
        outcome: Dict,
        previous_state: Optional[Tuple[int, ...]] = None
    ) -> float:
        """
        Calculate reward based on cluster-specific strategy
        
        Args:
            cluster_id: Cluster ID (0-5, already mapped)
            state: Current state tuple (cluster, module, progress, score, action, stuck)
            action: Action taken (dict with 'id', 'type', 'difficulty')
            outcome: Action outcome (dict with 'completed', 'score', 'time', 'success')
            previous_state: Previous state tuple (for delta calculation)
            
        Returns:
            Reward value (float)
        """
        cluster_level = self.get_cluster_level(cluster_id)
        
        # Extract state components (NOW USING recent_action!)
        _, module_idx, progress, score, recent_action, is_stuck = state
        
        # Extract previous state if available
        prev_score = previous_state[3] if previous_state else score
        prev_recent_action = previous_state[4] if previous_state else None
        
        # Map current action to type ID
        current_action_type = self._map_action_to_type(action.get('type', ''))
        
        # Base reward
        reward = 0.0
        
        # === Component 1: Completion Reward (cluster-adaptive) ===
        if outcome.get('completed', False):
            if cluster_level == 'weak':
                reward += 10.0  # High reward for any completion
            elif cluster_level == 'medium':
                reward += 7.0
            else:  # strong
                reward += 5.0  # Lower reward, expect more
        
        # === Component 2: Score Improvement (all clusters value this) ===
        outcome_score = outcome.get('score', 0.0)
        score_delta = outcome_score - prev_score
        
        if score_delta > 0:
            # Positive score improvement
            reward += score_delta * 10.0
            
            # Bonus for weak clusters reaching milestones
            if cluster_level == 'weak' and outcome_score > 0.7:
                reward += 3.0  # Milestone bonus
        
        # === Component 3: Stuck Penalty (stronger for weak clusters) ===
        if is_stuck == 1:
            if cluster_level == 'weak':
                reward -= 3.0  # Need to guide away from stuck
            elif cluster_level == 'medium':
                reward -= 2.0
            else:
                reward -= 1.0
        
        # === Component 4: Progression Bonus (cluster-specific) ===
        action_difficulty = action.get('difficulty', 'medium')
        
        if outcome.get('completed', False):
            if cluster_level == 'weak':
                # Any progress is good
                reward += 5.0
            elif cluster_level == 'medium':
                # Reward appropriate difficulty
                if action_difficulty == 'medium':
                    reward += 7.0
                elif action_difficulty == 'easy':
                    reward += 4.0
                else:  # hard
                    reward += 5.0
            else:  # strong
                # Challenge seekers
                if action_difficulty == 'hard':
                    reward += 10.0
                elif action_difficulty == 'medium':
                    reward += 6.0
                else:  # easy
                    reward += 3.0
        
        # === Component 5: Time Efficiency (strong clusters value this) ===
        if cluster_level == 'strong':
            time_taken = outcome.get('time', 0)
            expected_time = action.get('expected_time', 30)
            
            if time_taken > 0 and time_taken < expected_time * 0.8:
                reward += 3.0  # Bonus for efficiency
        
        # === Component 6: High Score Bonus (all clusters) ===
        if outcome_score >= 0.9:
            if cluster_level == 'weak':
                reward += 5.0  # Major achievement
            elif cluster_level == 'medium':
                reward += 3.0
            else:
                reward += 2.0  # Expected for strong
        
        # === Component 7: Failure Penalty ===
        if not outcome.get('success', True):
            if cluster_level == 'weak':
                reward -= 1.0  # Small penalty, don't discourage
            else:
                reward -= 2.0
        
        # === Component 8: Action Diversity Bonus ===
        # Encourage variety in learning activities (except for weak clusters when stuck)
        if recent_action is not None and recent_action != current_action_type:
            if cluster_level == 'weak':
                # Weak clusters benefit from variety, but not when stuck
                if not is_stuck:
                    reward += 0.5
            elif cluster_level == 'medium':
                reward += 1.0  # Moderate variety bonus
            else:  # strong
                reward += 1.5  # Strong learners benefit most from diverse approaches
        
        # === Component 9: Action Sequence Logic ===
        # Reward beneficial learning sequences (e.g., read → quiz)
        if recent_action is not None:
            sequence_key = (recent_action, current_action_type)
            if sequence_key in self.BENEFICIAL_SEQUENCES:
                sequence_bonus = self.BENEFICIAL_SEQUENCES[sequence_key]
                
                # Scale bonus by cluster level
                if cluster_level == 'weak':
                    reward += sequence_bonus * 0.7  # Smaller bonus, still learning patterns
                elif cluster_level == 'medium':
                    reward += sequence_bonus  # Full bonus
                else:  # strong
                    reward += sequence_bonus * 1.3  # Bonus for strategic learning
        
        # === Component 10: Repetition Penalty ===
        # Discourage doing the same action repeatedly without progress
        if recent_action == current_action_type and prev_recent_action == recent_action:
            # Same action done 3 times in a row
            if cluster_level == 'weak':
                reward -= 0.5  # Gentle reminder to try something else
            elif cluster_level == 'medium':
                reward -= 1.5  # Moderate penalty
            else:  # strong
                reward -= 2.5  # Strong penalty for inefficient learning
        
        return reward
    
    def calculate_reward_simple(
        self,
        cluster_id: int,
        completed: bool,
        score: float,
        previous_score: float,
        is_stuck: bool,
        difficulty: str = 'medium'
    ) -> float:
        """
        Simplified reward calculation (for quick testing)
        
        Args:
            cluster_id: Cluster ID (0-5)
            completed: Whether action was completed
            score: Current score (0-1)
            previous_score: Previous score (0-1)
            is_stuck: Whether student is stuck
            difficulty: Action difficulty
            
        Returns:
            Reward value
        """
        cluster_level = self.get_cluster_level(cluster_id)
        reward = 0.0
        
        # Completion
        if completed:
            if cluster_level == 'weak':
                reward += 10.0
            elif cluster_level == 'medium':
                reward += 7.0
            else:
                reward += 5.0
        
        # Score improvement
        score_delta = score - previous_score
        if score_delta > 0:
            reward += score_delta * 10.0
        
        # Stuck penalty
        if is_stuck:
            reward -= (3.0 if cluster_level == 'weak' else 2.0)
        
        # Difficulty bonus for strong clusters
        if cluster_level == 'strong' and difficulty == 'hard' and completed:
            reward += 5.0
        
        return reward
    
    def get_reward_strategy_description(self, cluster_id: int) -> Dict:
        """
        Get description of reward strategy for a cluster
        
        Args:
            cluster_id: Cluster ID (0-4)
            
        Returns:
            Dict describing reward strategy
        """
        level = self.get_cluster_level(cluster_id)
        
        strategies = {
            'weak': {
                'focus': 'Completion and Progress',
                'completion_reward': 10.0,
                'stuck_penalty': -3.0,
                'philosophy': 'High rewards for any completion. Need motivation and guidance. '
                             'Small wins build confidence. Avoid harsh penalties.',
                'recommended_actions': 'Easy to medium difficulty. Step-by-step progression.'
            },
            'medium': {
                'focus': 'Balanced Growth',
                'completion_reward': 7.0,
                'stuck_penalty': -2.0,
                'philosophy': 'Balanced rewards. Focus on appropriate difficulty. '
                             'Build skills systematically. Moderate challenge.',
                'recommended_actions': 'Medium difficulty preferred. Mix of content and assessment.'
            },
            'strong': {
                'focus': 'Challenge and Mastery',
                'completion_reward': 5.0,
                'stuck_penalty': -1.0,
                'philosophy': 'Challenge-seeking. Reward hard tasks and efficiency. '
                             'High expectations. Focus on mastery and speed.',
                'recommended_actions': 'Hard difficulty preferred. Advanced topics. Time efficiency valued.'
            }
        }
        
        return {
            'cluster_id': cluster_id,
            'level': level,
            'strategy': strategies[level]
        }
    
    def get_all_strategies(self) -> Dict:
        """Get reward strategies for all clusters"""
        return {
            cid: self.get_reward_strategy_description(cid)
            for cid in self.cluster_levels.keys()
        }
    
    def get_action_sequence_info(self) -> Dict:
        """
        Get information about beneficial action sequences
        
        Returns:
            Dict with sequence information
        """
        action_names = {v: k for k, v in self.ACTION_TYPES.items()}
        
        sequences = []
        for (prev_id, curr_id), bonus in self.BENEFICIAL_SEQUENCES.items():
            prev_name = action_names.get(prev_id, 'unknown')
            curr_name = action_names.get(curr_id, 'unknown')
            sequences.append({
                'previous_action': prev_name,
                'current_action': curr_name,
                'bonus_reward': bonus,
                'rationale': self._get_sequence_rationale(prev_id, curr_id)
            })
        
        return {
            'total_sequences': len(self.BENEFICIAL_SEQUENCES),
            'sequences': sequences,
            'diversity_bonus': {
                'weak': 0.5,
                'medium': 1.0,
                'strong': 1.5
            },
            'repetition_penalty': {
                'weak': -0.5,
                'medium': -1.5,
                'strong': -2.5
            }
        }
    
    def _get_sequence_rationale(self, prev_id: int, curr_id: int) -> str:
        """Get explanation for why a sequence is beneficial"""
        rationales = {
            (4, 1): "Reading material before quiz demonstrates good preparation",
            (0, 1): "Watching video before quiz shows active learning",
            (1, 3): "Reviewing quiz after attempt promotes reflection",
            (4, 5): "Reading before assignment enables knowledge application",
            (0, 5): "Watching video before assignment enables knowledge application",
            (2, 1): "Forum discussion before quiz encourages collaborative learning",
        }
        return rationales.get((prev_id, curr_id), "Strategic learning sequence")


def test_reward_calculator():
    """Test RewardCalculatorV2"""
    print("=" * 60)
    print("Testing RewardCalculatorV2 with Action Sequence Logic")
    print("=" * 60)
    
    # Path
    base_path = Path(__file__).parent.parent
    cluster_path = base_path / 'data' / 'cluster_profiles.json'
    
    # Initialize
    calc = RewardCalculatorV2(cluster_profiles_path=str(cluster_path))
    
    # Test 1: Reward strategies
    print("\n1. Reward Strategies:")
    strategies = calc.get_all_strategies()
    for cid, strategy in strategies.items():
        print(f"\n   Cluster {cid} ({strategy['level']}):")
        print(f"      Focus: {strategy['strategy']['focus']}")
        print(f"      Completion reward: {strategy['strategy']['completion_reward']}")
        print(f"      Philosophy: {strategy['strategy']['philosophy'][:80]}...")
    
    # Test 2: Action sequences
    print("\n2. Beneficial Action Sequences:")
    seq_info = calc.get_action_sequence_info()
    print(f"   Total beneficial sequences: {seq_info['total_sequences']}")
    for seq in seq_info['sequences'][:3]:  # Show first 3
        print(f"\n   {seq['previous_action']} → {seq['current_action']}")
        print(f"      Bonus: +{seq['bonus_reward']}")
        print(f"      Why: {seq['rationale']}")
    
    # Test 3: Diversity & Repetition
    print("\n3. Diversity Bonuses:")
    for level, bonus in seq_info['diversity_bonus'].items():
        print(f"   {level:8s}: +{bonus}")
    
    print("\n4. Repetition Penalties:")
    for level, penalty in seq_info['repetition_penalty'].items():
        print(f"   {level:8s}: {penalty}")
    
    # Test 5: Sample reward calculations with action sequences
    print("\n5. Sample Reward Calculations with Recent Actions:")
    
    test_cases = [
        # (cluster, state, action, outcome, prev_state, description)
        (
            2,  # medium cluster
            (2, 5, 0.75, 0.7, 4, 0),  # recent_action=4 (read_resource)
            {'type': 'quiz', 'difficulty': 'medium'},
            {'completed': True, 'score': 0.85, 'success': True},
            (2, 5, 0.5, 0.7, 3, 0),  # prev recent_action=3
            'Medium cluster: read_resource → quiz (beneficial sequence)'
        ),
        (
            4,  # strong cluster  
            (4, 10, 0.9, 0.8, 0, 0),  # recent_action=0 (watch_video)
            {'type': 'quiz', 'difficulty': 'hard'},
            {'completed': True, 'score': 0.95, 'success': True},
            (4, 10, 0.75, 0.8, 2, 0),
            'Strong cluster: watch_video → quiz (beneficial + diversity)'
        ),
        (
            0,  # weak cluster
            (0, 3, 0.5, 0.6, 1, 0),  # recent_action=1 (quiz)
            {'type': 'quiz', 'difficulty': 'easy'},
            {'completed': False, 'score': 0.55, 'success': False},
            (0, 3, 0.5, 0.6, 1, 0),  # Same action repeated
            'Weak cluster: quiz → quiz (repetition penalty)'
        ),
        (
            2,  # medium cluster
            (2, 7, 0.8, 0.75, 2, 0),  # recent_action=2 (forum)
            {'type': 'quiz', 'difficulty': 'medium'},
            {'completed': True, 'score': 0.85, 'success': True},
            (2, 7, 0.6, 0.75, 4, 0),
            'Medium cluster: forum → quiz (beneficial sequence)'
        ),
    ]
    
    for cluster, state, action, outcome, prev_state, desc in test_cases:
        reward = calc.calculate_reward(
            cluster, state, action, outcome, prev_state
        )
        level = calc.get_cluster_level(cluster)
        recent = state[4]
        prev_recent = prev_state[4] if prev_state else None
        
        print(f"\n   {desc}")
        print(f"      Cluster {cluster} ({level})")
        print(f"      Recent actions: {prev_recent} → {recent}")
        print(f"      → Total reward = {reward:.2f}")
    
    print("\n" + "=" * 60)
    print("✓ RewardCalculatorV2 test completed!")
    print("=" * 60)


if __name__ == '__main__':
    test_reward_calculator()
