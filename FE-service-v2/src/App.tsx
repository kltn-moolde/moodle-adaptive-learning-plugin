import { useState } from 'react';
import type { User } from './types';
import Header from './components/Header';
import Navigation from './components/Navigation';
import StudentDashboard from './pages/StudentDashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import Profile from './pages/Profile';
import { useLTIAuth, LTILoader, LTIError, LTIContext } from './components/lti';
import {
  mockUsers,
  mockStudentProgress,
  mockVideoAnalytics,
  mockActionAnalytics,
  mockSystemMetrics
} from './data/mockData';

function App() {
  // Use LTI authentication instead of mock users
  const { user: ltiUser, loading, isLTI, error, reinitialize } = useLTIAuth();

  // Fallback to mock user for testing when not in LTI context
  const [fallbackUser, setFallbackUser] = useState<User>(mockUsers[0]);


  // Use LTI user if available, otherwise fallback user
  const currentUser: User = ltiUser ? {
    id: ltiUser.id.toString(),
    name: ltiUser.name,
    email: ltiUser.email,
    role: ltiUser.roleName as 'STUDENT' | 'INSTRUCTOR' | 'ADMIN',
    avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(ltiUser.name)}&background=0D8ABC&color=fff`,
  } : fallbackUser;
  console.log('LTI User:', ltiUser);
  console.log('Current User:', currentUser);
  console.log('Current User Role:', currentUser.role);
  console.log('Role type:', typeof currentUser.role);
  const [currentPage, setCurrentPage] = useState<string>(() => {
    if (ltiUser) {
      return getDefaultPage(normalizeRole(ltiUser.roleName));
    }
    return 'roadmap';
  });

  const normalizeRole = (role: string): 'STUDENT' | 'INSTRUCTOR' | 'ADMIN' => {
    const upperRole = role.toUpperCase();
    if (upperRole === 'INSTRUCTOR' || upperRole === 'TEACHER') return 'INSTRUCTOR';
    if (upperRole === 'STUDENT' || upperRole === 'LEARNER') return 'STUDENT';
    if (upperRole === 'ADMIN' || upperRole === 'ADMINISTRATOR') return 'ADMIN';
    return 'STUDENT'; // Default fallback
  };

  const getDefaultPage = (role: string) => {
    switch (role) {
      case 'STUDENT': return 'roadmap';
      case 'INSTRUCTOR': return 'students';
      case 'ADMIN': return 'dashboard';
      default: return 'roadmap';
    }
  };

  // Show loading screen during LTI authentication
  if (loading) {
    return <LTILoader />;
  }

  // Show error screen if LTI authentication failed
  if (error && isLTI) {
    return <LTIError error={error} onRetry={reinitialize} />;
  }

  const handleProfileClick = () => {
    setCurrentPage('profile');
  };

  const handleLogout = () => {
    // Simulate logout
    console.log('Logging out...');
  };

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
  };

  const handleUpdateUser = (updatedUser: User) => {
    if (ltiUser) {
      // For LTI users, we can't really update the user data
      // since it comes from Moodle, so we just log it
      console.log('LTI user update attempt:', updatedUser);
    } else {
      setFallbackUser(updatedUser);
    }
  };

  const renderContent = () => {
    switch (currentPage) {
      case 'profile':
        return <Profile user={currentUser} onUpdateUser={handleUpdateUser} />;

      // Student pages
      case 'roadmap':
        if (currentUser.role === 'STUDENT') {
          return (
            <StudentDashboard
              userId={parseInt(currentUser.id)}
              courseId={parseInt(ltiUser?.courseId?.toString() || '3')}
            />
          );
        }
        break;
      case 'progress':
        if (currentUser.role === 'STUDENT') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">My Progress</h2>
            <p className="text-gray-600">Detailed progress analytics coming soon...</p>
          </div>;
        }
        break;
      case 'activities':
        if (currentUser.role === 'STUDENT') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">My Activities</h2>
            <p className="text-gray-600">Activity timeline coming soon...</p>
          </div>;
        }
        break;

      // Instructor pages
      case 'students':
        if (currentUser.role === 'INSTRUCTOR') {
          return (
            <InstructorDashboard
              students={mockStudentProgress}
              videoAnalytics={mockVideoAnalytics}
              actionAnalytics={mockActionAnalytics}
            />
          );
        }
        break;
      case 'analytics':
        if (currentUser.role === 'INSTRUCTOR') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">Video Analytics</h2>
            <p className="text-gray-600">Detailed video analytics coming soon...</p>
          </div>;
        }
        break;
      case 'reports':
        if (currentUser.role === 'INSTRUCTOR') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">Activity Reports</h2>
            <p className="text-gray-600">Comprehensive reports coming soon...</p>
          </div>;
        }
        break;

      // Admin pages
      case 'dashboard':
        if (currentUser.role === 'ADMIN') {
          return (
            <AdminDashboard
              users={mockUsers}
              systemMetrics={mockSystemMetrics}
            />
          );
        }
        break;
      case 'users':
        if (currentUser.role === 'ADMIN') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">User Management</h2>
            <p className="text-gray-600">User management features coming soon...</p>
          </div>;
        }
        break;
      case 'system':
        if (currentUser.role === 'ADMIN') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">System Analytics</h2>
            <p className="text-gray-600">System analytics coming soon...</p>
          </div>;
        }
        break;
      case 'settings':
        if (currentUser.role === 'ADMIN') {
          return <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">System Settings</h2>
            <p className="text-gray-600">System settings coming soon...</p>
          </div>;
        }
        break;

      default:
        return <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-primary-800 mb-4">Welcome</h2>
          <p className="text-gray-600">Select an option from the navigation menu.</p>
        </div>;
    }

    return <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-primary-800 mb-4">Access Denied</h2>
      <p className="text-gray-600">You don't have permission to access this page.</p>
    </div>;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header
        user={currentUser}
        onProfileClick={handleProfileClick}
        onLogout={handleLogout}
      />

      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-64 min-h-screen bg-white shadow-lg">
          <Navigation
            userRole={currentUser.role}
            currentPage={currentPage}
            onNavigate={handleNavigate}
          />
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {renderContent()}
        </div>
      </div>

      {/* Role Switcher for Testing - Only show when not in LTI context */}
      {!isLTI && (
        <div className="fixed bottom-4 right-4 z-50">
          <div className="bg-white border rounded-lg shadow-lg p-3">
            <p className="text-xs text-gray-600 mb-2">Test as:</p>
            <div className="flex space-x-2">
              {mockUsers.slice(0, 3).map((user) => (
                <button
                  key={user.id}
                  onClick={() => {
                    setFallbackUser(user);
                    setCurrentPage(user.role === 'STUDENT' ? 'roadmap' :
                      user.role === 'INSTRUCTOR' ? 'students' : 'dashboard');
                  }}
                  className={`px-2 py-1 text-xs rounded ${currentUser.id === user.id
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                >
                  {user.role}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* LTI Context Indicator */}
      {isLTI && ltiUser && (
        <div className="fixed top-4 right-4 z-50">
          <LTIContext user={ltiUser} />
        </div>
      )}
    </div>
  );
}

export default App;
