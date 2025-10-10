interface LearningPathExplanation {
  reason: string;
  current_status: string;
  benefit: string;
  motivation: string;
  next_steps: string[];
}

interface ExplanationResponse {
  success: boolean;
  data: LearningPathExplanation;
  from_cache: boolean;
  note?: string;
}

interface LearningPathData {
  suggested_action: string;
  q_value: number;
  source_state: {
    section_id: number;
    lesson_name: string;
    quiz_level: string;
    complete_rate_bin: number;
    score_bin: number;
  };
}

class LearningPathExplanationService {
  private baseUrl = import.meta.env.VITE_KONG_GATEWAY_URL + '/api';

  async getExplanation(
    userId: string, 
    courseId: string, 
    learningPath: LearningPathData
  ): Promise<LearningPathExplanation | null> {
    try {
      const response = await fetch(`${this.baseUrl}/learning-path/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          course_id: courseId,
          learning_path: learningPath
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ExplanationResponse = await response.json();
      return result.success ? result.data : null;
    } catch (error) {
      console.error('Error getting learning path explanation:', error);
      return null;
    }
  }

  async getUserExplanations(userId: string, courseId: string): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/learning-path/explanations/${userId}/${courseId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result.success ? result.data : [];
    } catch (error) {
      console.error('Error getting user explanations:', error);
      return [];
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/learning-path/health`);
      return response.ok;
    } catch (error) {
      console.error('Learning path service health check failed:', error);
      return false;
    }
  }
}

export const learningPathExplanationService = new LearningPathExplanationService();

export type {
  LearningPathExplanation,
  LearningPathData,
  ExplanationResponse
};