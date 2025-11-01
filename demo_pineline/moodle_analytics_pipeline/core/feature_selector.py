#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Selector Module
=======================
Tự động chọn features tối ưu cho clustering dựa trên:
- Variance threshold (loại bỏ features có variance thấp)
- Correlation analysis (loại bỏ features redundant)
- Statistical significance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class FeatureSelector:
    """
    Intelligent feature selection cho clustering
    
    Methods:
    - Variance-based filtering
    - Correlation-based filtering
    - Feature importance ranking
    - Visualization
    """
    
    def __init__(self, variance_threshold: float = 0.01, 
                 correlation_threshold: float = 0.95):
        """
        Args:
            variance_threshold: Minimum variance để giữ feature (0-1)
            correlation_threshold: Maximum correlation để loại redundant features
        """
        self.variance_threshold = variance_threshold
        self.correlation_threshold = correlation_threshold
        self.selected_features = []
        self.feature_scores = {}
        self.removed_features = {
            'low_variance': [],
            'high_correlation': []
        }
        
    def calculate_variance_scores(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Tính variance score cho mỗi feature
        
        Args:
            df: Features DataFrame (đã scaled)
            
        Returns:
            Dict {feature_name: variance_score}
        """
        logger.info("Calculating variance scores...")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'userid']
        
        variance_scores = {}
        for col in numeric_cols:
            var = df[col].var()
            variance_scores[col] = float(var)
        
        logger.info(f"  Computed variance for {len(variance_scores)} features")
        return variance_scores
    
    def filter_by_variance(self, df: pd.DataFrame, 
                          variance_scores: Dict[str, float]) -> List[str]:
        """
        Lọc features theo variance threshold
        
        Returns:
            List of features vượt qua threshold
        """
        logger.info(f"Filtering by variance (threshold={self.variance_threshold})...")
        
        passed_features = []
        for feature, var_score in variance_scores.items():
            if var_score >= self.variance_threshold:
                passed_features.append(feature)
            else:
                self.removed_features['low_variance'].append(feature)
        
        logger.info(f"  ✓ Retained: {len(passed_features)} features")
        logger.info(f"  ✗ Removed: {len(self.removed_features['low_variance'])} low-variance features")
        
        return passed_features
    
    def calculate_correlation_matrix(self, df: pd.DataFrame, 
                                    features: List[str]) -> pd.DataFrame:
        """
        Tính correlation matrix cho selected features
        
        Returns:
            Correlation matrix DataFrame
        """
        logger.info("Computing correlation matrix...")
        
        corr_matrix = df[features].corr().abs()
        
        logger.info(f"  ✓ Correlation matrix: {corr_matrix.shape}")
        return corr_matrix
    
    def filter_by_correlation(self, corr_matrix: pd.DataFrame) -> List[str]:
        """
        Loại bỏ redundant features dựa trên high correlation
        
        Strategy: Với mỗi cặp features có corr > threshold, giữ feature có variance cao hơn
        
        Returns:
            List of features sau khi loại redundant
        """
        logger.info(f"Filtering by correlation (threshold={self.correlation_threshold})...")
        
        # Upper triangle of correlation matrix
        upper_tri = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        
        # Find features với high correlation
        to_drop = set()
        for column in upper_tri.columns:
            if column in to_drop:
                continue
            
            # Find correlated features
            correlated = upper_tri.index[upper_tri[column] > self.correlation_threshold].tolist()
            
            if correlated:
                # Giữ feature này, drop các features correlated
                to_drop.update(correlated)
                self.removed_features['high_correlation'].extend(correlated)
        
        # Features còn lại
        retained_features = [f for f in corr_matrix.columns if f not in to_drop]
        
        logger.info(f"  ✓ Retained: {len(retained_features)} features")
        logger.info(f"  ✗ Removed: {len(to_drop)} highly-correlated features")
        
        return retained_features
    
    def rank_features(self, df: pd.DataFrame, features: List[str]) -> Dict[str, float]:
        """
        Rank features theo composite score (variance + stability)
        
        Returns:
            Dict {feature: composite_score} (sorted descending)
        """
        logger.info("Ranking features by importance...")
        
        feature_scores = {}
        
        for feature in features:
            # Variance score (normalized)
            var_score = df[feature].var()
            
            # Stability score (1 - CV coefficient of variation)
            mean_val = df[feature].mean()
            std_val = df[feature].std()
            cv = std_val / (mean_val + 1e-10)  # Avoid division by zero
            stability_score = 1 / (1 + cv)  # Higher = more stable
            
            # Composite score (weighted average)
            composite = 0.7 * var_score + 0.3 * stability_score
            feature_scores[feature] = float(composite)
        
        # Sort by score descending
        feature_scores = dict(sorted(feature_scores.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True))
        
        logger.info(f"  ✓ Ranked {len(feature_scores)} features")
        return feature_scores
    
    def select_features(self, df: pd.DataFrame, 
                       max_features: int = None) -> List[str]:
        """
        Main method: Tự động select features tối ưu
        
        Args:
            df: Features DataFrame (scaled)
            max_features: Maximum số features (None = không limit)
            
        Returns:
            List of selected features
        """
        logger.info("="*70)
        logger.info("FEATURE SELECTION PROCESS")
        logger.info("="*70)
        
        # Step 1: Variance filtering
        variance_scores = self.calculate_variance_scores(df)
        features_after_variance = self.filter_by_variance(df, variance_scores)
        
        if not features_after_variance:
            logger.error("No features passed variance threshold!")
            return []
        
        # Step 2: Correlation filtering
        corr_matrix = self.calculate_correlation_matrix(df, features_after_variance)
        features_after_correlation = self.filter_by_correlation(corr_matrix)
        
        if not features_after_correlation:
            logger.error("No features passed correlation threshold!")
            return features_after_variance[:5]  # Fallback: top 5 variance
        
        # Step 3: Ranking
        self.feature_scores = self.rank_features(df, features_after_correlation)
        
        # Step 4: Limit by max_features
        if max_features and len(features_after_correlation) > max_features:
            logger.info(f"Limiting to top {max_features} features...")
            self.selected_features = list(self.feature_scores.keys())[:max_features]
        else:
            self.selected_features = features_after_correlation
        
        logger.info("="*70)
        logger.info(f"✅ SELECTED {len(self.selected_features)} OPTIMAL FEATURES")
        logger.info("="*70)
        
        # Log top features
        logger.info("\nTop 10 selected features:")
        for i, (feat, score) in enumerate(list(self.feature_scores.items())[:10], 1):
            if feat in self.selected_features:
                logger.info(f"  {i:2d}. {feat:30s} (score: {score:.4f})")
        
        return self.selected_features
    
    def visualize_selection(self, df: pd.DataFrame, output_dir: str):
        """
        Tạo visualizations cho feature selection process
        
        Args:
            df: Original features DataFrame
            output_dir: Directory to save plots
        """
        logger.info("Creating feature selection visualizations...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # ========== Plot 1: Variance Distribution ==========
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1.1: Variance scores
        all_features = list(self.feature_scores.keys())
        scores = list(self.feature_scores.values())
        
        axes[0, 0].barh(all_features[:15], scores[:15], color='steelblue', alpha=0.7)
        axes[0, 0].set_xlabel('Composite Score', fontweight='bold')
        axes[0, 0].set_title('Top 15 Features by Importance Score', 
                            fontweight='bold', fontsize=12)
        axes[0, 0].grid(axis='x', alpha=0.3)
        
        # 1.2: Variance histogram
        variance_vals = [self.calculate_variance_scores(df)[f] 
                        for f in self.selected_features]
        axes[0, 1].hist(variance_vals, bins=20, color='green', alpha=0.7, edgecolor='black')
        axes[0, 1].axvline(self.variance_threshold, color='red', 
                          linestyle='--', linewidth=2, label=f'Threshold ({self.variance_threshold})')
        axes[0, 1].set_xlabel('Variance', fontweight='bold')
        axes[0, 1].set_ylabel('Frequency', fontweight='bold')
        axes[0, 1].set_title('Variance Distribution (Selected Features)', 
                            fontweight='bold', fontsize=12)
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)
        
        # 1.3: Correlation heatmap (selected features only)
        if len(self.selected_features) > 1:
            corr_selected = df[self.selected_features].corr()
            sns.heatmap(corr_selected, annot=False, cmap='coolwarm', 
                       center=0, vmin=-1, vmax=1, ax=axes[1, 0],
                       cbar_kws={'label': 'Correlation'})
            axes[1, 0].set_title('Correlation Matrix (Selected Features)', 
                                fontweight='bold', fontsize=12)
        
        # 1.4: Selection summary
        axes[1, 1].axis('off')
        
        summary_text = "FEATURE SELECTION SUMMARY\n" + "="*50 + "\n\n"
        summary_text += f"Total features (input):           {len(df.columns) - 1}\n"
        summary_text += f"Removed (low variance):           {len(self.removed_features['low_variance'])}\n"
        summary_text += f"Removed (high correlation):       {len(self.removed_features['high_correlation'])}\n"
        summary_text += f"Final selected:                   {len(self.selected_features)}\n\n"
        summary_text += "="*50 + "\n"
        summary_text += "THRESHOLDS:\n"
        summary_text += f"  Variance threshold:             {self.variance_threshold}\n"
        summary_text += f"  Correlation threshold:          {self.correlation_threshold}\n\n"
        summary_text += "="*50 + "\n"
        summary_text += "TOP 5 FEATURES:\n"
        for i, (feat, score) in enumerate(list(self.feature_scores.items())[:5], 1):
            summary_text += f"  {i}. {feat[:25]:25s} ({score:.3f})\n"
        
        axes[1, 1].text(0.1, 0.9, summary_text,
                       transform=axes[1, 1].transAxes,
                       verticalalignment='top',
                       fontfamily='monospace',
                       fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        viz_path = output_path / 'feature_selection_analysis.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  ✓ Saved: {viz_path}")
    
    def save_selection_report(self, output_dir: str):
        """
        Save feature selection report
        
        Args:
            output_dir: Directory to save report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # JSON report
        report = {
            'selected_features': self.selected_features,
            'feature_scores': self.feature_scores,
            'removed_features': self.removed_features,
            'thresholds': {
                'variance_threshold': self.variance_threshold,
                'correlation_threshold': self.correlation_threshold
            },
            'summary': {
                'total_selected': len(self.selected_features),
                'removed_low_variance': len(self.removed_features['low_variance']),
                'removed_high_correlation': len(self.removed_features['high_correlation'])
            }
        }
        
        json_path = output_path / 'feature_selection_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ Saved: {json_path}")
        
        # Text report
        text_report = []
        text_report.append("="*70)
        text_report.append("FEATURE SELECTION REPORT")
        text_report.append("="*70)
        text_report.append(f"\nTotal Selected Features: {len(self.selected_features)}")
        text_report.append(f"Removed (Low Variance): {len(self.removed_features['low_variance'])}")
        text_report.append(f"Removed (High Correlation): {len(self.removed_features['high_correlation'])}")
        text_report.append(f"\nThresholds:")
        text_report.append(f"  - Variance: {self.variance_threshold}")
        text_report.append(f"  - Correlation: {self.correlation_threshold}")
        text_report.append("\n" + "="*70)
        text_report.append("SELECTED FEATURES (Ranked by Importance)")
        text_report.append("="*70)
        
        for i, (feat, score) in enumerate(self.feature_scores.items(), 1):
            if feat in self.selected_features:
                text_report.append(f"{i:3d}. {feat:35s} Score: {score:.4f}")
        
        text_path = output_path / 'feature_selection_report.txt'
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_report))
        
        logger.info(f"  ✓ Saved: {text_path}")
    
    def process_pipeline(self, df: pd.DataFrame, output_dir: str,
                        max_features: int = None) -> List[str]:
        """
        Complete feature selection pipeline
        
        Args:
            df: Features DataFrame (scaled)
            output_dir: Directory to save outputs
            max_features: Maximum features to select
            
        Returns:
            List of selected feature names
        """
        # Select features
        selected = self.select_features(df, max_features)
        
        # Visualize
        self.visualize_selection(df, output_dir)
        
        # Save report
        self.save_selection_report(output_dir)
        
        return selected


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load test data
    import json
    with open('../outputs/features/features_scaled.json', 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    
    # Run selector
    selector = FeatureSelector(variance_threshold=0.01, correlation_threshold=0.95)
    selected_features = selector.process_pipeline(
        df=df,
        output_dir='../outputs/feature_selection',
        max_features=15
    )
    
    print(f"\n✅ Selected {len(selected_features)} features")
    print(selected_features)
