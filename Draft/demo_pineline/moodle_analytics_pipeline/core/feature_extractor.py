#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Extractor Module
========================
Trích xuất và chuẩn hóa features từ Moodle logs và grades data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import json
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extract và normalize features từ Moodle data
    
    Features extracted:
    - Total events per user
    - Event frequencies (pivot từ eventname)
    - Action frequencies (pivot từ action)
    - Target frequencies (pivot từ target)
    - Module count và mean grades
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.feature_stats = {}
        self.features_raw = None
        self.features_scaled = None
        
    def load_data(self, grades_path: str, logs_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load dữ liệu từ CSV files
        
        Args:
            grades_path: Path to grades CSV
            logs_path: Path to logs CSV
            
        Returns:
            (df_grades, df_logs): DataFrames
        """
        logger.info(f"Loading data from:")
        logger.info(f"  Grades: {grades_path}")
        logger.info(f"  Logs: {logs_path}")
        
        df_grades = pd.read_csv(grades_path)
        df_logs = pd.read_csv(logs_path)
        
        logger.info(f"✓ Loaded {len(df_grades)} grade records")
        logger.info(f"✓ Loaded {len(df_logs)} log records")
        
        return df_grades, df_logs
    
    def extract_features(self, df_grades: pd.DataFrame, df_logs: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features từ raw data
        
        Returns:
            DataFrame with extracted features
        """
        logger.info("Extracting features...")
        
        # Filter grades for modules only
        df_grades_mod = df_grades[df_grades['itemtype'] == 'mod']
        
        # 1. Total events per user
        total_events = df_logs.groupby('userid').size().reset_index(name='total_events')
        
        # 2. Event features (pivot from eventname)
        event_features = df_logs.pivot_table(
            index='userid',
            columns='eventname',
            aggfunc='size',
            fill_value=0
        ).reset_index().rename_axis(None, axis=1)
        
        # 3. Action features (pivot from action)
        action_features = df_logs.pivot_table(
            index='userid',
            columns='action',
            aggfunc='size',
            fill_value=0
        ).reset_index().rename_axis(None, axis=1)
        
        # 4. Target features (pivot from target)
        target_features = df_logs.pivot_table(
            index='userid',
            columns='target',
            aggfunc='size',
            fill_value=0
        ).reset_index().rename_axis(None, axis=1)
        
        # 5. Grade features
        module_count = df_grades_mod.groupby('userid')['id'].count().reset_index()\
                                     .rename(columns={'id': 'module_count'})
        mean_module_grade = df_grades_mod.groupby('userid')['finalgrade'].mean().reset_index()\
                                         .rename(columns={'finalgrade': 'mean_module_grade'})
        
        # Merge all features
        features = total_events.merge(event_features, on='userid', how='outer')
        features = features.merge(action_features, on='userid', how='outer')
        features = features.merge(target_features, on='userid', how='outer')
        features = features.merge(module_count, on='userid', how='outer')
        features = features.merge(mean_module_grade, on='userid', how='outer')
        
        features = features.fillna(0)
        
        self.features_raw = features
        
        logger.info(f"✓ Extracted features:")
        logger.info(f"  Students: {len(features)}")
        logger.info(f"  Features: {len(features.columns) - 1}")  # -1 for userid
        
        return features
    
    def normalize_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize features using MinMaxScaler
        
        Returns:
            DataFrame with normalized features [0, 1]
        """
        logger.info("Normalizing features...")
        
        cols_to_scale = features.columns.difference(['userid'])
        features_scaled = features.copy()
        
        # Scale features
        features_scaled[cols_to_scale] = self.scaler.fit_transform(features_scaled[cols_to_scale])
        
        self.features_scaled = features_scaled
        
        # Calculate statistics
        self._calculate_feature_stats(cols_to_scale)
        
        logger.info(f"✓ Features normalized to [0, 1]")
        
        return features_scaled
    
    def _calculate_feature_stats(self, feature_cols):
        """Calculate statistics for all features"""
        self.feature_stats = {
            'num_users': int(self.features_scaled['userid'].nunique()),
            'num_features': len(feature_cols),
            'feature_names': list(feature_cols),
            'feature_statistics': {}
        }
        
        for col in feature_cols:
            self.feature_stats['feature_statistics'][col] = {
                'min': float(self.features_scaled[col].min()),
                'max': float(self.features_scaled[col].max()),
                'mean': float(self.features_scaled[col].mean()),
                'median': float(self.features_scaled[col].median()),
                'std': float(self.features_scaled[col].std())
            }
    
    def save_features(self, output_dir: str):
        """
        Save extracted features và statistics
        
        Args:
            output_dir: Directory to save outputs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save scaled features (JSON format)
        features_json_path = output_path / 'features_scaled.json'
        self.features_scaled.to_json(features_json_path, orient='records', 
                                     force_ascii=False, indent=2)
        logger.info(f"✓ Saved: {features_json_path}")
        
        # Save raw features (CSV format)
        features_csv_path = output_path / 'features_raw.csv'
        self.features_raw.to_csv(features_csv_path, index=False)
        logger.info(f"✓ Saved: {features_csv_path}")
        
        # Save statistics
        stats_path = output_path / 'feature_statistics.json'
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.feature_stats, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved: {stats_path}")
    
    def process_pipeline(self, grades_path: str, logs_path: str, output_dir: str) -> pd.DataFrame:
        """
        Run complete feature extraction pipeline
        
        Args:
            grades_path: Path to grades CSV
            logs_path: Path to logs CSV  
            output_dir: Directory to save outputs
            
        Returns:
            DataFrame with normalized features
        """
        logger.info("="*70)
        logger.info("FEATURE EXTRACTION PIPELINE")
        logger.info("="*70)
        
        # Load data
        df_grades, df_logs = self.load_data(grades_path, logs_path)
        
        # Extract features
        features = self.extract_features(df_grades, df_logs)
        
        # Normalize
        features_scaled = self.normalize_features(features)
        
        # Save
        self.save_features(output_dir)
        
        logger.info("="*70)
        logger.info("✅ FEATURE EXTRACTION COMPLETED")
        logger.info("="*70)
        
        return features_scaled


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    extractor = FeatureExtractor()
    features = extractor.process_pipeline(
        grades_path='../../data/udk_moodle_grades_course_670.filtered.csv',
        logs_path='../../data/udk_moodle_log_course_670.filtered.csv',
        output_dir='../outputs/features'
    )
    
    print(f"\n📊 Extracted {len(features)} students with {len(features.columns)-1} features")
    print(features.head())
