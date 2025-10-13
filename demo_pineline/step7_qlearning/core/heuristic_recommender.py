#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heuristic Recommendation Engine
================================
Rule-based fallback khi Q-Learning không có data (Q=0)
"""

import numpy as np
from typing import List, Dict, Tuple

try:
    from .action_space import Action
except ImportError:
    from action_space import Action


class HeuristicRecommender:
    """
    Rule-based recommendation engine
    
    Sử dụng khi Q-Learning chưa explore state (Q-values = 0)
    """
    
    # Difficulty mapping
    DIFFICULTY_SCORE = {
        'easy': 0.3,
        'medium': 0.6,
        'hard': 0.9,
        None: 0.5  # Unknown difficulty
    }
    
    # Action type priorities
    ACTION_PRIORITIES = {
        # Engagement boosters
        'watch_video': {'engagement_threshold': 0.5, 'priority': 1},
        'read_page': {'engagement_threshold': 0.5, 'priority': 2},
        
        # Assessment
        'take_quiz': {'knowledge_threshold': 0.4, 'priority': 3},
        'take_quiz_easy': {'knowledge_threshold': 0.0, 'priority': 1},
        'take_quiz_medium': {'knowledge_threshold': 0.4, 'priority': 2},
        'take_quiz_hard': {'knowledge_threshold': 0.7, 'priority': 3},
        
        # Collaboration
        'participate_forum': {'engagement_threshold': 0.3, 'priority': 4},
        
        # Resource access
        'study_resource': {'priority': 5},
        'read_book': {'priority': 6},
        'visit_url': {'priority': 7},
    }
    
    def __init__(self):
        """Initialize heuristic recommender"""
        pass
    
    def classify_student(self, state: np.ndarray) -> Dict[str, str]:
        """
        Classify student dựa trên state
        
        Args:
            state: 12-dim state vector
                [0] knowledge_level (mean_module_grade)
                [1] engagement (total_events)
                [2] struggle (attempt rate)
        
        Returns:
            Dict with student profile
        """
        knowledge = state[0]
        engagement = state[1]
        struggle = state[2]
        
        # Knowledge level
        if knowledge >= 0.7:
            knowledge_level = 'high'
        elif knowledge >= 0.4:
            knowledge_level = 'medium'
        else:
            knowledge_level = 'low'
        
        # Engagement level
        if engagement >= 0.7:
            engagement_level = 'high'
        elif engagement >= 0.4:
            engagement_level = 'medium'
        else:
            engagement_level = 'low'
        
        # Struggle level
        if struggle >= 0.3:
            struggle_level = 'high'
        elif struggle >= 0.15:
            struggle_level = 'medium'
        else:
            struggle_level = 'low'
        
        return {
            'knowledge_level': knowledge_level,
            'engagement_level': engagement_level,
            'struggle_level': struggle_level,
            'knowledge_score': float(knowledge),
            'engagement_score': float(engagement),
            'struggle_score': float(struggle)
        }
    
    def score_action(self, 
                    action: Action, 
                    student_profile: Dict[str, str]) -> float:
        """
        Score action cho student profile
        
        Args:
            action: Action object
            student_profile: Student classification
        
        Returns:
            Score (0-1), higher = better match
        """
        score = 0.0
        
        knowledge_level = student_profile['knowledge_level']
        engagement_level = student_profile['engagement_level']
        struggle_level = student_profile['struggle_level']
        
        knowledge_score = student_profile['knowledge_score']
        engagement_score = student_profile['engagement_score']
        
        # 1. Difficulty matching (40% weight)
        difficulty_score = self._score_difficulty_match(
            action.difficulty,
            knowledge_level,
            knowledge_score
        )
        score += 0.4 * difficulty_score
        
        # 2. Action type matching (30% weight)
        action_type_score = self._score_action_type(
            action.action_type,
            student_profile
        )
        score += 0.3 * action_type_score
        
        # 3. Engagement boost (20% weight)
        engagement_boost = self._score_engagement_need(
            action.action_type,
            engagement_level,
            engagement_score
        )
        score += 0.2 * engagement_boost
        
        # 4. Struggle mitigation (10% weight)
        struggle_score = self._score_struggle_help(
            action.action_type,
            struggle_level
        )
        score += 0.1 * struggle_score
        
        return np.clip(score, 0.0, 1.0)
    
    def _score_difficulty_match(self,
                               difficulty: str,
                               knowledge_level: str,
                               knowledge_score: float) -> float:
        """
        Score difficulty match với student knowledge
        
        Perfect match: difficulty aligned với knowledge
        """
        if difficulty is None:
            return 0.5  # Neutral for unknown difficulty
        
        diff_score = self.DIFFICULTY_SCORE[difficulty]
        
        # Perfect match = 1.0, mismatch decreases linearly
        match_quality = 1.0 - abs(diff_score - knowledge_score)
        
        return match_quality
    
    def _score_action_type(self,
                          action_type: str,
                          student_profile: Dict) -> float:
        """Score action type appropriateness"""
        knowledge = student_profile['knowledge_level']
        engagement = student_profile['engagement_level']
        
        # High knowledge students → challenging activities
        if knowledge == 'high':
            if 'quiz_hard' in action_type or 'assignment' in action_type:
                return 1.0
            elif 'quiz' in action_type:
                return 0.7
            else:
                return 0.5
        
        # Low knowledge students → foundational learning
        elif knowledge == 'low':
            if 'video' in action_type or 'read' in action_type:
                return 1.0
            elif 'quiz_easy' in action_type:
                return 0.8
            else:
                return 0.4
        
        # Medium students → balanced
        else:
            if 'quiz_medium' in action_type:
                return 1.0
            elif 'quiz' in action_type or 'video' in action_type:
                return 0.7
            else:
                return 0.6
    
    def _score_engagement_need(self,
                              action_type: str,
                              engagement_level: str,
                              engagement_score: float) -> float:
        """
        Score based on engagement needs
        
        Low engagement → prefer engaging activities (videos, forums)
        """
        engagement_boosters = ['video', 'forum', 'game', 'interactive']
        
        is_engaging = any(term in action_type for term in engagement_boosters)
        
        if engagement_level == 'low':
            # Low engagement needs boosters
            return 1.0 if is_engaging else 0.3
        elif engagement_level == 'high':
            # High engagement can do anything
            return 0.8
        else:
            # Medium engagement benefits from boosters
            return 0.9 if is_engaging else 0.6
    
    def _score_struggle_help(self,
                            action_type: str,
                            struggle_level: str) -> float:
        """
        Score based on struggle mitigation
        
        High struggle → prefer supportive resources
        """
        supportive_types = ['video', 'read', 'resource', 'tutorial', 'example']
        
        is_supportive = any(term in action_type for term in supportive_types)
        
        if struggle_level == 'high':
            # High struggle needs support
            return 1.0 if is_supportive else 0.4
        elif struggle_level == 'low':
            # Low struggle can challenge
            return 0.7 if 'quiz' in action_type else 0.6
        else:
            return 0.7
    
    def recommend(self,
                 state: np.ndarray,
                 available_actions: List[Action],
                 top_k: int = 5) -> List[Dict]:
        """
        Generate rule-based recommendations
        
        Args:
            state: Student state (12 dims)
            available_actions: List of available actions
            top_k: Number of recommendations
        
        Returns:
            List of recommendation dicts
        """
        if not available_actions:
            return []
        
        # Classify student
        student_profile = self.classify_student(state)
        
        # Score all actions
        scored_actions = []
        for action in available_actions:
            score = self.score_action(action, student_profile)
            
            rec = action.to_dict()
            rec['heuristic_score'] = float(score)
            rec['student_profile'] = student_profile
            scored_actions.append(rec)
        
        # Sort by score
        scored_actions.sort(key=lambda x: x['heuristic_score'], reverse=True)
        
        return scored_actions[:top_k]
    
    def __repr__(self) -> str:
        return "HeuristicRecommender(rule-based)"


def test_heuristic():
    """Test heuristic recommender"""
    print("\n" + "="*70)
    print("TEST: Heuristic Recommender")
    print("="*70)
    
    recommender = HeuristicRecommender()
    
    # Test actions
    actions = [
        Action(
            action_id='1',
            resource_id=1,
            resource_name='Video Tutorial - Easy',
            resource_type='hvp',
            action_type='watch_video',
            difficulty='easy'
        ),
        Action(
            action_id='2',
            resource_id=2,
            resource_name='Quiz - Medium',
            resource_type='quiz',
            action_type='take_quiz_medium',
            difficulty='medium'
        ),
        Action(
            action_id='3',
            resource_id=3,
            resource_name='Advanced Assignment',
            resource_type='assign',
            action_type='submit_assignment',
            difficulty='hard'
        ),
    ]
    
    # Test with different student profiles
    test_states = [
        ('High Achiever', np.array([0.9, 0.8, 0.1] + [0.5]*9)),
        ('Average Student', np.array([0.6, 0.5, 0.2] + [0.5]*9)),
        ('Struggling Student', np.array([0.3, 0.3, 0.4] + [0.5]*9)),
    ]
    
    for name, state in test_states:
        print(f"\n{'='*70}")
        print(f"{name}")
        print(f"{'='*70}")
        
        profile = recommender.classify_student(state)
        print(f"Profile: {profile['knowledge_level']} knowledge, "
              f"{profile['engagement_level']} engagement, "
              f"{profile['struggle_level']} struggle")
        
        recommendations = recommender.recommend(state, actions, top_k=3)
        
        print("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['resource_name']}")
            print(f"   Type: {rec['action_type']}")
            print(f"   Difficulty: {rec.get('difficulty', 'N/A')}")
            print(f"   Heuristic Score: {rec['heuristic_score']:.3f}")
    
    print("\n" + "="*70)
    print("✅ Test completed!")


if __name__ == '__main__':
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    # Import for testing
    from action_space import Action
    import numpy as np
    
    test_heuristic()
