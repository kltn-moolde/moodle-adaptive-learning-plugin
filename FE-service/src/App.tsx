import { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Login from './components/Login';
import StudentDashboard from './components/StudentDashboard';
import InstructorDashboard from './components/InstructorDashboard';
import AdminDashboard from './components/AdminDashboard';
import { 
  mockUsers, 
  mockLearningPath, 
  mockStudentProgress, 
  mockCourseStats
} from './data/mockData';
import { courseService } from './service/courseService';
import type { User, Course } from './types';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);

  useEffect(() => {
    if (currentUser?.role === 'INSTRUCTOR') {
      courseService.getCourses()
        .then(setCourses)
        .catch(err => console.error("Lỗi khi load courses:", err));
    }
  }, [currentUser]);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setCourses([]); // clear khi logout
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
            courses={courses}   // ✅ truyền courses từ API
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