export type UserRole = 'STUDENT' | 'INSTRUCTOR' | 'ADMIN';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

// export interface Lesson {
//   id: string;
//   title: string;
//   description: string;
//   status: 'not_started' | 'in_progress' | 'completed';
//   score?: number;
//   difficulty: 'easy' | 'medium' | 'hard';
//   estimatedTime: number; // minutes
//   order: number;
//   views?: number;
// }

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


// Resource: Tài nguyên (quiz, video, sgk,...)
export interface Resource {
  id: number | string;
  name: string;
  modname: string; // forum, qbank, quiz, resource, hvp,...
}

// Lesson: Bài học trong section
export interface Lesson {
  sectionIdOld: number;
  sectionIdNew: number;
  name: string;
  resources: Resource[];
}

// Section: Một chủ đề hoặc phần (có thể chứa lessons hoặc resources)
export interface Section {
  sectionid?: number;        // với "General" thì có field này
  sectionIdOld?: number;     // với các section còn lại thì có field này
  name: string;
  lessons?: Lesson[];
  resources?: Resource[];
}

// Course: Tổng thể một khoá học
export interface Course {
  _id: string;
  courseCode: string;
  title: string;
  sections: Section[];
}