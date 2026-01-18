export type UserRole = 'STUDENT' | 'INSTRUCTOR' | 'ADMIN';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  lastActivity?: string;
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  progress: number;
  totalSteps: number;
  currentStep: number;
  estimatedTime: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  topics: Topic[];
}

export interface Topic {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  videos: Video[];
  assignments: Assignment[];
  order: number;
}

export interface Video {
  id: string;
  title: string;
  duration: string;
  watchCount: number;
  watched: boolean;
  thumbnail?: string;
  url: string;
}

export interface Assignment {
  id: string;
  title: string;
  type: 'quiz' | 'essay' | 'project';
  completed: boolean;
  score?: number;
  dueDate: string;
}

export interface StudentProgress {
  studentId: string;
  studentName: string;
  avatar?: string;
  overallProgress: number;
  learningPath: LearningPath;
  recentActivities: Activity[];
  performanceMetrics: {
    videosWatched: number;
    assignmentsCompleted: number;
    averageScore: number;
    timeSpent: string;
  };
}

export interface Activity {
  id: string;
  type: 'video_watch' | 'assignment_submit' | 'quiz_complete' | 'login';
  description: string;
  timestamp: string;
  metadata?: any;
}

export interface VideoAnalytics {
  videoId: string;
  title: string;
  totalViews: number;
  uniqueViewers: number;
  averageWatchTime: string;
  completionRate: number;
  thumbnail?: string;
}

export interface ActionAnalytics {
  actionType: string;
  count: number;
  description: string;
  trend: 'up' | 'down' | 'stable';
  percentage: number;
}
