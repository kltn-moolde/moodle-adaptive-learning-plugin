import React, { useState, useEffect } from 'react';
import { moodleApiService, type DashboardAnalytics } from '../services/moodleApiService';

interface DashboardAnalyticsProps {
  userId: number;
  courseId: number;
  isTeacher?: boolean;
  onAnalyticsLoaded?: (analytics: DashboardAnalytics) => void;
}

const DashboardAnalyticsComponent: React.FC<DashboardAnalyticsProps> = ({ 
  userId, 
  courseId, 
  isTeacher = false,
  onAnalyticsLoaded
}) => {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  userId = 4;
  courseId = 3;
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await moodleApiService.getDashboardAnalytics(userId, courseId, isTeacher);
        setAnalytics(data);
        
        // Callback để truyền dữ liệu lên parent component
        if (onAnalyticsLoaded && data) {
          onAnalyticsLoaded(data);
        }
      } catch (err) {
        console.error('Error fetching dashboard analytics:', err);
        setError('Failed to load dashboard analytics. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [userId, courseId, isTeacher]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <i className="fas fa-exclamation-triangle text-red-500 mr-2"></i>
          <span className="text-red-700">{error}</span>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">No analytics data available.</p>
      </div>
    );
  }

  const getCompletionColor = (status: number) => {
    switch (status) {
      case 1: return 'text-green-600';
      case 2: return 'text-blue-600';
      case 3: return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getCompletionIcon = (status: number) => {
    switch (status) {
      case 1: return 'fas fa-check-circle';
      case 2: return 'fas fa-check-circle';
      case 3: return 'fas fa-times-circle';
      default: return 'fas fa-clock';
    }
  };

  const getCompletionText = (status: number) => {
    switch (status) {
      case 0: return 'Not Started';
      case 1: return 'Complete';
      case 2: return 'Complete Pass';
      case 3: return 'Complete Fail';
      default: return 'Unknown';
    }
  };

  const getGradeColor = (grade: number, max: number) => {
    const percentage = (grade / max) * 100;
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 80) return 'text-blue-600';
    if (percentage >= 70) return 'text-yellow-600';
    if (percentage >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Course Progress Overview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-chart-line mr-2"></i>
          Course Progress Overview
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Overall Progress */}
          <div className="bg-gradient-to-r from-blue-50 to-primary-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-blue-800">Overall Progress</h4>
              <i className="fas fa-chart-pie text-blue-600"></i>
            </div>
            <div className="text-3xl font-bold text-blue-700 mb-2">
              {analytics.courseCompletion.progress}%
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${analytics.courseCompletion.progress}%` }}
              ></div>
            </div>
            <div className="text-sm text-blue-600 mt-2">
              {analytics.courseCompletion.completionstatus === 1 ? 'Course Completed!' : 'In Progress'}
            </div>
          </div>

          {/* Activities Completed */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-green-800">Activities</h4>
              <i className="fas fa-tasks text-green-600"></i>
            </div>
            <div className="text-3xl font-bold text-green-700 mb-2">
              {analytics.activitiesCompletion.filter(a => a.state >= 1).length} / {analytics.activitiesCompletion.length}
            </div>
            <div className="text-sm text-green-600">
              {Math.round((analytics.activitiesCompletion.filter(a => a.state >= 1).length / analytics.activitiesCompletion.length) * 100)}% Complete
            </div>
          </div>

          {/* Current Grade */}
          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-purple-800">Current Grade</h4>
              <i className="fas fa-graduation-cap text-purple-600"></i>
            </div>
            <div className="text-3xl font-bold text-purple-700 mb-2">
              {analytics.courseGrades.length > 0 ? analytics.courseGrades[0].grade : 'N/A'}
            </div>
            <div className="text-sm text-purple-600">
              Course Average
            </div>
          </div>
        </div>
      </div>

      {/* Activities Progress */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-list-check mr-2"></i>
          Activities Progress
        </h3>
        
        <div className="space-y-3">
          {analytics.activitiesCompletion.map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <i className={`${getCompletionIcon(activity.state)} ${getCompletionColor(activity.state)} mr-3`}></i>
                <div>
                  <div className="font-medium text-gray-800 capitalize">
                    {activity.modname} #{activity.instance}
                  </div>
                  <div className="text-sm text-gray-600">
                    {getCompletionText(activity.state)}
                  </div>
                </div>
              </div>
              {activity.timecompleted && (
                <div className="text-sm text-gray-500">
                  {new Date(activity.timecompleted).toLocaleDateString()}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Grade Items */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-chart-bar mr-2"></i>
          Grade Breakdown
        </h3>
        
        <div className="space-y-4">
          {analytics.gradeItems.map((item, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-800">{item.itemname}</h4>
                <div className="flex items-center space-x-2">
                  {item.grade && (
                    <span className={`font-bold ${getGradeColor(item.grade.grade, item.grademax)}`}>
                      {item.grade.str_grade} / {item.grademax}
                    </span>
                  )}
                </div>
              </div>
              
              {item.grade && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Score: {item.grade.str_long_grade}</span>
                    <span>Percentage: {((item.grade.grade / item.grademax) * 100).toFixed(1)}%</span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${
                        (item.grade.grade / item.grademax) >= 0.9 ? 'bg-green-500' :
                        (item.grade.grade / item.grademax) >= 0.8 ? 'bg-blue-500' :
                        (item.grade.grade / item.grademax) >= 0.7 ? 'bg-yellow-500' :
                        (item.grade.grade / item.grademax) >= 0.6 ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${(item.grade.grade / item.grademax) * 100}%` }}
                    ></div>
                  </div>
                  
                  {item.grade.feedback && (
                    <div className="text-sm text-gray-600 italic">
                      Feedback: {item.grade.feedback}
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-500">
                    Graded: {new Date(item.grade.dategraded).toLocaleDateString()}
                  </div>
                </div>
              )}
              
              {!item.grade && (
                <div className="text-sm text-gray-500 italic">
                  Not yet graded
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Competency Report */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
          <i className="fas fa-certificate mr-2"></i>
          Competency Report
        </h3>
        
        {/* <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analytics.competencyReport.competencies.map((comp, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-800">{comp.competency.shortname}</h4>
                <div className="flex items-center">
                  {comp.usercompetencycourse?.proficiency ? (
                    <i className="fas fa-check-circle text-green-500"></i>
                  ) : (
                    <i className="fas fa-clock text-yellow-500"></i>
                  )}
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-3">{comp.competency.description}</p>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  Framework: {comp.competency.framework.name}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Grade:</span>
                  <span className={`font-semibold ${
                    comp.usercompetencycourse?.proficiency ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {comp.usercompetencycourse?.grade || 'N/A'}
                  </span>
                </div>
              </div>
              
              <div className="mt-2">
                <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                  comp.usercompetencycourse?.proficiency 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {comp.usercompetencycourse?.proficiency ? 'Proficient' : 'In Progress'}
                </span>
              </div>
            </div>
          ))}
        </div> */}
      </div>

      {/* Teacher Dashboard - Simple Overview */}
      {isTeacher && analytics.enrolledUsers && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-primary-800 mb-4 flex items-center">
            <i className="fas fa-users mr-2"></i>
            Class Overview
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600">{analytics.enrolledUsers.length}</div>
              <div className="text-sm text-gray-600">Total Students</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {analytics.enrolledUsers.filter(u => u.roles.some(r => r.shortname === 'student')).length}
              </div>
              <div className="text-sm text-gray-600">Active Students</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {analytics.competencyReport?.competencies?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Competencies</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardAnalyticsComponent;