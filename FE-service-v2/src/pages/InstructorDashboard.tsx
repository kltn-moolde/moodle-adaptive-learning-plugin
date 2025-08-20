import React, { useState } from 'react';
import type { StudentProgress, VideoAnalytics, ActionAnalytics } from '../types';

interface InstructorDashboardProps {
  students: StudentProgress[];
  videoAnalytics: VideoAnalytics[];
  actionAnalytics: ActionAnalytics[];
}

const InstructorDashboard: React.FC<InstructorDashboardProps> = ({ 
  students, 
  videoAnalytics, 
  actionAnalytics 
}) => {
  const [selectedStudent, setSelectedStudent] = useState<StudentProgress | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'videos' | 'actions'>('overview');

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'fas fa-arrow-up text-green-500';
      case 'down':
        return 'fas fa-arrow-down text-red-500';
      default:
        return 'fas fa-minus text-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-primary-800 mb-2">Instructor Dashboard</h2>
        <p className="text-gray-600">Monitor student progress and course analytics</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { id: 'overview', label: 'Students Overview', icon: 'fas fa-users' },
              { id: 'videos', label: 'Video Analytics', icon: 'fas fa-video' },
              { id: 'actions', label: 'Action Analytics', icon: 'fas fa-chart-bar' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className={`${tab.icon} mr-2`}></i>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Students Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Students List */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Students ({students.length})</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {students.map((student) => (
                      <div 
                        key={student.studentId}
                        onClick={() => setSelectedStudent(student)}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          selectedStudent?.studentId === student.studentId
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-primary-300 bg-white'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                            {student.avatar ? (
                              <img src={student.avatar} alt={student.studentName} className="w-10 h-10 rounded-full" />
                            ) : (
                              <span className="text-white font-medium">
                                {student.studentName.charAt(0).toUpperCase()}
                              </span>
                            )}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-800">{student.studentName}</h4>
                            <div className="flex items-center space-x-2 mt-1">
                              <div className="w-24 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-primary-500 h-2 rounded-full"
                                  style={{ width: `${student.overallProgress}%` }}
                                ></div>
                              </div>
                              <span className="text-sm text-gray-600">{student.overallProgress}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Selected Student Details */}
                <div>
                  {selectedStudent ? (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        {selectedStudent.studentName}'s Progress
                      </h3>
                      
                      {/* Student Metrics */}
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">
                            {selectedStudent.performanceMetrics.videosWatched}
                          </div>
                          <div className="text-sm text-gray-600">Videos Watched</div>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {selectedStudent.performanceMetrics.assignmentsCompleted}
                          </div>
                          <div className="text-sm text-gray-600">Assignments Done</div>
                        </div>
                        <div className="bg-purple-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">
                            {selectedStudent.performanceMetrics.averageScore}%
                          </div>
                          <div className="text-sm text-gray-600">Average Score</div>
                        </div>
                        <div className="bg-orange-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-orange-600">
                            {selectedStudent.performanceMetrics.timeSpent}
                          </div>
                          <div className="text-sm text-gray-600">Time Spent</div>
                        </div>
                      </div>

                      {/* Learning Path Progress */}
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-semibold text-gray-800 mb-2">Current Learning Path</h4>
                        <p className="text-gray-600 mb-3">{selectedStudent.learningPath.title}</p>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div 
                            className="bg-primary-500 h-3 rounded-full"
                            style={{ width: `${selectedStudent.learningPath.progress}%` }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-2">
                          Step {selectedStudent.learningPath.currentStep} of {selectedStudent.learningPath.totalSteps}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 py-12">
                      <i className="fas fa-users text-4xl mb-4"></i>
                      <p>Select a student to view their progress details</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Video Analytics Tab */}
          {activeTab === 'videos' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Video Performance Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {videoAnalytics.map((video) => (
                  <div key={video.videoId} className="bg-white border rounded-lg p-4 shadow-sm">
                    <div className="mb-3">
                      {video.thumbnail ? (
                        <img src={video.thumbnail} alt={video.title} className="w-full h-32 object-cover rounded" />
                      ) : (
                        <div className="w-full h-32 bg-gray-200 rounded flex items-center justify-center">
                          <i className="fas fa-video text-gray-400 text-2xl"></i>
                        </div>
                      )}
                    </div>
                    <h4 className="font-semibold text-gray-800 mb-2">{video.title}</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Views:</span>
                        <span className="font-medium">{video.totalViews}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Unique Viewers:</span>
                        <span className="font-medium">{video.uniqueViewers}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Avg. Watch Time:</span>
                        <span className="font-medium">{video.averageWatchTime}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Completion Rate:</span>
                        <span className="font-medium">{video.completionRate}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Analytics Tab */}
          {activeTab === 'actions' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Student Action Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {actionAnalytics.map((action, index) => (
                  <div key={index} className="bg-white border rounded-lg p-4 shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-gray-800">{action.actionType}</h4>
                      <i className={getTrendIcon(action.trend)}></i>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{action.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold text-primary-600">{action.count}</span>
                      <span className={`text-sm px-2 py-1 rounded-full ${
                        action.trend === 'up' ? 'bg-green-100 text-green-800' :
                        action.trend === 'down' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {action.percentage > 0 ? '+' : ''}{action.percentage}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InstructorDashboard;
