#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning System for Moodle Adaptive Learning
==============================================
Clean, modular implementation with clear separation of concerns
"""

from .state_builder import MoodleStateBuilder
from .action_space import ActionSpace
from .reward_calculator import RewardCalculator
from .qlearning_agent import QLearningAgent
from .simulator import LearningSimulator

__all__ = [
    'MoodleStateBuilder',
    'ActionSpace',
    'RewardCalculator',
    'QLearningAgent',
    'LearningSimulator'
]

__version__ = '2.0.0'
