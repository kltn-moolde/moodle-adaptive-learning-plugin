import type { 
  User, 
  LearningPath, 
  Activity, 
  StudentProgress, 
  VideoAnalytics, 
  ActionAnalytics 
} from '../types';

// Mock Users
export const mockUsers: User[] = [
  {
    id: '1',
    name: 'John Student',
    email: 'john.student@example.com',
    role: 'STUDENT',
    lastActivity: '2025-08-20T10:30:00Z'
  },
  {
    id: '2',
    name: 'Alice Smith',
    email: 'alice.smith@example.com',
    role: 'INSTRUCTOR',
    lastActivity: '2025-08-20T09:15:00Z'
  },
  {
    id: '3',
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'ADMIN',
    lastActivity: '2025-08-20T11:00:00Z'
  },
  {
    id: '4',
    name: 'Jane Doe',
    email: 'jane.doe@example.com',
    role: 'STUDENT',
    lastActivity: '2025-08-19T16:45:00Z'
  },
  {
    id: '5',
    name: 'Bob Teacher',
    email: 'bob.teacher@example.com',
    role: 'INSTRUCTOR',
    lastActivity: '2025-08-20T08:30:00Z'
  }
];

// Mock Learning Path
export const mockLearningPath: LearningPath = {
  id: 'lp-1',
  title: 'Introduction to Data Science',
  description: 'Learn the fundamentals of data science including statistics, programming, and machine learning.',
  progress: 65,
  totalSteps: 8,
  currentStep: 5,
  estimatedTime: '6 weeks',
  difficulty: 'Intermediate',
  topics: [
    {
      id: 'topic-1',
      title: 'Python Fundamentals',
      description: 'Learn basic Python programming concepts',
      completed: true,
      order: 1,
      videos: [
        { id: 'v1', title: 'Python Basics', duration: '45:00', watchCount: 120, watched: true, url: '#' },
        { id: 'v2', title: 'Data Types', duration: '30:00', watchCount: 98, watched: true, url: '#' }
      ],
      assignments: [
        { id: 'a1', title: 'Python Quiz', type: 'quiz', completed: true, score: 85, dueDate: '2025-08-15' }
      ]
    },
    {
      id: 'topic-2',
      title: 'Data Manipulation with Pandas',
      description: 'Master data manipulation using Pandas library',
      completed: true,
      order: 2,
      videos: [
        { id: 'v3', title: 'Pandas Introduction', duration: '60:00', watchCount: 87, watched: true, url: '#' }
      ],
      assignments: [
        { id: 'a2', title: 'Data Cleaning Project', type: 'project', completed: true, score: 92, dueDate: '2025-08-18' }
      ]
    },
    {
      id: 'topic-3',
      title: 'Data Visualization',
      description: 'Create compelling visualizations with Matplotlib and Seaborn',
      completed: true,
      order: 3,
      videos: [
        { id: 'v4', title: 'Matplotlib Basics', duration: '50:00', watchCount: 76, watched: true, url: '#' },
        { id: 'v5', title: 'Seaborn Advanced', duration: '40:00', watchCount: 65, watched: true, url: '#' }
      ],
      assignments: [
        { id: 'a3', title: 'Visualization Project', type: 'project', completed: true, score: 88, dueDate: '2025-08-22' }
      ]
    },
    {
      id: 'topic-4',
      title: 'Statistical Analysis',
      description: 'Learn statistical methods for data analysis',
      completed: true,
      order: 4,
      videos: [
        { id: 'v6', title: 'Descriptive Statistics', duration: '35:00', watchCount: 54, watched: true, url: '#' }
      ],
      assignments: [
        { id: 'a4', title: 'Statistics Quiz', type: 'quiz', completed: true, score: 90, dueDate: '2025-08-25' }
      ]
    },
    {
      id: 'topic-5',
      title: 'Machine Learning Basics',
      description: 'Introduction to machine learning concepts',
      completed: false,
      order: 5,
      videos: [
        { id: 'v7', title: 'ML Overview', duration: '45:00', watchCount: 42, watched: false, url: '#' },
        { id: 'v8', title: 'Supervised Learning', duration: '55:00', watchCount: 38, watched: false, url: '#' }
      ],
      assignments: [
        { id: 'a5', title: 'ML Project', type: 'project', completed: false, dueDate: '2025-09-01' }
      ]
    },
    {
      id: 'topic-6',
      title: 'Deep Learning',
      description: 'Advanced neural networks and deep learning',
      completed: false,
      order: 6,
      videos: [
        { id: 'v9', title: 'Neural Networks', duration: '60:00', watchCount: 25, watched: false, url: '#' }
      ],
      assignments: [
        { id: 'a6', title: 'Neural Network Project', type: 'project', completed: false, dueDate: '2025-09-08' }
      ]
    },
    {
      id: 'topic-7',
      title: 'Model Deployment',
      description: 'Deploy machine learning models to production',
      completed: false,
      order: 7,
      videos: [
        { id: 'v10', title: 'Model Deployment', duration: '50:00', watchCount: 18, watched: false, url: '#' }
      ],
      assignments: [
        { id: 'a7', title: 'Deployment Project', type: 'project', completed: false, dueDate: '2025-09-15' }
      ]
    },
    {
      id: 'topic-8',
      title: 'Final Project',
      description: 'Comprehensive data science project',
      completed: false,
      order: 8,
      videos: [],
      assignments: [
        { id: 'a8', title: 'Capstone Project', type: 'project', completed: false, dueDate: '2025-09-22' }
      ]
    }
  ]
};

