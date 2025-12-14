import {
  LayoutDashboard,
  Users,
  Brain,
  BarChart3,
  Settings,
  BookOpen,
  MessageSquare,
  ArrowRight,
  GraduationCap,
} from "lucide-react";
import { cn } from "./ui/utils";

interface SidebarProps {
  userRole: "student" | "teacher";
  currentPage: string;
  onNavigate: (page: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

const studentMenuItems = [
  { id: "dashboard", label: "My Overview", icon: LayoutDashboard },
  // { id: "ai-feedback", label: "AI Feedback", icon: Brain },
  // { id: "next-lesson", label: "Next Lesson", icon: ArrowRight },
  // { id: "learning-path", label: "Learning Path", icon: BookOpen },
];

const teacherMenuItems = [
  { id: "dashboard", label: "Bảng điều khiển", icon: LayoutDashboard },
  // { id: "class-overview", label: "Class Overview", icon: GraduationCap },
  { id: "students", label: "Danh sách học sinh", icon: Users },
  { id: "course-analytics", label: "Phân tích khóa học", icon: BarChart3 },
  // { id: "ai-insights", label: "AI Insights", icon: Brain },
  { id: "settings", label: "Cài đặt", icon: Settings },
];

export function Sidebar({ userRole, currentPage, onNavigate, isOpen, onClose }: SidebarProps) {
  const menuItems =
    userRole === "student" ? studentMenuItems : teacherMenuItems;

  const handleNavigate = (page: string) => {
    onNavigate(page);
    onClose?.();
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
      <aside className={cn(
        "w-64 border-r bg-card h-full overflow-y-auto transition-transform duration-300 ease-in-out",
        "md:translate-x-0",
        "fixed md:relative top-16 md:top-0 left-0 z-50",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="p-4">
          <div className="mb-6">
            <p className="text-xs text-muted-foreground uppercase tracking-wider px-3 mb-2">
              {userRole === "student" ? "Quản lý thông tin" : "Quản lý lớp học"}
            </p>
          </div>

          <nav className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-md"
                      : "text-foreground hover:bg-secondary"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}
