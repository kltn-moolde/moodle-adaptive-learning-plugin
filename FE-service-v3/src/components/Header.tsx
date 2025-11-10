import { Bell, Moon, Sun, User } from "lucide-react";
import { Button } from "./ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Badge } from "./ui/badge";

interface HeaderProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
  userRole: "student" | "teacher";
  userName: string;
  userAvatar?: string;
}

export function Header({
  darkMode,
  toggleDarkMode,
  userRole,
  userName,
  userAvatar,
}: HeaderProps) {
  return (
    <header className="h-16 border-b bg-card px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary to-green-400 flex items-center justify-center">
          <span className="text-white text-xl">🎓</span>
        </div>
        <div>
          <h1 className="text-lg text-foreground">Smart Learning Path</h1>
          <p className="text-xs text-muted-foreground">Learn Smarter with AI</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleDarkMode}
          className="rounded-xl"
        >
          {darkMode ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-xl relative">
              <Bell className="h-5 w-5" />
              <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center bg-accent text-accent-foreground border-0">
                3
              </Badge>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="flex flex-col items-start py-3">
              <p className="text-sm">🤖 AI Insight</p>
              <p className="text-xs text-muted-foreground">
                {userRole === "student"
                  ? "You're doing great! Review Bayes' Theorem next."
                  : "80% of students need help with If-Else Statements"}
              </p>
            </DropdownMenuItem>
            <DropdownMenuItem className="flex flex-col items-start py-3">
              <p className="text-sm">📚 New Lesson Available</p>
              <p className="text-xs text-muted-foreground">
                Advanced Python Functions is now ready
              </p>
            </DropdownMenuItem>
            <DropdownMenuItem className="flex flex-col items-start py-3">
              <p className="text-sm">⭐ Achievement Unlocked</p>
              <p className="text-xs text-muted-foreground">
                {userRole === "student"
                  ? "Completed 10 lessons this week!"
                  : "Your class achieved 90% completion rate"}
              </p>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 rounded-xl px-3"
            >
              <Avatar className="h-8 w-8">
                <AvatarImage src={userAvatar} alt={userName} />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {userName
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="hidden md:inline">{userName}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
