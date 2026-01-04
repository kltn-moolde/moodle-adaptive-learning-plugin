// TypeScript types for Student Clustering Analysis

export interface ClusteringOverview {
  course_id: number;
  run_timestamp: string;
  overview: {
    overall_metrics: {
      total_students: number;
      total_logs: number;
      features_analyzed: number;
      optimal_clusters: number;
      clustering_quality: {
        silhouette_score: number;
        davies_bouldin_index: number;
      };
    };
    cluster_distribution: ClusterDistribution[];
    cluster_summaries: ClusterSummary[];
  };
}

export interface ClusterDistribution {
  cluster_id: number;
  cluster_name: string;
  student_count: number;
  percentage: number;
}

export interface ClusterSummary {
  cluster_id: number;
  name: string;
  description: string;
  student_count: number;
  key_characteristics: string[];
}

export interface ClusteringResults {
  _id: string;
  course_id: number;
  run_timestamp: string;
  optimal_k: number;
  clusters: ClusterDetail[];
  features_used: string[];
  metadata: {
    total_students: number;
    total_logs: number;
    features_extracted: number;
    features_selected: number;
    execution_time_seconds: number;
    clustering_metrics: {
      inertia: number;
      silhouette: number;
      davies_bouldin: number;
    };
  };
}

export interface ClusterDetail {
  cluster_id: number;
  user_ids: number[];
  size: number;
  percentage: number;
  name: string;
  description: string;
  characteristics: string[];
  recommendations: string[];
  statistics: {
    feature_means: Record<string, number>;
    feature_stds: Record<string, number>;
    top_features: TopFeature[];
  };
}

export interface TopFeature {
  feature: string;
  value: number;
  interpretation: "higher" | "lower" | "similar";
}

// Cluster color mapping constants
export const CLUSTER_COLORS = [
  "#16A34A", // Green - Cluster 0 - Evening Active
  "#14B8A6", // Teal - Cluster 1 - Super Engager
  "#A855F7", // Purple - Cluster 2 - Passive/Average
  "#3B82F6", // Blue - Cluster 3 - Quiz Focused
  "#F59E0B", // Amber - Cluster 4 - Structure Explorer
  "#EF4444", // Red - Cluster 5 - Result Oriented
];

// Helper function to get cluster color
export function getClusterColor(clusterId: number): string {
  return CLUSTER_COLORS[clusterId] || "#64748B"; // Fallback to gray
}
