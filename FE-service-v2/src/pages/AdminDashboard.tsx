import React, { useState } from 'react';
import type { User } from '../types';

interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalCourses: number;
  totalVideos: number;
  systemUptime: string;
  averageResponseTime: string;
}

interface AdminDashboardProps {
  users: User[];
  systemMetrics: SystemMetrics;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ users, systemMetrics }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'system'>('overview');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const getRoleStats = () => {
    const stats = { STUDENT: 0, INSTRUCTOR: 0, ADMIN: 0 };
    users.forEach(user => {
      stats[user.role]++;
    });
    return stats;
  };

  const roleStats = getRoleStats();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-primary-800 mb-2">Admin Dashboard</h2>
        <p className="text-gray-600">System overview and user management</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { id: 'overview', label: 'System Overview', icon: 'fas fa-tachometer-alt' },
              { id: 'users', label: 'User Management', icon: 'fas fa-users-cog' },
              { id: 'system', label: 'System Analytics', icon: 'fas fa-server' },
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
          {/* System Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100">Total Users</p>
                      <p className="text-3xl font-bold">{systemMetrics.totalUsers}</p>
                    </div>
                    <i className="fas fa-users text-2xl text-blue-200"></i>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-100">Active Users</p>
                      <p className="text-3xl font-bold">{systemMetrics.activeUsers}</p>
                    </div>
                    <i className="fas fa-user-check text-2xl text-green-200"></i>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-lg text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100">Total Courses</p>
                      <p className="text-3xl font-bold">{systemMetrics.totalCourses}</p>
                    </div>
                    <i className="fas fa-graduation-cap text-2xl text-purple-200"></i>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-6 rounded-lg text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-orange-100">Total Videos</p>
                      <p className="text-3xl font-bold">{systemMetrics.totalVideos}</p>
                    </div>
                    <i className="fas fa-video text-2xl text-orange-200"></i>
                  </div>
                </div>
              </div>

              {/* Role Distribution */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">User Role Distribution</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{roleStats.STUDENT}</div>
                    <div className="text-sm text-gray-600">Students</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{roleStats.INSTRUCTOR}</div>
                    <div className="text-sm text-gray-600">Instructors</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{roleStats.ADMIN}</div>
                    <div className="text-sm text-gray-600">Admins</div>
                  </div>
                </div>
              </div>

              {/* System Status */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">System Status</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">System Uptime</span>
                      <span className="font-medium text-green-600">{systemMetrics.systemUptime}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Response Time</span>
                      <span className="font-medium">{systemMetrics.averageResponseTime}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Server Status</span>
                      <span className="flex items-center text-green-600">
                        <i className="fas fa-circle text-xs mr-2"></i>
                        Online
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
                  <div className="space-y-2">
                    <button className="w-full text-left px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors">
                      <i className="fas fa-user-plus mr-2"></i>
                      Add New User
                    </button>
                    <button className="w-full text-left px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
                      <i className="fas fa-plus mr-2"></i>
                      Create Course
                    </button>
                    <button className="w-full text-left px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors">
                      <i className="fas fa-cogs mr-2"></i>
                      System Settings
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* User Management Tab */}
          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">User Management</h3>
                <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
                  <i className="fas fa-plus mr-2"></i>
                  Add User
                </button>
              </div>
              
              {/* Users Table */}
              <div className="bg-white rounded-lg border overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Activity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                              {user.avatar ? (
                                <img src={user.avatar} alt={user.name} className="w-10 h-10 rounded-full" />
                              ) : (
                                <span className="text-white font-medium">
                                  {user.name.charAt(0).toUpperCase()}
                                </span>
                              )}
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{user.name}</div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.role === 'ADMIN' ? 'bg-red-100 text-red-800' :
                            user.role === 'INSTRUCTOR' ? 'bg-green-100 text-green-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.lastActivity || 'Never'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button 
                            onClick={() => setSelectedUser(user)}
                            className="text-primary-600 hover:text-primary-900 mr-3"
                          >
                            Edit
                          </button>
                          <button className="text-red-600 hover:text-red-900">
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* System Analytics Tab */}
          {activeTab === 'system' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-800">System Analytics</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Performance Metrics */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Performance Metrics</h4>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>CPU Usage</span>
                        <span>23%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '23%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Memory Usage</span>
                        <span>67%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '67%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Disk Usage</span>
                        <span>45%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recent Logs */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Recent System Logs</h4>
                  <div className="space-y-2 text-sm max-h-48 overflow-y-auto">
                    <div className="flex items-start space-x-2">
                      <i className="fas fa-circle text-green-500 text-xs mt-1"></i>
                      <span className="text-gray-600">2025-08-20 10:30:15 - User login successful</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <i className="fas fa-circle text-blue-500 text-xs mt-1"></i>
                      <span className="text-gray-600">2025-08-20 10:28:42 - Video upload completed</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <i className="fas fa-circle text-yellow-500 text-xs mt-1"></i>
                      <span className="text-gray-600">2025-08-20 10:25:18 - Database backup started</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <i className="fas fa-circle text-green-500 text-xs mt-1"></i>
                      <span className="text-gray-600">2025-08-20 10:20:03 - Course created successfully</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
