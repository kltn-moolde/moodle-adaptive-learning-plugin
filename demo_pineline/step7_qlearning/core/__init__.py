"""
Core Q-Learning package - Version 2.0
New design với Moodle integration
"""

# ✅ New design (v2.0)
from .moodle_state_builder import MoodleStateBuilder
from .action_space import ActionSpace, Action
from .state_discretizer import StateDiscretizer
from .heuristic_recommender import HeuristicRecommender
from .qlearning_agent_v2 import QLearningAgentV2, QLearningAgent

# 🔄 Old design (deprecated)
# from .reward_calculator import RewardCalculator
# from .qlearning_agent import QLearningAgent (old)

__all__ = [
    'MoodleStateBuilder',
    'Action',
    'ActionSpace',
    'QLearningAgentV2',
    'QLearningAgent',  # Alias to V2
]
