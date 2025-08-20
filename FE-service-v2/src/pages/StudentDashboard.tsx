import React from 'react';
import type { LearningPath, Activity } from '../types';

interface StudentDashboardProps {
  learningPath: LearningPath;
  recentActivities: Activity[];
}

const StudentDashboard: React.FC<StudentDashboardProps> = ({ learningPath, recentActivities }) => {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800';
      case 'Intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'Advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'video_watch':
        return 'fas fa-play-circle text-blue-500';
      case 'assignment_submit':
        return 'fas fa-upload text-green-500';
      case 'quiz_complete':
        return 'fas fa-check-circle text-purple-500';
      case 'login':
        return 'fas fa-sign-in-alt text-gray-500';
      default:
        return 'fas fa-circle text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Learning Path Overview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-primary-800">My Learning Path</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(learningPath.difficulty)}`}>
            {learningPath.difficulty}
          </span>
        </div>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-2">{learningPath.title}</h3>
        <p className="text-gray-600 mb-4">{learningPath.description}</p>
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress: {learningPath.currentStep} of {learningPath.totalSteps} steps</span>
            <span>{learningPath.progress}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-primary-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${learningPath.progress}%` }}
            ></div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span><i className="fas fa-clock mr-1"></i> {learningPath.estimatedTime}</span>
          <span><i className="fas fa-list mr-1"></i> {learningPath.topics.length} Topics</span>
        </div>
      </div>

      {/* Roadmap */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-6">Learning Roadmap</h3>
        
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-primary-200"></div>
          
          <div className="space-y-6">
            {learningPath.topics.map((topic, index) => (
              <div key={topic.id} className="relative flex items-start">
                {/* Step circle */}
                <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full border-4 ${
                  topic.completed 
                    ? 'bg-primary-500 border-primary-500' 
                    : index === learningPath.currentStep - 1
                    ? 'bg-white border-primary-500'
                    : 'bg-white border-gray-300'
                }`}>
                  {topic.completed ? (
                    <i className="fas fa-check text-white text-lg"></i>
                  ) : index === learningPath.currentStep - 1 ? (
                    <span className="text-primary-500 font-bold">{index + 1}</span>
                  ) : (
                    <span className="text-gray-400 font-bold">{index + 1}</span>
                  )}
                </div>
                
                {/* Content */}
                <div className="ml-6 flex-1">
                  <div className={`p-4 rounded-lg border-2 ${
                    topic.completed 
                      ? 'bg-primary-50 border-primary-200' 
                      : index === learningPath.currentStep - 1
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}>
                    <h4 className="font-semibold text-gray-800 mb-2">{topic.title}</h4>
                    <p className="text-gray-600 text-sm mb-3">{topic.description}</p>
                    
                    {/* Videos and Assignments */}
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="flex items-center text-blue-600">
                        <i className="fas fa-video mr-1"></i>
                        {topic.videos.length} Videos
                      </span>
                      <span className="flex items-center text-green-600">
                        <i className="fas fa-tasks mr-1"></i>
                        {topic.assignments.length} Assignments
                      </span>
                    </div>
                    
                    {/* Action Button */}
                    {!topic.completed && index === learningPath.currentStep - 1 && (
                      <button className="mt-3 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
                        Continue Learning
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4">Recent Activities</h3>
        
        <div className="space-y-4">
          {recentActivities.map((activity) => (
            <div key={activity.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
              <i className={getActivityIcon(activity.type)}></i>
              <div className="flex-1">
                <p className="text-gray-800">{activity.description}</p>
                <p className="text-sm text-gray-500">{activity.timestamp}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
