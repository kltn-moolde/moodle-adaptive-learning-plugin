#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAP Analysis for Q-Learning Model
===================================
Explainable AI using SHAP to analyze Q-Learning decisions
"""

import sys
import numpy as np
import pandas as pd
import pickle
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shap
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.rl.agent import QLearningAgentV2
from core.rl.state_builder import StateBuilderV2
from core.rl.action_space import ActionSpace


class QLearningShapAnalyzer:
    """
    SHAP analyzer for Q-Learning model
    
    Explains Q-value predictions by analyzing feature contributions
    """
    
    # State dimension names
    STATE_FEATURES = [
        'cluster_id',
        'module_id', 
        'progress_bin',
        'score_bin',
        'learning_phase',
        'engagement_level'
    ]
    
    def __init__(self, qtable_path: str, course_id: int = 5):
        """
        Initialize SHAP analyzer
        
        Args:
            qtable_path: Path to trained Q-table pickle file
            course_id: Course ID for data loading
        """
        self.qtable_path = Path(qtable_path)
        self.course_id = course_id
        
        # Load Q-table
        print(f"Loading Q-table from: {self.qtable_path}")
        with open(self.qtable_path, 'rb') as f:
            data = pickle.load(f)
        
        # Handle different Q-table formats
        if 'agent' in data:
            # New format: {agent: QLearningAgent, action_space: ActionSpace, ...}
            self.agent = data['agent']
            self.action_space = data.get('action_space', ActionSpace())
            self.q_table = self.agent.q_table
        elif 'q_table' in data:
            # Old format: {q_table: dict, config: dict, stats: dict}
            self.q_table = data['q_table']
            self.action_space = ActionSpace()
            # Create mock agent with q_table
            class MockAgent:
                def __init__(self, q_table):
                    self.q_table = q_table
            self.agent = MockAgent(self.q_table)
        else:
            raise ValueError(f"Unknown Q-table format. Keys: {list(data.keys())}")
        
        print(f"✓ Loaded Q-table with {len(self.q_table)} states")
        print(f"✓ Action space: {self.action_space.get_action_count()} actions")
        
        # Extract all states from Q-table
        self.states = list(self.q_table.keys())
        self.n_actions = self.action_space.get_action_count()
        
    def state_to_features(self, state: Tuple) -> np.ndarray:
        """Convert state tuple to feature array"""
        # Handle string representation of state
        if isinstance(state, str):
            # Parse string like "(2, 0, 0.25, 0.75, 0, 0)" to tuple
            import ast
            state = ast.literal_eval(state)
        
        return np.array(list(state))
    
    def build_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build dataset from Q-table for SHAP analysis
        
        Returns:
            X: Feature matrix (states)
            y: Q-values for best actions
        """
        X = []
        y = []
        
        for state in self.states:
            # Get best action Q-value
            q_values = self.q_table[state]
            if isinstance(q_values, dict) and len(q_values) > 0:
                max_q = max(q_values.values())
            else:
                max_q = 0.0
            
            X.append(self.state_to_features(state))
            y.append(max_q)
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"\n✓ Built dataset: {X.shape[0]} samples, {X.shape[1]} features")
        
        return X, y
    
    def create_prediction_function(self, action_idx: Optional[int] = None):
        """
        Create prediction function for SHAP
        
        Args:
            action_idx: Specific action to analyze (None = best action)
        
        Returns:
            Function that predicts Q-values from feature matrix
        """
        def predict(X):
            """Predict Q-values from features"""
            predictions = []
            
            # Build lookup dict from string states to q_values
            state_lookup = {}
            import ast
            for state_str, q_vals in self.q_table.items():
                if isinstance(state_str, str):
                    state_tuple = ast.literal_eval(state_str)
                    state_lookup[state_tuple] = q_vals
                else:
                    state_lookup[state_str] = q_vals
            
            for features in X:
                # Try to match state in lookup
                state_tuple = tuple(features)
                
                # Try exact match first
                if state_tuple in state_lookup:
                    q_values = state_lookup[state_tuple]
                else:
                    # Try finding closest match (for numerical precision issues)
                    q_values = None
                    for s, q in state_lookup.items():
                        if len(s) == len(state_tuple):
                            # Check if all elements are close
                            if all(abs(float(a) - float(b)) < 1e-6 for a, b in zip(s, state_tuple)):
                                q_values = q
                                break
                
                if q_values is not None:
                    if action_idx is not None:
                        # Specific action
                        if isinstance(q_values, dict):
                            q_value = q_values.get(action_idx, 0.0)
                        else:
                            q_value = 0.0
                    else:
                        # Best action
                        if isinstance(q_values, dict) and len(q_values) > 0:
                            q_value = max(q_values.values())
                        else:
                            q_value = 0.0
                else:
                    q_value = 0.0
                
                predictions.append(q_value)
            
            return np.array(predictions)
        
        return predict
    
    def compute_shap_values(
        self,
        X: np.ndarray,
        action_idx: Optional[int] = None,
        max_samples: int = 100
    ) -> shap.Explanation:
        """
        Compute SHAP values using KernelExplainer
        
        Args:
            X: Feature matrix
            action_idx: Action to analyze (None = best action)
            max_samples: Number of background samples
        
        Returns:
            SHAP explanation object
        """
        print(f"\n{'='*60}")
        print(f"Computing SHAP values...")
        print(f"{'='*60}")
        
        # Sample background data
        if len(X) > max_samples:
            background_indices = np.random.choice(len(X), max_samples, replace=False)
            background = X[background_indices]
        else:
            background = X
        
        print(f"Background samples: {len(background)}")
        
        # Create prediction function
        predict_fn = self.create_prediction_function(action_idx)
        
        # Create SHAP explainer
        explainer = shap.KernelExplainer(predict_fn, background)
        
        # Compute SHAP values for all samples
        print(f"Computing SHAP values for {len(X)} samples...")
        shap_values = explainer.shap_values(X)
        
        print(f"✓ SHAP values computed: shape={shap_values.shape}")
        
        return shap.Explanation(
            values=shap_values,
            base_values=explainer.expected_value,
            data=X,
            feature_names=self.STATE_FEATURES
        )
    
    def analyze_feature_importance(self, explanation: shap.Explanation) -> pd.DataFrame:
        """
        Analyze feature importance from SHAP values
        
        Args:
            explanation: SHAP explanation object
        
        Returns:
            DataFrame with feature importance statistics
        """
        shap_values = explanation.values
        
        # Calculate mean absolute SHAP value for each feature
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        # Calculate variance
        shap_variance = np.var(shap_values, axis=0)
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': self.STATE_FEATURES,
            'mean_abs_shap': mean_abs_shap,
            'shap_variance': shap_variance,
            'importance_rank': pd.Series(mean_abs_shap).rank(ascending=False)
        })
        
        importance_df = importance_df.sort_values('mean_abs_shap', ascending=False)
        
        return importance_df
    
    def analyze_by_cluster(self, X: np.ndarray, explanation: shap.Explanation) -> Dict:
        """
        Analyze SHAP values by cluster
        
        Args:
            X: Feature matrix
            explanation: SHAP explanation
        
        Returns:
            Dictionary with cluster-specific analysis
        """
        cluster_analysis = {}
        
        # Group by cluster (first feature)
        clusters = X[:, 0].astype(int)
        unique_clusters = np.unique(clusters)
        
        for cluster_id in unique_clusters:
            cluster_mask = clusters == cluster_id
            cluster_shap = explanation.values[cluster_mask]
            cluster_features = X[cluster_mask]
            
            # Feature importance for this cluster
            mean_abs_shap = np.mean(np.abs(cluster_shap), axis=0)
            
            cluster_analysis[int(cluster_id)] = {
                'n_samples': int(np.sum(cluster_mask)),
                'mean_abs_shap': mean_abs_shap.tolist(),
                'top_feature': self.STATE_FEATURES[np.argmax(mean_abs_shap)],
                'top_importance': float(np.max(mean_abs_shap))
            }
        
        return cluster_analysis
    
    def save_results(self, output_path: str, explanation: shap.Explanation,
                     importance_df: pd.DataFrame, cluster_analysis: Dict):
        """Save analysis results"""
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save SHAP explanation
        with open(output_path / 'shap_explanation.pkl', 'wb') as f:
            pickle.dump(explanation, f)
        
        # Save feature importance
        importance_df.to_csv(output_path / 'feature_importance.csv', index=False)
        
        # Save cluster analysis
        with open(output_path / 'cluster_analysis.json', 'w') as f:
            json.dump(cluster_analysis, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='SHAP Analysis for Q-Learning')
    parser.add_argument('--qtable', type=str, required=True,
                        help='Path to Q-table pickle file')
    parser.add_argument('--course-id', type=int, default=5,
                        help='Course ID (default: 5)')
    parser.add_argument('--output', type=str, default='data/simulated/shap_analysis',
                        help='Output directory for results')
    parser.add_argument('--max-samples', type=int, default=100,
                        help='Max background samples for SHAP (default: 100)')
    parser.add_argument('--action-idx', type=int, default=None,
                        help='Specific action to analyze (default: best action)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("SHAP ANALYSIS FOR Q-LEARNING")
    print("="*70)
    
    # Initialize analyzer
    analyzer = QLearningShapAnalyzer(args.qtable, args.course_id)
    
    # Build dataset
    X, y = analyzer.build_dataset()
    
    # Compute SHAP values
    explanation = analyzer.compute_shap_values(X, args.action_idx, args.max_samples)
    
    # Analyze feature importance
    importance_df = analyzer.analyze_feature_importance(explanation)
    print("\n=== FEATURE IMPORTANCE ===")
    print(importance_df)
    
    # Analyze by cluster
    cluster_analysis = analyzer.analyze_by_cluster(X, explanation)
    print("\n=== CLUSTER ANALYSIS ===")
    for cluster_id, analysis in cluster_analysis.items():
        print(f"\nCluster {cluster_id}:")
        print(f"  Samples: {analysis['n_samples']}")
        print(f"  Top feature: {analysis['top_feature']} ({analysis['top_importance']:.4f})")
    
    # Save results
    analyzer.save_results(args.output, explanation, importance_df, cluster_analysis)
    
    print("\n"+"="*70)
    print("SHAP ANALYSIS COMPLETED!")
    print("="*70)
    print(f"\nNext step: Run plot_shap_visualizations.py to create plots")


if __name__ == '__main__':
    main()
