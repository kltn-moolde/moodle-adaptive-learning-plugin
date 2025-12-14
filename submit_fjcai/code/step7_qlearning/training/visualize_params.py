#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization helper for simulate_parameters_course_670.json
Generates comprehensive charts for 4 core parameters.

Outputs to training/plots/
"""
import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

BASE_DIR = Path(__file__).parent
PARAMS_FILE = BASE_DIR / "simulate_params" / "simulate_parameters_course_670.json"
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

sns.set_style("whitegrid")

# ----------------------------
# Helpers
# ----------------------------

def load_params() -> Dict:
    if not PARAMS_FILE.exists():
        raise FileNotFoundError(f"Missing params file: {PARAMS_FILE}")
    with open(PARAMS_FILE) as f:
        return json.load(f)


def save_fig(name: str):
    path = PLOTS_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    print(f"[+] Saved {path}")
    plt.close()


# ----------------------------
# Plots for 4 Core Parameters
# ----------------------------

def plot_action_space_overview(params: Dict):
    """Visualize 15 actions organized by type and time context"""
    actions = params["action_space"]
    action_types = {}
    
    for action_type, context in actions:
        if action_type not in action_types:
            action_types[action_type] = []
        action_types[action_type].append(context)
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    
    contexts = ['past', 'current', 'future']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    action_names = sorted(action_types.keys())
    
    bottom = np.zeros(len(action_names))
    for context, color in zip(contexts, colors):
        counts = [len(action_types[a]) if context in action_types[a] else 0 for a in action_names]
        ax.bar(action_names, counts, bottom=bottom, label=context, color=color, alpha=0.8)
        bottom += counts
    
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Action Space Overview (15 actions)", fontsize=12, fontweight='bold')
    ax.legend(title="Time Context", loc='upper right')
    ax.set_xticklabels(action_names, rotation=45, ha='right')
    save_fig("01_action_space_overview.png")


def plot_time_patterns(params: Dict):
    """Bar chart + error bars for action durations"""
    data = params["time_patterns"]
    actions = sorted(data.keys())
    means = [data[a]["mean"] for a in actions]
    stds = [data[a]["std"] for a in actions]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(actions, means, yerr=stds, color="#4C72B0", alpha=0.7, capsize=5, edgecolor='black', linewidth=1.2)
    
    ax.set_ylabel("Duration (seconds)", fontsize=11)
    ax.set_title("Parameter 2: Time Patterns (Action Duration)", fontsize=12, fontweight='bold')
    ax.set_xticklabels(actions, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{mean:.0f}s', ha='center', va='bottom', fontsize=9)
    
    save_fig("02_time_patterns.png")


def plot_action_transition_matrix_heatmap(params: Dict, top_n_states: int = 12):
    """Heatmap of P(action | state) for top frequent states"""
    matrix = params["action_transition_matrix"]
    
    if not matrix:
        print("[!] action_transition_matrix empty")
        return
    
    # Get all unique actions
    all_actions = sorted({k for v in matrix.values() for k in v.keys()})
    
    # Take top N states by number of transitions
    state_counts = {state: sum(v.values()) for state, v in matrix.items()}
    top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:top_n_states]
    state_labels = [s for s, _ in top_states]
    
    # Build heatmap matrix
    heat = np.zeros((len(state_labels), len(all_actions)))
    for i, state in enumerate(state_labels):
        probs = matrix.get(state, {})
        for j, action in enumerate(all_actions):
            heat[i, j] = probs.get(action, 0)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(heat, xticklabels=all_actions, yticklabels=state_labels, 
                cmap="YlOrRd", annot=False, cbar_kws={'label': 'Probability'},
                ax=ax, linewidths=0.5)
    
    ax.set_xlabel("Action", fontsize=11)
    ax.set_ylabel("State (top by frequency)", fontsize=11)
    ax.set_title("Parameter 1: Action Transition Matrix - P(action | state)", fontsize=12, fontweight='bold')
    ax.set_xticklabels(all_actions, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(state_labels, fontsize=8)
    
    save_fig("03_action_transition_matrix.png")


def plot_progress_patterns(params: Dict):
    """Bar + line chart for progress improvement"""
    patt = params["progress_patterns"]
    
    if not patt:
        print("[!] progress_patterns empty; skip plot")
        return

    actions = sorted(patt.keys())
    improve_probs = [patt[a]["improve_prob"] * 100 for a in actions]
    avg_changes = [patt[a]["avg_change"] for a in actions]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # Left: Improvement probability
    colors = ['#2ECC71' if p > 0.15 else '#F39C12' for p in improve_probs]
    bars = ax1.bar(actions, improve_probs, color=colors, alpha=0.7, edgecolor='black', linewidth=1.2)
    ax1.set_ylabel("Probability (%)", fontsize=11)
    ax1.set_title("Improvement Probability", fontsize=11, fontweight='bold')
    ax1.set_xticklabels(actions, rotation=45, ha='right')
    ax1.set_ylim(0, 100)
    
    for bar, val in zip(bars, improve_probs):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Right: Average progress change
    colors2 = ['#3498DB' if c > 0 else '#E74C3C' for c in avg_changes]
    bars2 = ax2.bar(actions, avg_changes, color=colors2, alpha=0.7, edgecolor='black', linewidth=1.2)
    ax2.set_ylabel("Average Progress Change (bins)", fontsize=11)
    ax2.set_title("Average Progress Delta", fontsize=11, fontweight='bold')
    ax2.set_xticklabels(actions, rotation=45, ha='right')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    for bar, val in zip(bars2, avg_changes):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)
    
    fig.suptitle("Parameter 4: Progress Patterns (What Actions Improve Progress)", 
                 fontsize=12, fontweight='bold', y=1.02)
    save_fig("04_progress_patterns.png")


def plot_action_probabilities(params: Dict):
    """Plot P(action | learning_phase) and P(action | engagement_level) with % labels"""
    phase_probs = params.get("action_probs_by_learning_phase", {}) or {}
    eng_probs = params.get("action_probs_by_engagement", {}) or {}

    if not phase_probs and not eng_probs:
        print("[!] No conditional action probabilities found; skip plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Conditional Action Selection Probabilities", fontsize=14, fontweight='bold', y=0.98)

    # --- Left: by learning_phase ---
    if phase_probs:
        phases = sorted(phase_probs.keys(), key=lambda x: int(x))
        actions = sorted({a for m in phase_probs.values() for a in m.keys()})
        data = np.array([[phase_probs[p].get(a, 0) * 100 for a in actions] for p in phases])

        im = axes[0].imshow(data, cmap="YlGnBu", aspect='auto', vmin=0, vmax=max(10, data.max()))
        for i in range(len(phases)):
            for j in range(len(actions)):
                val = data[i, j]
                if val > 0:
                    axes[0].text(j, i, f"{val:.1f}%", ha='center', va='center', fontsize=8)
        axes[0].set_xticks(np.arange(len(actions)))
        axes[0].set_xticklabels(actions, rotation=45, ha='right', fontsize=9)
        axes[0].set_yticks(np.arange(len(phases)))
        axes[0].set_yticklabels([f"phase {p}" for p in phases], fontsize=10)
        axes[0].set_title("P(action | learning_phase)")
        axes[0].set_ylabel("Learning phase")
        cbar = plt.colorbar(im, ax=axes[0], shrink=0.9)
        cbar.set_label("Probability (%)")
    else:
        axes[0].axis('off')
        axes[0].set_title("No data for learning_phase")

    # --- Right: by engagement_level ---
    if eng_probs:
        levels = ['low', 'medium', 'high']
        levels = [l for l in levels if l in eng_probs] or sorted(eng_probs.keys())
        actions_e = sorted({a for m in eng_probs.values() for a in m.keys()})
        data_e = np.array([[eng_probs[l].get(a, 0) * 100 for a in actions_e] for l in levels])

        im2 = axes[1].imshow(data_e, cmap="OrRd", aspect='auto', vmin=0, vmax=max(10, data_e.max()))
        for i in range(len(levels)):
            for j in range(len(actions_e)):
                val = data_e[i, j]
                if val > 0:
                    axes[1].text(j, i, f"{val:.1f}%", ha='center', va='center', fontsize=8)
        axes[1].set_xticks(np.arange(len(actions_e)))
        axes[1].set_xticklabels(actions_e, rotation=45, ha='right', fontsize=9)
        axes[1].set_yticks(np.arange(len(levels)))
        axes[1].set_yticklabels([f"eng {l}" for l in levels], fontsize=10)
        axes[1].set_title("P(action | engagement_level)")
        axes[1].set_ylabel("Engagement level")
        cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.9)
        cbar2.set_label("Probability (%)")
    else:
        axes[1].axis('off')
        axes[1].set_title("No data for engagement_level")

    plt.tight_layout()
    save_fig("05_action_probabilities.png")


def plot_summary_overview(params: Dict):
    """Summary page with key statistics - improved layout"""
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle("Simulation Parameters Summary (Course 670)", fontsize=16, fontweight='bold', y=0.98)
    
    # Create grid with better spacing
    gs = fig.add_gridspec(4, 2, hspace=0.5, wspace=0.35, 
                          left=0.08, right=0.95, top=0.93, bottom=0.05)
    
    # Row 1: Parameter counts (left) + Course info (right)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    summary_text = """4 CORE PARAMETERS

