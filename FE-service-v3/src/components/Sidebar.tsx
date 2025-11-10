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
}

const studentMenuItems = [
  { id: "dashboard", label: "My Overview", icon: LayoutDashboard },
  // { id: "ai-feedback", label: "AI Feedback", icon: Brain },
  // { id: "next-lesson", label: "Next Lesson", icon: ArrowRight },
  // { id: "learning-path", label: "Learning Path", icon: BookOpen },
];

const teacherMenuItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  // { id: "class-overview", label: "Class Overview", icon: GraduationCap },
  { id: "students", label: "Student List", icon: Users },
  { id: "course-analytics", label: "Course Analytics", icon: BarChart3 },
  // { id: "ai-insights", label: "AI Insights", icon: Brain },
  { id: "settings", label: "Settings", icon: Settings },
];

export function Sidebar({ userRole, currentPage, onNavigate }: SidebarProps) {
  const menuItems =
    userRole === "student" ? studentMenuItems : teacherMenuItems;

  return (
    <aside className="w-64 border-r bg-card h-full overflow-y-auto">
      <div className="p-4">
        <div className="mb-6">
          <p className="text-xs text-muted-foreground uppercase tracking-wider px-3 mb-2">
            {userRole === "student" ? "Student Portal" : "Teacher Portal"}
          </p>
        </div>

        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
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
  );
}
