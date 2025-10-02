import React, { useState, useEffect } from 'react';
import DashboardAnalytics from '../components/DashboardAnalytics';
import StudentsLearningPaths from '../components/StudentsLearningPaths';

interface TeacherDashboardProps {
  userId: number;
  courseId: number;
}

interface ContentRecommendation {
  type: 'difficulty_adjustment' | 'content_addition' | 'activity_suggestion' | 'competency_focus';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  targetStudents: number;
  reasoning: string;
  suggestedActions: string[];
}

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ userId, courseId }) => {
  const [contentRecommendations, setContentRecommendations] = useState<ContentRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const generateContentRecommendations = async () => {
      try {
        setLoading(true);
        
        // In a real implementation, this would analyze class performance data
        // and generate AI-powered recommendations for content adjustments
        const mockRecommendations: ContentRecommendation[] = [
          {
            type: 'difficulty_adjustment',
            title: 'Reduce Quiz Difficulty in Section 3',
            description: 'Multiple students are struggling with quiz complexity in Section 3',
            priority: 'high',
            targetStudents: 8,
            reasoning: 'Analysis shows 80% of students scored below 60% on Section 3 quizzes. The current difficulty level may be too advanced for the majority of the class.',
            suggestedActions: [
              'Add more practice questions before the main quiz',
              'Break complex questions into smaller parts',
              'Provide additional study materials for foundational concepts',
              'Consider adding a practice quiz with immediate feedback'
            ]
          },
          {
            type: 'content_addition',
            title: 'Add Video Explanations for Problem Solving',
            description: 'Students need more visual learning resources for complex problem-solving topics',
            priority: 'high',
            targetStudents: 12,
            reasoning: 'Students with visual learning preferences are underperforming. Adding video content could improve comprehension by 25-30%.',
            suggestedActions: [
              'Create step-by-step video walkthroughs',
              'Add interactive problem-solving demos',
              'Include visual diagrams and flowcharts',
              'Provide screen-recorded solutions'
            ]
          },
          {
            type: 'activity_suggestion',
            title: 'Introduce Peer Collaboration Activities',
            description: 'Class would benefit from more collaborative learning opportunities',
            priority: 'medium',
            targetStudents: 15,
            reasoning: 'Student engagement data suggests collaborative activities could improve retention. Social learning can boost performance by 15-20%.',
            suggestedActions: [
              'Add group discussion forums',
              'Create peer review assignments',
              'Implement study group features',
              'Design collaborative problem-solving tasks'
            ]
          },
          {
            type: 'competency_focus',
            title: 'Strengthen Critical Thinking Competency',
            description: 'Multiple students showing gaps in critical thinking skills',
            priority: 'medium',
            targetStudents: 6,
            reasoning: 'Competency analysis reveals 40% of students have not achieved proficiency in critical thinking. This affects performance across multiple modules.',
            suggestedActions: [
              'Add case study exercises',
              'Include analytical thinking challenges',
              'Create reflection assignments',
              'Provide critical thinking frameworks'
            ]
          }
        ];

        setContentRecommendations(mockRecommendations);
      } catch (error) {
        console.error('Error generating content recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    generateContentRecommendations();
  }, [userId, courseId]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };


  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'difficulty_adjustment': return 'fas fa-balance-scale';
      case 'content_addition': return 'fas fa-plus-circle';
      case 'activity_suggestion': return 'fas fa-users';
      case 'competency_focus': return 'fas fa-target';
      default: return 'fas fa-lightbulb';
    }
  };

  return (
    <div className="space-y-6">
      {/* Teacher Dashboard Header */}
      <div className="bg-gradient-to-r from-primary-600 to-blue-600 rounded-lg shadow-md p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Teacher Dashboard</h1>
            <p className="text-primary-100">Course {courseId} - Instructional Analytics & Recommendations</p>
          </div>
          <div className="text-right">
            <div className="text-primary-100 text-sm">Instructor ID</div>
            <div className="text-2xl font-bold">{userId}</div>
          </div>
        </div>
      </div>

      {/* AI Content Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-lightbulb mr-2"></i>
          AI Teaching Suggestions
        </h2>

        {loading ? (
          <div className="flex items-center justify-center h-20">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
            <span className="ml-2 text-gray-600">Analyzing class...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {contentRecommendations.slice(0, 4).map((recommendation, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <i className={`${getTypeIcon(recommendation.type)} text-primary-600 text-sm`}></i>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-gray-800 text-sm truncate">{recommendation.title}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(recommendation.priority)}`}>
                        {recommendation.priority}
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-2 line-clamp-2">{recommendation.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        <i className="fas fa-users mr-1"></i>{recommendation.targetStudents} students
                      </span>
                      <button className="px-3 py-1 bg-primary-500 text-white rounded text-xs hover:bg-primary-600 transition-colors">
                        Apply
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Students Learning Paths */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-route mr-2"></i>
          Students Learning Paths
        </h2>
        <StudentsLearningPaths courseId={courseId} />
      </div>

      {/* Class Overview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-chart-bar mr-2"></i>
          Class Overview
        </h2>
        <DashboardAnalytics 
          userId={userId} 
          courseId={courseId} 
          isTeacher={true}
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-bolt mr-2"></i>
          Quick Actions
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors">
            <i className="fas fa-plus-circle text-blue-600 text-2xl mb-2"></i>
            <div className="font-semibold text-blue-800">Add Content</div>
            <div className="text-sm text-blue-600">Create new materials</div>
          </button>
          
          <button className="p-4 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg transition-colors">
            <i className="fas fa-chart-bar text-green-600 text-2xl mb-2"></i>
            <div className="font-semibold text-green-800">View Reports</div>
            <div className="text-sm text-green-600">Detailed analytics</div>
          </button>
          
          <button className="p-4 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg transition-colors">
            <i className="fas fa-users text-purple-600 text-2xl mb-2"></i>
            <div className="font-semibold text-purple-800">Manage Students</div>
            <div className="text-sm text-purple-600">Student progress</div>
          </button>
          
          <button className="p-4 bg-orange-50 hover:bg-orange-100 border border-orange-200 rounded-lg transition-colors">
            <i className="fas fa-cog text-orange-600 text-2xl mb-2"></i>
            <div className="font-semibold text-orange-800">Course Settings</div>
            <div className="text-sm text-orange-600">Configure course</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;