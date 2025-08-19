import React, { useState } from 'react';
import { Users, TrendingUp, Award, Eye, EyeOff, X } from 'lucide-react';
import type { StudentProgress, CourseStats, Course } from '../types';

interface InstructorDashboardProps {
  students: StudentProgress[];
  courseStats: CourseStats;
  courses: Course[];
}

const InstructorDashboard: React.FC<InstructorDashboardProps> = ({ 
  students, 
  courseStats, 
  courses
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'statistics' | 'courses'>('overview');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  const handleViewDetails = (course: Course) => {
    setSelectedCourse(course);
  };
  
  const handleCloseDetails = () => {
    setSelectedCourse(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'text-green-600 bg-green-100';
    if (progress >= 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Tổng học sinh</p>
              <p className="text-2xl font-semibold text-gray-900">{courseStats.totalStudents}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Tiến độ TB</p>
              <p className="text-2xl font-semibold text-gray-900">{courseStats.averageProgress.toFixed(1)}%</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Award className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Điểm TB</p>
              <p className="text-2xl font-semibold text-gray-900">{courseStats.averageScore.toFixed(1)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Eye className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Bài học phổ biến</p>
              <p className="text-2xl font-semibold text-gray-900">{courseStats.mostViewedLessons.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Hoạt động gần đây</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {students.slice(0, 5).map((student) => (
              <div key={student.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{student.name}</p>
                  <p className="text-sm text-gray-600">{student.currentLesson}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{student.progress}%</p>
                  <p className="text-xs text-gray-500">{formatDate(student.lastActivity)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStudents = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Danh sách học sinh</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Học sinh
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiến độ
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Điểm số
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Bài học hiện tại
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Hoạt động cuối
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {students.map((student) => (
              <tr key={student.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{student.name}</div>
                    <div className="text-sm text-gray-500">{student.email}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${student.progress}%` }}
                      ></div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getProgressColor(student.progress)}`}>
                      {student.progress}%
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {student.totalScore}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {student.currentLesson}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(student.lastActivity)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderStatistics = () => (
    <div className="space-y-6">
      {/* Most Viewed Lessons */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Bài học được xem nhiều nhất</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {courseStats.mostViewedLessons.map((lesson) => (
              <div key={lesson.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{lesson.title}</h4>
                  <p className="text-sm text-gray-600">{lesson.description}</p>
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Eye className="h-4 w-4 mr-1" />
                  {lesson.views} lượt xem
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Least Viewed Lessons */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Bài học ít được quan tâm</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {courseStats.leastViewedLessons.map((lesson) => (
              <div key={lesson.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{lesson.title}</h4>
                  <p className="text-sm text-gray-600">{lesson.description}</p>
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <EyeOff className="h-4 w-4 mr-1" />
                  {lesson.views} lượt xem
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
  
  const renderCourses = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Danh sách khóa học</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-blue-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-blue-600 uppercase tracking-wider">
                Mã khóa học
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-blue-600 uppercase tracking-wider">
                Tên khóa học
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-blue-600 uppercase tracking-wider">
                Hành động
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {courses.map((course) => (
              <tr key={course.id} className="hover:bg-blue-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {course.courseCode}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {course.title}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => handleViewDetails(course)}
                    className="px-3 py-1 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
                  >
                    Xem chi tiết
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );


  const renderCourseDetailsModal = () => {
    if (!selectedCourse) {
      return null;
    }

    return (
      <div className="flex items-center justify-center bg-black bg-opacity-50 z-50">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-2xl w-full mx-4 relative">
          <button
            onClick={handleCloseDetails}
            className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
            aria-label="Close"
          >
            <X className="h-6 w-6" />
          </button>
          
          <h2 className="text-2xl font-bold mb-4 text-gray-900">Chi tiết khóa học</h2>
          <p className="text-gray-700 mb-4">
            <span className="font-semibold">Mã khóa học:</span> {selectedCourse.courseCode}
          </p>
          <p className="text-gray-700 mb-6">
            <span className="font-semibold">Tiêu đề:</span> {selectedCourse.title}
          </p>
          
          {selectedCourse.sections && selectedCourse.sections.length > 0 ? (
            selectedCourse.sections.map((section, sectionIndex) => (
              <div key={sectionIndex} className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
                <h4 className="text-lg font-semibold text-blue-700 mb-2">{section.name}</h4>
                
                {section.lessons && section.lessons.length > 0 && (
                  <div className="mt-4">
                    <h5 className="text-md font-medium text-gray-600 mb-2">Bài học</h5>
                    <ul className="list-none space-y-3">
                      {section.lessons.map((lesson, lessonIndex) => (
                        <li key={lessonIndex} className="bg-white p-3 rounded-md shadow-sm">
                          <p className="font-semibold text-gray-800">{lesson.name}</p>
                          <ul className="mt-2 text-sm text-gray-600 space-y-1">
                            {lesson.resources.map((resource, resIndex) => (
                              <li key={resIndex}>{resource.name} ({resource.modname})</li>
                            ))}
                          </ul>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {section.resources && section.resources.length > 0 && (
                  <div className="mt-4">
                    <h5 className="text-md font-medium text-gray-600 mb-2">Tài nguyên học phần</h5>
                    <ul className="list-disc pl-6 text-gray-700 space-y-1">
                      {section.resources.map((resource, resIndex) => (
                        <li key={resIndex} className="text-sm">{resource.name} ({resource.modname})</li>
                      ))}
                    </ul>
                  </div>
                )}

              </div>
            ))
          ) : (
            <p className="text-gray-500 italic">Không có thông tin chi tiết về các học phần.</p>
          )}

          <div className="flex justify-end mt-6">
            <button
              onClick={handleCloseDetails}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition"
            >
              Đóng
            </button>
          </div>
        </div>
      </div>
    );
  };


  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Tổng quan
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'students'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Học sinh
          </button>
           <button
            onClick={() => setActiveTab('courses')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'courses'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Khoá học
          </button>
          <button
            onClick={() => setActiveTab('statistics')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'statistics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Thống kê
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'students' && renderStudents()}
      {activeTab === 'statistics' && renderStatistics()}
      {activeTab === 'courses' && renderCourses()}

      {renderCourseDetailsModal()}
      
    </div>
  );
};

export default InstructorDashboard;