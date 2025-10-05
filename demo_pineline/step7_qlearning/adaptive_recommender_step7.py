
# ============================================================================
# ADAPTIVE LEARNING RECOMMENDATION SYSTEM
# Generated from Q-Learning Training (Bước 7)
# ============================================================================

import numpy as np
import json

class AdaptiveLearningRecommender:
    """
    Q-learning based content recommendation system
    """

    def __init__(self, q_table_path, metadata_path, mappings_path):
        """Load trained Q-table và metadata"""
        # Load Q-table
        self.Q_table = np.load(q_table_path)

        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        self.knowledge_bins = metadata['state_space']['knowledge_bins']
        self.performance_bins = metadata['state_space']['performance_bins']
        self.actions = metadata['action_space']['actions']

        # Load mappings
        with open(mappings_path, 'r') as f:
            mappings = json.load(f)

        self.state_to_idx = {eval(k): v for k, v in mappings['state_to_idx'].items()}
        self.action_to_idx = mappings['action_to_idx']

        print("✅ Recommender system loaded successfully!")

    def discretize_state(self, archetype, knowledge, performance):
        """Convert continuous state to discrete"""
        k_bin = np.digitize([knowledge], self.knowledge_bins)[0] - 1
        k_bin = max(0, min(len(self.knowledge_bins) - 2, k_bin))

        p_bin = np.digitize([performance], self.performance_bins)[0] - 1
        p_bin = max(0, min(len(self.performance_bins) - 2, p_bin))

        return (archetype, k_bin, p_bin)

    def recommend(self, archetype, knowledge_level, recent_performance):
        """
        Recommend content based on student state

        Args:
            archetype: Student learning archetype (string)
            knowledge_level: Current knowledge level [0, 1]
            recent_performance: Recent average grade [0, 10]

        Returns:
            recommended_action: Best content type to recommend
            q_value: Confidence score
        """
        # Discretize state
        state = self.discretize_state(archetype, knowledge_level, recent_performance)

        # Look up in Q-table
        if state in self.state_to_idx:
            state_idx = self.state_to_idx[state]
            q_values = self.Q_table[state_idx]

            best_action_idx = np.argmax(q_values)
            recommended_action = self.actions[best_action_idx]
            q_value = float(q_values[best_action_idx])
        else:
            # Fallback to most common action if state not seen
            recommended_action = "video_view"  # Safe default
            q_value = 0.0

        return recommended_action, q_value

    def recommend_top_k(self, archetype, knowledge_level, recent_performance, k=3):
        """Recommend top-k actions"""
        state = self.discretize_state(archetype, knowledge_level, recent_performance)

        if state in self.state_to_idx:
            state_idx = self.state_to_idx[state]
            q_values = self.Q_table[state_idx]

            # Get top-k actions
            top_k_indices = np.argsort(q_values)[-k:][::-1]
            recommendations = [
                {{
                    'action': self.actions[idx],
                    'q_value': float(q_values[idx])
                }}
                for idx in top_k_indices
            ]
        else:
            recommendations = [
                {{'action': 'video_view', 'q_value': 0.0}},
                {{'action': 'resource_view', 'q_value': 0.0}},
                {{'action': 'quiz_attempt', 'q_value': 0.0}}
            ][:k]

        return recommendations

# Example usage:
# recommender = AdaptiveLearningRecommender(
#     'q_table_step7.npy',
#     'qlearning_metadata_step7.json',
#     'state_action_mappings_step7.json'
# )
# 
# action, confidence = recommender.recommend(
#     archetype='High Achiever',
#     knowledge_level=0.65,
#     recent_performance=7.5
# )
# print(f"Recommended: {{action}} (confidence: {{confidence:.2f}})")
