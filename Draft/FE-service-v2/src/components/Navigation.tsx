import React from 'react';
import type { UserRole } from '../types';

interface NavigationProps {
  userRole: UserRole;
  currentPage: string;
  onNavigate: (page: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ userRole, currentPage, onNavigate }) => {
  const getMenuItems = () => {
    const commonItems = [
      { id: 'profile', label: 'Profile', icon: 'fas fa-user' },
      { id: 'qlearning', label: 'Q-Learning AI', icon: 'fas fa-brain' },
    ];

    switch (userRole) {
      case 'STUDENT':
        return [
          ...commonItems,
          { id: 'roadmap', label: 'Learning Roadmap', icon: 'fas fa-road' },
          { id: 'progress', label: 'My Progress', icon: 'fas fa-chart-line' },
          { id: 'activities', label: 'My Activities', icon: 'fas fa-list-ul' },
        ];
      
      case 'INSTRUCTOR':
        return [
          ...commonItems,
          { id: 'students', label: 'Students Overview', icon: 'fas fa-users' },
          { id: 'analytics', label: 'Video Analytics', icon: 'fas fa-video' },
          { id: 'reports', label: 'Activity Reports', icon: 'fas fa-chart-bar' },
        ];
      
      case 'ADMIN':
        return [
          ...commonItems,
          { id: 'dashboard', label: 'Admin Dashboard', icon: 'fas fa-tachometer-alt' },
          { id: 'users', label: 'User Management', icon: 'fas fa-users-cog' },
          { id: 'system', label: 'System Analytics', icon: 'fas fa-server' },
          { id: 'settings', label: 'System Settings', icon: 'fas fa-cogs' },
        ];
      
      default:
        return commonItems;
    }
  };

  const menuItems = getMenuItems();

  return (
    <nav className="bg-white shadow-lg h-full border-r border-primary-200">
      <div className="p-4">
        <h2 className="text-lg font-semibold text-primary-800 mb-4">
          {userRole === 'STUDENT' && 'Student Portal'}
          {userRole === 'INSTRUCTOR' && 'Instructor Dashboard'}
          {userRole === 'ADMIN' && 'Admin Panel'}
        </h2>
        
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                  currentPage === item.id
                    ? 'bg-primary-500 text-white shadow-md'
                    : 'text-gray-700 hover:bg-primary-50 hover:text-primary-700'
                }`}
              >
                <i className={`${item.icon} text-lg`}></i>
                <span className="font-medium">{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
