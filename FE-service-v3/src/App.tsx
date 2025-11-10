import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { StudentDashboard } from "./components/student/StudentDashboard";
import { TeacherDashboard } from "./components/teacher/TeacherDashboard";
import { StudentList } from "./components/teacher/StudentList";
import { CourseAnalytics } from "./components/teacher/CourseAnalytics";
import { Button } from "./components/ui/button";
import { Users, GraduationCap } from "lucide-react";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [userRole, setUserRole] = useState<"student" | "teacher">("student");
  const [currentPage, setCurrentPage] = useState("dashboard");

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const toggleUserRole = () => {
    setUserRole(userRole === "student" ? "teacher" : "student");
    setCurrentPage("dashboard");
  };

  const renderContent = () => {
    if (userRole === "student") {
      switch (currentPage) {
        case "dashboard":
        case "ai-feedback":
        case "next-lesson":
        case "learning-path":
          return <StudentDashboard />;
        default:
          return <StudentDashboard />;
      }
    } else {
      switch (currentPage) {
        case "dashboard":
          return <TeacherDashboard />;
        case "class-overview":
          return <TeacherDashboard />;
        case "students":
          return <StudentList />;
        case "course-analytics":
          return <CourseAnalytics />;
        case "ai-insights":
          return <TeacherDashboard />;
        case "settings":
          return (
            <div className="p-6">
              <div className="max-w-2xl mx-auto">
                <h2 className="text-2xl mb-4">Settings</h2>
                <p className="text-muted-foreground">
                  Course and platform settings will be available here.
                </p>
              </div>
            </div>
          );
        default:
          return <TeacherDashboard />;
      }
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
        userRole={userRole}
        userName={userRole === "student" ? "Hoàng Sinh" : "Giáo viên Nguyễn"}
      />
      
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          userRole={userRole}
          currentPage={currentPage}
          onNavigate={setCurrentPage}
        />
        
        <main className="flex-1 overflow-y-auto bg-background">
          <AnimatePresence mode="wait">
            <motion.div
              key={`${userRole}-${currentPage}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Demo Role Toggle Button */}
      <Button
        onClick={toggleUserRole}
        className="fixed bottom-6 right-6 rounded-full h-14 px-6 shadow-2xl bg-primary hover:bg-primary/90 z-50"
      >
        {userRole === "student" ? (
          <>
            <Users className="h-5 w-5 mr-2" />
            Switch to Teacher View
          </>
        ) : (
          <>
            <GraduationCap className="h-5 w-5 mr-2" />
            Switch to Student View
          </>
        )}
      </Button>
    </div>
  );
}
