import { useState, useEffect } from 'react';
import {
  getClusters,
  getClusterDetail,
  getRecommendation,
  getQTableStats,
  type ClusterInfo,
  type ClusterDetail,
  type RecommendationResponse,
} from '../services/qlearningService';

const QLearningDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Clusters data
  const [clusters, setClusters] = useState<ClusterInfo[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<ClusterDetail | null>(null);
  
  // Q-table stats
  const [qTableStats, setQTableStats] = useState<{
    total_states: number;
    total_actions: number;
    trained_states: number;
    coverage_percentage: number;
  } | null>(null);
  
  // Recommendation form
  const [studentId, setStudentId] = useState<string>('1');
  const [courseId, setCourseId] = useState<string>('3');
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Load clusters and Q-table stats in parallel
      const [clustersData, statsData] = await Promise.all([
        getClusters(),
        getQTableStats(),
      ]);
      
      setClusters(clustersData.clusters);
      setQTableStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleClusterClick = async (clusterId: number) => {
    try {
      const detail = await getClusterDetail(clusterId);
      setSelectedCluster(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load cluster detail');
    }
  };

  const handleGetRecommendation = async () => {
    setError(null);
    try {
      const result = await getRecommendation({
        student_id: parseInt(studentId),
        features: {
          knowledge_level: 0.75,
          engagement_level: 0.75,
          struggle_indicator: 0.0,
          submission_activity: 0.5,
          review_activity: 0.75,
          resource_usage: 0.75,
          assessment_engagement: 0.75,
          collaborative_activity: 0.0,
          overall_progress: 0.75,
          module_completion_rate: 0.75,
          activity_diversity: 0.25,
          completion_consistency: 0.5,
        },
        top_k: 5,
      });
      
      setRecommendation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendation');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full border-4 border-purple-200"></div>
            <div className="absolute inset-0 rounded-full border-4 border-t-purple-600 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
          </div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Đang tải dữ liệu</h3>
          <p className="text-gray-500">Vui lòng đợi trong giây lát...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-2">
      {/* Modern Header with Gradient */}
      <div className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 rounded-3xl shadow-2xl p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-5 rounded-full -ml-24 -mb-24"></div>
        
        <div className="relative z-10">
          <div className="flex items-center mb-4">
            <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-2xl p-4 mr-4">
              <i className="fas fa-brain text-4xl text-white"></i>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Q-Learning Analytics
              </h1>
              <p className="text-blue-100 text-lg">
                Hệ thống gợi ý học tập thông minh với AI
              </p>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-4 mt-6">
            <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl px-4 py-2">
              <span className="text-white text-sm font-medium">
                <i className="fas fa-robot mr-2"></i>
                AI-Powered Recommendations
              </span>
            </div>
            <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl px-4 py-2">
              <span className="text-white text-sm font-medium">
                <i className="fas fa-users mr-2"></i>
                Student Clustering
              </span>
            </div>
            <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl px-4 py-2">
              <span className="text-white text-sm font-medium">
                <i className="fas fa-chart-line mr-2"></i>
                Real-time Analytics
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Modern Error Display */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-200 rounded-2xl p-6 shadow-lg">
          <div className="flex items-start">
            <div className="bg-red-500 rounded-xl p-3 mr-4">
              <i className="fas fa-exclamation-circle text-2xl text-white"></i>
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-xl text-red-800 mb-2">Đã xảy ra lỗi</h3>
              <p className="text-red-700 leading-relaxed">{error}</p>
              <button
                onClick={loadInitialData}
                className="mt-4 bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-2 rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
              >
                <i className="fas fa-redo mr-2"></i>
                Thử lại
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modern Q-Table Statistics Cards */}
      {qTableStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1 - Total States */}
          <div className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative p-6 group-hover:text-white transition-colors duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-blue-100 group-hover:bg-white group-hover:bg-opacity-20 rounded-xl p-3 transition-all duration-300">
                  <i className="fas fa-database text-2xl text-blue-600 group-hover:text-white"></i>
                </div>
                <span className="text-xs font-semibold text-blue-600 group-hover:text-blue-100 bg-blue-50 group-hover:bg-white group-hover:bg-opacity-20 px-3 py-1 rounded-full">
                  Q-Table
                </span>
              </div>
              <p className="text-gray-600 group-hover:text-blue-100 text-sm font-medium mb-1">Tổng States</p>
              <p className="text-3xl font-bold text-gray-900 group-hover:text-white">
                {(qTableStats.total_states || 0).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Card 2 - Total Actions */}
          <div className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500 to-green-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative p-6 group-hover:text-white transition-colors duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-green-100 group-hover:bg-white group-hover:bg-opacity-20 rounded-xl p-3 transition-all duration-300">
                  <i className="fas fa-directions text-2xl text-green-600 group-hover:text-white"></i>
                </div>
                <span className="text-xs font-semibold text-green-600 group-hover:text-green-100 bg-green-50 group-hover:bg-white group-hover:bg-opacity-20 px-3 py-1 rounded-full">
                  Actions
                </span>
              </div>
              <p className="text-gray-600 group-hover:text-green-100 text-sm font-medium mb-1">Tổng Actions</p>
              <p className="text-3xl font-bold text-gray-900 group-hover:text-white">
                {(qTableStats.total_actions || 0).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Card 3 - Trained States */}
          <div className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative p-6 group-hover:text-white transition-colors duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-purple-100 group-hover:bg-white group-hover:bg-opacity-20 rounded-xl p-3 transition-all duration-300">
                  <i className="fas fa-check-circle text-2xl text-purple-600 group-hover:text-white"></i>
                </div>
                <span className="text-xs font-semibold text-purple-600 group-hover:text-purple-100 bg-purple-50 group-hover:bg-white group-hover:bg-opacity-20 px-3 py-1 rounded-full">
                  Trained
                </span>
              </div>
              <p className="text-gray-600 group-hover:text-purple-100 text-sm font-medium mb-1">States Đã Train</p>
              <p className="text-3xl font-bold text-gray-900 group-hover:text-white">
                {(qTableStats.trained_states || 0).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Card 4 - Coverage */}
          <div className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500 to-orange-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative p-6 group-hover:text-white transition-colors duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-orange-100 group-hover:bg-white group-hover:bg-opacity-20 rounded-xl p-3 transition-all duration-300">
                  <i className="fas fa-percentage text-2xl text-orange-600 group-hover:text-white"></i>
                </div>
                <span className="text-xs font-semibold text-orange-600 group-hover:text-orange-100 bg-orange-50 group-hover:bg-white group-hover:bg-opacity-20 px-3 py-1 rounded-full">
                  Progress
                </span>
              </div>
              <p className="text-gray-600 group-hover:text-orange-100 text-sm font-medium mb-1">Coverage</p>
              <p className="text-3xl font-bold text-gray-900 group-hover:text-white">
                {(qTableStats.coverage_percentage || 0).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Modern Student Clusters Section */}
      <div className="bg-white rounded-3xl shadow-xl p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
              Phân Cụm Học Sinh
            </h2>
            <p className="text-gray-500">Khám phá các nhóm học sinh với đặc điểm tương đồng</p>
          </div>
          <div className="bg-gradient-to-br from-purple-100 to-blue-100 rounded-2xl p-4">
            <i className="fas fa-users text-3xl text-purple-600"></i>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clusters.map((cluster, index) => {
            const colors = [
              'from-pink-500 to-rose-500',
              'from-purple-500 to-indigo-500',
              'from-blue-500 to-cyan-500',
              'from-green-500 to-emerald-500',
              'from-yellow-500 to-orange-500',
              'from-red-500 to-pink-500'
            ];
            const bgColors = [
              'bg-gradient-to-br from-pink-50 to-rose-50',
              'bg-gradient-to-br from-purple-50 to-indigo-50',
              'bg-gradient-to-br from-blue-50 to-cyan-50',
              'bg-gradient-to-br from-green-50 to-emerald-50',
              'bg-gradient-to-br from-yellow-50 to-orange-50',
              'bg-gradient-to-br from-red-50 to-pink-50'
            ];
            
            return (
              <button
                key={cluster.cluster_id}
                onClick={() => handleClusterClick(cluster.cluster_id)}
                className={`relative text-left p-6 rounded-2xl border-2 transition-all duration-300 hover:scale-105 hover:shadow-2xl ${
                  selectedCluster?.cluster_id === cluster.cluster_id
                    ? 'border-purple-500 shadow-xl ' + bgColors[index % 6]
                    : 'border-gray-200 bg-white hover:border-purple-300'
                }`}
              >
                {/* Decorative Circle */}
                <div className={`absolute -top-3 -right-3 w-12 h-12 bg-gradient-to-br ${colors[index % 6]} rounded-full flex items-center justify-center text-white font-bold shadow-lg`}>
                  {cluster.cluster_id}
                </div>
                
                {/* Content */}
                <div className="mb-4">
                  <h3 className="font-bold text-xl text-gray-800 mb-2">
                    {cluster.profile_name}
                  </h3>
                  
                  <div className="flex items-center gap-3 mb-3">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${colors[index % 6]} text-white`}>
                      {(cluster.percentage || 0).toFixed(1)}%
                    </span>
                    <span className="text-gray-600 text-sm font-medium">
                      <i className="fas fa-user mr-1"></i>
                      {cluster.n_students || 0} học sinh
                    </span>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${colors[index % 6]} transition-all duration-500`}
                    style={{ width: `${Math.min(100, Math.max(0, cluster.percentage || 0))}%` }}
                  ></div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Modern Selected Cluster Detail */}
      {selectedCluster && (
        <div className="bg-gradient-to-br from-white to-gray-50 rounded-3xl shadow-2xl p-8 border border-gray-100">
          <div className="flex items-center mb-6">
            <div className="bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl p-4 mr-4 shadow-lg">
              <i className="fas fa-info-circle text-3xl text-white"></i>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-gray-800">
                Chi Tiết Cluster {selectedCluster.cluster_id}
              </h2>
              <p className="text-gray-500 mt-1">Phân tích chuyên sâu về nhóm học sinh</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Modern Statistics */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100">
              <h3 className="font-bold text-lg text-gray-800 mb-4 flex items-center">
                <div className="bg-blue-500 rounded-lg p-2 mr-3">
                  <i className="fas fa-chart-bar text-white"></i>
                </div>
                Thống kê
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <p className="text-sm text-gray-600 mb-1">Số học sinh</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    {selectedCluster.statistics?.n_students || 0}
                  </p>
                </div>
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <p className="text-sm text-gray-600 mb-1">Tỷ lệ</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    {(selectedCluster.statistics?.percentage || 0).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Modern Top Features */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
              <h3 className="font-bold text-lg text-gray-800 mb-4 flex items-center">
                <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg p-2 mr-3">
                  <i className="fas fa-star text-white"></i>
                </div>
                Đặc điểm nổi bật
              </h3>
              <div className="space-y-3">
                {(selectedCluster.statistics?.top_features || []).slice(0, 5).map((feat, idx) => (
                  <div key={idx} className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                            #{idx + 1}
                          </span>
                          <p className="font-bold text-gray-800">{feat.feature || 'N/A'}</p>
                        </div>
                        <p className="text-sm text-gray-600 ml-9">{feat.interpretation || ''}</p>
                      </div>
                      <span className={`ml-4 px-4 py-2 rounded-xl text-sm font-bold shadow-sm ${
                        (feat.z_score || 0) > 1 ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white' :
                        (feat.z_score || 0) < -1 ? 'bg-gradient-to-r from-red-400 to-pink-500 text-white' :
                        'bg-gradient-to-r from-gray-400 to-gray-500 text-white'
                      }`}>
                        {(feat.z_score || 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Modern Existing Profile */}
            {selectedCluster.existing_profile && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-100">
                <div className="flex items-center mb-4">
                  <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl p-3 mr-3">
                    <i className="fas fa-user-graduate text-2xl text-white"></i>
                  </div>
                  <h3 className="font-bold text-2xl text-gray-800">
                    {selectedCluster.existing_profile?.profile_name || 'Unnamed Profile'}
                  </h3>
                </div>
                
                <div className="bg-white rounded-xl p-4 mb-4 shadow-sm">
                  <p className="text-gray-700 leading-relaxed">
                    {selectedCluster.existing_profile?.description || 'No description available'}
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {(selectedCluster.existing_profile?.strengths || []).length > 0 && (
                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <h4 className="font-bold text-lg mb-3 flex items-center text-green-700">
                        <div className="bg-green-100 rounded-lg p-2 mr-2">
                          <i className="fas fa-plus-circle"></i>
                        </div>
                        Điểm mạnh
                      </h4>
                      <ul className="space-y-2">
                        {(selectedCluster.existing_profile?.strengths || []).map((s, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-2 mt-0.5 flex-shrink-0">
                              {idx + 1}
                            </span>
                            <span className="text-gray-700">{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(selectedCluster.existing_profile?.weaknesses || []).length > 0 && (
                    <div className="bg-white rounded-xl p-5 shadow-sm">
                      <h4 className="font-bold text-lg mb-3 flex items-center text-orange-700">
                        <div className="bg-orange-100 rounded-lg p-2 mr-2">
                          <i className="fas fa-exclamation-triangle"></i>
                        </div>
                        Điểm yếu
                      </h4>
                      <ul className="space-y-2">
                        {(selectedCluster.existing_profile?.weaknesses || []).map((w, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-2 mt-0.5 flex-shrink-0">
                              {idx + 1}
                            </span>
                            <span className="text-gray-700">{w}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {(selectedCluster.existing_profile?.recommendations || []).length > 0 && (
                  <div className="mt-4 bg-white rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-lg mb-3 flex items-center text-blue-700">
                      <div className="bg-blue-100 rounded-lg p-2 mr-2">
                        <i className="fas fa-lightbulb"></i>
                      </div>
                      Đề xuất cho giáo viên
                    </h4>
                    <ul className="space-y-2">
                      {(selectedCluster.existing_profile?.recommendations || []).map((r, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-2 mt-0.5 flex-shrink-0">
                            {idx + 1}
                          </span>
                          <span className="text-gray-700">{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modern Recommendation Form */}
      <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-3xl shadow-xl p-8 border border-indigo-100">
        <div className="flex items-center mb-6">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl p-4 mr-4 shadow-lg">
            <i className="fas fa-magic text-3xl text-white"></i>
          </div>
          <div>
            <h2 className="text-3xl font-bold text-gray-800">
              Lấy Gợi Ý Học Tập
            </h2>
            <p className="text-gray-500 mt-1">Nhận gợi ý cá nhân hóa từ AI</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center">
              <i className="fas fa-user-circle mr-2 text-indigo-500"></i>
              Student ID
            </label>
            <input
              type="number"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
              placeholder="Nhập Student ID"
            />
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center">
              <i className="fas fa-book mr-2 text-purple-500"></i>
              Course ID
            </label>
            <input
              type="number"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
              placeholder="Nhập Course ID"
            />
          </div>
        </div>

        <button
          onClick={handleGetRecommendation}
          className="w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center justify-center"
        >
          <i className="fas fa-sparkles mr-2"></i>
          Lấy Gợi Ý Từ AI
          <i className="fas fa-arrow-right ml-2"></i>
        </button>

        {/* Modern Recommendation Result */}
        {recommendation && (
          <div className="mt-8 space-y-6">
            {/* Learning State */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-indigo-100">
              <h3 className="font-bold text-xl text-gray-800 mb-4 flex items-center">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl p-2 mr-3">
                  <i className="fas fa-user-circle text-white"></i>
                </div>
                Thông tin học sinh
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4">
                  <p className="text-sm font-semibold text-gray-600 mb-2">Cluster ID</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    {recommendation.cluster_id || 0}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 md:col-span-2">
                  <p className="text-sm font-semibold text-gray-600 mb-2">Nhóm học sinh</p>
                  <p className="text-xl font-bold text-gray-800">
                    {recommendation.cluster_name || 'Unknown Cluster'}
                  </p>
                </div>
              </div>
            </div>

            {/* State Description */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-blue-100">
              <h3 className="font-bold text-xl text-gray-800 mb-4 flex items-center">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl p-2 mr-3">
                  <i className="fas fa-chart-line text-white"></i>
                </div>
                Trạng thái học tập
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Performance */}
                <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4">
                  <h4 className="font-semibold text-sm text-blue-700 mb-3">📊 Hiệu suất</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Knowledge</span>
                      <span className="font-bold text-blue-600">
                        {((recommendation.state_description?.performance?.knowledge_level || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Engagement</span>
                      <span className="font-bold text-blue-600">
                        {((recommendation.state_description?.performance?.engagement_level || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Struggle</span>
                      <span className="font-bold text-blue-600">
                        {((recommendation.state_description?.performance?.struggle_indicator || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Activity Patterns */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4">
                  <h4 className="font-semibold text-sm text-purple-700 mb-3">🎯 Hoạt động</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Submission</span>
                      <span className="font-bold text-purple-600">
                        {((recommendation.state_description?.activity_patterns?.submission_activity || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Review</span>
                      <span className="font-bold text-purple-600">
                        {((recommendation.state_description?.activity_patterns?.review_activity || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Assessment</span>
                      <span className="font-bold text-purple-600">
                        {((recommendation.state_description?.activity_patterns?.assessment_engagement || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Completion Metrics */}
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4">
                  <h4 className="font-semibold text-sm text-green-700 mb-3">✅ Hoàn thành</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-bold text-green-600">
                        {((recommendation.state_description?.completion_metrics?.overall_progress || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Module Rate</span>
                      <span className="font-bold text-green-600">
                        {((recommendation.state_description?.completion_metrics?.module_completion_rate || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Consistency</span>
                      <span className="font-bold text-green-600">
                        {((recommendation.state_description?.completion_metrics?.completion_consistency || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-green-100">
              <h3 className="font-bold text-xl text-gray-800 mb-4 flex items-center">
                <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl p-2 mr-3">
                  <i className="fas fa-book text-white"></i>
                </div>
                Tài liệu được đề xuất (Top {recommendation.recommendations?.length || 0})
              </h3>
              <div className="space-y-4">
                {(recommendation.recommendations || []).map((rec, idx) => (
                  <div key={idx} className="relative bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-200 border border-green-100">
                    <div className="absolute -top-3 -left-3 bg-gradient-to-br from-green-500 to-emerald-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shadow-lg">
                      {idx + 1}
                    </div>
                    <div className="ml-6">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-bold text-lg text-gray-800 mb-2">
                            {rec.name || 'Unknown Resource'}
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                              <i className="fas fa-book mr-1"></i>
                              {rec.type || 'N/A'}
                            </span>
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700">
                              <i className="fas fa-target mr-1"></i>
                              {rec.purpose || 'N/A'}
                            </span>
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                              rec.difficulty === 'hard' ? 'bg-red-100 text-red-700' :
                              rec.difficulty === 'medium' ? 'bg-orange-100 text-orange-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              <i className="fas fa-signal mr-1"></i>
                              {rec.difficulty || 'N/A'}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white text-sm font-bold px-4 py-2 rounded-full shadow-sm">
                            Q: {(rec.q_value || 0).toFixed(2)}
                          </div>
                        </div>
                      </div>
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-gray-600 text-sm">
                          <i className="fas fa-info-circle text-blue-500 mr-2"></i>
                          <span className="font-semibold">Action ID:</span> {rec.action_id}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Model Info */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
              <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
                <div className="flex items-center">
                  <i className="fas fa-database mr-2 text-indigo-500"></i>
                  <span><span className="font-semibold">{(recommendation.model_info?.n_states_in_qtable || 0).toLocaleString()}</span> states</span>
                </div>
                <span className="text-gray-400">•</span>
                <div className="flex items-center">
                  <i className="fas fa-sync-alt mr-2 text-purple-500"></i>
                  <span><span className="font-semibold">{(recommendation.model_info?.total_updates || 0).toLocaleString()}</span> updates</span>
                </div>
                <span className="text-gray-400">•</span>
                <div className="flex items-center">
                  <i className="fas fa-play-circle mr-2 text-green-500"></i>
                  <span><span className="font-semibold">{(recommendation.model_info?.episodes || 0).toLocaleString()}</span> episodes</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QLearningDashboard;
