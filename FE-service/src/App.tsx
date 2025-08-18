import { useState } from 'react';
import Layout from './components/Layout';
import Login from './components/Login';
import StudentDashboard from './components/StudentDashboard';
import InstructorDashboard from './components/InstructorDashboard';
import AdminDashboard from './components/AdminDashboard';
import { 
  mockUsers, 
  mockLearningPath, 
  mockStudentProgress, 
  mockCourseStats,
  mockLessons 
} from './data/mockData';
import type { User } from './types';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  const renderDashboard = () => {
    if (!currentUser) return null;

    switch (currentUser.role) {
      case 'STUDENT':
        return <StudentDashboard learningPath={mockLearningPath} />;
      case 'INSTRUCTOR':
        return (
          <InstructorDashboard 
            students={mockStudentProgress} 
            courseStats={mockCourseStats}
            lessons={mockLessons}
          />
        );
      case 'ADMIN':
        return (
          <AdminDashboard 
            users={mockUsers} 
            courseStats={mockCourseStats}
          />
        );
      default:
        return <div>Không tìm thấy dashboard cho role này</div>;
    }
  };

  if (!currentUser) {
    return <Login onLogin={handleLogin} mockUsers={mockUsers} />;
  }

  return (
    <Layout user={currentUser} onLogout={handleLogout}>
      {renderDashboard()}
    </Layout>
  );
}

export default App;
