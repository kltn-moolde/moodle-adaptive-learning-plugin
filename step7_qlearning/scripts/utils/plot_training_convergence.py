#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Training Convergence Visualizer
================================
Visualize Q-Learning convergence: reward progression, epsilon decay, Q-table growth
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.rl.agent import QLearningAgentV2
from core.rl.action_space import ActionSpace


class ConvergenceVisualizer:
    """
    Visualize Q-Learning training convergence metrics
    """
    
    def __init__(
        self,
        qtable_path: Optional[str] = None,
        course_id: int = 5,
        output_dir: str = 'plots/convergence'
    ):
        """
        Initialize convergence visualizer
        
        Args:
            qtable_path: Path to trained Q-table
            course_id: Course ID
            output_dir: Directory to save plots
        """
        self.qtable_path = qtable_path
        self.course_id = course_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load agent
        self.action_space = ActionSpace()
        self.agent = QLearningAgentV2(n_actions=self.action_space.get_action_count())
        
        if qtable_path and Path(qtable_path).exists():
            self.agent.load(qtable_path)
            print(f"✓ Loaded Q-table from {qtable_path}")
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 10
        
        print(f"✓ ConvergenceVisualizer initialized")
        print(f"  Output directory: {self.output_dir}")
    
    def plot_reward_convergence(
        self,
        episode_rewards: List[float],
        save: bool = True,
        window: int = 10
    ):
        """
        Plot reward progression and convergence
        
        Args:
            episode_rewards: List of average rewards per episode
            save: Save plot to file
            window: Window size for moving average
        """
        print(f"\n📊 Plotting reward convergence ({len(episode_rewards)} episodes)...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Reward Convergence Analysis', fontsize=16, fontweight='bold')
        
        episodes = np.arange(len(episode_rewards))
        
        # 1. Full reward progression
        ax1 = axes[0, 0]
        ax1.plot(episodes, episode_rewards, 'b-', alpha=0.3, linewidth=1, label='Raw rewards')
        
        # Moving average
        if len(episode_rewards) >= window:
            ma = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')
            ax1.plot(range(window-1, len(episode_rewards)), ma, 'r-', linewidth=2.5, 
                    label=f'MA({window})')
        
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Average Reward')
        ax1.set_title('Reward Progression (Raw + Moving Average)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Convergence detection (last 50 episodes)
        ax2 = axes[0, 1]
        recent_episodes = episodes[-50:] if len(episodes) > 50 else episodes
        recent_rewards = episode_rewards[-50:] if len(episode_rewards) > 50 else episode_rewards
        
        ax2.plot(recent_episodes, recent_rewards, 'g-', linewidth=2, marker='o', markersize=4)
        
        # Fit trend line
        if len(recent_episodes) > 2:
            z = np.polyfit(range(len(recent_rewards)), recent_rewards, 1)
            p = np.poly1d(z)
            ax2.plot(range(len(recent_rewards)), p(range(len(recent_rewards))), "r--", 
                    linewidth=2, alpha=0.8, label=f'Trend (slope={z[0]:.4f})')
        
        ax2.set_xlabel('Episode (last 50)')
        ax2.set_ylabel('Average Reward')
        ax2.set_title('Recent Reward Trend (Convergence Check)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Reward improvement rate
        ax3 = axes[1, 0]
        improvement = np.diff(episode_rewards)
        ax3.bar(episodes[:-1], improvement, color=['green' if x > 0 else 'red' for x in improvement], 
               alpha=0.6, edgecolor='black', linewidth=0.5)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Reward Change (Δ)')
        ax3.set_title('Episode-to-Episode Reward Improvement')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Convergence statistics
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        # Calculate convergence metrics
        best_reward = max(episode_rewards)
        best_episode = np.argmax(episode_rewards) + 1
        final_reward = episode_rewards[-1]
        
        # Moving average of recent episodes
        recent_ma = np.mean(episode_rewards[-20:]) if len(episode_rewards) >= 20 else np.mean(episode_rewards)
        
        # Convergence indicator: variance in last 20 episodes
        recent_var = np.var(episode_rewards[-20:]) if len(episode_rewards) >= 20 else np.var(episode_rewards)
        convergence_score = 1.0 - min(recent_var / max(np.var(episode_rewards), 0.01), 1.0)
        
        # Improvement rate
        early_avg = np.mean(episode_rewards[:10]) if len(episode_rewards) >= 10 else episode_rewards[0]
        improvement_rate = ((recent_ma - early_avg) / (early_avg + 1e-6)) * 100
        
        stats_text = f"""
CONVERGENCE STATISTICS
{'='*50}

Total Episodes:        {len(episode_rewards)}
Best Reward:           {best_reward:.2f} (episode {best_episode})
Final Reward:          {final_reward:.2f}
Recent MA (20 eps):    {recent_ma:.2f}

Improvement:
  Early avg (1-10):    {early_avg:.2f}
  Improvement rate:    {improvement_rate:+.1f}%
  
Convergence:
  Recent variance:     {recent_var:.4f}
  Convergence score:   {convergence_score:.2%}
  
Trend:
  Last 10 eps change:  {episode_rewards[-1] - np.mean(episode_rewards[-11:-1]):+.2f}
  Last 5 eps change:   {episode_rewards[-1] - np.mean(episode_rewards[-6:-1]):+.2f}
        """
        
        ax4.text(0.1, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'reward_convergence.png'
            filename_pdf = self.output_dir / 'reward_convergence.pdf'
            plt.savefig(filename_png, dpi=150, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.show()
        
        return {
            'best_reward': best_reward,
            'best_episode': best_episode,
            'final_reward': final_reward,
            'convergence_score': convergence_score,
            'improvement_rate': improvement_rate
        }
    
    def plot_epsilon_decay(
        self,
        epsilon_history: List[float],
        save: bool = True
    ):
        """
        Plot epsilon decay schedule
        
        Args:
            epsilon_history: List of epsilon values per episode
            save: Save plot
        """
        print(f"\n📊 Plotting epsilon decay ({len(epsilon_history)} episodes)...")
        
        episodes = np.arange(len(epsilon_history))
        
        # Linear scale (single plot for paper)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(episodes, epsilon_history, 'b-', linewidth=2)
        ax.fill_between(episodes, 0, epsilon_history, alpha=0.3)
        
        # Mark important thresholds
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='ε=0.5 (50% explore)')
        ax.axhline(y=0.1, color='red', linestyle='--', alpha=0.5, label='ε=0.1 (10% explore)')
        ax.axhline(y=0.01, color='darkred', linestyle='--', alpha=0.5, label='ε=0.01 (1% explore)')
        
        ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
        ax.set_ylabel('Epsilon (ε)', fontsize=12, fontweight='bold')
        ax.set_ylim([-0.05, 1.05])
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'epsilon_decay_linear.png'
            filename_pdf = self.output_dir / 'epsilon_decay_linear.pdf'
            plt.savefig(filename_png, dpi=300, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.close()
        
        # Log scale (separate plot for paper)
        fig, ax = plt.subplots(figsize=(10, 6))
        epsilon_safe = [max(e, 0.001) for e in epsilon_history]
        ax.semilogy(episodes, epsilon_safe, 'g-', linewidth=2)
        
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='ε=0.5')
        ax.axhline(y=0.1, color='red', linestyle='--', alpha=0.5, label='ε=0.1')
        ax.axhline(y=0.01, color='darkred', linestyle='--', alpha=0.5, label='ε=0.01')
        
        ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
        ax.set_ylabel('Epsilon (ε, log scale)', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, which='both')
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'epsilon_decay_log.png'
            filename_pdf = self.output_dir / 'epsilon_decay_log.pdf'
            plt.savefig(filename_png, dpi=300, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.close()
    
    def plot_qtable_growth(
        self,
        q_table_size_history: List[int],
        total_updates_history: List[int],
        save: bool = True
    ):
        """
        Plot Q-table size growth and update counts
        
        Args:
            q_table_size_history: List of Q-table state counts per episode
            total_updates_history: List of cumulative updates per episode
            save: Save plot
        """
        print(f"\n📊 Plotting Q-table growth ({len(q_table_size_history)} episodes)...")
        
        episodes = np.arange(len(q_table_size_history))
        
        # Q-table size progression (single clean plot for paper)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(episodes, q_table_size_history, 'b-', linewidth=2, marker='o', markersize=3)
        ax.fill_between(episodes, 0, q_table_size_history, alpha=0.3)
        ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of States in Q-table', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add annotation for final size
        final_size = q_table_size_history[-1]
        ax.text(len(episodes)-1, final_size, f'  {final_size} states', 
                verticalalignment='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'qtable_growth_states.png'
            filename_pdf = self.output_dir / 'qtable_growth_states.pdf'
            plt.savefig(filename_png, dpi=300, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.close()
        
        # Q-table growth rate (separate plot)
        fig, ax = plt.subplots(figsize=(10, 6))
        if len(q_table_size_history) > 1:
            growth_rate = np.diff(q_table_size_history)
            growth_rate = np.insert(growth_rate, 0, q_table_size_history[0])
        else:
            growth_rate = np.array(q_table_size_history)
        
        colors = ['green' if x > 0 else 'gray' for x in growth_rate]
        ax.bar(episodes, growth_rate, color=colors, alpha=0.6, edgecolor='black', linewidth=0.5)
        ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
        ax.set_ylabel('New States per Episode', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'qtable_growth_rate.png'
            filename_pdf = self.output_dir / 'qtable_growth_rate.pdf'
            plt.savefig(filename_png, dpi=300, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.close()
        
        # Cumulative updates (separate plot)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(episodes, total_updates_history, 'r-', linewidth=2)
        ax.fill_between(episodes, 0, total_updates_history, alpha=0.3, color='red')
        ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Q-Table Updates', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'qtable_cumulative_updates.png'
            filename_pdf = self.output_dir / 'qtable_cumulative_updates.pdf'
            plt.savefig(filename_png, dpi=300, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.close()
    
    def plot_combined_convergence(
        self,
        episode_rewards: List[float],
        epsilon_history: List[float],
        q_table_size_history: List[int],
        save: bool = True
    ):
        """
        Plot all convergence metrics on one figure
        
        Args:
            episode_rewards: List of average rewards per episode
            epsilon_history: List of epsilon values
            q_table_size_history: List of Q-table sizes
            save: Save plot
        """
        print(f"\n📊 Plotting combined convergence metrics...")
        
        fig = plt.figure(figsize=(18, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        fig.suptitle('Complete Q-Learning Training Convergence Analysis', 
                    fontsize=18, fontweight='bold')
        
        episodes = np.arange(len(episode_rewards))
        
        # 1. Reward (large)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(episodes, episode_rewards, 'b-', alpha=0.3, linewidth=1)
        window = 10
        if len(episode_rewards) >= window:
            ma = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')
            ax1.plot(range(window-1, len(episode_rewards)), ma, 'r-', linewidth=2.5, label=f'MA({window})')
        ax1.set_ylabel('Avg Reward', fontweight='bold')
        ax1.set_title('Reward Progression', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Convergence status
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        best_reward = max(episode_rewards)
        best_ep = np.argmax(episode_rewards) + 1
        final_reward = episode_rewards[-1]
        status = "✓ CONVERGED" if abs(final_reward - best_reward) < best_reward * 0.05 else "⟳ CONVERGING"
        ax2.text(0.5, 0.5, status, ha='center', va='center', fontsize=20, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen' if '✓' in status else 'lightyellow', 
                         alpha=0.7))
        ax2.text(0.5, 0.2, f'Best: {best_reward:.1f}\n(ep {best_ep})', ha='center', va='center', 
                fontsize=11, family='monospace')
        
        # 3. Epsilon
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(episodes, epsilon_history, 'g-', linewidth=2)
        ax3.fill_between(episodes, 0, epsilon_history, alpha=0.3, color='green')
        ax3.set_ylabel('Epsilon (ε)', fontweight='bold')
        ax3.set_title('Exploration Decay', fontweight='bold')
        ax3.set_ylim([-0.05, 1.05])
        ax3.grid(True, alpha=0.3)
        
        # 4. Q-table size
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(episodes, q_table_size_history, 'purple', linewidth=2, marker='.')
        ax4.fill_between(episodes, 0, q_table_size_history, alpha=0.3, color='purple')
        ax4.set_ylabel('Q-Table States', fontweight='bold')
        ax4.set_title('State Space Discovery', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. Recent convergence
        ax5 = fig.add_subplot(gs[1, 2])
        recent_rewards = episode_rewards[-30:] if len(episode_rewards) >= 30 else episode_rewards
        recent_eps = episodes[-30:] if len(episodes) >= 30 else episodes
        ax5.plot(recent_eps, recent_rewards, 'o-', color='darkblue', linewidth=2, markersize=6)
        ax5.set_ylabel('Avg Reward', fontweight='bold')
        ax5.set_title('Last 30 Episodes', fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # 6. Summary stats
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        recent_ma = np.mean(episode_rewards[-20:]) if len(episode_rewards) >= 20 else np.mean(episode_rewards)
        convergence_score = 1.0 - min(np.var(episode_rewards[-20:]) / max(np.var(episode_rewards), 0.01), 1.0)
        
        summary = f"""
TRAINING CONVERGENCE SUMMARY
{'─'*100}
Episodes: {len(episodes):3d}  |  Best Reward: {best_reward:7.2f} @ ep{best_ep:3d}  |  Final Reward: {final_reward:7.2f}  |  Recent MA: {recent_ma:7.2f}
States: {q_table_size_history[-1]:3d}  |  Epsilon: {epsilon_history[-1]:5.3f}  |  Convergence: {convergence_score:5.1%}  |  Status: {status}
        """
        
        ax6.text(0.5, 0.5, summary, ha='center', va='center', fontsize=11, family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        
        if save:
            filename_png = self.output_dir / 'convergence_combined.png'
            filename_pdf = self.output_dir / 'convergence_combined.pdf'
            plt.savefig(filename_png, dpi=150, bbox_inches='tight')
            plt.savefig(filename_pdf, bbox_inches='tight')
            print(f"  ✓ Saved to {filename_png}")
            print(f"  ✓ Saved to {filename_pdf}")
        
        plt.show()


def plot_from_training_stats(
    episode_rewards: List[float],
    epsilon_history: List[float],
    q_table_size_history: List[int],
    total_updates_history: List[int],
    course_id: int = 5,
    output_dir: str = 'plots/convergence'
):
    """
    Generate all convergence plots from training statistics
    """
    viz = ConvergenceVisualizer(course_id=course_id, output_dir=output_dir)
    
    print("\n" + "="*80)
    print("CONVERGENCE ANALYSIS")
    print("="*80)
    
    # Plot 1: Reward convergence
    reward_stats = viz.plot_reward_convergence(episode_rewards)
    
    # Plot 2: Epsilon decay
    viz.plot_epsilon_decay(epsilon_history)
    
    # Plot 3: Q-table growth
    viz.plot_qtable_growth(q_table_size_history, total_updates_history)
    
    # Plot 4: Combined view
    viz.plot_combined_convergence(episode_rewards, epsilon_history, q_table_size_history)
    
    print("\n" + "="*80)
    print("✓ All convergence plots saved to:", output_dir)
    print("="*80)
    
    return reward_stats


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot Q-Learning training convergence')
    parser.add_argument('--course-id', type=int, default=5, help='Course ID')
    parser.add_argument('--demo', action='store_true', help='Run demo with synthetic data')
    parser.add_argument('--history-file', type=str, default='data/simulated/training_history.json',
                        help='Path to training history JSON file')
    
    args = parser.parse_args()
    
    if args.demo:
        # Demo with synthetic convergence data
        print("Running demo with synthetic data...")
        
        # Simulate training progression
        n_episodes = 500
        episodes = np.arange(n_episodes)
        
        # Reward: starts low, converges to higher value
        episode_rewards = 50 + 150 * (1 - np.exp(-episodes / 100)) + np.random.normal(0, 5, n_episodes)
        episode_rewards = np.maximum(episode_rewards, 0)
        
        # Epsilon: exponential decay
        epsilon_history = np.maximum(0.01, 1.0 * np.power(0.995, episodes))
        
        # Q-table size: grows then plateaus
        q_table_size = np.minimum(500, 10 + 450 * (1 - np.exp(-episodes / 50)))
        q_table_size_history = q_table_size.astype(int).tolist()
        
        # Total updates: increases linearly
        total_updates_history = (episodes * 900).tolist()
        
        plot_from_training_stats(
            episode_rewards=episode_rewards.tolist(),
            epsilon_history=epsilon_history.tolist(),
            q_table_size_history=q_table_size_history,
            total_updates_history=total_updates_history,
            course_id=args.course_id
        )
    else:
        # Load real training history
        import json
        from pathlib import Path
        
        history_path = Path(args.history_file)
        if not history_path.exists():
            print(f"❌ Error: Training history file not found: {history_path}")
            print(f"   Please run training first or use --demo flag for synthetic data")
            print(f"\nUsage:")
            print(f"  Demo mode:  python3 {__file__} --demo")
            print(f"  Real data:  python3 {__file__} --history-file path/to/training_history.json")
            exit(1)
        
        print(f"Loading training history from: {history_path}")
        with open(history_path, 'r') as f:
            history = json.load(f)
        
        # Extract training stats
        episode_rewards = history.get('episode_rewards', [])
        epsilon_history = history.get('epsilon_history', [])
        q_table_size_history = history.get('q_table_size_history', [])
        total_updates_history = history.get('total_updates_history', [])
        
        if not episode_rewards:
            print("❌ Error: No training data found in history file")
            print("   Use --demo flag to generate plots with synthetic data")
            exit(1)
        
        print(f"✓ Loaded {len(episode_rewards)} episodes")
        
        plot_from_training_stats(
            episode_rewards=episode_rewards,
            epsilon_history=epsilon_history,
            q_table_size_history=q_table_size_history,
            total_updates_history=total_updates_history,
            course_id=args.course_id
        )
