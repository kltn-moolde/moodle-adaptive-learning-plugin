import type { User, Lesson, LearningPath, CourseStats, StudentProgress } from '../types';

export const mockUsers: User[] = [
  {
    id: '1',
    name: 'Nguyễn Văn A',
    email: 'student@example.com',
    role: 'STUDENT',
    avatar: 'https://via.placeholder.com/40'
  },
  {
    id: '2',
    name: 'Trần Thị B',
    email: 'instructor@example.com',
    role: 'INSTRUCTOR',
    avatar: 'https://via.placeholder.com/40'
  },
  {
    id: '3',
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'ADMIN',
    avatar: 'https://via.placeholder.com/40'
  }
];

export const mockLessons: Lesson[] = [
  {
    id: '1',
    title: 'Giới thiệu về JavaScript',
    description: 'Tìm hiểu những khái niệm cơ bản về JavaScript',
    status: 'completed',
    score: 95,
    difficulty: 'easy',
    estimatedTime: 30,
    order: 1,
    views: 150
  },
  {
    id: '2',
    title: 'Biến và kiểu dữ liệu',
    description: 'Học cách khai báo biến và các kiểu dữ liệu trong JS',
    status: 'completed',
    score: 88,
    difficulty: 'easy',
    estimatedTime: 45,
    order: 2,
    views: 142
  },
  {
    id: '3',
    title: 'Hàm trong JavaScript',
    description: 'Tìm hiểu về cách tạo và sử dụng hàm',
    status: 'in_progress',
    difficulty: 'medium',
    estimatedTime: 60,
    order: 3,
    views: 98
  },
  {
    id: '4',
    title: 'DOM Manipulation',
    description: 'Học cách thao tác với DOM',
    status: 'not_started',
    difficulty: 'medium',
    estimatedTime: 75,
    order: 4,
    views: 45
  },
  {
    id: '5',
    title: 'Async/Await và Promises',
    description: 'Xử lý bất đồng bộ trong JavaScript',
    status: 'not_started',
    difficulty: 'hard',
    estimatedTime: 90,
    order: 5,
    views: 23
  }
];

export const mockLearningPath: LearningPath = {
  id: '1',
  studentId: '1',
  studentName: 'Nguyễn Văn A',
  lessons: mockLessons,
  progress: 45,
  totalScore: 183,
  lastUpdated: '2025-08-17T09:00:00Z'
};

export const mockStudentProgress: StudentProgress[] = [
  {
    id: '1',
    name: 'Nguyễn Văn A',
    email: 'student1@example.com',
    progress: 45,
    totalScore: 183,
    currentLesson: 'Hàm trong JavaScript',
    lastActivity: '2025-08-17T08:30:00Z'
  },
  {
    id: '2',
    name: 'Trần Thị B',
    email: 'student2@example.com',
    progress: 80,
    totalScore: 456,
    currentLesson: 'Async/Await và Promises',
    lastActivity: '2025-08-17T07:45:00Z'
  },
  {
    id: '3',
    name: 'Lê Văn C',
    email: 'student3@example.com',
    progress: 25,
    totalScore: 120,
    currentLesson: 'Biến và kiểu dữ liệu',
    lastActivity: '2025-08-16T15:20:00Z'
  },
  {
    id: '4',
    name: 'Phạm Thị D',
    email: 'student4@example.com',
    progress: 100,
    totalScore: 487,
    currentLesson: 'Hoàn thành',
    lastActivity: '2025-08-17T06:15:00Z'
  }
];

export const mockCourseStats: CourseStats = {
  totalStudents: 4,
  averageProgress: 62.5,
  averageScore: 311.5,
  mostViewedLessons: mockLessons.slice(0, 3),
  leastViewedLessons: mockLessons.slice(-2)
};