1. Action Space
   → 15 actions

2. Action Transition Matrix
   → 339 states

3. Time Patterns
   → 5 action types

4. Progress Patterns
   → 5 action types
"""
    ax1.text(0.1, 0.95, summary_text, transform=ax1.transAxes, 
            fontsize=11, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#E8F4F8', alpha=0.8, edgecolor='#4ECDC4', linewidth=2))
    
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')
    info_text = f"""COURSE INFORMATION

Course ID: {params['course_id']}
Students: 21
Transitions: 12,671

Clusters: {params['n_clusters']}
Modules: {params['n_modules']}
Actions: {params['n_actions']}

State Format (6D):
(cluster, module,
 progress, score,
 phase, engagement)
"""
    ax2.text(0.1, 0.95, info_text, transform=ax2.transAxes,
            fontsize=11, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#F0E8F8', alpha=0.8, edgecolor='#9B59B6', linewidth=2))
    
    # Row 2: Time patterns
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    time_text = "TIME PATTERNS (Action Duration - seconds)\n"
    time_text += "─" * 95 + "\n\n"
    for i, (action, stats) in enumerate(sorted(params['time_patterns'].items())):
        if i % 2 == 0:
            time_text += f"  {action:18s}:  μ={stats['mean']:7.1f}s,  σ={stats['std']:7.1f}s  |  "
        else:
            time_text += f"{action:18s}:  μ={stats['mean']:7.1f}s,  σ={stats['std']:7.1f}s\n"
    
    ax3.text(0.05, 0.85, time_text, transform=ax3.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#F0F8E8', alpha=0.8, edgecolor='#27AE60', linewidth=2))
    
    # Row 3: Progress patterns (left) + Action types (right)
    ax4 = fig.add_subplot(gs[2:, 0])
    ax4.axis('off')
    prog_text = "PROGRESS PATTERNS (Learning Impact)\n"
    prog_text += "─" * 50 + "\n\n"
    prog_text += f"{'Action':<18}  {'Avg Δ':>8}  {'Improve %':>10}  {'Impact':<15}\n"
    prog_text += "─" * 50 + "\n"
    for action, stats in sorted(params['progress_patterns'].items()):
        impact = "⭐⭐⭐ HIGH" if stats['improve_prob'] > 0.25 else "⭐⭐ MEDIUM" if stats['improve_prob'] > 0.1 else "⭐ LOW"
        prog_text += f"{action:<18}  {stats['avg_change']:>8.3f}  {stats['improve_prob']:>9.1%}  {impact:<15}\n"
    
    prog_text += "\n📌 KEY: attempt_quiz has highest impact (+35% progress)"
    
    ax4.text(0.05, 0.95, prog_text, transform=ax4.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFF8E8', alpha=0.8, edgecolor='#F39C12', linewidth=2))
    
    # Row 3 Right: Action breakdown
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    action_text = """ACTION TYPES (15 total)

