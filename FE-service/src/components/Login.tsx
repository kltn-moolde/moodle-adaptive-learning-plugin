import React, { useState } from 'react';
import { LogIn } from 'lucide-react';
import type { User, UserRole } from '../types';

interface LoginProps {
  onLogin: (user: User) => void;
  mockUsers: User[];
}

const Login: React.FC<LoginProps> = ({ onLogin, mockUsers }) => {
  const [selectedRole, setSelectedRole] = useState<UserRole>('STUDENT');

  const handleLogin = () => {
    const user = mockUsers.find(u => u.role === selectedRole);
    if (user) {
      onLogin(user);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="bg-white bg-opacity-20 backdrop-blur-md rounded-full p-4 shadow-xl">
            <LogIn className="h-12 w-12 text-white" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-4xl font-extrabold text-white">
          🚀 Adaptive Learning
        </h2>
        <p className="mt-2 text-center text-lg text-white text-opacity-80">
          Hệ thống học tăng cường thông minh
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white bg-opacity-90 backdrop-blur-md py-8 px-4 shadow-2xl sm:rounded-2xl sm:px-10 border border-white border-opacity-20">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-4">
                🎭 Chọn vai trò để demo
              </label>
              <div className="mt-3 space-y-4">
                <div className="flex items-center p-4 rounded-xl border-2 border-gray-200 hover:border-blue-300 transition-all cursor-pointer bg-gradient-to-r from-blue-50 to-indigo-50">
                  <input
                    id="student"
                    name="role"
                    type="radio"
                    checked={selectedRole === 'STUDENT'}
                    onChange={() => setSelectedRole('STUDENT')}
                    className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300"
                  />
                  <label htmlFor="student" className="ml-3 block text-sm font-bold text-gray-700">
                    🎓 <span className="text-blue-600">Học sinh</span> - Xem lộ trình học và điểm số
                  </label>
                </div>
                <div className="flex items-center p-4 rounded-xl border-2 border-gray-200 hover:border-purple-300 transition-all cursor-pointer bg-gradient-to-r from-purple-50 to-pink-50">
                  <input
                    id="instructor"
                    name="role"
                    type="radio"
                    checked={selectedRole === 'INSTRUCTOR'}
                    onChange={() => setSelectedRole('INSTRUCTOR')}
                    className="focus:ring-purple-500 h-4 w-4 text-purple-600 border-gray-300"
                  />
                  <label htmlFor="instructor" className="ml-3 block text-sm font-bold text-gray-700">
                    👨‍🏫 <span className="text-purple-600">Giảng viên</span> - Quản lý học sinh và thống kê
                  </label>
                </div>
                <div className="flex items-center p-4 rounded-xl border-2 border-gray-200 hover:border-red-300 transition-all cursor-pointer bg-gradient-to-r from-red-50 to-orange-50">
                  <input
                    id="admin"
                    name="role"
                    type="radio"
                    checked={selectedRole === 'ADMIN'}
                    onChange={() => setSelectedRole('ADMIN')}
                    className="focus:ring-red-500 h-4 w-4 text-red-600 border-gray-300"
                  />
                  <label htmlFor="admin" className="ml-3 block text-sm font-bold text-gray-700">
                    ⚙️ <span className="text-red-600">Quản trị viên</span> - Quản lý hệ thống
                  </label>
                </div>
              </div>
            </div>

            <div>
              <button
                onClick={handleLogin}
                className="w-full flex justify-center py-4 px-4 border border-transparent rounded-xl shadow-lg text-lg font-bold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-xl"
              >
                <LogIn className="h-6 w-6 mr-2" />
                🎯 Đăng nhập Demo
              </button>
            </div>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500 font-bold">📋 Thông tin demo</span>
                </div>
              </div>

              <div className="mt-6 text-sm text-gray-600 space-y-2">
                <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                  <p><span className="font-bold text-blue-600">🎓 Học sinh:</span> Xem lộ trình học được AI gợi ý</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg border-l-4 border-purple-400">
                  <p><span className="font-bold text-purple-600">👨‍🏫 Giảng viên:</span> Theo dõi tiến độ học sinh</p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg border-l-4 border-red-400">
                  <p><span className="font-bold text-red-600">⚙️ Quản trị:</span> Quản lý hệ thống và người dùng</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
