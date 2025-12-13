#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clustering Job
==============
Main job logic for running clustering pipeline
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

# Add clustering_service to path first
CLUSTERING_SERVICE_PATH = Path(__file__).resolve().parent.parent
if str(CLUSTERING_SERVICE_PATH) not in sys.path:
    sys.path.insert(0, str(CLUSTERING_SERVICE_PATH))

# Import config BEFORE adding other paths to avoid conflicts
import config

# Add moodle_analytics_pipeline to path to reuse existing modules
MOODLE_PIPELINE_PATH = Path(__file__).resolve().parent.parent.parent / 'moodle_analytics_pipeline'
if str(MOODLE_PIPELINE_PATH) not in sys.path:
    sys.path.append(str(MOODLE_PIPELINE_PATH))  # Use append instead of insert

# Import from moodle_analytics_pipeline
from core.feature_selector import FeatureSelector
from core.optimal_cluster_finder import OptimalClusterFinder
from core.cluster_profiler import ClusterProfiler

# Import from clustering_service
from moodle_api import MoodleCustomAPIClient
from pipeline.feature_extractor import EventActionFeatureExtractor
from models import CourseClusterModel, UserClusterHistoryModel

logger = logging.getLogger(__name__)


class ClusteringJob:
    """Main clustering job that orchestrates the entire pipeline"""
    
    def __init__(self, moodle_client: MoodleCustomAPIClient, 
                 course_cluster_model: CourseClusterModel,
                 user_history_model: UserClusterHistoryModel):
        """
        Initialize clustering job
        
        Args:
            moodle_client: Moodle API client
            course_cluster_model: MongoDB model for course clusters
            user_history_model: MongoDB model for user cluster history
        """
        self.moodle_client = moodle_client
        self.course_cluster_model = course_cluster_model
        self.user_history_model = user_history_model
        
        # Initialize pipeline components
        self.feature_extractor = EventActionFeatureExtractor()
        self.feature_selector = FeatureSelector(
            variance_threshold=config.MIN_VARIANCE_THRESHOLD,
            correlation_threshold=config.MAX_CORRELATION_THRESHOLD
        )
        self.cluster_finder = OptimalClusterFinder(
            k_range=range(config.MIN_CLUSTERS, config.MAX_CLUSTERS + 1)
        )
        self.cluster_profiler = ClusterProfiler(
            llm_provider=config.LLM_PROVIDER,
            api_key=config.GEMINI_API_KEY
        )
    
    async def run(self, course_id: int) -> Dict:
        """
        Run full clustering pipeline for a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            Dictionary with clustering results and metadata
        """
        start_time = datetime.utcnow()
        logger.info(f"=" * 80)
        logger.info(f"Starting clustering job for course {course_id}")
        logger.info(f"=" * 80)
        
        try:
            # Phase 1: Fetch data from Moodle
            logger.info("PHASE 1: Fetching data from Moodle API")
            logs_df = self.moodle_client.get_logs_course(course_id, limit=config.MOODLE_LOG_LIMIT)
            
            if logs_df.empty:
                logger.warning(f"No logs found for course {course_id}")
                return {"status": "no_data", "message": "No logs available"}
            
            # Get unique students
            student_ids = logs_df['userid'].dropna().unique().astype(int).tolist()
            total_students = len(student_ids)
            
            logger.info(f"  Found {len(logs_df)} log entries from {total_students} students")
            
            # Phase 2: Feature extraction
            logger.info("PHASE 2: Feature Extraction")
            features_raw = self.feature_extractor.extract_features(logs_df)
            features_normalized = self.feature_extractor.normalize_features(features_raw)
            
            logger.info(f"  Extracted {len(features_normalized.columns)} features for {len(features_normalized)} students")
            
            # Save features for debugging
            output_dir = config.OUTPUTS_PATH / f"course_{course_id}"
            output_dir.mkdir(parents=True, exist_ok=True)
            features_normalized.to_csv(output_dir / f"features_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv")
            
            # Phase 3: Feature selection
            logger.info("PHASE 3: Feature Selection")
            variance_scores = self.feature_selector.calculate_variance_scores(features_normalized)
            features_after_variance = self.feature_selector.filter_by_variance(features_normalized, variance_scores)
            
            df_selected = features_normalized[features_after_variance]
            corr_matrix = self.feature_selector.calculate_correlation_matrix(df_selected, features_after_variance)
            selected_features = self.feature_selector.filter_by_correlation(corr_matrix)
            
            final_features = df_selected[selected_features]
            
            logger.info(f"  Selected {len(selected_features)} features after variance + correlation filtering")
            
            # Phase 4: Find optimal clusters
            logger.info("PHASE 4: Finding Optimal Number of Clusters (KMeans + Voting)")
            
            X = final_features.values
            n_samples = len(X)
            
            # Adjust k_range based on number of samples
            # KMeans requires n_clusters <= n_samples
            max_k = min(config.MAX_CLUSTERS, n_samples)
            if max_k < config.MIN_CLUSTERS:
                logger.warning(f"Not enough samples ({n_samples}) for clustering. Need at least {config.MIN_CLUSTERS}")
                max_k = n_samples
            
            # Update cluster finder k_range
            self.cluster_finder.k_range = range(config.MIN_CLUSTERS, max_k + 1)
            
            logger.info(f"  Testing k from {config.MIN_CLUSTERS} to {max_k} (total students: {n_samples})")
            
            # find_optimal_k returns optimal_k (int), results stored in self.cluster_finder.results
            optimal_k = self.cluster_finder.find_optimal_k(X, random_state=config.KMEANS_RANDOM_STATE)
            optimal_kmeans = self.cluster_finder.optimal_kmeans
            results = self.cluster_finder.results  # Dict[int, Dict] with metrics for each k
            
            logger.info(f"  Optimal k = {optimal_k} (selected by voting)")
            
            # Add cluster labels to dataframe (use .copy() to avoid SettingWithCopyWarning)
            final_features = final_features.copy()
            final_features['cluster'] = optimal_kmeans.labels_
            
            # Phase 5: Cluster profiling with LLM
            logger.info("PHASE 5: Cluster Profiling with AI")
            
            # Calculate statistics
            cluster_profiles_full = self.cluster_profiler.calculate_cluster_statistics(final_features)
            cluster_stats_dict = cluster_profiles_full['cluster_stats']
            
            # Generate LLM descriptions for all clusters at once
            profiles = self.cluster_profiler.profile_all_clusters(final_features)
            
            # Prepare cluster data for MongoDB
            clusters_data = []
            user_cluster_map = {}  # Map user_id -> cluster_id
            
            # Extract profiles dict from cluster_profiles structure
            cluster_profiles_dict = profiles.get('profiles', {})
            
            for cluster_id in range(optimal_k):
                cluster_mask = final_features['cluster'] == cluster_id
                cluster_users = final_features[cluster_mask].index.tolist()
                
                # Map users to clusters
                for user_id in cluster_users:
                    user_cluster_map[int(user_id)] = cluster_id
                
                # Get cluster stats
                stats = cluster_stats_dict.get(cluster_id, {})
                profile = cluster_profiles_dict.get(cluster_id, {})
                
                cluster_info = {
                    "cluster_id": cluster_id,
                    "user_ids": [int(uid) for uid in cluster_users],
                    "size": len(cluster_users),
                    "percentage": stats.get('percentage', 0),
                    "name": profile.get('name', f'Cluster {cluster_id}'),
                    "description": profile.get('description', ''),
                    "characteristics": profile.get('characteristics', []),
                    "recommendations": profile.get('recommendations', []),
                    "statistics": {
                        "feature_means": stats.get('feature_means', {}),
                        "feature_stds": stats.get('feature_stds', {}),
                        "top_features": stats.get('top_distinguishing_features', [])
                    }
                }
                
                clusters_data.append(cluster_info)
                
                logger.info(f"  Cluster {cluster_id}: {len(cluster_users)} students")
            
            # Phase 6: Save to MongoDB
            logger.info("PHASE 6: Saving results to MongoDB")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            metadata = {
                "total_students": total_students,
                "total_logs": len(logs_df),
                "features_extracted": len(features_normalized.columns),
                "features_selected": len(selected_features),
                "execution_time_seconds": execution_time,
                "clustering_metrics": {
                    "inertia": float(results[optimal_k]['inertia']),
                    "silhouette": float(results[optimal_k]['silhouette']) if results[optimal_k]['silhouette'] is not None else None,
                    "davies_bouldin": float(results[optimal_k]['davies_bouldin']) if results[optimal_k]['davies_bouldin'] is not None else None
                }
            }
            
            # Save clustering result
            result_id = await self.course_cluster_model.save_clustering_result(
                course_id=course_id,
                optimal_k=optimal_k,
                clusters=clusters_data,
                features_used=selected_features,
                metadata=metadata
            )
            
            # Update user cluster history
            await self.user_history_model.bulk_add_assignments(course_id, user_cluster_map)
            
            logger.info(f"✓ Clustering job completed for course {course_id}")
            logger.info(f"  Execution time: {execution_time:.2f}s")
            logger.info(f"  Result ID: {result_id}")
            
            return {
                "status": "success",
                "course_id": course_id,
                "optimal_k": optimal_k,
                "total_students": total_students,
                "execution_time": execution_time,
                "result_id": result_id
            }
            
        except Exception as e:
            logger.error(f"Clustering job failed for course {course_id}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "course_id": course_id,
                "error": str(e)
            }
