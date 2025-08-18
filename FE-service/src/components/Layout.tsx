import React from 'react';
import { LogOut, Home, Users, BarChart3, Settings } from 'lucide-react';
import type { User as UserType } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  user: UserType;
  onLogout: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, user, onLogout }) => {
  const getNavigationItems = () => {
    switch (user.role) {
      case 'STUDENT':
        return [
          { icon: Home, label: 'Lộ trình học', href: '#roadmap' },
          { icon: BarChart3, label: 'Điểm số', href: '#scores' },
        ];
      case 'INSTRUCTOR':
        return [
          { icon: Home, label: 'Tổng quan', href: '#overview' },
          { icon: Users, label: 'Học sinh', href: '#students' },
          { icon: BarChart3, label: 'Thống kê', href: '#statistics' },
        ];
      case 'ADMIN':
        return [
          { icon: Home, label: 'Dashboard', href: '#dashboard' },
          { icon: Users, label: 'Quản lý người dùng', href: '#users' },
          { icon: Settings, label: 'Cài đặt', href: '#settings' },
        ];
      default:
        return [];
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white bg-opacity-90 backdrop-blur-md shadow-lg border-b border-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                <h1 className="text-xl font-bold">
                  Adaptive Learning System
                </h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700 font-medium">
                {user.name} ({user.role === 'ADMIN' ? 'Quản trị' : user.role === 'INSTRUCTOR' ? 'Giảng viên' : 'Học sinh'})
              </span>
              {user.avatar && (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="h-8 w-8 rounded-full ring-2 ring-indigo-200"
                />
              )}
              <button
                onClick={onLogout}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 bg-white bg-opacity-80 backdrop-blur-sm shadow-xl h-[calc(100vh-4rem)] border-r border-indigo-100">
          <div className="p-4">
            <ul className="space-y-2">
              {navigationItems.map((item, index) => (
                <li key={index}>
                  <a
                    href={item.href}
                    className="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 hover:text-indigo-700 transition-all duration-200 group"
                  >
                    <item.icon className="h-5 w-5 mr-3 group-hover:text-indigo-600 transition-colors" />
                    <span className="font-medium">{item.label}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
