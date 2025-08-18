export type UserRole = 'STUDENT' | 'INSTRUCTOR' | 'ADMIN';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

export interface Lesson {
  id: string;
  title: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed';
  score?: number;
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedTime: number; // minutes
  order: number;
  views?: number;
}

export interface LearningPath {
  id: string;
  studentId: string;
  studentName: string;
  lessons: Lesson[];
  progress: number; // percentage
  totalScore: number;
  lastUpdated: string;
}

export interface CourseStats {
  totalStudents: number;
  averageProgress: number;
  averageScore: number;
  mostViewedLessons: Lesson[];
  leastViewedLessons: Lesson[];
}

export interface StudentProgress {
  id: string;
  name: string;
  email: string;
  progress: number;
  totalScore: number;
  currentLesson?: string;
  lastActivity: string;
}
