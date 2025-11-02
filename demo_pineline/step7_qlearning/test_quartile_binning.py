#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Quartile Binning Implementation
=====================================
Quick test to verify binning logic works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
from core.qlearning_agent import QLearningAgent
from config import QUARTILE_BINS, BINNING_STRATEGY

def test_binning_logic():
    """Test that binning logic works correctly"""
    print("="*70)
    print("TESTING QUARTILE BINNING IMPLEMENTATION")
    print("="*70)
    
    # Initialize agent with Quartile bins
    print(f"\n[1/4] Initializing agent with {BINNING_STRATEGY} binning...")
    agent = QLearningAgent(
        n_actions=10,
        state_bins=QUARTILE_BINS
    )
    print(f"  ✓ Agent initialized")
    print(f"  ✓ Bins: {agent.state_bins}")
    
    # Test case 1: State with values in each quartile
    print("\n[2/4] Test case 1: Mixed quartile values")
    test_state_1 = np.array([
        0.3,   # [0.25, 0.5) → 0.25 (Low-Med)
        0.65,  # [0.5, 0.75) → 0.5 (Med-High)
        0.12,  # [0.0, 0.25) → 0.0 (Low)
        0.88,  # [0.75, 1.0] → 0.75 (High)
        0.5,   # [0.5, 0.75) → 0.5 (boundary)
        0.0,   # [0.0, 0.25) → 0.0 (min)
        0.75,  # [0.75, 1.0] → 0.75 (boundary)
        0.99,  # [0.75, 1.0] → 0.75 (High)
        0.2,   # [0.0, 0.25) → 0.0 (Low)
        0.4,   # [0.25, 0.5) → 0.25 (Low-Med)
        0.6,   # [0.5, 0.75) → 0.5 (Med-High)
        0.8    # [0.75, 1.0] → 0.75 (High)
    ])
    
    hashed_1 = agent.hash_state(test_state_1)
    expected_1 = (0.25, 0.5, 0.0, 0.75, 0.5, 0.0, 0.75, 0.75, 0.0, 0.25, 0.5, 0.75)
    
    print(f"  Input:    {test_state_1}")
    print(f"  Hashed:   {hashed_1}")
    print(f"  Expected: {expected_1}")
    
    # Verify
    match_1 = hashed_1 == expected_1
    print(f"  ✓ Match: {match_1}")
    if not match_1:
        print(f"  ❌ FAILED: Binning logic incorrect!")
        return False
    
    # Test case 2: Edge values (0.0, 0.25, 0.5, 0.75)
    print("\n[3/4] Test case 2: Boundary values")
    test_state_2 = np.array([
        0.0, 0.25, 0.5, 0.75,  # Exact boundaries
        0.249, 0.499, 0.749,   # Just below boundaries
        0.251, 0.501, 0.751,   # Just above boundaries
        1.0, 0.999              # Max values
    ])
    
    hashed_2 = agent.hash_state(test_state_2)
    expected_2 = (
        0.0,   # 0.0   ∈ [0.0, 0.25) → 0.0
        0.25,  # 0.25  ∈ [0.25, 0.5) → 0.25
        0.5,   # 0.5   ∈ [0.5, 0.75) → 0.5
        0.75,  # 0.75  ∈ [0.75, 1.0] → 0.75
        0.0,   # 0.249 ∈ [0.0, 0.25) → 0.0
        0.25,  # 0.499 ∈ [0.25, 0.5) → 0.25
        0.5,   # 0.749 ∈ [0.5, 0.75) → 0.5
        0.25,  # 0.251 ∈ [0.25, 0.5) → 0.25
        0.5,   # 0.501 ∈ [0.5, 0.75) → 0.5
        0.75,  # 0.751 ∈ [0.75, 1.0] → 0.75
        0.75,  # 1.0   ∈ [0.75, 1.0] → 0.75 (special case)
        0.75   # 0.999 ∈ [0.75, 1.0] → 0.75
    )
    
    print(f"  Input:    {test_state_2}")
    print(f"  Hashed:   {hashed_2}")
    print(f"  Expected: {expected_2}")
    
    match_2 = hashed_2 == expected_2
    print(f"  ✓ Match: {match_2}")
    if not match_2:
        print(f"  ❌ FAILED: Boundary handling incorrect!")
        return False
    
    # Test case 3: Verify state space reduction
    print("\n[4/4] Verify state space reduction")
    
    old_state_space = 11 ** 12  # Old approach (decimals=1)
    new_state_space = 4 ** 12   # New approach (quartile)
    reduction_factor = old_state_space / new_state_space
    
    print(f"  Old state space (11 bins): {old_state_space:,} ({old_state_space/1e12:.1f}T)")
    print(f"  New state space (4 bins):  {new_state_space:,} ({new_state_space/1e6:.1f}M)")
    print(f"  Reduction factor: {reduction_factor:.0f}x")
    
    # Simulate coverage improvement
    q_table_size = 69_836  # Current Q-table size
    old_coverage = q_table_size / old_state_space * 100
    new_coverage = q_table_size / new_state_space * 100
    improvement = new_coverage / old_coverage
    
    print(f"\n  Q-table size: {q_table_size:,} states")
    print(f"  Old coverage: {old_coverage:.6f}%")
    print(f"  New coverage: {new_coverage:.4f}%")
    print(f"  Coverage improvement: {improvement:.1f}x")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - QUARTILE BINNING WORKING CORRECTLY")
    print("="*70)
    
    print("\n📝 Next Steps:")
    print("  1. Retrain model: python train_qlearning_v2.py --epochs 10")
    print("  2. Test API with test cases from test_cases_from_simulation.json")
    print("  3. Verify q_values > 0 for most requests")
    
    return True


if __name__ == '__main__':
    try:
        success = test_binning_logic()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
