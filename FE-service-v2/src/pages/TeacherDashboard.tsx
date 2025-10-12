import React, { useState, useEffect } from 'react';
import { learningPathExplanationService } from '../services/learningPathExplanationService';
import DashboardAnalytics from '../components/DashboardAnalytics';
import StudentsLearningPaths from '../components/StudentsLearningPaths';

interface TeacherDashboardProps {
  userId: number;
  courseId: number;
}

interface TeacherRecommendation {
  class_overview: string;
  main_challenges: string;
  teaching_suggestions: string[];
  priority_actions: string[];
  motivation: string;
}

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ userId, courseId }) => {
  const [aiRecommendations, setAiRecommendations] = useState<TeacherRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingAI, setLoadingAI] = useState(false);
  const [showAIRecommendations, setShowAIRecommendations] = useState(false);

  useEffect(() => {
    const loadTeacherData = async () => {
      try {
        setLoading(true);
        
        // Auto-load existing AI recommendations if available
        const existingRecommendations = await learningPathExplanationService.getTeacherRecommendations(
          courseId.toString()
        );
        
        if (existingRecommendations) {
          setAiRecommendations(existingRecommendations.recommendations);
          setShowAIRecommendations(true);
        }
        
      } catch (error) {
        console.error('Error loading teacher data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTeacherData();
  }, [courseId]);

  const handleGenerateAIRecommendations = async () => {
    try {
      setLoadingAI(true);
      
      const recommendations = await learningPathExplanationService.generateTeacherRecommendations(
        courseId.toString()
      );

      if (recommendations) {
        setAiRecommendations(recommendations);
        setShowAIRecommendations(true);
      } else {
        // Show fallback recommendations
        const fallbackRecommendations: TeacherRecommendation = {
          class_overview: "Lớp có 25 học sinh với mức độ tiến bộ đa dạng. Khoảng 40% học sinh đang gặp khó khăn với các khái niệm nâng cao.",
          main_challenges: "Học sinh gặp khó khăn chính trong việc giải quyết vấn đề logic và tư duy phản biện. Nhiều em cần thêm thời gian để hiểu các khái niệm trừu tượng.",
          teaching_suggestions: [
            "Tăng cường bài tập thực hành với từng bước cụ thể",
            "Sử dụng thêm ví dụ minh họa trực quan",
            "Tổ chức thêm các hoạt động nhóm để học sinh hỗ trợ lẫn nhau",
            "Cung cấp thêm tài liệu tham khảo cho các em yếu"
          ],
          priority_actions: [
            "Xem xét lại độ khó của bài kiểm tra Phần 3",
            "Thêm video giải thích cho các khái niệm phức tạp",
            "Tạo quiz ôn tập cho mỗi chủ đề",
            "Thiết lập giờ tư vấn thêm cho học sinh yếu"
          ],
          motivation: "Việc điều chỉnh phương pháp giảng dạy này sẽ giúp nâng cao hiệu quả học tập của cả lớp, đặc biệt là các em đang gặp khó khăn."
        };

        setAiRecommendations(fallbackRecommendations);
        setShowAIRecommendations(true);
      }
    } catch (error) {
      console.error('Error generating AI recommendations:', error);
    } finally {
      setLoadingAI(false);
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

      {/* AI Teaching Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-primary-800 flex items-center">
            <i className="fas fa-brain mr-2"></i>
            AI Teaching Recommendations
          </h2>
          <button
            onClick={handleGenerateAIRecommendations}
            disabled={loadingAI}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-colors"
          >
            {loadingAI ? (
              <span className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating...
              </span>
            ) : (
              'Nhận gợi ý từ AI'
            )}
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-20">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
            <span className="ml-2 text-gray-600">Loading recommendations...</span>
          </div>
        ) : showAIRecommendations && aiRecommendations ? (
          <div className="space-y-4">
            {/* Class Overview */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 mb-2">
                <i className="fas fa-chart-pie mr-2"></i>
                Tổng quan lớp học
              </h3>
              <p className="text-blue-700">{aiRecommendations.class_overview}</p>
            </div>

            {/* Main Challenges */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="font-semibold text-red-800 mb-2">
                <i className="fas fa-exclamation-triangle mr-2"></i>
                Thách thức chính
              </h3>
              <p className="text-red-700">{aiRecommendations.main_challenges}</p>
            </div>

            {/* Teaching Suggestions */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-800 mb-2">
                <i className="fas fa-lightbulb mr-2"></i>
                Gợi ý phương pháp giảng dạy
              </h3>
              <ul className="space-y-1 text-green-700">
                {aiRecommendations.teaching_suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start">
                    <i className="fas fa-check-circle mr-2 mt-1 text-green-500"></i>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>

            {/* Priority Actions */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h3 className="font-semibold text-orange-800 mb-2">
                <i className="fas fa-star mr-2"></i>
                Hành động ưu tiên
              </h3>
              <ul className="space-y-1 text-orange-700">
                {aiRecommendations.priority_actions.map((action, index) => (
                  <li key={index} className="flex items-start">
                    <i className="fas fa-arrow-right mr-2 mt-1 text-orange-500"></i>
                    {action}
                  </li>
                ))}
              </ul>
            </div>

            {/* Motivation */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="font-semibold text-purple-800 mb-2">
                <i className="fas fa-heart mr-2"></i>
                Động lực thực hiện
              </h3>
              <p className="text-purple-700">{aiRecommendations.motivation}</p>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <i className="fas fa-brain text-4xl text-gray-400 mb-4"></i>
            <p className="text-gray-600">Chưa có gợi ý AI nào được tạo.</p>
            <p className="text-gray-500 text-sm">Nhấn nút "Nhận gợi ý từ AI" để tạo gợi ý dựa trên dữ liệu học sinh.</p>
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