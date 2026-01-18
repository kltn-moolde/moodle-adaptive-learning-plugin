#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event & Action Feature Extractor
=================================
Extract features from Moodle logs focusing on event_name and action columns
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


class EventActionFeatureExtractor:
    """Extract engagement features from eventname and action columns"""
    
    def __init__(self):
        """Initialize feature extractor"""
        self.scaler = MinMaxScaler()
        self.feature_columns = []
        
    def extract_features(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from logs DataFrame
        
        Args:
            logs_df: DataFrame with columns [userid, eventname, action, timecreated]
            
        Returns:
            DataFrame with extracted features per user
        """
        if logs_df.empty:
            logger.warning("Empty logs DataFrame provided")
            return pd.DataFrame()
        
        logger.info(f"Extracting features from {len(logs_df)} log entries")
        
        # Ensure required columns
        required_cols = ['userid', 'eventname', 'action']
        missing = [col for col in required_cols if col not in logs_df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Remove rows with null values in key columns
        logs_df = logs_df.dropna(subset=['userid', 'eventname', 'action'])
        
        # Convert userid to int
        logs_df['userid'] = logs_df['userid'].astype(int)
        
        # 1. Event name frequency features
        event_features = self._extract_event_features(logs_df)
        
        # 2. Action type features
        action_features = self._extract_action_features(logs_df)
        
        # 3. Combined event-action interaction features
        interaction_features = self._extract_interaction_features(logs_df)
        
        # 4. Temporal features (if timecreated available)
        temporal_features = self._extract_temporal_features(logs_df)
        
        # Merge all features
        features = event_features.copy()
        for feature_df in [action_features, interaction_features, temporal_features]:
            if not feature_df.empty:
                features = features.join(feature_df, how='outer')
        
        # Fill NaN with 0 (students with no activity in specific categories)
        features = features.fillna(0)
        
        # Store feature columns
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} features for {len(features)} users")
        logger.debug(f"Feature columns: {self.feature_columns[:10]}...")
        
        return features
    
    def _extract_event_features(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from eventname column"""
        
        # Count events per user per event type
        event_counts = logs_df.pivot_table(
            index='userid',
            columns='eventname',
            aggfunc='size',
            fill_value=0
        )
        
        # Rename columns to be more descriptive
        event_counts.columns = [f'event_{col}' for col in event_counts.columns]
        
        # Add total events count
        event_counts['total_events'] = event_counts.sum(axis=1)
        
        logger.debug(f"Extracted {len(event_counts.columns)} event features")
        
        return event_counts
    
    def _extract_action_features(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from action column"""
        
        # Count actions per user per action type
        action_counts = logs_df.pivot_table(
            index='userid',
            columns='action',
            aggfunc='size',
            fill_value=0
        )
        
        # Rename columns to be more descriptive
        action_counts.columns = [f'action_{col}' for col in action_counts.columns]
        
        # Add total actions count
        action_counts['total_actions'] = action_counts.sum(axis=1)
        
        logger.debug(f"Extracted {len(action_counts.columns)} action features")
        
        return action_counts
    
    def _extract_interaction_features(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """Extract combined event-action interaction features"""
        
        # Create event-action combinations
        logs_df['event_action'] = logs_df['eventname'] + '_' + logs_df['action']
        
        # Count combinations per user
        interaction_counts = logs_df.pivot_table(
            index='userid',
            columns='event_action',
            aggfunc='size',
            fill_value=0
        )
        
        # Only keep top interactions to avoid too many features
        # Keep interactions that appear for at least 5% of users
        threshold = len(interaction_counts) * 0.05
        active_interactions = (interaction_counts > 0).sum() >= threshold
        interaction_counts = interaction_counts.loc[:, active_interactions]
        
        # Rename columns
        interaction_counts.columns = [f'combo_{col}' for col in interaction_counts.columns]
        
        logger.debug(f"Extracted {len(interaction_counts.columns)} interaction features")
        
        return interaction_counts
    
    def _extract_temporal_features(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """Extract temporal features if timecreated is available"""
        
        if 'timecreated' not in logs_df.columns or logs_df['timecreated'].isna().all():
            logger.debug("No temporal data available")
            return pd.DataFrame()
        
        # Convert timestamp to datetime
        logs_df['datetime'] = pd.to_datetime(logs_df['timecreated'], unit='s', errors='coerce')
        logs_df = logs_df.dropna(subset=['datetime'])
        
        if logs_df.empty:
            return pd.DataFrame()
        
        # Group by user
        temporal_features = []
        
        for userid, user_logs in logs_df.groupby('userid'):
            user_logs = user_logs.sort_values('datetime')
            
            features = {
                'userid': userid,
                'total_days_active': (user_logs['datetime'].max() - user_logs['datetime'].min()).days + 1,
                'unique_dates': user_logs['datetime'].dt.date.nunique(),
                'avg_events_per_day': len(user_logs) / max((user_logs['datetime'].max() - user_logs['datetime'].min()).days + 1, 1),
            }
            
            # Hour of day distribution
            user_logs['hour'] = user_logs['datetime'].dt.hour
            features['morning_activity'] = ((user_logs['hour'] >= 6) & (user_logs['hour'] < 12)).sum()
            features['afternoon_activity'] = ((user_logs['hour'] >= 12) & (user_logs['hour'] < 18)).sum()
            features['evening_activity'] = ((user_logs['hour'] >= 18) & (user_logs['hour'] < 24)).sum()
            features['night_activity'] = ((user_logs['hour'] >= 0) & (user_logs['hour'] < 6)).sum()
            
            # Day of week distribution
            user_logs['dayofweek'] = user_logs['datetime'].dt.dayofweek
            features['weekday_activity'] = (user_logs['dayofweek'] < 5).sum()
            features['weekend_activity'] = (user_logs['dayofweek'] >= 5).sum()
            
            temporal_features.append(features)
        
        temporal_df = pd.DataFrame(temporal_features).set_index('userid')
        
        logger.debug(f"Extracted {len(temporal_df.columns)} temporal features")
        
        return temporal_df
    
    def normalize_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize features to 0-1 range using MinMaxScaler
        
        Args:
            features_df: DataFrame with extracted features
            
        Returns:
            Normalized DataFrame
        """
        if features_df.empty:
            return features_df
        
        # Keep user IDs
        user_ids = features_df.index
        
        # Normalize
        normalized_data = self.scaler.fit_transform(features_df)
        normalized_df = pd.DataFrame(
            normalized_data,
            index=user_ids,
            columns=features_df.columns
        )
        
        logger.info(f"Normalized {len(features_df.columns)} features for {len(features_df)} users")
        
        return normalized_df
    
    def get_feature_summary(self, features_df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of extracted features
        
        Args:
            features_df: DataFrame with features
            
        Returns:
            Dictionary with summary statistics
        """
        if features_df.empty:
            return {}
        
        summary = {
            'total_users': len(features_df),
            'total_features': len(features_df.columns),
            'feature_names': features_df.columns.tolist(),
            'statistics': {
                'mean': features_df.mean().to_dict(),
                'std': features_df.std().to_dict(),
                'min': features_df.min().to_dict(),
                'max': features_df.max().to_dict(),
            }
        }
        
        return summary
