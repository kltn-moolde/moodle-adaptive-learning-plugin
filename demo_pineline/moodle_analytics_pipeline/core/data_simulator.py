#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Simulator Module
====================
Simulate student data dựa trên cluster statistics
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)


class DataSimulator:
    """
    Simulate student profiles và learning behaviors
    dựa trên real cluster statistics
    """
    
    def __init__(self, cluster_stats_path: str):
        """
        Args:
            cluster_stats_path: Path to cluster_statistics.json
        """
        with open(cluster_stats_path, 'r', encoding='utf-8') as f:
            self.cluster_stats = json.load(f)
        
        self.simulated_data = None
        
        logger.info(f"Simulator initialized with {len(self.cluster_stats)} clusters")
    
    def simulate_student_profile(self, cluster_id: str, noise_level: float = 0.1) -> Dict:
        """
        Simulate single student profile from cluster
        
        Args:
            cluster_id: Cluster ID (e.g., 'cluster_0')
            noise_level: Amount of noise to add (0-1)
            
        Returns:
            Dict of student features
        """
        cluster_data = self.cluster_stats[cluster_id]
        feature_stats = cluster_data['feature_statistics']
        
        profile = {'userid': np.random.randint(100000, 999999)}
        
        for feature, stats in feature_stats.items():
            mean = stats['mean']
            std = stats['std']
            
            # Generate value with Gaussian noise
            value = np.random.normal(mean, std * noise_level)
            value = np.clip(value, 0, 1)  # Clip to [0, 1]
            
            profile[feature] = float(value)
        
        profile['cluster'] = cluster_id
        
        return profile
    
    def simulate_students(self, n_students: int, noise_level: float = 0.1) -> pd.DataFrame:
        """
        Simulate multiple students distributed across clusters
        
        Args:
            n_students: Total number of students to simulate
            noise_level: Amount of noise (0-1)
            
        Returns:
            DataFrame of simulated students
        """
        logger.info(f"Simulating {n_students} students...")
        
        # Get cluster distribution from real data
        cluster_ids = list(self.cluster_stats.keys())
        cluster_percentages = [self.cluster_stats[cid]['percentage'] / 100.0 
                             for cid in cluster_ids]
        
        # Assign students to clusters
        cluster_assignments = np.random.choice(
            cluster_ids,
            size=n_students,
            p=cluster_percentages
        )
        
        # Simulate students
        simulated_students = []
        for cluster_id in cluster_assignments:
            profile = self.simulate_student_profile(cluster_id, noise_level)
            simulated_students.append(profile)
        
        self.simulated_data = pd.DataFrame(simulated_students)
        
        logger.info(f"✓ Simulated {len(self.simulated_data)} students")
        logger.info(f"  Cluster distribution:")
        for cluster_id in cluster_ids:
            count = len(self.simulated_data[self.simulated_data['cluster'] == cluster_id])
            pct = count / len(self.simulated_data) * 100
            logger.info(f"    {cluster_id}: {count} students ({pct:.1f}%)")
        
        return self.simulated_data
    
    def save_simulated_data(self, output_dir: str):
        """
        Save simulated data
        
        Args:
            output_dir: Directory to save outputs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save CSV
        csv_path = output_path / 'simulated_students.csv'
        self.simulated_data.to_csv(csv_path, index=False)
        logger.info(f"✓ Saved: {csv_path}")
        
        # Save JSON
        json_path = output_path / 'simulated_students.json'
        self.simulated_data.to_json(json_path, orient='records', 
                                    force_ascii=False, indent=2)
        logger.info(f"✓ Saved: {json_path}")
        
        # Save summary
        summary = {
            'total_students': int(len(self.simulated_data)),
            'clusters': {}
        }
        
        for cluster_id in self.simulated_data['cluster'].unique():
            cluster_data = self.simulated_data[self.simulated_data['cluster'] == cluster_id]
            summary['clusters'][cluster_id] = {
                'count': int(len(cluster_data)),
                'percentage': float(len(cluster_data) / len(self.simulated_data) * 100)
            }
        
        summary_path = output_path / 'simulation_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved: {summary_path}")
    
    def visualize_simulated_clusters(self, output_dir: str):
        """
        Tạo visualization cho simulated data clusters
        
        Args:
            output_dir: Directory to save visualization
        """
        logger.info("Creating simulated clusters visualization...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get numeric features (exclude userid and cluster)
        numeric_cols = [col for col in self.simulated_data.columns 
                       if col not in ['userid', 'cluster'] and 
                       pd.api.types.is_numeric_dtype(self.simulated_data[col])]
        
        if len(numeric_cols) < 2:
            logger.warning("Not enough numeric features for visualization")
            return
        
        # Prepare data
        X = self.simulated_data[numeric_cols].fillna(0)
        
        # Extract cluster numbers from 'cluster_X' format
        def extract_cluster_num(cluster_name):
            if isinstance(cluster_name, str) and cluster_name.startswith('cluster_'):
                return int(cluster_name.split('_')[1])
            return int(cluster_name)
        
        clusters = self.simulated_data['cluster'].apply(extract_cluster_num).values
        
        # PCA for visualization
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Color palette
        n_clusters = len(np.unique(clusters))
        colors = plt.cm.viridis(np.linspace(0, 1, n_clusters))
        
        # Plot each cluster
        for i, cluster_id in enumerate(sorted(np.unique(clusters))):
            mask = clusters == cluster_id
            ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                      c=[colors[i]], label=f'Cluster {cluster_id}',
                      alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
        
        # Labels and title
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', 
                     fontsize=12, fontweight='bold')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)',
                     fontsize=12, fontweight='bold')
        ax.set_title('Simulated Student Clusters (PCA Visualization)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add info text
        info_text = f'Total Students: {len(self.simulated_data)}\n'
        info_text += f'Number of Clusters: {n_clusters}\n'
        info_text += f'Features Used: {len(numeric_cols)}'
        
        ax.text(0.02, 0.98, info_text,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=10)
        
        plt.tight_layout()
        
        # Save
        viz_path = output_path / 'simulated_cluster_visualization.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✓ Saved: {viz_path}")
    
    def process_pipeline(self, n_students: int, output_dir: str, 
                        noise_level: float = 0.1) -> pd.DataFrame:
        """
        Run complete simulation pipeline
        
        Args:
            n_students: Number of students to simulate
            output_dir: Directory to save outputs
            noise_level: Amount of noise (0-1)
            
        Returns:
            DataFrame of simulated students
        """
        logger.info("="*70)
        logger.info("DATA SIMULATION PIPELINE")
        logger.info("="*70)
        
        # Simulate
        simulated_data = self.simulate_students(n_students, noise_level)
        
        # Visualize
        self.visualize_simulated_clusters(output_dir)
        
        # Save
        self.save_simulated_data(output_dir)
        
        logger.info("="*70)
        logger.info("✅ DATA SIMULATION COMPLETED")
        logger.info("="*70)
        
        return simulated_data


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    simulator = DataSimulator(
        cluster_stats_path='../outputs/clustering/cluster_statistics.json'
    )
    
    simulated = simulator.process_pipeline(
        n_students=100,
        output_dir='../outputs/simulation',
        noise_level=0.15
    )
    
    print(f"\n📊 Simulated {len(simulated)} students")
    print(simulated.head())
