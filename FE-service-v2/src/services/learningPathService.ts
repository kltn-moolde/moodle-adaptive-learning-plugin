// Learning Path API Service
import { kongApi } from './kongApiService';

export interface SuggestedAction {
  course_id: number;
  q_value: number;
  source_state: {
    complete_rate_bin: number;
    lesson_name: string;
    quiz_level: string;
    score_bin: number;
    section_id: number;
  };
  suggested_action: string;
  user_id: number;
}

export interface LearningStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  current: boolean;
  action: string;
  section_id: number;
  quiz_level: string;
  score_bin: number;
  complete_rate: number;
  lesson_name: string;
}

export interface LearningPathData {
  course_id: number;
  user_id: number;
  current_step: number;
  total_steps: number;
  progress: number;
  steps: LearningStep[];
  next_action: SuggestedAction | null;
}

export class LearningPathService {
  private baseURL: string;

  constructor(baseURL: string = import.meta.env.VITE_KONG_GATEWAY_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  // Get suggested next action for user
  async getSuggestedAction(userId: number, courseId: number): Promise<SuggestedAction> {
    try {
      const response = await fetch(`${this.baseURL}/api/suggest-action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${kongApi.getToken()}`
        },
        body: JSON.stringify({
          user_id: userId,
          course_id: courseId
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to get suggested action: ${response.status}`);
      }

      const data: SuggestedAction = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting suggested action:', error);
      throw error;
    }
  }

  // Get complete learning path for user
  async getLearningPath(userId: number, courseId: number): Promise<LearningPathData> {
    try {
      // Get suggested action first
      const suggestedAction = await this.getSuggestedAction(userId, courseId);
      
      // Generate learning path based on suggested action
      const learningPath = this.generateLearningPathFromAction(suggestedAction);
      
      return learningPath;
    } catch (error) {
      console.error('Error getting learning path:', error);
      // Return fallback data if API fails
      return this.getFallbackLearningPath(userId, courseId);
    }
  }

  // Generate learning path based on suggested action
  private generateLearningPathFromAction(action: SuggestedAction): LearningPathData {
    const steps = this.generateStepsFromAction(action);
    const currentStepIndex = steps.findIndex(step => step.current);
    
    return {
      course_id: action.course_id,
      user_id: action.user_id,
      current_step: currentStepIndex + 1,
      total_steps: steps.length,
      progress: Math.round((currentStepIndex / steps.length) * 100),
      steps: steps,
      next_action: action
    };
  }

  // Generate steps based on suggested action
  private generateStepsFromAction(action: SuggestedAction): LearningStep[] {
    const { source_state, suggested_action } = action;

    // Generate steps based on current state and suggested action
    const steps: LearningStep[] = [
      {
        id: 'intro',
        title: 'Introduction to Course',
        description: 'Get familiar with course materials and objectives',
        completed: source_state.complete_rate_bin > 0.2,
        current: false,
        action: 'read_material',
        section_id: 1,
        quiz_level: 'easy',
        score_bin: 1,
        complete_rate: 0.1,
        lesson_name: source_state.lesson_name
      },
      {
        id: 'basic_concepts',
        title: 'Basic Concepts',
        description: 'Learn fundamental concepts and terminology',
        completed: source_state.complete_rate_bin > 0.4,
        current: false,
        action: 'watch_video',
        section_id: 2,
        quiz_level: 'easy',
        score_bin: 3,
        complete_rate: 0.3,
        lesson_name: source_state.lesson_name
      },
      {
        id: 'current_section',
        title: `Section ${source_state.section_id}`,
        description: this.getActionDescription(suggested_action),
        completed: false,
        current: true,
        action: suggested_action,
        section_id: source_state.section_id,
        quiz_level: source_state.quiz_level,
        score_bin: source_state.score_bin,
        complete_rate: source_state.complete_rate_bin,
        lesson_name: source_state.lesson_name
      }
    ];

    // Add future steps based on suggested action
    if (suggested_action.includes('quiz')) {
      steps.push({
        id: 'advanced_practice',
        title: 'Advanced Practice',
        description: 'Apply knowledge with advanced exercises',
        completed: false,
        current: false,
        action: 'do_advanced_quiz',
        section_id: source_state.section_id + 1,
        quiz_level: 'hard',
        score_bin: source_state.score_bin + 2,
        complete_rate: source_state.complete_rate_bin + 0.2,
        lesson_name: source_state.lesson_name
      });
    }

    steps.push({
      id: 'final_assessment',
      title: 'Final Assessment',
      description: 'Complete the course with final evaluation',
      completed: false,
      current: false,
      action: 'final_exam',
      section_id: source_state.section_id + 2,
      quiz_level: 'hard',
      score_bin: 10,
      complete_rate: 1.0,
      lesson_name: source_state.lesson_name
    });

    return steps;
  }

  // Get action description based on suggested action
  private getActionDescription(action: string): string {
    const actionDescriptions: Record<string, string> = {
      'do_quiz_same': 'Take a quiz at your current level to reinforce understanding',
      'do_quiz_easy': 'Start with an easier quiz to build confidence',
      'do_quiz_hard': 'Challenge yourself with a more difficult quiz',
      'watch_video': 'Watch instructional videos to learn new concepts',
      'read_material': 'Read course materials and documentation',
      'review_notes': 'Review your notes and previous materials',
      'get_help': 'Seek help from instructor or peers',
      'practice_more': 'Complete additional practice exercises'
    };

    return actionDescriptions[action] || 'Continue with the next learning activity';
  }

  // Fallback learning path if API fails
  private getFallbackLearningPath(userId: number, courseId: number): LearningPathData {
    return {
      course_id: courseId,
      user_id: userId,
      current_step: 1,
      total_steps: 4,
      progress: 25,
      steps: [
        {
          id: 'intro',
          title: 'Course Introduction',
          description: 'Get started with the course basics',
          completed: false,
          current: true,
          action: 'read_material',
          section_id: 1,
          quiz_level: 'easy',
          score_bin: 1,
          complete_rate: 0.0,
          lesson_name: 'Introduction to Course'
        },
        {
          id: 'concepts',
          title: 'Core Concepts',
          description: 'Learn the fundamental concepts',
          completed: false,
          current: false,
          action: 'watch_video',
          section_id: 2,
          quiz_level: 'medium',
          score_bin: 5,
          complete_rate: 0.3,
          lesson_name: 'Basic Concepts'
        },
        {
          id: 'practice',
          title: 'Practice Exercises',
          description: 'Apply what you have learned',
          completed: false,
          current: false,
          action: 'do_quiz_same',
          section_id: 3,
          quiz_level: 'medium',
          score_bin: 7,
          complete_rate: 0.6,
          lesson_name: 'Practice Exercises'
        },
        {
          id: 'assessment',
          title: 'Final Assessment',
          description: 'Complete the final evaluation',
          completed: false,
          current: false,
          action: 'final_exam',
          section_id: 4,
          quiz_level: 'hard',
          score_bin: 10,
          complete_rate: 1.0,
          lesson_name: 'Final Assessment'
        }
      ],
      next_action: null
    };
  }

  // Execute suggested action (navigate to action)
  async executeAction(action: SuggestedAction): Promise<void> {
    try {
      // This could trigger navigation to specific content or update user progress
      console.log('Executing action:', action.suggested_action);
      
      // You can add specific logic here based on action type
      switch (action.suggested_action) {
        case 'do_quiz_same':
        case 'do_quiz_easy':
        case 'do_quiz_hard':
          // Navigate to quiz page
          window.location.href = `/quiz/${action.course_id}/${action.source_state.section_id}`;
          break;
        case 'watch_video':
          // Navigate to video page
          window.location.href = `/video/${action.course_id}/${action.source_state.section_id}`;
          break;
        case 'read_material':
          // Navigate to reading material
          window.location.href = `/material/${action.course_id}/${action.source_state.section_id}`;
          break;
        default:
          console.log('Unknown action type:', action.suggested_action);
      }
    } catch (error) {
      console.error('Error executing action:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const learningPathService = new LearningPathService();