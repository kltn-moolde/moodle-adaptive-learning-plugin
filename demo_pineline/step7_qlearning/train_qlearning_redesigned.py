"""
Training Script for Q-Learning Agent V2
Redesigned to properly match the API of QLearningAgentV2

This script:
1. Loads simulated trajectories from JSON
2. Converts format to match agent expectations
3. Trains QLearningAgentV2
4. Saves trained Q-table

Author: Redesigned based on actual API analysis
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Dict, List
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.qlearning_agent_v2 import QLearningAgentV2


def load_trajectories(filepath: str) -> Dict[int, List[Dict]]:
    """
    Load trajectories from JSON file
    
    Args:
        filepath: Path to JSON file containing trajectories
        
    Returns:
        Dict mapping student_id (int) -> trajectory (list of transitions)
    """
    print(f"\n{'='*60}")
    print("Loading Simulated Trajectories")
    print(f"{'='*60}")
    print(f"File: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert keys from string to int AND convert states from list to tuple
    trajectories = {}
    for student_id_str, trajectory in data.items():
        student_id = int(student_id_str)
        
        # Convert states to tuples (required for Q-table dict keys)
        converted_trajectory = []
        for transition in trajectory:
            converted_transition = transition.copy()
            converted_transition['state'] = tuple(transition['state'])
            converted_transition['next_state'] = tuple(transition['next_state'])
            converted_trajectory.append(converted_transition)
        
        trajectories[student_id] = converted_trajectory
    
    # Print statistics
    n_students = len(trajectories)
    n_transitions = sum(len(traj) for traj in trajectories.values())
    avg_trajectory_length = n_transitions / n_students if n_students > 0 else 0
    
    print(f"\n✓ Loaded successfully:")
    print(f"  Students: {n_students}")
    print(f"  Total transitions: {n_transitions}")
    print(f"  Avg trajectory length: {avg_trajectory_length:.1f}")
    
    # Analyze state space coverage
    unique_states = set()
    for trajectory in trajectories.values():
        for transition in trajectory:
            unique_states.add(tuple(transition['state']))
    
    print(f"  Unique states observed: {len(unique_states)}")
    
    return trajectories


def verify_data_format(trajectories: Dict[int, List[Dict]]) -> bool:
    """
    Verify that trajectories have correct format
    
    Args:
        trajectories: Trajectories to verify
        
    Returns:
        True if format is valid, False otherwise
    """
    print(f"\n{'='*60}")
    print("Verifying Data Format")
    print(f"{'='*60}")
    
    required_keys = {'state', 'action', 'reward', 'next_state', 'is_terminal'}
    
    # Check first trajectory
    if not trajectories:
        print("✗ Error: No trajectories found")
        return False
    
    first_student_id = list(trajectories.keys())[0]
    first_trajectory = trajectories[first_student_id]
    
    if not first_trajectory:
        print("✗ Error: First trajectory is empty")
        return False
    
    first_transition = first_trajectory[0]
    
    # Check required keys
    missing_keys = required_keys - set(first_transition.keys())
    if missing_keys:
        print(f"✗ Error: Missing required keys: {missing_keys}")
        return False
    
    # Check state format
    state = first_transition['state']
    if not isinstance(state, (list, tuple)):
        print(f"✗ Error: State must be list or tuple, got {type(state)}")
        return False
    
    print(f"✓ Data format verified:")
    print(f"  State length: {len(state)}")
    print(f"  State example: {state}")
    print(f"  All required keys present: {required_keys}")
    
    return True


def get_n_actions(trajectories: Dict[int, List[Dict]]) -> int:
    """
    Determine number of actions from trajectory data
    
    Args:
        trajectories: Trajectory data
        
    Returns:
        Number of unique actions (modules)
    """
    all_actions = set()
    for trajectory in trajectories.values():
        for transition in trajectory:
            all_actions.add(transition['action'])
    
    n_actions = len(all_actions)
    print(f"\n  Detected {n_actions} unique actions (modules)")
    
    return n_actions


def train_agent(
    trajectories: Dict[int, List[Dict]],
    n_actions: int,
    n_epochs: int = 10,
    learning_rate: float = 0.1,
    discount_factor: float = 0.95,
    epsilon: float = 0.1,
    epsilon_decay: float = 0.995,
    shuffle: bool = True
) -> QLearningAgentV2:
    """
    Train Q-learning agent on trajectories
    
    Args:
        trajectories: Training data
        n_actions: Number of possible actions
        n_epochs: Number of training epochs
        learning_rate: Learning rate for Q-learning
        discount_factor: Discount factor (gamma)
        epsilon: Initial exploration rate
        epsilon_decay: Epsilon decay rate per episode
        shuffle: Whether to shuffle trajectories each epoch
        
    Returns:
        Trained QLearningAgentV2 agent
    """
    print(f"\n{'='*60}")
    print("Initializing Q-Learning Agent")
    print(f"{'='*60}")
    print(f"\nHyperparameters:")
    print(f"  Actions (modules): {n_actions}")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Discount factor: {discount_factor}")
    print(f"  Initial epsilon: {epsilon}")
    print(f"  Epsilon decay: {epsilon_decay}")
    print(f"  Training epochs: {n_epochs}")
    print(f"  Shuffle: {shuffle}")
    
    # Initialize agent
    agent = QLearningAgentV2(
        n_actions=n_actions,
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon=epsilon,
        epsilon_decay=epsilon_decay
    )
    
    # Train agent
    epoch_stats = agent.train_batch(
        trajectories=trajectories,
        n_epochs=n_epochs,
        shuffle=shuffle,
        verbose=True
    )
    
    return agent


def save_agent(agent: QLearningAgentV2, filepath: str):
    """
    Save trained agent to file
    
    Args:
        agent: Trained agent
        filepath: Output file path
    """
    print(f"\n{'='*60}")
    print("Saving Trained Agent")
    print(f"{'='*60}")
    
    # Create output directory if needed
    output_dir = Path(filepath).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save agent
    agent.save(filepath)
    
    # Verify file size
    file_size = Path(filepath).stat().st_size / (1024 * 1024)  # MB
    print(f"\n✓ Saved successfully:")
    print(f"  File: {filepath}")
    print(f"  Size: {file_size:.2f} MB")
    print(f"  Q-table states: {len(agent.q_table)}")


def main():
    """Main training pipeline"""
    
    print("\n" + "="*60)
    print("Q-LEARNING TRAINING PIPELINE V2")
    print("="*60)
    
    # Configuration
    INPUT_FILE = "data/simulated_trajectories_best.json"
    OUTPUT_FILE = "models/qtable_best.pkl"
    
    # Training hyperparameters
    N_EPOCHS = 10
    LEARNING_RATE = 0.1
    DISCOUNT_FACTOR = 0.95
    EPSILON = 0.1
    EPSILON_DECAY = 0.995
    SHUFFLE = True
    
    # Step 1: Load trajectories
    try:
        trajectories = load_trajectories(INPUT_FILE)
    except FileNotFoundError:
        print(f"\n✗ Error: File not found: {INPUT_FILE}")
        print("\nPlease run generate_large_simulation_data.py first to create training data.")
        return
    except Exception as e:
        print(f"\n✗ Error loading trajectories: {e}")
        return
    
    # Step 2: Verify data format
    if not verify_data_format(trajectories):
        print("\n✗ Data format verification failed. Exiting.")
        return
    
    # Step 3: Determine number of actions
    n_actions = get_n_actions(trajectories)
    
    # Step 4: Train agent
    try:
        agent = train_agent(
            trajectories=trajectories,
            n_actions=n_actions,
            n_epochs=N_EPOCHS,
            learning_rate=LEARNING_RATE,
            discount_factor=DISCOUNT_FACTOR,
            epsilon=EPSILON,
            epsilon_decay=EPSILON_DECAY,
            shuffle=SHUFFLE
        )
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Save trained agent
    try:
        save_agent(agent, OUTPUT_FILE)
    except Exception as e:
        print(f"\n✗ Error saving agent: {e}")
        return
    
    # Done
    print(f"\n{'='*60}")
    print("✓ TRAINING COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"\nTrained Q-table saved to: {OUTPUT_FILE}")
    print(f"\nNext steps:")
    print(f"  1. Evaluate agent:")
    print(f"     python3 evaluate_agent.py --model {OUTPUT_FILE} --trajectories {INPUT_FILE} --output results/evaluation_results.json")
    print(f"  2. Test API: python3 test_api_v2.py")
    print(f"  3. Export Q-table info: python3 export_qtable_info.py")


if __name__ == "__main__":
    main()
