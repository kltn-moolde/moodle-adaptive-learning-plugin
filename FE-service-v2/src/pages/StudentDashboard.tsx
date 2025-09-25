import React, { useState, useEffect } from 'react';
import { learningPathService, type LearningPathData } from '../services/learningPathService';

interface StudentDashboardProps {
  userId: number;
  courseId: number;
}

const StudentDashboard: React.FC<StudentDashboardProps> = ({ userId, courseId }) => {
  const [learningPath, setLearningPath] = useState<LearningPathData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load learning path on component mount
  useEffect(() => {
    const loadLearningPath = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Call real API to get learning path
        const pathData = await learningPathService.getLearningPath(userId, courseId);
        setLearningPath(pathData);
      } catch (err) {
        console.error('Error loading learning path:', err);
        setError('Failed to load learning path. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadLearningPath();
  }, [userId, courseId]);

  const getDifficultyColor = (quizLevel: string) => {
    switch (quizLevel) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };



  const handleExecuteAction = async () => {
    if (learningPath?.next_action) {
      try {
        await learningPathService.executeAction(learningPath.next_action);
      } catch (err) {
        console.error('Error executing action:', err);
      }
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <i className="fas fa-exclamation-triangle text-red-500 mr-2"></i>
          <span className="text-red-700">{error}</span>
        </div>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Retry
        </button>
      </div>
    );
  }

  // No data state
  if (!learningPath) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">No learning path available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Learning Path Overview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-primary-800">My Learning Path</h2>
          {learningPath.next_action && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(learningPath.next_action.source_state.quiz_level)}`}>
              {learningPath.next_action.source_state.quiz_level}
            </span>
          )}
        </div>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-2">Course {learningPath.course_id} Learning Path</h3>
        <p className="text-gray-600 mb-4">
          {learningPath.next_action ? 
            `Next recommended action: ${learningPath.next_action.suggested_action.replace(/_/g, ' ')}` :
            'Continue with your learning journey'
          }
        </p>
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress: {learningPath.current_step} of {learningPath.total_steps} steps</span>
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
          <span><i className="fas fa-user mr-1"></i> User {learningPath.user_id}</span>
          <span><i className="fas fa-list mr-1"></i> {learningPath.steps.length} Steps</span>
          {learningPath.next_action && (
            <span><i className="fas fa-chart-line mr-1"></i> Q-Value: {learningPath.next_action.q_value.toFixed(2)}</span>
          )}
        </div>

        {/* Next Action Button */}
        {learningPath.next_action && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button 
              onClick={handleExecuteAction}
              className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              <i className="fas fa-play mr-2"></i>
              {learningPath.next_action.suggested_action.replace(/_/g, ' ').toUpperCase()}
            </button>
          </div>
        )}
      </div>

      {/* Roadmap */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-6">Learning Roadmap</h3>
        
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-primary-200"></div>
          
          <div className="space-y-6">
            {learningPath.steps.map((step, index) => (
              <div key={index} className="relative flex items-start">
                {/* Step circle */}
                <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full border-4 ${
                  step.completed 
                    ? 'bg-primary-500 border-primary-500' 
                    : index === learningPath.current_step - 1
                    ? 'bg-white border-primary-500'
                    : 'bg-white border-gray-300'
                }`}>
                  {step.completed ? (
                    <i className="fas fa-check text-white text-lg"></i>
                  ) : index === learningPath.current_step - 1 ? (
                    <span className="text-primary-500 font-bold">{index + 1}</span>
                  ) : (
                    <span className="text-gray-400 font-bold">{index + 1}</span>
                  )}
                </div>
                
                {/* Content */}
                <div className="ml-6 flex-1">
                  <div className={`p-4 rounded-lg border-2 ${
                    step.completed 
                      ? 'bg-primary-50 border-primary-200' 
                      : index === learningPath.current_step - 1
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}>
                    <h4 className="font-semibold text-gray-800 mb-2">Step {index + 1}: {step.action}</h4>
                    <p className="text-gray-600 text-sm mb-3">
                      Action: {step.action.replace(/_/g, ' ')}
                      {index === learningPath.current_step - 1 && learningPath.next_action && 
                        ` (Q-Value: ${learningPath.next_action.q_value.toFixed(2)})`}
                    </p>
                    
                    {/* Step Status */}
                    <div className="flex items-center space-x-4 text-sm">
                      <span className={`flex items-center ${step.completed ? 'text-green-600' : 'text-gray-600'}`}>
                        <i className={`fas ${step.completed ? 'fa-check-circle' : 'fa-clock'} mr-1`}></i>
                        {step.completed ? 'Completed' : 'Pending'}
                      </span>
                    </div>
                    
                    {/* Action Button */}
                    {!step.completed && index === learningPath.current_step - 1 && (
                      <button 
                        onClick={handleExecuteAction}
                        className="mt-3 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                      >
                        Execute Action
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Learning Insights */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4">Learning Insights</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Current State */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">Current State</h4>
            {learningPath.next_action && (
              <div className="space-y-2 text-sm">
                <p><span className="font-medium">Quiz Level:</span> {learningPath.next_action.source_state.quiz_level}</p>
                <p><span className="font-medium">Complete Rate Bin:</span> {learningPath.next_action.source_state.complete_rate_bin}</p>
                <p><span className="font-medium">Score Bin:</span> {learningPath.next_action.source_state.score_bin}</p>
                <p><span className="font-medium">Section ID:</span> {learningPath.next_action.source_state.section_id}</p>
              </div>
            )}
          </div>

          {/* Next Action */}
          <div className="bg-green-50 rounded-lg p-4">
            <h4 className="font-semibold text-green-800 mb-2">Recommended Action</h4>
            {learningPath.next_action && (
              <div className="space-y-2 text-sm">
                <p><span className="font-medium">Action:</span> {learningPath.next_action.suggested_action.replace(/_/g, ' ')}</p>
                <p><span className="font-medium">Q-Value:</span> {learningPath.next_action.q_value.toFixed(4)}</p>
                <p><span className="font-medium">Confidence:</span> {(learningPath.next_action.q_value * 100).toFixed(1)}%</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
