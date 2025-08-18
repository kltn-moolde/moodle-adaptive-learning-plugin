import React from 'react';
import { CheckCircle, Circle, Clock, Award, TrendingUp, BarChart3 } from 'lucide-react';
import type { LearningPath } from '../types';

interface StudentDashboardProps {
  learningPath: LearningPath;
}

const StudentDashboard: React.FC<StudentDashboardProps> = ({ learningPath }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
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

  const completedLessons = learningPath.lessons.filter(lesson => lesson.status === 'completed');
  const averageScore = completedLessons.length > 0 
    ? completedLessons.reduce((sum, lesson) => sum + (lesson.score || 0), 0) / completedLessons.length 
    : 0;

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-blue-100" />
            <div className="ml-4">
              <p className="text-sm font-medium text-blue-100">Tiến độ</p>
              <p className="text-2xl font-bold text-white">{learningPath.progress}%</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center">
            <Award className="h-8 w-8 text-yellow-100" />
            <div className="ml-4">
              <p className="text-sm font-medium text-yellow-100">Tổng điểm</p>
              <p className="text-2xl font-bold text-white">{learningPath.totalScore}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-100" />
            <div className="ml-4">
              <p className="text-sm font-medium text-green-100">Hoàn thành</p>
              <p className="text-2xl font-bold text-white">
                {completedLessons.length}/{learningPath.lessons.length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center">
            <BarChart3 className="h-8 w-8 text-purple-100" />
            <div className="ml-4">
              <p className="text-sm font-medium text-purple-100">Điểm TB</p>
              <p className="text-2xl font-bold text-white">{averageScore.toFixed(1)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Learning Roadmap */}
      <div className="bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-xl border border-white border-opacity-20">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-t-xl">
          <h2 className="text-lg font-bold text-gray-900">🚀 Lộ trình học tập</h2>
          <p className="text-sm text-gray-600">
            Cập nhật lần cuối: {new Date(learningPath.lastUpdated).toLocaleDateString('vi-VN')}
          </p>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {learningPath.lessons.map((lesson) => (
              <div key={lesson.id} className="flex items-center p-6 border-2 border-gray-100 rounded-xl hover:border-indigo-200 hover:shadow-lg transition-all duration-300 bg-gradient-to-r from-white to-gray-50/50">
                <div className="flex-shrink-0">
                  {getStatusIcon(lesson.status)}
                </div>
                
                <div className="ml-4 flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-gray-900">{lesson.title}</h3>
                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 text-xs font-bold rounded-full ${getDifficultyColor(lesson.difficulty)} shadow-sm`}>
                        {lesson.difficulty === 'easy' ? '🟢 Dễ' : lesson.difficulty === 'medium' ? '🟡 Trung bình' : '🔴 Khó'}
                      </span>
                      {lesson.score && (
                        <span className="text-sm font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                          ⭐ {lesson.score} điểm
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mt-2">{lesson.description}</p>
                  
                  <div className="flex items-center mt-3 text-xs text-gray-500">
                    <Clock className="h-4 w-4 mr-1" />
                    <span className="font-medium">{lesson.estimatedTime} phút</span>
                  </div>
                </div>
                
                <div className="ml-4">
                  {lesson.status === 'not_started' && (
                    <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white text-sm font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5">
                      ▶️ Bắt đầu
                    </button>
                  )}
                  {lesson.status === 'in_progress' && (
                    <button className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 text-white text-sm font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5">
                      ⏳ Tiếp tục
                    </button>
                  )}
                  {lesson.status === 'completed' && (
                    <button className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white text-sm font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5">
                      ✅ Xem lại
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
