import React from 'react';
import type { User } from '../types';

interface HeaderProps {
  user: User;
  onProfileClick: () => void;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, onProfileClick, onLogout }) => {
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-red-100 text-red-800';
      case 'INSTRUCTOR':
        return 'bg-green-100 text-green-800';
      case 'STUDENT':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <header className="bg-white shadow-lg border-b border-primary-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-primary-600">
                <i className="fas fa-graduation-cap mr-2"></i>
                Adaptive Learning
              </h1>
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {/* Role Badge */}
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRoleColor(user.role)}`}>
              {user.role}
            </span>

            {/* User Profile */}
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
              
              <div className="relative">
                <button
                  onClick={onProfileClick}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-primary-50 transition-colors"
                >
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full" />
                    ) : (
                      <span className="text-white text-sm font-medium">
                        {user.name.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <i className="fas fa-chevron-down text-gray-400 text-xs"></i>
                </button>
              </div>

              {/* Logout Button */}
              <button
                onClick={onLogout}
                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                title="Logout"
              >
                <i className="fas fa-sign-out-alt"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
