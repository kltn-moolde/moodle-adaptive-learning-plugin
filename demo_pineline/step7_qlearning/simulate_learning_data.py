#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulate Learning Data
=======================
Generate simulated learning data for Q-learning training

Can operate in two modes:
1. Random generation (default): Generate N random students
2. CSV mode: Load synthetic students from pipeline CSV with cluster_id
"""

import os
import argparse
from datetime import datetime
import json
import shutil
import html
import numpy as np
import csv
from typing import List, Dict, Optional

from core.state_builder import MoodleStateBuilder
from core.action_space import ActionSpace
from core.reward_calculator import RewardCalculator
from core.simulator import LearningSimulator


def load_synthetic_students_from_csv(csv_path: str) -> List[Dict]:
    """
    Load synthetic students from pipeline CSV
    
    Returns:
        List of student dicts with features and cluster_id
    """
    students = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric values
            student = {}
            for key, val in row.items():
                try:
                    # Try to convert to float
                    student[key] = float(val)
                except (ValueError, TypeError):
                    # Keep as string if conversion fails
                    student[key] = val
            
            students.append(student)
    
    return students


def simulate_learning_data(
    n_students: int = 100,
    n_actions_per_student: int = 30,
    output_dir: str = 'data/simulated',
    source_csv: Optional[str] = None
):
    """
    Main function to generate simulated learning data
    
    Args:
        n_students: Number of students to simulate (ignored if source_csv provided)
        n_actions_per_student: Number of actions per student
        output_dir: Output directory for simulated data
        source_csv: Path to CSV with synthetic students (from pipeline)
    """
    print("=" * 70)
    print("SIMULATE LEARNING DATA")
    print("=" * 70)
    
    # Setup paths
    data_dir = 'data'
    course_structure_path = os.path.join(data_dir, 'course_structure.json')
    cluster_profiles_path = os.path.join(data_dir, 'cluster_profiles.json')
    
    # Initialize components
    print("\n[1/5] Initializing components...")
    state_builder = MoodleStateBuilder()
    action_space = ActionSpace(course_structure_path)
    reward_calculator = RewardCalculator(cluster_profiles_path)
    simulator = LearningSimulator(state_builder, action_space, reward_calculator)
    
    print(f"  ✓ Action space: {action_space.get_action_count()} actions")
    print(f"  ✓ Clusters: {reward_calculator.get_cluster_count()}")
    
    # Load students from CSV or generate random
    if source_csv and os.path.exists(source_csv):
        print(f"\n[2/5] Loading students from CSV: {source_csv}")
        synthetic_students = load_synthetic_students_from_csv(source_csv)
        print(f"  ✓ Loaded {len(synthetic_students)} synthetic students from pipeline")
        
        # Show cluster distribution
        cluster_counts = {}
        for student in synthetic_students:
            cluster_id = int(student.get('cluster', 0))
            cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1
        
        print(f"  Cluster distribution:")
        for cid in sorted(cluster_counts.keys()):
            count = cluster_counts[cid]
            pct = count / len(synthetic_students) * 100
            print(f"    Cluster {cid}: {count:3d} ({pct:5.1f}%)")
        
        # Simulate using synthetic students with known clusters
        print(f"\n[3/5] Simulating learning interactions...")
        interactions = []
        
        for student in synthetic_students:
            student_id = int(student.get('userid', 0))
            cluster_id = int(student.get('cluster', 0))
            
            # Build initial state from student features
            # Use the features that state_builder expects
            
            # ✅ ADD DIVERSE FEATURES: submitted and comment (not always 0)
            # Generate based on student performance to create realistic diversity
            mean_grade = student.get('mean_module_grade', 0.5)
            
            # Higher performing students tend to submit more
            submitted_activity = np.clip(
                np.random.normal(mean_grade * 0.7, 0.2), 0.0, 1.0
            )
            
            # Collaborative activity varies by student engagement
            engagement_proxy = student.get('started', 0.5)
            collaborative_activity = np.clip(
                np.random.normal(engagement_proxy * 0.5, 0.25), 0.0, 1.0
            )
            
            features = {
                'mean_module_grade': student.get('mean_module_grade', 0.5),
                'total_events': student.get('started', 0.5),  # Use 'started' as proxy for events
                'viewed': student.get('viewed', 0.5),
                'attempt': student.get('attempt_summary', 0.0),
                'feedback_viewed': student.get('submission_status', 0.0),
                'module_count': student.get('module_count', 0.5),
                'course_module_completion': student.get('course', 0.5),
                
                # ✅ NEW: Add submission and collaborative activities
                'submitted': float(submitted_activity),
                'assessable_submitted': float(submitted_activity * 0.8),  # Related to submitted
                'comment': float(collaborative_activity),
                '\\mod_forum\\event\\course_module_viewed': float(collaborative_activity * 0.6)
            }
            initial_state = state_builder.build_state(features)
            
            # Simulate actions for this student
            student_interactions = simulator.simulate_student_learning(
                student_id=student_id,
                cluster_id=cluster_id,
                initial_state=initial_state,
                n_actions=n_actions_per_student
            )
            interactions.extend(student_interactions)
        
        print(f"  ✓ Generated {len(interactions)} interactions from {len(synthetic_students)} students")
    else:
        if source_csv:
            print(f"\n[2/5] WARNING: CSV not found: {source_csv}")
            print(f"  Falling back to random generation")
        else:
            print(f"\n[2/5] Using random student generation")
        
        # Original random simulation
        print(f"\n[3/5] Simulating {n_students} random students...")
        interactions = simulator.simulate_batch(
            n_students=n_students,
            n_actions_per_student=n_actions_per_student
        )
    
    print(f"  ✓ Generated {len(interactions)} interactions")
    
    # Get statistics
    print("\n[4/5] Calculating statistics...")
    stats = simulator.get_simulation_stats(interactions)
    
    print(f"\nSimulation Statistics:")
    print(f"  Total interactions: {stats['total_interactions']}")
    print(f"  Unique students: {stats['unique_students']}")
    print(f"  Avg score: {stats['avg_score']:.2f}")
    print(f"  Completion rate: {stats['completion_rate']:.2%}")
    print(f"  Avg attempts: {stats['avg_attempts']:.2f}")
    print(f"  Avg time spent: {stats['avg_time_spent']:.1f} min")
    print(f"  Avg reward: {stats['avg_reward']:.2f}")
    
    print(f"\n  Cluster distribution:")
    for cid, count in stats['cluster_distribution'].items():
        pct = count / stats['total_interactions'] * 100
        print(f"    Cluster {cid}: {count:4d} ({pct:5.1f}%)")
    
    # Save data
    print(f"\n[5/5] Saving data...")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(
        output_dir,
        f'simulated_data_{timestamp}.json'
    )
    
    simulator.save_simulated_data(interactions, output_file)
    print(f"  ✓ Saved to: {output_file}")
    
    # Save latest
    latest_file = os.path.join(output_dir, 'latest_simulation.json')
    simulator.save_simulated_data(interactions, latest_file)
    print(f"  ✓ Saved latest: {latest_file}")

    # Also save a full JSON with numpy-safe conversion and generate HTML report
    print(f"\n[6/6] Generating HTML report and full JSON...")
    
    def _make_json_serializable(obj):
        import numpy as _np
        if isinstance(obj, (_np.integer,)):
            return int(obj)
        if isinstance(obj, (_np.floating,)):
            return float(obj)
        if isinstance(obj, (_np.bool_,)):
            return bool(obj)
        if isinstance(obj, _np.ndarray):
            return obj.tolist()
        if isinstance(obj, (list, tuple)):
            return [_make_json_serializable(v) for v in obj]
        if isinstance(obj, dict):
            return {str(k): _make_json_serializable(v) for k, v in obj.items()}
        if hasattr(obj, '__dict__'):
            return _make_json_serializable(obj.__dict__)
        return obj

    full_out = os.path.join(output_dir, 'simulation_full.json')
    raw = [i.__dict__ for i in interactions]
    data = [_make_json_serializable(item) for item in raw]
    with open(full_out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Saved full JSON: {full_out}")

    # HTML report
    report_path = os.path.join(output_dir, 'simulation_report.html')
    by_student = {}
    for it in interactions:
        by_student.setdefault(it.student_id, []).append(it)

    parts = []
    parts.append('<!doctype html>')
    parts.append('<html><head><meta charset="utf-8"><title>Simulation report</title>')
    parts.append('<style>body{font-family:Arial,Helvetica,sans-serif;padding:16px} .student{margin-bottom:20px;border:1px solid #ddd;padding:8px;border-radius:6px} .header{display:flex;justify-content:space-between;align-items:center} table{width:100%;border-collapse:collapse;margin-top:8px} th,td{border:1px solid #eee;padding:6px;text-align:left;font-size:13px} th{background:#f7f7f7} .toggle{background:#007bff;color:#fff;padding:6px 10px;border-radius:4px;border:none;cursor:pointer} .jsonbox{white-space:pre-wrap;background:#fafafa;border:1px solid #eee;padding:8px;margin-top:8px;display:none}</style>')
    parts.append('<script>function toggle(id){var e=document.getElementById(id);e.style.display=(e.style.display=="none")?"block":"none"}</script>')
    parts.append('</head><body>')
    parts.append(f'<h1>Simulation report</h1>')
    parts.append(f'<p>Total interactions: {len(interactions)} | Students: {len(by_student)}</p>')
    parts.append(f'<p>Download full JSON: <a href="{os.path.basename(full_out)}">{os.path.basename(full_out)}</a></p>')

    for sid, seq in sorted(by_student.items()):
        avg_score = np.mean([s.score for s in seq]) if seq else 0
        avg_reward = np.mean([s.reward for s in seq]) if seq else 0
        cluster = seq[0].cluster_id if seq else ''
        parts.append(f'<div class="student"><div class="header"><strong>Student {sid} (cluster {cluster})</strong>')
        parts.append(f'<div>Interactions: {len(seq)} | avg_score: {avg_score:.2f} | avg_reward: {avg_reward:.2f}</div></div>')
        parts.append('<table><thead><tr><th>#</th><th>timestamp</th><th>action</th><th>type</th><th>completed</th><th>score</th><th>attempts</th><th>time_min</th><th>reward</th><th>state_before</th><th>state_after</th></tr></thead><tbody>')
        for i, it in enumerate(seq):
            sbefore = html.escape(json.dumps(_make_json_serializable(it.state_before), ensure_ascii=False))
            safter = html.escape(json.dumps(_make_json_serializable(it.state_after), ensure_ascii=False))
            parts.append('<tr>')
            parts.append(f'<td>{i+1}</td>')
            parts.append(f'<td>{it.timestamp}</td>')
            parts.append(f'<td>{html.escape(str(it.action_name))}</td>')
            parts.append(f'<td>{html.escape(str(it.action_type))}</td>')
            parts.append(f'<td>{str(it.completed)}</td>')
            parts.append(f'<td>{it.score:.3f}</td>')
            parts.append(f'<td>{it.attempts}</td>')
            parts.append(f'<td>{it.time_spent}</td>')
            parts.append(f'<td>{it.reward:.3f}</td>')
            parts.append(f"<td><button class='toggle' onclick=\"toggle('sb-{sid}-{i}')\">view</button><div id='sb-{sid}-{i}' class='jsonbox'>{sbefore}</div></td>")
            parts.append(f"<td><button class='toggle' onclick=\"toggle('sa-{sid}-{i}')\">view</button><div id='sa-{sid}-{i}' class='jsonbox'>{safter}</div></td>")
            parts.append('</tr>')
        parts.append('</tbody></table></div>')

    parts.append('</body></html>')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))
    print(f"  ✓ Saved HTML report: {report_path}")
    
    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETE")
    print("=" * 70)
    
    return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate simulated learning data'
    )
    parser.add_argument(
        '--n-students',
        type=int,
        default=100,
        help='Number of students to simulate (default: 100)'
    )
    parser.add_argument(
        '--n-actions',
        type=int,
        default=30,
        help='Number of actions per student (default: 30)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/simulated',
        help='Output directory (default: data/simulated)'
    )
    parser.add_argument(
        '--source-csv',
        type=str,
        default=None,
        help='Path to synthetic students CSV from pipeline (e.g., data/synthetic_students_gmm.csv)'
    )
    
    args = parser.parse_args()
    
    simulate_learning_data(
        n_students=args.n_students,
        n_actions_per_student=args.n_actions,
        output_dir=args.output_dir,
        source_csv=args.source_csv
    )
