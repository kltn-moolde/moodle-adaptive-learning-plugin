#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimal Cluster Finder Module
==============================
Tự động xác định số cụm tối ưu cho KMeans clustering dựa trên:
- Elbow Method (Inertia)
- Silhouette Score
- Davies-Bouldin Index
- Voting mechanism để chọn k tối ưu
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from pathlib import Path
from typing import Dict, List
import json
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class OptimalClusterFinder:
    """
    Tìm số cụm tối ưu cho KMeans clustering
    
    Features:
    - Test multiple k values
    - Elbow Method (Inertia)
    - Silhouette Score
    - Davies-Bouldin Index
    - Voting mechanism để chọn k tối ưu
    """
    
    def __init__(self, k_range: range = range(2, 11)):
        """
        Args:
            k_range: Range of k values to test (default: 2-10)
        """
        self.k_range = k_range
        self.results = {}
        self.optimal_k = None
        self.optimal_kmeans = None
        self.votes = {}  # Lưu vote từ từng method
        
    def evaluate_k(self, X: np.ndarray, k: int, random_state: int = 42) -> Dict:
        """
        Evaluate clustering performance cho một giá trị k
        
        Args:
            X: Feature matrix (scaled)
            k: Number of clusters
            random_state: Random seed
            
        Returns:
            Dict chứa metrics (Inertia, Silhouette, Davies-Bouldin)
        """
        # Fit KMeans
        kmeans = KMeans(n_clusters=k, 
                       random_state=random_state,
                       n_init=10,
                       max_iter=300)
        kmeans.fit(X)
        
        # Predict labels
        labels = kmeans.labels_
        
        # Calculate metrics
        inertia = kmeans.inertia_  # Within-cluster sum of squares (lower is better)
        
        # Silhouette score (only if k >= 2 and k < n_samples)
        if k >= 2 and k < len(X):
            try:
                silhouette = silhouette_score(X, labels)
            except Exception as e:
                logger.warning(f"Could not compute silhouette for k={k}: {e}")
                silhouette = np.nan
        else:
            silhouette = np.nan
        
        # Davies-Bouldin Index (lower is better)
        if k >= 2 and k < len(X):
            try:
                db_index = davies_bouldin_score(X, labels)
            except Exception as e:
                logger.warning(f"Could not compute Davies-Bouldin for k={k}: {e}")
                db_index = np.nan
        else:
            db_index = np.nan
        
        return {
            'k': k,
            'inertia': float(inertia),
            'silhouette': float(silhouette) if not np.isnan(silhouette) else None,
            'davies_bouldin': float(db_index) if not np.isnan(db_index) else None,
            'n_iter': kmeans.n_iter_,
            'kmeans': kmeans
        }
    
    def find_optimal_k_elbow(self, results: List[Dict]) -> int:
        """
        Tìm k tối ưu bằng Elbow Method (phương pháp khuỷu tay)
        """
        inertias = [r['inertia'] for r in results]
        k_values = [r['k'] for r in results]
        
        # Tính góc cho mỗi điểm (angle method)
        angles = []
        for i in range(1, len(inertias) - 1):
            # Vector từ point trước đến point hiện tại
            v1 = np.array([k_values[i] - k_values[i-1], inertias[i] - inertias[i-1]])
            # Vector từ point hiện tại đến point sau
            v2 = np.array([k_values[i+1] - k_values[i], inertias[i+1] - inertias[i]])
            
            # Tính góc
            angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angles.append((k_values[i], angle))
        
        # Điểm có góc nhỏ nhất (góc gấp khúc nhất) là elbow
        if angles:
            elbow_k = min(angles, key=lambda x: x[1])[0]
        else:
            elbow_k = k_values[1]  # Default to k=3 if can't determine
            
        return elbow_k
    
    def find_optimal_k_silhouette(self, results: List[Dict]) -> int:
        """
        Tìm k tối ưu bằng Silhouette Score (higher is better)
        """
        valid_results = [r for r in results if r['silhouette'] is not None]
        if not valid_results:
            return results[0]['k']
        
        best_k = max(valid_results, key=lambda x: x['silhouette'])['k']
        return best_k
    
    def find_optimal_k_davies_bouldin(self, results: List[Dict]) -> int:
        """
        Tìm k tối ưu bằng Davies-Bouldin Index (lower is better)
        """
        valid_results = [r for r in results if r['davies_bouldin'] is not None]
        if not valid_results:
            return results[0]['k']
        
        best_k = min(valid_results, key=lambda x: x['davies_bouldin'])['k']
        return best_k
    
    def find_optimal_k(self, X: np.ndarray, random_state: int = 42) -> int:
        """
        Tìm k tối ưu bằng voting mechanism từ 3 phương pháp
        
        Args:
            X: Feature matrix (scaled)
            random_state: Random seed
            
        Returns:
            Optimal k value
        """
        logger.info("="*70)
        logger.info("FINDING OPTIMAL NUMBER OF CLUSTERS (KMeans)")
        logger.info("="*70)
        logger.info(f"Testing k from {min(self.k_range)} to {max(self.k_range)}...")
        
        results = []
        
        for k in self.k_range:
            logger.info(f"\nEvaluating k={k}...")
            result = self.evaluate_k(X, k, random_state)
            results.append(result)
            
            logger.info(f"  Inertia: {result['inertia']:.2f}")
            if result['silhouette'] is not None:
                logger.info(f"  Silhouette: {result['silhouette']:.3f}")
            if result['davies_bouldin'] is not None:
                logger.info(f"  Davies-Bouldin: {result['davies_bouldin']:.3f}")
        
        self.results = {r['k']: r for r in results}
        
        # ========== VOTING MECHANISM ==========
        logger.info("\n" + "="*70)
        logger.info("VOTING FOR OPTIMAL K")
        logger.info("="*70)
        
        # Method 1: Elbow Method
        k_elbow = self.find_optimal_k_elbow(results)
        logger.info(f"📊 Elbow Method votes for k={k_elbow}")
        
        # Method 2: Silhouette Score
        k_silhouette = self.find_optimal_k_silhouette(results)
        logger.info(f"📊 Silhouette Analysis votes for k={k_silhouette}")
        
        # Method 3: Davies-Bouldin Index
        k_db = self.find_optimal_k_davies_bouldin(results)
        logger.info(f"📊 Davies-Bouldin Index votes for k={k_db}")
        
        # Voting: Chọn k có nhiều vote nhất
        votes = [k_elbow, k_silhouette, k_db]
        vote_counts = Counter(votes)
        self.votes = {
            'elbow': k_elbow,
            'silhouette': k_silhouette,
            'davies_bouldin': k_db,
            'vote_counts': dict(vote_counts)
        }
        
        # Chọn k có vote cao nhất
        self.optimal_k = vote_counts.most_common(1)[0][0]
        self.optimal_kmeans = self.results[self.optimal_k]['kmeans']
        
        logger.info("\n" + "="*70)
        logger.info("VOTING RESULTS")
        logger.info("="*70)
        for k, count in vote_counts.most_common():
            logger.info(f"  k={k}: {count} vote(s)")
        
        logger.info(f"\n🎯 OPTIMAL K (by majority vote): {self.optimal_k}")
        logger.info(f"   Inertia: {self.results[self.optimal_k]['inertia']:.2f}")
        if self.results[self.optimal_k]['silhouette'] is not None:
            logger.info(f"   Silhouette: {self.results[self.optimal_k]['silhouette']:.3f}")
        if self.results[self.optimal_k]['davies_bouldin'] is not None:
            logger.info(f"   Davies-Bouldin: {self.results[self.optimal_k]['davies_bouldin']:.3f}")
        
        logger.info("="*70)
        
        return self.optimal_k
    
    def visualize_evaluation(self, output_dir: str):
        """
        Tạo comprehensive visualization cho evaluation results
        
        Args:
            output_dir: Directory to save plots
        """
        logger.info("Creating cluster evaluation visualizations...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        k_values = sorted(self.results.keys())
        inertia_values = [self.results[k]['inertia'] for k in k_values]
        silhouette_values = [self.results[k]['silhouette'] if self.results[k]['silhouette'] is not None else np.nan 
                            for k in k_values]
        db_values = [self.results[k]['davies_bouldin'] if self.results[k]['davies_bouldin'] is not None else np.nan 
                    for k in k_values]
        
        # ========== Main Plot: 2x2 grid ==========
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Elbow Method (Inertia)
        axes[0, 0].plot(k_values, inertia_values, marker='o', linewidth=2, 
                       markersize=8, color='steelblue')
        # Đánh dấu elbow point
        if 'elbow' in self.votes:
            axes[0, 0].axvline(self.votes['elbow'], color='orange', linestyle='--', 
                              linewidth=2, label=f"Elbow k={self.votes['elbow']}")
        axes[0, 0].axvline(self.optimal_k, color='red', linestyle='-', 
                          linewidth=2.5, label=f'Optimal k={self.optimal_k}')
        axes[0, 0].set_xlabel('Number of Clusters (k)', fontweight='bold', fontsize=11)
        axes[0, 0].set_ylabel('Inertia (WCSS)', fontweight='bold', fontsize=11)
        axes[0, 0].set_title('Elbow Method\nLower is Better', 
                            fontweight='bold', fontsize=12)
        axes[0, 0].grid(alpha=0.3, linestyle='--')
        axes[0, 0].legend(fontsize=10)
        
        # Plot 2: Silhouette Score
        valid_sil = [(k, s) for k, s in zip(k_values, silhouette_values) if not np.isnan(s)]
        if valid_sil:
            valid_k, valid_s = zip(*valid_sil)
            axes[0, 1].plot(valid_k, valid_s, marker='^', linewidth=2, 
                           markersize=8, color='green')
            # Đánh dấu silhouette best
            if 'silhouette' in self.votes:
                axes[0, 1].axvline(self.votes['silhouette'], color='orange', linestyle='--', 
                                  linewidth=2, label=f"Silhouette k={self.votes['silhouette']}")
            axes[0, 1].axvline(self.optimal_k, color='red', linestyle='-', 
                              linewidth=2.5, label=f'Optimal k={self.optimal_k}')
            axes[0, 1].axhline(0.5, color='gray', linestyle=':', 
                              linewidth=1.5, label='Good threshold (0.5)')
            axes[0, 1].set_xlabel('Number of Clusters (k)', fontweight='bold', fontsize=11)
            axes[0, 1].set_ylabel('Silhouette Score', fontweight='bold', fontsize=11)
            axes[0, 1].set_title('Silhouette Analysis\nHigher is Better (>0.5: Good)', 
                                fontweight='bold', fontsize=12)
            axes[0, 1].grid(alpha=0.3, linestyle='--')
            axes[0, 1].legend(fontsize=10)
            axes[0, 1].set_ylim([-0.1, 1.0])
        
        # Plot 3: Davies-Bouldin Index
        valid_db = [(k, d) for k, d in zip(k_values, db_values) if not np.isnan(d)]
        if valid_db:
            valid_k, valid_d = zip(*valid_db)
            axes[1, 0].plot(valid_k, valid_d, marker='s', linewidth=2, 
                           markersize=8, color='purple')
            # Đánh dấu DB best
            if 'davies_bouldin' in self.votes:
                axes[1, 0].axvline(self.votes['davies_bouldin'], color='orange', linestyle='--', 
                                  linewidth=2, label=f"Davies-Bouldin k={self.votes['davies_bouldin']}")
            axes[1, 0].axvline(self.optimal_k, color='red', linestyle='-', 
                              linewidth=2.5, label=f'Optimal k={self.optimal_k}')
            axes[1, 0].set_xlabel('Number of Clusters (k)', fontweight='bold', fontsize=11)
            axes[1, 0].set_ylabel('Davies-Bouldin Index', fontweight='bold', fontsize=11)
            axes[1, 0].set_title('Davies-Bouldin Index\nLower is Better', 
                                fontweight='bold', fontsize=12)
            axes[1, 0].grid(alpha=0.3, linestyle='--')
            axes[1, 0].legend(fontsize=10)
        
        # Plot 4: Voting Results (Bar chart)
        if 'vote_counts' in self.votes:
            vote_k = list(self.votes['vote_counts'].keys())
            vote_counts = list(self.votes['vote_counts'].values())
            colors = ['red' if k == self.optimal_k else 'lightblue' for k in vote_k]
            axes[1, 1].bar(vote_k, vote_counts, color=colors, alpha=0.7, edgecolor='black')
            axes[1, 1].set_xlabel('Number of Clusters (k)', fontweight='bold', fontsize=11)
            axes[1, 1].set_ylabel('Number of Votes', fontweight='bold', fontsize=11)
            axes[1, 1].set_title(f'Voting Results\nOptimal k={self.optimal_k} (Majority Vote)', 
                                fontweight='bold', fontsize=12)
            axes[1, 1].grid(axis='y', alpha=0.3, linestyle='--')
            axes[1, 1].set_ylim([0, 4])
            # Annotate vote counts
            for k, count in zip(vote_k, vote_counts):
                axes[1, 1].text(k, count + 0.1, str(count), ha='center', va='bottom', 
                               fontweight='bold', fontsize=10)
        
        plt.suptitle('KMeans Cluster Evaluation - Finding Optimal K by Voting', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        viz_png = output_path / 'optimal_clusters_evaluation.png'
        viz_pdf = output_path / 'optimal_clusters_evaluation.pdf'
        plt.savefig(viz_png, dpi=300, bbox_inches='tight')
        plt.savefig(viz_pdf, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  ✓ Saved: {viz_png}")
        logger.info(f"  ✓ Saved: {viz_pdf}")
    
    def save_evaluation_report(self, output_dir: str):
        """
        Save evaluation report (JSON + text)
        
        Args:
            output_dir: Directory to save report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare report data
        report = {
            'optimal_k': self.optimal_k,
            'k_range_tested': [min(self.k_range), max(self.k_range)],
            'voting_results': self.votes,
            'evaluation_results': {}
        }
        
        for k, result in self.results.items():
            report['evaluation_results'][str(k)] = {
                'inertia': result['inertia'],
                'silhouette': result['silhouette'],
                'davies_bouldin': result['davies_bouldin'],
                'n_iter': result['n_iter']
            }
        
        # Save JSON
        json_path = output_path / 'optimal_clusters_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ Saved: {json_path}")
        
        # Save text report
        text_lines = []
        text_lines.append("="*70)
        text_lines.append("OPTIMAL CLUSTER EVALUATION REPORT (KMeans)")
        text_lines.append("="*70)
        text_lines.append(f"\n🎯 OPTIMAL K: {self.optimal_k} (by majority vote)")
        text_lines.append(f"\nK Range Tested: {min(self.k_range)} to {max(self.k_range)}")
        text_lines.append("\n" + "="*70)
        text_lines.append("VOTING RESULTS")
        text_lines.append("="*70)
        if 'vote_counts' in self.votes:
            for k, count in sorted(self.votes['vote_counts'].items(), key=lambda x: x[1], reverse=True):
                text_lines.append(f"  k={k}: {count} vote(s)")
        text_lines.append(f"\nElbow Method voted for: k={self.votes.get('elbow', 'N/A')}")
        text_lines.append(f"Silhouette Analysis voted for: k={self.votes.get('silhouette', 'N/A')}")
        text_lines.append(f"Davies-Bouldin Index voted for: k={self.votes.get('davies_bouldin', 'N/A')}")
        text_lines.append("\n" + "="*70)
        text_lines.append("DETAILED RESULTS FOR EACH K")
        text_lines.append("="*70)
        
        for k in sorted(self.results.keys()):
            result = self.results[k]
            text_lines.append(f"\n{'='*70}")
            text_lines.append(f"K = {k}" + (" ← OPTIMAL" if k == self.optimal_k else ""))
            text_lines.append(f"{'='*70}")
            text_lines.append(f"  Inertia:          {result['inertia']:>12.2f}  (lower is better)")
            
            if result['silhouette'] is not None:
                sil_str = f"{result['silhouette']:.3f}"
                quality = "Excellent" if result['silhouette'] > 0.7 else \
                         "Good" if result['silhouette'] > 0.5 else \
                         "Fair" if result['silhouette'] > 0.3 else "Poor"
                text_lines.append(f"  Silhouette:       {sil_str:>12s}  ({quality})")
            else:
                text_lines.append(f"  Silhouette:       {'N/A':>12s}")
            
            if result['davies_bouldin'] is not None:
                text_lines.append(f"  Davies-Bouldin:   {result['davies_bouldin']:>12.3f}  (lower is better)")
            else:
                text_lines.append(f"  Davies-Bouldin:   {'N/A':>12s}")
            
            text_lines.append(f"  Iterations:       {result['n_iter']}")
        
        text_lines.append("\n" + "="*70)
        text_lines.append("INTERPRETATION GUIDE")
        text_lines.append("="*70)
        text_lines.append("Inertia:         Within-cluster sum of squares (lower is better)")
        text_lines.append("Silhouette:      Measures cluster separation quality")
        text_lines.append("                 > 0.7: Excellent,  0.5-0.7: Good,  0.3-0.5: Fair,  < 0.3: Poor")
        text_lines.append("Davies-Bouldin:  Average similarity between clusters (lower is better)")
        text_lines.append("                 < 1.0: Excellent,  1.0-2.0: Good,  > 2.0: Poor")
        text_lines.append("="*70)
        
        text_path = output_path / 'optimal_clusters_report.txt'
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_lines))
        
        logger.info(f"  ✓ Saved: {text_path}")
    
    def process_pipeline(self, X: np.ndarray, output_dir: str, 
                        random_state: int = 42):
        """
        Complete pipeline: find optimal k + visualization + report
        
        Args:
            X: Feature matrix (scaled)
            output_dir: Directory to save outputs
            random_state: Random seed
            
        Returns:
            (optimal_k, optimal_gmm)
        """
        # Find optimal k
        optimal_k = self.find_optimal_k(X, random_state)
        
        # Visualize
        self.visualize_evaluation(output_dir)
        
        # Save report
        self.save_evaluation_report(output_dir)
        
        return optimal_k, self.optimal_kmeans


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Generate test data
    from sklearn.datasets import make_blobs
    X, _ = make_blobs(n_samples=300, n_features=5, centers=4, random_state=42)
    
    # Find optimal clusters
    finder = OptimalClusterFinder(k_range=range(2, 10))
    optimal_k, optimal_kmeans = finder.process_pipeline(
        X=X,
        output_dir='../outputs/optimal_clusters',
        random_state=42
    )
    
    print(f"\n✅ Optimal K: {optimal_k}")
