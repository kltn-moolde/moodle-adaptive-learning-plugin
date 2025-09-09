import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useLTIAuth, LTILoader, LTIError, LTIContext } from './components/lti';
import type { User } from './types';
import Header from './components/Header';
import Navigation from './components/Navigation';
import StudentDashboard from './pages/StudentDashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import Profile from './pages/Profile';
import {
  mockUsers,
  mockLearningPath,
  mockActivities,
  mockStudentProgress,
  mockVideoAnalytics,
  mockActionAnalytics,
  mockSystemMetrics
} from './data/mockData';

// Main Dashboard Component (works for both LTI and regular access)
const Dashboard: React.FC = () => {
  const { user: ltiUser, loading, isLTI, error, reinitialize } = useLTIAuth();
  
  // Show loading screen during LTI authentication
  if (loading) {
    return <LTILoader />;
  }

  // Show error screen if LTI authentication failed
  if (error && isLTI) {
    return <LTIError error={error} onRetry={reinitialize} />;
  }

  // Use LTI user if available, otherwise fallback user
  const currentUser: User = ltiUser ? {
    id: ltiUser.id.toString(),
    name: ltiUser.name,
    email: ltiUser.email,
    role: ltiUser.role as 'STUDENT' | 'INSTRUCTOR' | 'ADMIN',
    avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(ltiUser.name)}&background=0D8ABC&color=fff`,
  } : mockUsers[0]; // Default to first mock user

  const handleLogout = () => {
    console.log('Logging out...');
  };

  const handleUpdateUser = (updatedUser: User) => {
    if (ltiUser) {
      console.log('LTI user update attempt:', updatedUser);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* LTI Context Indicator */}
      {isLTI && ltiUser && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
          <LTIContext user={ltiUser} />
        </div>
      )}

      <Header 
        user={currentUser} 
        onProfileClick={() => {}}
        onLogout={handleLogout}
      />
      
      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-64 min-h-screen bg-white shadow-lg">
          <Navigation 
            userRole={currentUser.role}
            currentPage=""
            onNavigate={() => {}}
          />
        </div>
        
        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Route-based content will be rendered here by React Router */}
          <Routes>
            <Route path="/profile" element={
              <Profile user={currentUser} onUpdateUser={handleUpdateUser} />
            } />
            
            {/* Student Routes */}
            {currentUser.role === 'STUDENT' && (
              <>
                <Route path="/roadmap" element={
                  <StudentDashboard 
                    learningPath={mockLearningPath} 
                    recentActivities={mockActivities} 
                  />
                } />
                <Route path="/progress" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">My Progress</h2>
                    <p className="text-gray-600">Detailed progress analytics coming soon...</p>
                  </div>
                } />
                <Route path="/activities" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">My Activities</h2>
                    <p className="text-gray-600">Activity timeline coming soon...</p>
                  </div>
                } />
                <Route path="/" element={<Navigate to="/roadmap" replace />} />
              </>
            )}
            
            {/* Instructor Routes */}
            {currentUser.role === 'INSTRUCTOR' && (
              <>
                <Route path="/students" element={
                  <InstructorDashboard 
                    students={mockStudentProgress}
                    videoAnalytics={mockVideoAnalytics}
                    actionAnalytics={mockActionAnalytics}
                  />
                } />
                <Route path="/analytics" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">Video Analytics</h2>
                    <p className="text-gray-600">Detailed video analytics coming soon...</p>
                  </div>
                } />
                <Route path="/reports" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">Activity Reports</h2>
                    <p className="text-gray-600">Comprehensive reports coming soon...</p>
                  </div>
                } />
                <Route path="/" element={<Navigate to="/students" replace />} />
              </>
            )}
            
            {/* Admin Routes */}
            {currentUser.role === 'ADMIN' && (
              <>
                <Route path="/dashboard" element={
                  <AdminDashboard 
                    users={mockUsers}
                    systemMetrics={mockSystemMetrics}
                  />
                } />
                <Route path="/users" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">User Management</h2>
                    <p className="text-gray-600">User management features coming soon...</p>
                  </div>
                } />
                <Route path="/system" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">System Analytics</h2>
                    <p className="text-gray-600">System analytics coming soon...</p>
                  </div>
                } />
                <Route path="/settings" element={
                  <div className="p-6 bg-white rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-primary-800 mb-4">System Settings</h2>
                    <p className="text-gray-600">System settings coming soon...</p>
                  </div>
                } />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </>
            )}
            
            <Route path="*" element={
              <div className="p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-bold text-primary-800 mb-4">Welcome</h2>
                <p className="text-gray-600">Select an option from the navigation menu.</p>
              </div>
            } />
          </Routes>
        </div>
      </div>
    </div>
  );
};

// Main App Component with Router
const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* LTI Dashboard Route (from Python LTI service) */}
        <Route path="/lti-dashboard/*" element={<Dashboard />} />
        
        {/* Default Dashboard Route */}
        <Route path="/*" element={<Dashboard />} />
      </Routes>
    </Router>
  );
};

export default App;
