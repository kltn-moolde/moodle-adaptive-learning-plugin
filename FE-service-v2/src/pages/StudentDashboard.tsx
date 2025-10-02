import React, { useState, useEffect } from 'react';
import { learningPathService, type LearningPathData } from '../services/learningPathService';
import DashboardAnalytics from '../components/DashboardAnalytics';

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

      {/* Current Recommended Action */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-6">Current Recommended Action</h3>
        
        {learningPath.steps.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-primary-50 rounded-lg p-6 border-l-4 border-primary-500">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-3">
                  <div className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center mr-4">
                    <i className="fas fa-lightbulb text-white text-lg"></i>
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold text-gray-800">{learningPath.steps[0].title}</h4>
                    <p className="text-sm text-primary-700">{learningPath.steps[0].lesson_name}</p>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4">{learningPath.steps[0].description}</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Section</div>
                    <div className="font-semibold">{learningPath.steps[0].section_id}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Level</div>
                    <div className={`font-semibold px-2 py-1 rounded text-xs ${getDifficultyColor(learningPath.steps[0].quiz_level)}`}>
                      {learningPath.steps[0].quiz_level}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Score Bin</div>
                    <div className="font-semibold">{learningPath.steps[0].score_bin}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Complete Rate</div>
                    <div className="font-semibold">{(learningPath.steps[0].complete_rate * 100).toFixed(0)}%</div>
                  </div>
                </div>
                
                <button 
                  onClick={handleExecuteAction}
                  className="w-full md:w-auto px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center justify-center"
                >
                  <i className="fas fa-play mr-2"></i>
                  {learningPath.steps[0].action.replace(/_/g, ' ').toUpperCase()}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Learning Analytics from ML API */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4">ML Learning Analytics</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Current Learning State */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
              <i className="fas fa-chart-bar mr-2"></i>
              Current State
            </h4>
            {learningPath.next_action && (
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Lesson:</span>
                  <span className="font-medium">{learningPath.next_action.source_state.lesson_name || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Quiz Level:</span>
                  <span className={`font-medium px-2 py-1 rounded text-xs ${getDifficultyColor(learningPath.next_action.source_state.quiz_level)}`}>
                    {learningPath.next_action.source_state.quiz_level}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Complete Rate:</span>
                  <span className="font-medium">{(learningPath.next_action.source_state.complete_rate_bin * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Score Bin:</span>
                  <span className="font-medium">{learningPath.next_action.source_state.score_bin}/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Section:</span>
                  <span className="font-medium">{learningPath.next_action.source_state.section_id}</span>
                </div>
              </div>
            )}
          </div>

          {/* ML Recommendation */}
          <div className="bg-green-50 rounded-lg p-4">
            <h4 className="font-semibold text-green-800 mb-3 flex items-center">
              <i className="fas fa-robot mr-2"></i>
              ML Recommendation
            </h4>
            {learningPath.next_action && (
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">Suggested Action:</span>
                  <div className="font-medium text-green-700 mt-1">
                    {learningPath.next_action.suggested_action.replace(/_/g, ' ').toUpperCase()}
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Q-Value:</span>
                  <span className="font-medium">{learningPath.next_action.q_value.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence:</span>
                  <span className="font-medium">{Math.abs(learningPath.next_action.q_value * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">User ID:</span>
                  <span className="font-medium">{learningPath.next_action.user_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Course ID:</span>
                  <span className="font-medium">{learningPath.next_action.course_id}</span>
                </div>
              </div>
            )}
          </div>

          {/* Action Explanation */}
          <div className="bg-yellow-50 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-800 mb-3 flex items-center">
              <i className="fas fa-info-circle mr-2"></i>
              Why This Action?
            </h4>
            {learningPath.steps.length > 0 && (
              <div className="text-sm text-gray-700">
                <p className="leading-relaxed">{learningPath.steps[0].description}</p>
                <div className="mt-3 pt-3 border-t border-yellow-200">
                  <p className="text-xs text-gray-500">
                    Based on your current performance and learning patterns, 
                    our ML algorithm recommends this action to optimize your learning progression.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Moodle Analytics Dashboard */}
      <DashboardAnalytics 
        userId={userId} 
        courseId={courseId} 
        isTeacher={false}
      />
    </div>
  );
};

export default StudentDashboard;
