/**
 * Q-Learning API Service
 * Calls to http://139.99.103.223:8088
 */

const QLEARNING_API_BASE = 'http://139.99.103.223:8088/api';

export interface ClusterInfo {
  cluster_id: number;
  profile_name: string;
  n_students: number;
  percentage: number;
}

export interface ClusterProfile {
  profile_name: string;
  description: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  created_at?: string;
}

export interface ClusterDetail {
  cluster_id: number;
  statistics: {
    n_students: number;
    percentage: number;
    top_features: Array<{
      feature: string;
      z_score: number;
      interpretation: string;
    }>;
  };
  existing_profile: ClusterProfile | null;
}

export interface RecommendationRequest {
  student_id: number;
  features: {
    knowledge_level: number;
    engagement_level: number;
    struggle_indicator: number;
    submission_activity: number;
    review_activity: number;
    resource_usage: number;
    assessment_engagement: number;
    collaborative_activity: number;
    overall_progress: number;
    module_completion_rate: number;
    activity_diversity: number;
    completion_consistency: number;
  };
  top_k?: number;
}

export interface RecommendationResponse {
  success: boolean;
  student_id: number;
  cluster_id: number;
  cluster_name: string;
  state_vector: number[];
  state_description: {
    performance: {
      knowledge_level: number;
      engagement_level: number;
      struggle_indicator: number;
    };
    activity_patterns: {
      submission_activity: number;
      review_activity: number;
      resource_usage: number;
      assessment_engagement: number;
      collaborative_activity: number;
    };
    completion_metrics: {
      overall_progress: number;
      module_completion_rate: number;
      activity_diversity: number;
      completion_consistency: number;
    };
  };
  recommendations: Array<{
    action_id: number;
    name: string;
    type: string;
    purpose: string;
    difficulty: string;
    q_value: number;
  }>;
  model_info: {
    model_loaded: boolean;
    n_states_in_qtable: number;
    total_updates: number;
    episodes: number;
  };
}

/**
 * Get list of all clusters
 */
export async function getClusters(): Promise<{
  total_clusters: number;
  total_students: number;
  clusters: ClusterInfo[];
}> {
  const response = await fetch(`${QLEARNING_API_BASE}/clusters/list`);
  if (!response.ok) {
    throw new Error(`Failed to fetch clusters: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get detailed cluster information
 */
export async function getClusterDetail(clusterId: number): Promise<ClusterDetail> {
  const response = await fetch(`${QLEARNING_API_BASE}/clusters/${clusterId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch cluster ${clusterId}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Generate LLM profile for a cluster
 */
export async function generateClusterProfile(clusterId: number): Promise<{
  cluster_id: number;
  profile: ClusterProfile;
  llm_provider: string;
}> {
  const response = await fetch(`${QLEARNING_API_BASE}/clusters/${clusterId}/profile`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to generate profile for cluster ${clusterId}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get recommendation for student
 */
export async function getRecommendation(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  const response = await fetch(`${QLEARNING_API_BASE}/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Failed to get recommendation: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get Q-table statistics
 */
export async function getQTableStats(): Promise<{
  total_states: number;
  total_actions: number;
  trained_states: number;
  coverage_percentage: number;
}> {
  const response = await fetch(`${QLEARNING_API_BASE}/qtable/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch Q-table stats: ${response.statusText}`);
  }
  return response.json();
}
