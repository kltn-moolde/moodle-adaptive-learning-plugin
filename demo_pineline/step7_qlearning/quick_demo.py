#!/usr/bin/env python3
"""
Quick Demo: Enhanced StudentSimulatorV2
Demonstrates key features in 5 minutes
"""

import sys
sys.path.insert(0, '.')

from core.simulator_v2 import StudentSimulatorV2
from datetime import datetime
import numpy as np

print("\n" + "="*80)
print("🎓 ENHANCED SIMULATOR QUICK DEMO")
print("="*80)

# 1. Initialize với learned parameters
print("\n1️⃣  Initializing với learned parameters...")
simulator = StudentSimulatorV2(
    use_learned_params=True,
    learning_curve_type='logistic',
    seed=42
)
print("   ✓ Parameters learned from cluster_profiles.json")

# 2. Show learned params
print("\n2️⃣  Learned Parameters (Sample):")
for cluster_id in [0, 2]:  # weak and strong
    params = simulator.cluster_params[cluster_id]
    print(f"\n   Cluster {cluster_id} ({params['level'].upper()}):")
    print(f"     • Success rate:      {params['success_rate']:.2f}")
    print(f"     • Stuck probability: {params['stuck_probability']:.2f}")
    print(f"     • Preferred actions: {', '.join(params['preferred_actions'][:2])}")

# 3. Demonstrate learning curve
print("\n3️⃣  Learning Curve Effect:")
print("   WEAK Learner progress over attempts:")
for attempt in [1, 3, 5, 8, 10]:
    progress = simulator._compute_learning_curve_progress(
        n_attempts=attempt,
        cluster_level='weak',
        current_progress=0.0
    )
    print(f"     Attempt {attempt:2d}: {progress:.3f}")

print("\n   STRONG Learner progress over attempts:")
for attempt in [1, 3, 5]:
    progress = simulator._compute_learning_curve_progress(
        n_attempts=attempt,
        cluster_level='strong',
        current_progress=0.0
    )
    print(f"     Attempt {attempt:2d}: {progress:.3f}")

# 4. Simulate one student
print("\n4️⃣  Simulating Weak Learner (Cluster 0):")
trajectory = simulator.simulate_trajectory(
    student_id=1001,
    cluster_id=0,
    max_steps=15,
    start_time=datetime(2024, 1, 1, 9, 0),
    verbose=False
)

print(f"   ✓ Generated {len(trajectory)} transitions")
print(f"   ✓ Total reward: {sum(t['reward'] for t in trajectory):.2f}")
print(f"   ✓ Final progress: {trajectory[-1]['module_progress']:.2f}")

print("\n   First 5 actions:")
for i, t in enumerate(trajectory[:5]):
    print(f"     {i+1}. {t['action_type']:15s} → "
          f"Progress: {t['module_progress']:.3f}, "
          f"Reward: {t['reward']:+.2f}")

# 5. Demonstrate score improvement
print("\n5️⃣  Score Improvement Over Attempts:")
scores = []
previous_score = None
for attempt in range(1, 6):
    score = simulator._compute_score_with_improvement(
        n_attempts=attempt,
        cluster_level='medium',
        previous_score=previous_score,
        base_score_range=(0.5, 0.9)
    )
    scores.append(score)
    
    if previous_score:
        improvement = score - previous_score
        print(f"   Attempt {attempt}: {score:.3f} (+{improvement:.3f})")
    else:
        print(f"   Attempt {attempt}: {score:.3f} (first)")
    
    previous_score = score

print(f"\n   📈 Total improvement: {scores[-1] - scores[0]:.3f}")

# 6. Batch simulation
print("\n6️⃣  Batch Simulation (2 students per cluster):")
trajectories = simulator.simulate_batch(
    n_students_per_cluster=2,
    max_steps_per_student=15,
    verbose=False
)

print(f"   ✓ Generated {len(trajectories)} students")
print(f"   ✓ Total transitions: {sum(len(t) for t in trajectories.values())}")
print(f"   ✓ Avg trajectory length: {np.mean([len(t) for t in trajectories.values()]):.1f}")

# Summary by cluster
from collections import Counter
cluster_rewards = {}
for traj in trajectories.values():
    if traj:
        cluster_id = traj[0]['state'][0]
        total_reward = sum(t['reward'] for t in traj)
        if cluster_id not in cluster_rewards:
            cluster_rewards[cluster_id] = []
        cluster_rewards[cluster_id].append(total_reward)

print("\n   Average reward by cluster:")
for cluster_id in sorted(cluster_rewards.keys()):
    avg_reward = np.mean(cluster_rewards[cluster_id])
    print(f"     Cluster {cluster_id}: {avg_reward:+.2f}")

print("\n" + "="*80)
print("✅ DEMO COMPLETE!")
print("="*80)
print("\nKey Features Demonstrated:")
print("  ✓ Learned parameters từ real data")
print("  ✓ Learning curve (slow start → fast → plateau)")
print("  ✓ Score improvement qua attempts")
print("  ✓ Complete trajectory simulation")
print("  ✓ Batch processing")
print("\n🎯 Ready for Q-learning training!")
print("="*80 + "\n")
