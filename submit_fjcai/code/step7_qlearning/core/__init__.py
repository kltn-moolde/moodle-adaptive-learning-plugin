#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-Learning System for Moodle Adaptive Learning
==============================================
Clean, modular implementation with clear separation of concerns
"""

# Re-export from submodules for backward compatibility
from .rl import (
    QLearningAgentV2,
    ActionSpace,
    LearningAction,
    StateBuilderV2,
    RewardCalculatorV2
)
from .log_processing import (
    LogEvent,
    UserLogSummary,
    ActionType,
    LogToStateBuilder,
    MoodleLogProcessorV2,
    StateUpdateManager,
    UserModuleContext,
    BufferedLog
)
from .simulation import (
    LearningPathSimulator,
    Student,
    StateTransitionLogger
)

__all__ = [
    # RL components
    'QLearningAgentV2',
    'ActionSpace',
    'LearningAction',
    'StateBuilderV2',
    'RewardCalculatorV2',
    # Log processing
    'LogEvent',
    'UserLogSummary',
    'ActionType',
    'LogToStateBuilder',
    'MoodleLogProcessorV2',
    'StateUpdateManager',
    'UserModuleContext',
    'BufferedLog',
    # Simulation
    'LearningPathSimulator',
    'Student',
    'StateTransitionLogger'
]

__version__ = '2.0.0'
