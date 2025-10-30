#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparison Visualizer Module
============================
So sánh và visualize differences giữa real và simulated data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ComparisonVisualizer:
    """
    Compare và visualize real vs simulated data
    
    Features:
    - Distribution comparisons
    - Statistical tests
    - Cluster proportion comparisons
    - Feature correlation comparisons
    """
    
    def __init__(self):
        self.real_data = None
        self.simulated_data = None
        self.comparison_stats = {}
        
    def load_data(self, real_path: str, simulated_path: str):
        """
        Load real và simulated data
        
        Args:
            real_path: Path to real data (JSON or CSV)
            simulated_path: Path to simulated data (JSON or CSV)
        """
        logger.info("Loading data for comparison...")
        
        # Load real data
        if real_path.endswith('.json'):
            with open(real_path, 'r', encoding='utf-8') as f:
                self.real_data = pd.DataFrame(json.load(f))
        else:
            self.real_data = pd.read_csv(real_path)
        
        # Load simulated data
        if simulated_path.endswith('.json'):
            with open(simulated_path, 'r', encoding='utf-8') as f:
                self.simulated_data = pd.DataFrame(json.load(f))
        else:
            self.simulated_data = pd.read_csv(simulated_path)
        
        logger.info(f"✓ Real data: {len(self.real_data)} students")
        logger.info(f"✓ Simulated data: {len(self.simulated_data)} students")
    
    def compare_distributions(self, features: List[str], output_dir: str = None):
        """
        Compare distributions of features
        
        Args:
            features: List of features to compare
            output_dir: Directory to save plots
        """
        logger.info(f"Comparing distributions for {len(features)} features...")
        
        n_features = len(features)
        n_cols = 3
        n_rows = (n_features + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5*n_rows))
        axes = axes.flatten() if n_features > 1 else [axes]
        
        for idx, feature in enumerate(features):
            if feature not in self.real_data.columns or feature not in self.simulated_data.columns:
                continue
                
            ax = axes[idx]
            
            # Plot distributions
            ax.hist(self.real_data[feature], bins=30, alpha=0.5, 
                   label='Real', color='blue', density=True)
            ax.hist(self.simulated_data[feature], bins=30, alpha=0.5,
                   label='Simulated', color='red', density=True)
            
            ax.set_xlabel(feature, fontsize=10)
            ax.set_ylabel('Density', fontsize=10)
            ax.set_title(f'{feature}', fontsize=11, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # KS test
            ks_stat, ks_pvalue = stats.ks_2samp(
                self.real_data[feature].dropna(),
                self.simulated_data[feature].dropna()
            )
            
            ax.text(0.02, 0.98, f'KS p-value: {ks_pvalue:.3f}',
                   transform=ax.transAxes, fontsize=8,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Hide extra subplots
        for idx in range(n_features, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'distribution_comparison.png',
                       dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {output_path / 'distribution_comparison.png'}")
        
        plt.show()
    
    def compare_cluster_proportions(self, output_dir: str = None):
        """
        Compare cluster proportions between real and simulated
        
        Args:
            output_dir: Directory to save plot
        """
        logger.info("Comparing cluster proportions...")
        
        # Get proportions
        real_props = self.real_data['cluster'].value_counts(normalize=True).sort_index()
        sim_props = self.simulated_data['cluster'].value_counts(normalize=True).sort_index()
        
        # Normalize cluster names (convert 'cluster_0' to 0, or keep as is)
        def normalize_cluster_name(x):
            if isinstance(x, str) and x.startswith('cluster_'):
                return int(x.split('_')[1])
            return int(x) if not isinstance(x, str) else x
        
        real_props.index = real_props.index.map(normalize_cluster_name)
        sim_props.index = sim_props.index.map(normalize_cluster_name)
        
        # Ensure same clusters
        all_clusters = sorted(set(list(real_props.index) + list(sim_props.index)))
        real_props = real_props.reindex(all_clusters, fill_value=0)
        sim_props = sim_props.reindex(all_clusters, fill_value=0)
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(all_clusters))
        width = 0.35
        
        ax.bar(x - width/2, real_props.values, width, label='Real', alpha=0.8, color='blue')
        ax.bar(x + width/2, sim_props.values, width, label='Simulated', alpha=0.8, color='red')
        
        ax.set_xlabel('Cluster', fontsize=12)
        ax.set_ylabel('Proportion', fontsize=12)
        ax.set_title('Cluster Distribution Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(all_clusters)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add percentage labels
        for i, (real_val, sim_val) in enumerate(zip(real_props.values, sim_props.values)):
            ax.text(i - width/2, real_val + 0.01, f'{real_val*100:.1f}%',
                   ha='center', va='bottom', fontsize=9)
            ax.text(i + width/2, sim_val + 0.01, f'{sim_val*100:.1f}%',
                   ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'cluster_proportion_comparison.png',
                       dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {output_path / 'cluster_proportion_comparison.png'}")
        
        plt.show()
        
        # Calculate chi-square test using proportions (not counts)
        real_counts = self.real_data['cluster'].value_counts().sort_index()
        sim_counts = self.simulated_data['cluster'].value_counts().sort_index()
        
        # Normalize to proportions  
        real_props_chi = real_props.values * len(sim_counts)  # Scale to simulated size
        sim_counts_values = sim_counts.reindex(all_clusters, fill_value=0).values
        
        try:
            chi2, pvalue = stats.chisquare(sim_counts_values, real_props_chi)
            logger.info(f"  Chi-square test: χ²={chi2:.3f}, p-value={pvalue:.3f}")
        except Exception as e:
            logger.warning(f"  Could not perform chi-square test: {e}")
    
    def compare_statistics(self, features: List[str]) -> Dict:
        """
        Compare basic statistics between real and simulated
        
        Args:
            features: List of features to compare
            
        Returns:
            Dict of comparison statistics
        """
        logger.info(f"Computing statistics for {len(features)} features...")
        
        comparison = {}
        
        for feature in features:
            if feature not in self.real_data.columns or feature not in self.simulated_data.columns:
                continue
            
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(self.real_data[feature]):
                continue
            if not pd.api.types.is_numeric_dtype(self.simulated_data[feature]):
                continue
            
            real_vals = self.real_data[feature].dropna()
            sim_vals = self.simulated_data[feature].dropna()
            
            # Skip if no data
            if len(real_vals) == 0 or len(sim_vals) == 0:
                continue
            
            comparison[feature] = {
                'real': {
                    'mean': float(real_vals.mean()),
                    'std': float(real_vals.std()),
                    'median': float(real_vals.median()),
                    'min': float(real_vals.min()),
                    'max': float(real_vals.max())
                },
                'simulated': {
                    'mean': float(sim_vals.mean()),
                    'std': float(sim_vals.std()),
                    'median': float(sim_vals.median()),
                    'min': float(sim_vals.min()),
                    'max': float(sim_vals.max())
                },
                'difference': {
                    'mean_diff': float(abs(real_vals.mean() - sim_vals.mean())),
                    'mean_diff_pct': float(abs(real_vals.mean() - sim_vals.mean()) / real_vals.mean() * 100) if real_vals.mean() != 0 else 0
                                     if real_vals.mean() != 0 else 0
                },
                'statistical_tests': {
                    'ks_statistic': float(stats.ks_2samp(real_vals, sim_vals)[0]),
                    'ks_pvalue': float(stats.ks_2samp(real_vals, sim_vals)[1])
                }
            }
        
        self.comparison_stats = comparison
        
        return comparison
    
    def create_comparison_dashboard(self, features: List[str], output_dir: str = None):
        """
        Create comprehensive comparison dashboard
        
        Args:
            features: List of features to include
            output_dir: Directory to save plot
        """
        logger.info("Creating comparison dashboard...")
        
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Sample size comparison
        ax1 = fig.add_subplot(gs[0, 0])
        sizes = [len(self.real_data), len(self.simulated_data)]
        ax1.bar(['Real', 'Simulated'], sizes, color=['blue', 'red'], alpha=0.7)
        ax1.set_ylabel('Number of Students')
        ax1.set_title('Sample Size Comparison', fontweight='bold')
        for i, v in enumerate(sizes):
            ax1.text(i, v + 5, str(v), ha='center', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Cluster distribution
        ax2 = fig.add_subplot(gs[0, 1])
        real_props = self.real_data['cluster'].value_counts(normalize=True).sort_index()
        sim_props = self.simulated_data['cluster'].value_counts(normalize=True).sort_index()
        
        x = np.arange(len(real_props))
        width = 0.35
        ax2.bar(x - width/2, real_props.values, width, label='Real', alpha=0.8, color='blue')
        ax2.bar(x + width/2, sim_props.values, width, label='Simulated', alpha=0.8, color='red')
        ax2.set_xlabel('Cluster')
        ax2.set_ylabel('Proportion')
        ax2.set_title('Cluster Distribution', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(real_props.index)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Mean comparison for key features
        ax3 = fig.add_subplot(gs[0, 2])
        key_features = features[:5]
        real_means = [self.real_data[f].mean() for f in key_features 
                     if f in self.real_data.columns]
        sim_means = [self.simulated_data[f].mean() for f in key_features
                    if f in self.simulated_data.columns]
        
        x = np.arange(len(key_features))
        width = 0.35
        ax3.bar(x - width/2, real_means, width, label='Real', alpha=0.8, color='blue')
        ax3.bar(x + width/2, sim_means, width, label='Simulated', alpha=0.8, color='red')
        ax3.set_xlabel('Feature')
        ax3.set_ylabel('Mean Value')
        ax3.set_title('Mean Comparison (Key Features)', fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels([f[:15] for f in key_features], rotation=45, ha='right', fontsize=8)
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # 4-9. Distribution comparisons for selected features
        plot_features = features[:6]
        for idx, feature in enumerate(plot_features):
            row = 1 + idx // 3
            col = idx % 3
            ax = fig.add_subplot(gs[row, col])
            
            if feature in self.real_data.columns and feature in self.simulated_data.columns:
                ax.hist(self.real_data[feature], bins=20, alpha=0.5,
                       label='Real', color='blue', density=True)
                ax.hist(self.simulated_data[feature], bins=20, alpha=0.5,
                       label='Simulated', color='red', density=True)
                ax.set_xlabel(feature[:20], fontsize=9)
                ax.set_ylabel('Density', fontsize=9)
                ax.set_title(f'{feature[:25]}', fontsize=10, fontweight='bold')
                ax.legend(fontsize=8)
                ax.grid(True, alpha=0.3)
        
        plt.suptitle('Real vs Simulated Data - Comprehensive Comparison',
                    fontsize=16, fontweight='bold', y=0.995)
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path / 'comparison_dashboard.png',
                       dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved: {output_path / 'comparison_dashboard.png'}")
        
        plt.show()
    
    def save_comparison_report(self, features: List[str], output_dir: str):
        """
        Save detailed comparison report
        
        Args:
            features: List of features to include
            output_dir: Directory to save report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Compute statistics if not already done
        if not self.comparison_stats:
            self.compare_statistics(features)
        
        # Save JSON report
        report_path = output_path / 'comparison_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.comparison_stats, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved: {report_path}")
        
        # Create text summary
        summary_lines = []
        summary_lines.append("="*70)
        summary_lines.append("REAL vs SIMULATED DATA - COMPARISON REPORT")
        summary_lines.append("="*70)
        summary_lines.append(f"\nReal Data: {len(self.real_data)} students")
        summary_lines.append(f"Simulated Data: {len(self.simulated_data)} students")
        summary_lines.append("\n" + "-"*70)
        summary_lines.append("FEATURE COMPARISONS")
        summary_lines.append("-"*70)
        
        for feature, stats in self.comparison_stats.items():
            summary_lines.append(f"\n{feature}:")
            summary_lines.append(f"  Real mean:       {stats['real']['mean']:.4f}")
            summary_lines.append(f"  Simulated mean:  {stats['simulated']['mean']:.4f}")
            summary_lines.append(f"  Difference:      {stats['difference']['mean_diff']:.4f} "
                               f"({stats['difference']['mean_diff_pct']:.2f}%)")
            summary_lines.append(f"  KS p-value:      {stats['statistical_tests']['ks_pvalue']:.4f}")
        
        summary_lines.append("\n" + "="*70)
        
        summary_text = "\n".join(summary_lines)
        
        summary_path = output_path / 'comparison_summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        logger.info(f"✓ Saved: {summary_path}")
        
        print(summary_text)
    
    def process_pipeline(self, real_path: str, simulated_path: str,
                        features: List[str], output_dir: str):
        """
        Run complete comparison pipeline
        
        Args:
            real_path: Path to real data
            simulated_path: Path to simulated data
            features: List of features to compare
            output_dir: Directory to save outputs
        """
        logger.info("="*70)
        logger.info("COMPARISON ANALYSIS PIPELINE")
        logger.info("="*70)
        
        # Load data
        self.load_data(real_path, simulated_path)
        
        # Compare distributions
        self.compare_distributions(features[:9], output_dir)
        
        # Compare cluster proportions
        self.compare_cluster_proportions(output_dir)
        
        # Compare statistics
        self.compare_statistics(features)
        
        # Create dashboard
        self.create_comparison_dashboard(features, output_dir)
        
        # Save report
        self.save_comparison_report(features, output_dir)
        
        logger.info("="*70)
        logger.info("✅ COMPARISON ANALYSIS COMPLETED")
        logger.info("="*70)


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    visualizer = ComparisonVisualizer()
    visualizer.process_pipeline(
        real_path='../outputs/clustering/clustered_students.csv',
        simulated_path='../outputs/simulation/simulated_students.csv',
        features=['mean_module_grade', 'total_events', 'viewed', 
                 'submitted', 'created', 'module_count'],
        output_dir='../outputs/comparison'
    )