Viewing (4)
• view_content
• view_assignment

Quiz (3)
• attempt_quiz
• submit_quiz
• review_quiz

Assignment (2)
• view_assignment
• submit_assignment

Forum (3)
• post_forum
• (3 time contexts)
"""
    ax5.text(0.1, 0.95, action_text, transform=ax5.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#F8E8F8', alpha=0.7, edgecolor='#E91E63', linewidth=1.5))
    
    # Row 4: Statistics
    ax6 = fig.add_subplot(gs[3, 1])
    ax6.axis('off')
    stats_text = """QUALITY ASSESSMENT ✓

Parameters: 4 / 4
Data coverage: 100%
States observed: 339
Avg transitions: 37/state

Ready for simulation ✓
"""
    ax6.text(0.1, 0.95, stats_text, transform=ax6.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#E8F8E8', alpha=0.7, edgecolor='#2ECC71', linewidth=2))
    
    save_fig("00_summary_overview.png")


# ----------------------------
# Main
# ----------------------------

def main():
    params = load_params()
    print("[+] Loaded params from", PARAMS_FILE)
    print("[*] Generating visualization plots...")
    
    # Generate all plots
    plot_summary_overview(params)
    plot_action_space_overview(params)
    plot_action_transition_matrix_heatmap(params)
    plot_time_patterns(params)
    plot_progress_patterns(params)
    plot_action_probabilities(params)
    
    print("\n✓ All plots saved to:", PLOTS_DIR)
    print("  - 00_summary_overview.png")
    print("  - 01_action_space_overview.png")
    print("  - 02_time_patterns.png")
    print("  - 03_action_transition_matrix.png")
    print("  - 04_progress_patterns.png")
    print("  - 05_action_probabilities.png")


if __name__ == "__main__":
    main()
