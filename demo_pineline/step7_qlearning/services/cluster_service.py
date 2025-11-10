"""
Cluster Service
Handles cluster prediction and profiling
"""
from typing import Dict, Tuple
import numpy as np


class ClusterService:
    """Service for cluster prediction and analysis"""
    
    def __init__(self, cluster_profiles: dict):
        self.cluster_profiles = cluster_profiles
        self.cluster_stats = cluster_profiles.get('cluster_stats', {})
    
    def find_closest_cluster(self, features: Dict[str, float]) -> Tuple[int, str]:
        """
        Find closest cluster by comparing student features to cluster feature_means
        using Euclidean distance
        
        Args:
            features: Student feature dict (flat format)
            
        Returns:
            (cluster_id, cluster_name)
        """
        if not self.cluster_stats:
            return (0, 'unknown')
        
        # Get common features
        first_cluster_key = list(self.cluster_stats.keys())[0]
        first_cluster = self.cluster_stats[first_cluster_key]
        feature_means = first_cluster.get('feature_means', {})
        common_features = [k for k in feature_means.keys() if k in features]
        
        if not common_features:
            # Fallback: if no common features, use cluster 0
            return (0, 'unknown')
        
        min_distance = float('inf')
        closest_cluster_id = 0
        closest_cluster_name = 'unknown'
        
        for cluster_key, cluster_data in self.cluster_stats.items():
            cluster_id = cluster_data.get('cluster_id', int(cluster_key))
            cluster_means = cluster_data.get('feature_means', {})
            
            # Get AI profile name if available
            ai_profile = cluster_data.get('ai_profile', {})
            cluster_name = ai_profile.get('profile_name', f'Cluster {cluster_id}')
            
            # Calculate Euclidean distance for common features
            distance = 0.0
            for feature_key in common_features:
                student_val = features.get(feature_key, 0.0)
                cluster_val = cluster_means.get(feature_key, 0.0)
                distance += (student_val - cluster_val) ** 2
            
            distance = np.sqrt(distance)
            
            if distance < min_distance:
                min_distance = distance
                closest_cluster_id = cluster_id
                closest_cluster_name = cluster_name
        
        return (closest_cluster_id, closest_cluster_name)
    
    def get_cluster_info(self, cluster_id: int) -> Dict:
        """Get detailed cluster information"""
        cluster_key = str(cluster_id)
        if cluster_key not in self.cluster_stats:
            return {
                'cluster_id': cluster_id,
                'cluster_name': f'Cluster {cluster_id}',
                'description': 'Unknown cluster'
            }
        
        cluster_data = self.cluster_stats[cluster_key]
        ai_profile = cluster_data.get('ai_profile', {})
        
        return {
            'cluster_id': cluster_id,
            'cluster_name': ai_profile.get('profile_name', f'Cluster {cluster_id}'),
            'description': ai_profile.get('learning_style', ''),
            'strengths': ai_profile.get('strengths', []),
            'challenges': ai_profile.get('challenges', []),
            'recommended_approaches': ai_profile.get('recommended_approaches', [])
        }
