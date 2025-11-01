#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation Metrics Module
=========================
Comprehensive validation giữa real và synthetic data
sử dụng statistical tests và visualizations
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class ValidationMetrics:
    """
    Validate similarity giữa real và synthetic data
    
    Methods:
    - Statistical tests (KS test, Chi-square, T-test)
    - Distribution comparisons
    - Correlation analysis
    - Comprehensive reporting
    """
    
    def __init__(self):
        self.real_data = None
        self.synthetic_data = None
        self.validation_results = {}
        
    def load_data(self, real_path: str, synthetic_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load real and synthetic data
        
        Args:
            real_path: Path to real data CSV
            synthetic_path: Path to synthetic data CSV
            
        Returns:
            (real_df, synthetic_df)
        """
        logger.info("Loading data for validation...")
        logger.info(f"  Real: {real_path}")
        logger.info(f"  Synthetic: {synthetic_path}")
        
        self.real_data = pd.read_csv(real_path)
        self.synthetic_data = pd.read_csv(synthetic_path)
        
        logger.info(f"✓ Loaded {len(self.real_data)} real students")
        logger.info(f"✓ Loaded {len(self.synthetic_data)} synthetic students")
        
        return self.real_data, self.synthetic_data
    
    def kolmogorov_smirnov_test(self, feature: str) -> Dict:
        """
        Perform KS test cho một feature
        
        Args:
            feature: Feature name
            
        Returns:
            Dict với KS statistic và p-value
        """
        real_vals = self.real_data[feature].dropna().values
        synth_vals = self.synthetic_data[feature].dropna().values
        
        ks_stat, p_value = stats.ks_2samp(real_vals, synth_vals)
        
        # Interpretation
        similar = p_value > 0.05  # α = 0.05
        
        return {
            'feature': feature,
            'ks_statistic': float(ks_stat),
            'p_value': float(p_value),
            'similar': bool(similar),
            'interpretation': 'Distributions are similar' if similar else 'Distributions differ significantly'
        }
    
    def distribution_comparison(self, feature: str) -> Dict:
        """
        So sánh distribution statistics cho một feature
        
        Args:
            feature: Feature name
            
        Returns:
            Dict với mean, std, median, skewness, kurtosis
        """
        real_vals = self.real_data[feature].dropna().values
        synth_vals = self.synthetic_data[feature].dropna().values
        
        comparison = {
            'feature': feature,
            'real': {
                'mean': float(np.mean(real_vals)),
                'std': float(np.std(real_vals)),
                'median': float(np.median(real_vals)),
                'min': float(np.min(real_vals)),
                'max': float(np.max(real_vals)),
                'skewness': float(stats.skew(real_vals)),
                'kurtosis': float(stats.kurtosis(real_vals))
            },
            'synthetic': {
                'mean': float(np.mean(synth_vals)),
                'std': float(np.std(synth_vals)),
                'median': float(np.median(synth_vals)),
                'min': float(np.min(synth_vals)),
                'max': float(np.max(synth_vals)),
                'skewness': float(stats.skew(synth_vals)),
                'kurtosis': float(stats.kurtosis(synth_vals))
            }
        }
        
        # Calculate relative errors
        comparison['relative_errors'] = {
            'mean_error': abs(comparison['real']['mean'] - comparison['synthetic']['mean']) / (abs(comparison['real']['mean']) + 1e-10),
            'std_error': abs(comparison['real']['std'] - comparison['synthetic']['std']) / (abs(comparison['real']['std']) + 1e-10),
            'skewness_diff': abs(comparison['real']['skewness'] - comparison['synthetic']['skewness'])
        }
        
        return comparison
    
    def correlation_comparison(self, features: list) -> Dict:
        """
        So sánh correlation matrices giữa real và synthetic
        
        Args:
            features: List of features to compare
            
        Returns:
            Dict với correlation matrices và similarity score
        """
        logger.info("Comparing correlation matrices...")
        
        # Get common features
        common_features = [f for f in features if f in self.real_data.columns and f in self.synthetic_data.columns]
        
        # Correlation matrices
        corr_real = self.real_data[common_features].corr()
        corr_synth = self.synthetic_data[common_features].corr()
        
        # Calculate similarity (Frobenius norm)
        corr_diff = corr_real - corr_synth
        frobenius_distance = np.linalg.norm(corr_diff.values, 'fro')
        
        # Normalized similarity score (0-1, higher is better)
        max_possible_distance = np.sqrt(2 * len(common_features)**2)  # Max distance for correlation matrices
        similarity_score = 1 - (frobenius_distance / max_possible_distance)
        
        return {
            'correlation_real': corr_real.to_dict(),
            'correlation_synthetic': corr_synth.to_dict(),
            'frobenius_distance': float(frobenius_distance),
            'similarity_score': float(similarity_score),
            'interpretation': 'Excellent' if similarity_score > 0.9 else 'Good' if similarity_score > 0.7 else 'Fair' if similarity_score > 0.5 else 'Poor'
        }
    
    def cluster_distribution_comparison(self) -> Dict:
        """
        So sánh cluster distribution giữa real và synthetic
        
        Returns:
            Dict với distribution statistics
        """
        logger.info("Comparing cluster distributions...")
        
        # Get cluster distributions (as proportions)
        real_dist = self.real_data['cluster'].value_counts(normalize=True).sort_index()
        synth_dist = self.synthetic_data['cluster'].value_counts(normalize=True).sort_index()
        
        # Chi-square test on proportions scaled to same total
        # Use same sample size for both to make them comparable
        sample_size = 100  # Scale both to 100 for comparison
        clusters = sorted(set(real_dist.index) | set(synth_dist.index))
        observed_real = [real_dist.get(c, 0) * sample_size for c in clusters]
        observed_synth = [synth_dist.get(c, 0) * sample_size for c in clusters]
        
        # Use chi-square test with expected frequencies
        chi2_stat, p_value = stats.chisquare(observed_synth, f_exp=observed_real)
        
        return {
            'real_distribution': {int(k): float(v) for k, v in real_dist.items()},
            'synthetic_distribution': {int(k): float(v) for k, v in synth_dist.items()},
            'chi_square_statistic': float(chi2_stat),
            'p_value': float(p_value),
            'similar': bool(p_value > 0.05),
            'interpretation': 'Distributions are similar' if p_value > 0.05 else 'Distributions differ'
        }
    
    def comprehensive_validation(self, features: list) -> Dict:
        """
        Run comprehensive validation trên tất cả features
        
        Args:
            features: List of features to validate
            
        Returns:
            Dict với all validation results
        """
        logger.info("="*70)
        logger.info("COMPREHENSIVE VALIDATION")
        logger.info("="*70)
        
        results = {
            'ks_tests': [],
            'distribution_comparisons': [],
            'overall_metrics': {}
        }
        
        # Filter features that exist in both datasets
        common_features = [f for f in features 
                          if f in self.real_data.columns and f in self.synthetic_data.columns
                          and f not in ['userid', 'cluster', 'group']]
        
        logger.info(f"\nValidating {len(common_features)} features...")
        
        # KS tests and distribution comparisons
        ks_pass_count = 0
        total_mean_error = 0
        total_std_error = 0
        
        for feature in common_features:
            # KS test
            ks_result = self.kolmogorov_smirnov_test(feature)
            results['ks_tests'].append(ks_result)
            
            if ks_result['similar']:
                ks_pass_count += 1
            
            # Distribution comparison
            dist_comp = self.distribution_comparison(feature)
            results['distribution_comparisons'].append(dist_comp)
            
            total_mean_error += dist_comp['relative_errors']['mean_error']
            total_std_error += dist_comp['relative_errors']['std_error']
            
            logger.info(f"  {feature:30s} - KS p-value: {ks_result['p_value']:.4f} ({'✓' if ks_result['similar'] else '✗'})")
        
        # Overall metrics
        results['overall_metrics'] = {
            'total_features_tested': len(common_features),
            'ks_tests_passed': ks_pass_count,
            'ks_pass_rate': ks_pass_count / len(common_features) if common_features else 0,
            'avg_mean_error': total_mean_error / len(common_features) if common_features else 0,
            'avg_std_error': total_std_error / len(common_features) if common_features else 0
        }
        
        # Correlation comparison
        logger.info("\nComparing correlation matrices...")
        results['correlation_comparison'] = self.correlation_comparison(common_features)
        logger.info(f"  Correlation similarity: {results['correlation_comparison']['similarity_score']:.3f} ({results['correlation_comparison']['interpretation']})")
        
        # Cluster distribution
        if 'cluster' in self.real_data.columns and 'cluster' in self.synthetic_data.columns:
            logger.info("\nComparing cluster distributions...")
            results['cluster_comparison'] = self.cluster_distribution_comparison()
            logger.info(f"  Chi-square p-value: {results['cluster_comparison']['p_value']:.4f} ({'✓' if results['cluster_comparison']['similar'] else '✗'})")
        
        # Overall quality score
        quality_score = (
            0.4 * results['overall_metrics']['ks_pass_rate'] +
            0.3 * results['correlation_comparison']['similarity_score'] +
            0.3 * (1 - min(results['overall_metrics']['avg_mean_error'], 1.0))
        ) * 100
        
        results['overall_quality_score'] = {
            'score': float(quality_score),
            'grade': 'Excellent' if quality_score >= 85 else 'Good' if quality_score >= 70 else 'Fair' if quality_score >= 50 else 'Poor',
            'interpretation': self._interpret_quality_score(quality_score)
        }
        
        logger.info(f"\n🎯 OVERALL QUALITY SCORE: {quality_score:.1f}% ({results['overall_quality_score']['grade']})")
        logger.info("="*70)
        
        self.validation_results = results
        return results
    
    def _interpret_quality_score(self, score: float) -> str:
        """Interpret quality score"""
        if score >= 85:
            return "Synthetic data very closely matches real data distribution"
        elif score >= 70:
            return "Synthetic data is similar to real data with minor differences"
        elif score >= 50:
            return "Synthetic data shows moderate similarity to real data"
        else:
            return "Synthetic data differs significantly from real data"
    
    def visualize_validation(self, output_dir: str, features: list):
        """
        Create comprehensive validation visualizations
        
        Args:
            output_dir: Directory to save plots
            features: Features to visualize
        """
        logger.info("Creating validation visualizations...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        common_features = [f for f in features[:12]  # Limit to 12 for visualization
                          if f in self.real_data.columns and f in self.synthetic_data.columns
                          and f not in ['userid', 'cluster', 'group']]
        
        # ========== Plot 1: KS Test Results ==========
        ks_results = self.validation_results.get('ks_tests', [])
        if ks_results:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            features_ks = [r['feature'] for r in ks_results]
            p_values = [r['p_value'] for r in ks_results]
            colors = ['green' if r['similar'] else 'red' for r in ks_results]
            
            bars = ax.barh(features_ks, p_values, color=colors, alpha=0.7, edgecolor='black')
            ax.axvline(0.05, color='blue', linestyle='--', linewidth=2, label='α = 0.05 threshold')
            ax.set_xlabel('P-value', fontweight='bold', fontsize=12)
            ax.set_title('Kolmogorov-Smirnov Test Results\n(p > 0.05: Similar distributions)', 
                        fontweight='bold', fontsize=14)
            ax.legend()
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            viz_path = output_path / 'ks_test_results.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"  ✓ Saved: {viz_path}")
        
        # ========== Plot 2: Distribution Comparison (Box plots) ==========
        n_features = min(6, len(common_features))
        if n_features > 0:
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            axes = axes.flatten()
            
            for i, feature in enumerate(common_features[:n_features]):
                real_vals = self.real_data[feature].dropna()
                synth_vals = self.synthetic_data[feature].dropna()
                
                data = pd.DataFrame({
                    'value': pd.concat([real_vals, synth_vals]),
                    'source': ['Real']*len(real_vals) + ['Synthetic']*len(synth_vals)
                })
                
                data.boxplot(column='value', by='source', ax=axes[i])
                axes[i].set_title(feature, fontweight='bold')
                axes[i].set_xlabel('')
                axes[i].set_ylabel('Value', fontweight='bold')
                axes[i].get_figure().suptitle('')
            
            # Hide unused subplots
            for i in range(n_features, len(axes)):
                axes[i].axis('off')
            
            plt.suptitle('Feature Distribution Comparison (Box Plots)', 
                        fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            viz_path = output_path / 'distribution_boxplots.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"  ✓ Saved: {viz_path}")
    
    def save_validation_report(self, output_dir: str):
        """
        Save validation report (JSON + text)
        
        Args:
            output_dir: Directory to save report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_path / 'validation_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ Saved: {json_path}")
        
        # Save text report
        text_lines = []
        text_lines.append("="*70)
        text_lines.append("VALIDATION REPORT - REAL VS SYNTHETIC DATA")
        text_lines.append("="*70)
        
        if 'overall_quality_score' in self.validation_results:
            score_info = self.validation_results['overall_quality_score']
            text_lines.append(f"\n🎯 OVERALL QUALITY SCORE: {score_info['score']:.1f}%")
            text_lines.append(f"   Grade: {score_info['grade']}")
            text_lines.append(f"   {score_info['interpretation']}")
        
        text_lines.append("\n" + "="*70)
        text_lines.append("SUMMARY METRICS")
        text_lines.append("="*70)
        
        if 'overall_metrics' in self.validation_results:
            metrics = self.validation_results['overall_metrics']
            text_lines.append(f"Features Tested:        {metrics['total_features_tested']}")
            text_lines.append(f"KS Tests Passed:        {metrics['ks_tests_passed']} ({metrics['ks_pass_rate']*100:.1f}%)")
            text_lines.append(f"Avg Mean Error:         {metrics['avg_mean_error']:.4f}")
            text_lines.append(f"Avg Std Error:          {metrics['avg_std_error']:.4f}")
        
        if 'correlation_comparison' in self.validation_results:
            corr = self.validation_results['correlation_comparison']
            text_lines.append(f"\nCorrelation Similarity: {corr['similarity_score']:.3f} ({corr['interpretation']})")
        
        text_lines.append("\n" + "="*70)
        text_lines.append("DETAILED KS TEST RESULTS")
        text_lines.append("="*70)
        
        for ks_result in self.validation_results.get('ks_tests', []):
            status = "✓ PASS" if ks_result['similar'] else "✗ FAIL"
            text_lines.append(f"{ks_result['feature']:30s} p={ks_result['p_value']:.4f}  {status}")
        
        text_path = output_path / 'validation_report.txt'
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_lines))
        
        logger.info(f"  ✓ Saved: {text_path}")
    
    def process_pipeline(self, real_path: str, synthetic_path: str,
                        features: list, output_dir: str) -> Dict:
        """
        Complete validation pipeline
        
        Args:
            real_path: Path to real data CSV
            synthetic_path: Path to synthetic data CSV
            features: Features to validate
            output_dir: Directory to save outputs
            
        Returns:
            Validation results dict
        """
        # Load data
        self.load_data(real_path, synthetic_path)
        
        # Run validation
        results = self.comprehensive_validation(features)
        
        # Visualize
        self.visualize_validation(output_dir, features)
        
        # Save report
        self.save_validation_report(output_dir)
        
        return results


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    validator = ValidationMetrics()
    
    results = validator.process_pipeline(
        real_path='../outputs/clustering/clustered_students.csv',
        synthetic_path='../outputs/gmm_generation/synthetic_students_gmm.csv',
        features=['total_events', 'mean_module_grade', 'viewed', 'submitted'],
        output_dir='../outputs/validation'
    )
    
    print(f"\n✅ Validation completed")
    print(f"Quality Score: {results['overall_quality_score']['score']:.1f}%")
