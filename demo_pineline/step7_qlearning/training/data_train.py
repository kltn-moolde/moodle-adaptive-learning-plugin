#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Parameter Extraction - Tham số simulate gọn
================================================

Mục tiêu: lấy tham số mô phỏng từ log khóa 670, đơn giản nhưng bám dữ liệu:
- Map event → ActionSpace 17 actions (kèm time_context)
- Mỗi bài kiểm tra/nhiệm vụ là 1 module (lấy từ cột `other`: quizid/assignid/forumid...)
- State 5D: (cluster, module_idx, progress_bin, score_bin, learning_phase)
- Xuất JSON gọn: action_transition_matrix, time_patterns, state_distribution,
    progress_patterns, score_patterns, learning_phase_distribution
"""

import pandas as pd
import numpy as np
import json
import sys
import ast
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# ==========================================
# 0. CONFIG
# ==========================================
COURSE_ID = 670
# Path: training/data_train.py → ../data/
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "simulate_params"
OUTPUT_DIR.mkdir(exist_ok=True)

LOG_FILE = DATA_DIR / f"udk_moodle_log_course_{COURSE_ID}.csv"
GRADE_FILE = DATA_DIR / f"udk_moodle_grades_course_{COURSE_ID}.csv"

# ------------------------------------------
# Helper utilities
# ------------------------------------------
def assign_engagement_level(action_count: int, low_th: float, high_th: float) -> str:
    """Bucket user engagement by activity volume"""
    if action_count <= low_th:
        return "low"
    if action_count >= high_th:
        return "high"
    return "medium"


def action_probs_by_group(df: pd.DataFrame, group_col: str, action_col: str = 'action_type') -> Dict:
    """Compute P(action | group) as nested dict"""
    grouped = df.groupby([group_col, action_col]).size()
    totals = grouped.groupby(level=0).sum()
    result = defaultdict(dict)
    for (group, action), cnt in grouped.items():
        total = totals[group]
        if total > 0:
            result[group][action] = float(cnt / total)
    return result

# ==========================================
# 1. ActionSpace Mapping (17 actions)
# ==========================================
ACTION_SPACE_DEFINITION = [
    # Past (5)
    ("view_assignment", "past"),
    ("view_content", "past"),
    ("attempt_quiz", "past"),
    ("review_quiz", "past"),
    ("post_forum", "past"),
    # Current (7)
    ("view_assignment", "current"),
    ("view_content", "current"),
    ("submit_assignment", "current"),
    ("attempt_quiz", "current"),
    ("submit_quiz", "current"),
    ("review_quiz", "current"),
    ("post_forum", "current"),
    # Future (3)
    ("view_content", "future"),
    ("attempt_quiz", "future"),
    ("post_forum", "future"),
]

# Map log eventname → ActionSpace action_type
EVENT_TO_ACTION_MAPPING = {
    # view_content
    'course_module_viewed': 'view_content',
    'course_viewed': 'view_content',
    'resource_viewed': 'view_content',
    'wiki_page_viewed': 'view_content',
    'book_chapter_viewed': 'view_content',
    
    # view_assignment
    'assignment_viewed': 'view_assignment',
    'assign_viewed': 'view_assignment',
    
    # attempt_quiz
    'quiz_attempt_started': 'attempt_quiz',
    'quiz_preview_started': 'attempt_quiz',
    'quiz_attempt_submitted': 'submit_quiz',
    
    # review_quiz
    'quiz_attempt_reviewed': 'review_quiz',
    'quiz_attempt_viewed': 'review_quiz',
    
    # submit_assignment
    'assignment_submitted': 'submit_assignment',
    'submission_created': 'submit_assignment',
    'submission_updated': 'submit_assignment',
    
    # post_forum
    'post_created': 'post_forum',
    'post_updated': 'post_forum',
    'discussion_created': 'post_forum',
    'discussion_viewed': 'post_forum',
}

def map_event_to_action_type(eventname: str) -> Optional[str]:
    """Map Moodle event → action_type"""
    eventname_lower = eventname.lower() if eventname else ""
    
    # Direct mapping
    if eventname_lower in EVENT_TO_ACTION_MAPPING:
        return EVENT_TO_ACTION_MAPPING[eventname_lower]
    
    # Fallback: pattern matching
    if 'quiz' in eventname_lower:
        if 'attempt' in eventname_lower:
            return 'attempt_quiz'
        elif 'submit' in eventname_lower:
            return 'submit_quiz'
        elif 'review' in eventname_lower:
            return 'review_quiz'
        return 'attempt_quiz'
    
    if 'assign' in eventname_lower:
        if 'submit' in eventname_lower:
            return 'submit_assignment'
        return 'view_assignment'
    
    if 'forum' in eventname_lower or 'discussion' in eventname_lower:
        if 'created' in eventname_lower or 'updated' in eventname_lower:
            return 'post_forum'
        return 'post_forum'
    
    if 'view' in eventname_lower or 'viewed' in eventname_lower:
        return 'view_content'
    
    return None


def parse_other(other_val: str) -> Dict:
    """Parse the 'other' column (stringified dict) safely."""
    if not isinstance(other_val, str) or not other_val.strip():
        return {}
    try:
        return ast.literal_eval(other_val)
    except Exception:
        return {}


def extract_module_id(row) -> str:
    """Infer module id: mỗi quiz/assign/forum là một module riêng."""
    other = parse_other(row.get('other'))
    if 'quizid' in other:
        return f"quiz_{other['quizid']}"
    if 'assignid' in other:
        return f"assign_{other['assignid']}"
    if 'forumid' in other:
        return f"forum_{other['forumid']}"
    if 'discussionid' in other:
        return f"forum_disc_{other['discussionid']}"
    if 'choiceid' in other:
        return f"choice_{other['choiceid']}"
    if 'resourceid' in other:
        return f"res_{other['resourceid']}"

    ev = str(row.get('eventname', '')).lower()
    if 'quiz' in ev:
        return 'quiz_generic'
    if 'assign' in ev:
        return 'assign_generic'
    if 'forum' in ev or 'discussion' in ev:
        return 'forum_generic'
    return 'module_generic'

def infer_time_context(action_type: str, module_progress: float, score: float) -> str:
    """
    Infer time context (past, current, future) từ module_progress
    - past: progress < 0.25 (mới bắt đầu → chưa làm, nhưng xem lại cũ)
    - current: 0.25 <= progress < 0.85 (đang làm)
    - future: progress >= 0.85 (sắp xong → preview module tiếp theo)
    
    Cơ chế đơn giản: Dùng progress để infer
    """
    if module_progress < 0.25:
        return "past"  # Just started, can only review past
    elif module_progress >= 0.85:
        return "future"  # Almost done, looking ahead
    else:
        return "current"  # In the middle

# ==========================================
# 2. Load Data
# ==========================================
print(f"[*] Loading data from {LOG_FILE} and {GRADE_FILE}")

if not LOG_FILE.exists() or not GRADE_FILE.exists():
    print(f"[ERROR] Data files not found. Check paths:")
    print(f"  - LOG: {LOG_FILE}")
    print(f"  - GRADE: {GRADE_FILE}")
    sys.exit(1)

logs = pd.read_csv(LOG_FILE)
grades = pd.read_csv(GRADE_FILE)

print(f"[+] Loaded {len(logs)} logs, {len(grades)} grades")
print(f"[+] Unique users: {logs['userid'].nunique()}")

# ==========================================
# 3. Process Logs
# ==========================================
print("[*] Processing logs...")

# Standardize timestamp column (timecreated vs timestamp)
if 'timecreated' in logs.columns:
    logs['timestamp'] = pd.to_datetime(logs['timecreated']).astype('int64') // 10**9  # Convert to unix timestamp
elif 'timestamp' in logs.columns:
    logs['timestamp'] = pd.to_numeric(logs['timestamp'])
else:
    print("[ERROR] No timestamp column found. Available columns:")
    print(logs.columns.tolist())
    sys.exit(1)

logs = logs.sort_values(['userid', 'timestamp']).reset_index(drop=True)

# 3.1 Map action_type từ eventname
print("[*] Mapping log events to ActionSpace actions...")
logs['action_type'] = logs['eventname'].apply(map_event_to_action_type)

# Count unmapped
unmapped_count = logs['action_type'].isna().sum()
print(f"[+] Mapped {len(logs) - unmapped_count}/{len(logs)} events")
if unmapped_count > 0:
    print(f"    (Dropped {unmapped_count} unmapped events)")
    logs = logs.dropna(subset=['action_type'])

# 3.2a Compute user engagement level (low/medium/high) based on activity volume
user_action_counts = logs.groupby('userid').size()
if len(user_action_counts) >= 3:
    low_th, high_th = user_action_counts.quantile([0.33, 0.66])
else:
    # Fallback thresholds if too few users
    low_th = user_action_counts.min()
    high_th = user_action_counts.max()

engagement_map = {
    uid: assign_engagement_level(cnt, low_th, high_th)
    for uid, cnt in user_action_counts.items()
}
logs['engagement_level'] = logs['userid'].map(engagement_map)

# 3.2 Tính duration (thời gian giữa 2 actions)
logs['next_timestamp'] = logs.groupby('userid')['timestamp'].shift(-1)
logs['duration'] = logs['next_timestamp'] - logs['timestamp']
logs.loc[logs['duration'] > 3600, 'duration'] = 300  # Cap > 1h as 5min
logs['duration'] = logs['duration'].fillna(300)

# 3.3 Gán module context: mỗi bài kiểm tra/nhiệm vụ là một module
logs['module_id'] = logs.apply(extract_module_id, axis=1)

# 3.4 Tính module_progress (phần trăm log của user trong module)
logs['user_module_log_num'] = logs.groupby(['userid', 'module_id']).cumcount()
user_module_counts = logs.groupby(['userid', 'module_id']).size().reset_index(name='total')
logs = logs.merge(user_module_counts, on=['userid', 'module_id'], how='left')
logs['module_progress'] = logs['user_module_log_num'] / logs['total']

# 3.5 Gán score từ grades (sync by timestamp)
print("[*] Preparing grades data...")

# Standardize grade timestamp column
if 'timemodified' in grades.columns:
    grades['grade_timestamp'] = pd.to_datetime(grades['timemodified']).astype('int64') // 10**9
else:
    grades['grade_timestamp'] = pd.to_numeric(grades.get('timecreated', grades.get('time', 0)))

grades = grades.sort_values(['userid', 'grade_timestamp']).reset_index(drop=True)

# Compute user's final grade (use as proxy for expected/potential score)
user_final_grades = grades.groupby('userid')['finalgrade'].max().reset_index()
user_final_grades.columns = ['userid', 'final_score']

def normalize_score(score):
    """Normalize score to [0, 1] from 10-point scale"""
    if pd.isna(score) or score < 0:  # -1 means no grade
        return 0.0
    # Grades are on 10-point scale (0-10), normalize to [0, 1]
    return min(float(score) / 10.0, 1.0)

user_final_grades['final_score_norm'] = user_final_grades['final_score'].apply(normalize_score)

def get_score_at_time(userid: int, timestamp: float, grades_df: pd.DataFrame, user_scores: pd.DataFrame) -> float:
    """
    Get score progress at given timestamp.
    - If grades exist at/before timestamp: use actual grade (normalized)
    - Otherwise: use normalized user's final grade (potential)
    Returns normalized score [0.0, 1.0]
    """
    u_grades = grades_df[grades_df['userid'] == userid]
    if u_grades.empty:
        # No grade data - use user's final score as baseline
        user_final = user_scores[user_scores['userid'] == userid]
        return float(user_final['final_score_norm'].iloc[0]) if not user_final.empty else 0.0
    
    # Get grades up to this timestamp
    past_grades = u_grades[u_grades['grade_timestamp'] <= timestamp]
    if not past_grades.empty:
        # Use actual grade earned by this time
        latest_grade = past_grades.iloc[-1]['finalgrade']
        if pd.notna(latest_grade) and latest_grade >= 0:
            # Normalize from 10-point scale
            return min(float(latest_grade) / 10.0, 1.0)
    
    # No grade yet at this timestamp - use user's expected final score
    user_final = user_scores[user_scores['userid'] == userid]
    return float(user_final['final_score_norm'].iloc[0]) if not user_final.empty else 0.0

print("[*] Computing scores from grades...")
logs['score'] = logs.apply(
    lambda row: get_score_at_time(row['userid'], row['timestamp'], grades, user_final_grades),
    axis=1
)

# 3.6 Infer time_context (past/current/future) từ module_progress
logs['time_context'] = logs.apply(
    lambda x: infer_time_context(x['action_type'], x['module_progress'], x['score']),
    axis=1
)

# ==========================================
# 4. Compute 6D State Features
# ==========================================
print("[*] Computing 6D state features...")

# 4.1 Cluster assignment (simplify: dùng userid % 5 để simulate clusters 0-4)
# Assuming cluster_id không có trong log, tính pseudo cluster từ user behavior
def assign_pseudo_cluster(userid, avg_score, n_clusters=5):
    """Assign pseudo cluster based on user score pattern"""
    # Deterministic: same userid → same cluster
    cluster = userid % n_clusters
    return cluster

logs['cluster_id'] = logs.apply(
    lambda x: assign_pseudo_cluster(x['userid'], x['score']),
    axis=1
)

# 4.2 Learning phase (dựa trên action_type frequency)
PHASE_MAP = {
    'view_content': 0,  # pre_learning
    'view_assignment': 0,  # pre_learning
    'attempt_quiz': 1,  # active_learning
    'submit_quiz': 1,  # active_learning
    'submit_assignment': 1,  # active_learning
    'review_quiz': 2,  # reflective_learning
    'post_forum': 2,  # reflective_learning
}

logs['learning_phase'] = logs['action_type'].map(PHASE_MAP).fillna(0).astype(int)

# 4.3 Progress & Score bins (quartiles)
logs['progress_bin'] = pd.cut(
    logs['module_progress'],
    bins=[0, 0.25, 0.5, 0.75, 1.0],
    labels=[0, 1, 2, 3],
    include_lowest=True
).astype(int)

# Score bins with handling for missing scores
logs['score_bin'] = pd.cut(
    logs['score'],
    bins=[-0.01, 0.25, 0.5, 0.75, 1.0],
    labels=[0, 1, 2, 3],
    include_lowest=True
)
logs['score_bin'] = logs['score_bin'].fillna(0).astype(int)  # Default to 0 if no score yet

# 4.4 Module index (normalized module_id)
module_ids = sorted(logs['module_id'].unique())
module_to_idx = {mid: i for i, mid in enumerate(module_ids)}
logs['module_idx'] = logs['module_id'].map(module_to_idx)

print(f"[+] Computed states:")
print(f"    - Clusters: {sorted(logs['cluster_id'].unique())}")
print(f"    - Modules: {sorted(logs['module_idx'].unique())}")
print(f"    - Progress bins: {sorted(logs['progress_bin'].unique())}")
print(f"    - Score bins: {sorted(logs['score_bin'].unique())}")
print(f"    - Learning phases: {sorted(logs['learning_phase'].unique())}")

# ==========================================
# 5. Build State Transition Data
# ==========================================
print("[*] Building state transition sequences...")

state_transitions = defaultdict(list)  # user_id → list of (state, action, next_state)

for userid, user_logs in logs.groupby('userid'):
    user_logs = user_logs.sort_values('timestamp').reset_index(drop=True)
    
    if len(user_logs) < 2:
        continue
    
    for i in range(len(user_logs) - 1):
        current_row = user_logs.iloc[i]
        next_row = user_logs.iloc[i + 1]
        
        # Current state (5D)
        state = (
            int(current_row['cluster_id']),
            int(current_row['module_idx']),
            int(current_row['progress_bin']),
            int(current_row['score_bin']),
            int(current_row['learning_phase'])
        )
        
        # Action taken (action_type, time_context)
        action = (current_row['action_type'], current_row['time_context'])
        
        # Next state
        next_state = (
            int(next_row['cluster_id']),
            int(next_row['module_idx']),
            int(next_row['progress_bin']),
            int(next_row['score_bin']),
            int(next_row['learning_phase'])
        )
        
        state_transitions[userid].append({
            'state': state,
            'action': action,
            'next_state': next_state,
            'duration': float(current_row['duration'])
        })

print(f"[+] Built {sum(len(v) for v in state_transitions.values())} transitions from {len(state_transitions)} users")

# ==========================================
# 6. Extract Simulation Parameters
# ==========================================
print("[*] Extracting simulation parameters...")

params = {
    'course_id': COURSE_ID,
    'n_clusters': 5,
    'n_modules': len(module_ids),
    'n_actions': len(ACTION_SPACE_DEFINITION),
    'action_space': ACTION_SPACE_DEFINITION,
    
    # Essential parameters for simulation (4 core parameters)
    # 1. Action transition probabilities: P(action | state)
    'action_transition_matrix': {},
    
    # 2. Time patterns: duration stats per action_type
    'time_patterns': {},
    
    # 3. Progress patterns: how progress changes per action
    'progress_patterns': {},

    # 4. Conditional action probabilities for simulation priors
    'action_probs_by_learning_phase': {},
    'action_probs_by_engagement': {},
}

# Count action transitions per (state, action)
action_transition_counts = defaultdict(lambda: defaultdict(int))
state_counts = defaultdict(int)

for userid, transitions in state_transitions.items():
    for trans in transitions:
        state = trans['state']
        action = trans['action']
        
        # Convert to string for JSON serialization
        state_key = str(state)  # "(cluster, module, progress, score, phase)"
        action_key = str(action)  # "(action_type, time_context)"
        
        action_transition_counts[state_key][action_key] += 1
        state_counts[state_key] += 1

# Convert counts to probabilities
for state_key, action_counts_dict in action_transition_counts.items():
    total = state_counts[state_key]
    action_probs = {}
    for action_key_str, count in action_counts_dict.items():
        # action_key_str is like "('view_content', 'current')"
        # Convert to readable format like "view_content_current"
        try:
            action_type, context = eval(action_key_str)
            action_str = f"{action_type}_{context}"
        except:
            action_str = action_key_str
        
        action_probs[action_str] = count / total
    
    params['action_transition_matrix'][state_key] = action_probs

# 6.2 Time patterns
time_stats = logs.groupby('action_type')['duration'].agg(['mean', 'std', 'min', 'max'])
for action_type in logs['action_type'].unique():
    row = time_stats.loc[action_type]
    params['time_patterns'][action_type] = {
        'mean': float(row['mean']),
        'std': float(row['std']),
        'min': float(row['min']),
        'max': float(row['max'])
    }

# 6.3 Progress change per action
progress_changes = defaultdict(list)
for userid, transitions in state_transitions.items():
    for trans in transitions:
        action_type = trans['action'][0]
        progress_change = trans['next_state'][2] - trans['state'][2]  # progress_bin diff
        progress_changes[action_type].append(progress_change)

for action_type, changes in progress_changes.items():
    if changes:
        params['progress_patterns'][action_type] = {
            'avg_change': float(np.mean(changes)),
            'std_change': float(np.std(changes)),
            'improve_prob': float(sum(1 for c in changes if c > 0) / len(changes))
        }

# 6.4 Conditional action probabilities for simulation priors
params['action_probs_by_learning_phase'] = action_probs_by_group(logs, 'learning_phase')
params['action_probs_by_engagement'] = action_probs_by_group(logs, 'engagement_level')

# ==========================================
# 7. Output Results
# ==========================================
output_file = OUTPUT_DIR / f'simulate_parameters_course_{COURSE_ID}.json'
print(f"\n[*] Writing parameters to {output_file}...")

# Custom function to convert all numpy types to native Python types
def convert_types(obj):
    """Recursively convert numpy types to Python types"""
    if isinstance(obj, dict):
        return {convert_types(k): convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# Convert all parameters to native Python types
params = convert_types(params)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(params, f, indent=2)

print(f"[+] Done! Wrote {output_file}")

# Print summary
print("\n" + "="*70)
print("SIMULATION PARAMETERS (CORE 4)")
print("="*70)
print(f"\nCourse {COURSE_ID}:")
print(f"  - Total users: {len(state_transitions)}")
print(f"  - Total transitions: {sum(len(v) for v in state_transitions.values())}")
print(f"  - Clusters: {params['n_clusters']}")
print(f"  - Modules: {params['n_modules']}")
print(f"  - Actions: {params['n_actions']}")

print(f"\n✓ Essential Parameters:")
print(f"  1. action_space: {params['n_actions']} actions")
print(f"  2. action_transition_matrix: {len(params['action_transition_matrix'])} states")
print(f"  3. time_patterns: {len(params['time_patterns'])} action types")
print(f"  4. progress_patterns: {len(params['progress_patterns'])} action types")
print(f"  5. action_probs_by_learning_phase: {len(params['action_probs_by_learning_phase'])} phases")
print(f"  6. action_probs_by_engagement: {len(params['action_probs_by_engagement'])} levels")

print(f"\nTime Patterns (mean duration):") 
for action_type, stats in sorted(params['time_patterns'].items()):
    print(f"  - {action_type:20s}: {stats['mean']:6.1f}s (±{stats['std']:5.1f})")

print(f"\nProgress Patterns (improvement per action):")
for action_type, stats in sorted(params['progress_patterns'].items()):
    print(f"  - {action_type:20s}: avg_change={stats['avg_change']:6.3f}, improve_prob={stats['improve_prob']:5.1%}")

print("\n" + "="*70)
print(f"✓ Parameters saved to: {output_file}")
print("="*70)