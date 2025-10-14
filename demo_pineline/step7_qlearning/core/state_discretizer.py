#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Discretizer for Q-Learning
=================================
Rời rạc hóa continuous state space thành discrete bins
"""

import numpy as np
from typing import List, Tuple, Dict


class StateDiscretizer:
    """
    Discretizer cho state space
    
    Chuyển continuous state [0, 1]^12 thành discrete bins
    để giảm state sparsity và improve generalization
    """
    
    def __init__(self, state_dim: int = 12, n_bins: int = 3):
        """
        Args:
            state_dim: State dimension (12 for Moodle)
            n_bins: Number of bins per dimension
                    3 bins → Low/Medium/High
                    5 bins → Very Low/Low/Medium/High/Very High
        """
        self.state_dim = state_dim
        self.n_bins = n_bins
        
        # Bin edges for [0, 1] range
        self.bin_edges = self._create_bin_edges()
        
        # Bin labels
        if n_bins == 3:
            self.bin_labels = ['low', 'medium', 'high']
        elif n_bins == 5:
            self.bin_labels = ['very_low', 'low', 'medium', 'high', 'very_high']
        else:
            self.bin_labels = [f'bin_{i}' for i in range(n_bins)]
    
    def _create_bin_edges(self) -> np.ndarray:
        """
        Create bin edges for discretization
        
        For n_bins=3: [0, 0.33, 0.67, 1.0]
        For n_bins=5: [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        """
        return np.linspace(0, 1, self.n_bins + 1)
    
    def discretize(self, state: np.ndarray) -> Tuple[int, ...]:
        """
        Discretize continuous state thành discrete tuple
        
        Args:
            state: Continuous state vector [12 dims, values in [0,1]]
        
        Returns:
            Discrete state tuple, e.g. (0, 1, 2, 1, 0, ...)
            
        Example:
            state = [0.1, 0.5, 0.9, ...]
            n_bins = 3
            → discrete = (0, 1, 2, ...)  # low, medium, high
        """
        # Clip to [0, 1] range
        state_clipped = np.clip(state, 0, 1)
        
        # Digitize: assign each value to a bin
        # np.digitize returns bin index (1-based), subtract 1 for 0-based
        discrete_indices = np.digitize(state_clipped, self.bin_edges[1:-1])
        
        return tuple(discrete_indices)
    
    def get_bin_center(self, bin_index: int) -> float:
        """Get center value of a bin"""
        left = self.bin_edges[bin_index]
        right = self.bin_edges[bin_index + 1]
        return (left + right) / 2
    
    def decode(self, discrete_state: Tuple[int, ...]) -> np.ndarray:
        """
        Decode discrete state back to continuous (using bin centers)
        
        Args:
            discrete_state: Tuple of bin indices
        
        Returns:
            Continuous state (approximate)
        """
        continuous = np.array([
            self.get_bin_center(idx) for idx in discrete_state
        ])
        return continuous
    
    def get_state_space_size(self) -> int:
        """
        Calculate total discrete state space size
        
        For 12 dims with 3 bins each: 3^12 = 531,441 possible states
        For 12 dims with 5 bins each: 5^12 = 244,140,625 states
        """
        return self.n_bins ** self.state_dim
    
    def get_bin_label(self, bin_index: int) -> str:
        """Get label for bin index"""
        if bin_index < len(self.bin_labels):
            return self.bin_labels[bin_index]
        return f'bin_{bin_index}'
    
    def describe_discrete_state(self, discrete_state: Tuple[int, ...],
                               feature_names: List[str] = None) -> Dict:
        """
        Human-readable description of discrete state
        
        Args:
            discrete_state: Tuple of bin indices
            feature_names: Names of state features
        
        Returns:
            Dictionary with feature → bin label mapping
        """
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(discrete_state))]
        
        description = {}
        for fname, bin_idx in zip(feature_names, discrete_state):
            description[fname] = self.get_bin_label(bin_idx)
        
        return description
    
    def __repr__(self) -> str:
        return (f"StateDiscretizer(dim={self.state_dim}, "
                f"bins={self.n_bins}, "
                f"space_size={self.get_state_space_size():,})")


def test_discretizer():
    """Test discretizer functionality"""
    print("\n" + "="*70)
    print("TEST: State Discretizer")
    print("="*70)
    
    # Create discretizer with 3 bins
    discretizer = StateDiscretizer(state_dim=12, n_bins=3)
    print(f"\n{discretizer}")
    print(f"Bin edges: {discretizer.bin_edges}")
    
    # Test cases
    test_states = [
        np.array([0.1, 0.5, 0.9] + [0.5]*9),  # Low, Medium, High
        np.array([0.2, 0.4, 0.6] + [0.5]*9),  # Low, Medium, Medium
        np.array([0.8, 0.8, 0.1] + [0.5]*9),  # High, High, Low
    ]
    
    for i, state in enumerate(test_states, 1):
        discrete = discretizer.discretize(state)
        decoded = discretizer.decode(discrete)
        
        print(f"\nTest {i}:")
        print(f"  Original: {state[:3]} ...")
        print(f"  Discrete: {discrete[:3]} ...")
        print(f"  Decoded:  {decoded[:3]} ...")
        print(f"  Labels: {[discretizer.get_bin_label(idx) for idx in discrete[:3]]}")
    
    # Test with 5 bins
    print("\n" + "="*70)
    discretizer5 = StateDiscretizer(state_dim=12, n_bins=5)
    print(f"\n{discretizer5}")
    
    state = np.array([0.1, 0.3, 0.5, 0.7, 0.9] + [0.5]*7)
    discrete = discretizer5.discretize(state)
    print(f"\nState: {state[:5]}")
    print(f"Discrete: {discrete[:5]}")
    print(f"Labels: {[discretizer5.get_bin_label(idx) for idx in discrete[:5]]}")
    
    print("\n" + "="*70)
    print("✅ Test completed!")


if __name__ == '__main__':
    test_discretizer()