// Mock Activities
export const mockActivities: Activity[] = [
  {
    id: 'act-1',
    type: 'video_watch',
    description: 'Completed watching "Statistical Analysis Overview"',
    timestamp: '2025-08-20T10:30:00Z'
  },
  {
    id: 'act-2',
    type: 'assignment_submit',
    description: 'Submitted "Data Visualization Project"',
    timestamp: '2025-08-20T09:15:00Z'
  },
  {
    id: 'act-3',
    type: 'quiz_complete',
    description: 'Completed "Python Fundamentals Quiz" with 85% score',
    timestamp: '2025-08-19T16:45:00Z'
  },
  {
    id: 'act-4',
    type: 'login',
    description: 'Logged into the learning platform',
    timestamp: '2025-08-19T14:20:00Z'
  }
];

// Mock Student Progress Data
export const mockStudentProgress: StudentProgress[] = [
  {
    studentId: '1',
    studentName: 'John Student',
    overallProgress: 65,
    learningPath: mockLearningPath,
    recentActivities: mockActivities,
    performanceMetrics: {
      videosWatched: 12,
      assignmentsCompleted: 8,
      averageScore: 88,
      timeSpent: '24.5h'
    }
  },
  {
    studentId: '4',
    studentName: 'Jane Doe',
    overallProgress: 42,
    learningPath: {
      ...mockLearningPath,
      progress: 42,
      currentStep: 3
    },
    recentActivities: mockActivities.slice(0, 2),
    performanceMetrics: {
      videosWatched: 8,
      assignmentsCompleted: 5,
      averageScore: 92,
      timeSpent: '18.2h'
    }
  },
  {
    studentId: '6',
    studentName: 'Mike Johnson',
    overallProgress: 78,
    learningPath: {
      ...mockLearningPath,
      progress: 78,
      currentStep: 6
    },
    recentActivities: mockActivities.slice(1, 3),
    performanceMetrics: {
      videosWatched: 15,
      assignmentsCompleted: 10,
      averageScore: 85,
      timeSpent: '32.1h'
    }
  }
];

// Mock Video Analytics
export const mockVideoAnalytics: VideoAnalytics[] = [
  {
    videoId: 'v1',
    title: 'Python Basics',
    totalViews: 245,
    uniqueViewers: 120,
    averageWatchTime: '38:30',
    completionRate: 85
  },
  {
    videoId: 'v2',
    title: 'Data Types in Python',
    totalViews: 198,
    uniqueViewers: 98,
    averageWatchTime: '25:45',
    completionRate: 78
  },
  {
    videoId: 'v3',
    title: 'Pandas Introduction',
    totalViews: 167,
    uniqueViewers: 87,
    averageWatchTime: '52:15',
    completionRate: 72
  },
  {
    videoId: 'v4',
    title: 'Matplotlib Basics',
    totalViews: 142,
    uniqueViewers: 76,
    averageWatchTime: '45:20',
    completionRate: 68
  },
  {
    videoId: 'v5',
    title: 'Seaborn Advanced',
    totalViews: 118,
    uniqueViewers: 65,
    averageWatchTime: '35:10',
    completionRate: 82
  },
  {
    videoId: 'v6',
    title: 'Descriptive Statistics',
    totalViews: 95,
    uniqueViewers: 54,
    averageWatchTime: '28:45',
    completionRate: 75
  }
];

// Mock Action Analytics
export const mockActionAnalytics: ActionAnalytics[] = [
  {
    actionType: 'Video Views',
    count: 1250,
    description: 'Total video views across all courses',
    trend: 'up',
    percentage: 12
  },
  {
    actionType: 'Assignment Submissions',
    count: 342,
    description: 'Assignments submitted by students',
    trend: 'up',
    percentage: 8
  },
  {
    actionType: 'Quiz Attempts',
    count: 567,
    description: 'Quiz attempts across all courses',
    trend: 'stable',
    percentage: 2
  },
  {
    actionType: 'Discussion Posts',
    count: 89,
    description: 'Posts in course discussion forums',
    trend: 'down',
    percentage: -5
  },
  {
    actionType: 'Course Completions',
    count: 45,
    description: 'Students who completed courses',
    trend: 'up',
    percentage: 15
  },
  {
    actionType: 'Help Requests',
    count: 23,
    description: 'Support tickets submitted',
    trend: 'down',
    percentage: -18
  }
];

// Mock System Metrics
export const mockSystemMetrics = {
  totalUsers: 1250,
  activeUsers: 847,
  totalCourses: 45,
  totalVideos: 320,
  systemUptime: '99.8%',
  averageResponseTime: '245ms'
};
