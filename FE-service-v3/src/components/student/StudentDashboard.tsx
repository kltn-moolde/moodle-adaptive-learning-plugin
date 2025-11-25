import { motion } from "motion/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Progress } from "../ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import { BookOpen, Brain, TrendingUp, Award, Clock, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";
import {
  getSiteInfo,
  getUserCourses,
  getStudentProgress,
  getActivityHeatmap,
  getCourseContent,
  getCourseCompletion,
} from "../../services/moodleApi";

// Mock data as fallback
const mockProgressData = [
  { week: "Week 1", score: 65 },
  { week: "Week 2", score: 72 },
  { week: "Week 3", score: 78 },
  { week: "Week 4", score: 85 },
  { week: "Week 5", score: 88 },
  { week: "Week 6", score: 92 },
];

const mockSkillsData = [
  { skill: "Reading", value: 85 },
  { skill: "Practice", value: 92 },
  { skill: "Tests", value: 78 },
  { skill: "Projects", value: 88 },
  { skill: "Quizzes", value: 95 },
];

const mockActivityHeatmap = [
  { day: "Mon", hours: 2.5 },
  { day: "Tue", hours: 3.2 },
  { day: "Wed", hours: 1.8 },
  { day: "Thu", hours: 4.1 },
  { day: "Fri", hours: 2.9 },
  { day: "Sat", hours: 1.2 },
  { day: "Sun", hours: 0.5 },
];

const mockLearningPath = [
  { id: 1, title: "Introduction to Python", status: "completed", score: 95 },
  { id: 2, title: "Data Types & Variables", status: "completed", score: 88 },
  { id: 3, title: "Control Flow", status: "in-progress", score: 0 },
  { id: 4, title: "Functions", status: "locked", score: 0 },
  { id: 5, title: "Object-Oriented Programming", status: "locked", score: 0 },
];

export function StudentDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userData, setUserData] = useState<any>(null);
  const [currentCourse, setCurrentCourse] = useState<any>(null);
  const [progressData, setProgressData] = useState(mockProgressData);
  const [skillsData, setSkillsData] = useState(mockSkillsData);
  const [activityHeatmap, setActivityHeatmap] = useState(mockActivityHeatmap);
  const [learningPath, setLearningPath] = useState(mockLearningPath);
  const [overallProgress, setOverallProgress] = useState(75);
  const [completedLessons, setCompletedLessons] = useState(0);
  const [totalLessons, setTotalLessons] = useState(0);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  async function fetchDashboardData() {
    try {
      setLoading(true);
      setError(null);

      // Get current user info
      const siteInfo = await getSiteInfo();
      console.log("Fetched site info:", siteInfo);
      setUserData(siteInfo);

      // Get user's courses
      const courses = await getUserCourses(siteInfo.userid);
      console.log("Fetched courses:", courses);
      
      if (courses.length > 0) {
        // Use first course for demo
        const course = courses[0];
        console.log("Using course:", course);
        setCurrentCourse(course);
        setOverallProgress(course.progress || 75);
        

        // Get progress data
        const progress = await getStudentProgress(course.id, siteInfo.userid);
        console.log("Fetched progress:", progress);
        // setOverallProgress(progress.overall);
        setCompletedLessons(progress.completedLessons);
        setTotalLessons(progress.totalLessons);
        setProgressData(progress.grades);

        // Get activity heatmap
        const activity = await getActivityHeatmap(course.id, siteInfo.userid);
        console.log("Fetched activity heatmap:", activity);
        if (activity.length > 0) {
          setActivityHeatmap(activity);
        }

        // Get course content for learning path
        const content = await getCourseContent(course.id).catch(() => []);
        const completion = await getCourseCompletion(course.id, siteInfo.userid).catch(() => ({ completions: [] }));
        console.log("Fetched course content:", content);
        console.log("Fetched course completion:", completion);
        
        // Get completion statuses (Moodle API can return either 'statuses' or 'completions')
        const completionStatuses = (completion as any)?.statuses || (completion as any)?.completions || [];
        
        // Transform to learning path format: show main sections (Chủ đề) with their subsections (Bài học)
        const pathData: any[] = [];
        
        // Filter to get only main topic sections (skip section 0 which is "General")
        const mainSections = content.filter(section => 
          section.section > 0 && 
          section.name && 
          !section.name.includes("Bài") && 
          section.modules.length > 0
        );
        
        // Take first 5 main sections or all if less than 5
        const displaySections = mainSections.slice(0, 5);
        
        displaySections.forEach(section => {
          // Get subsections (modules with modname === 'subsection')
          const subsections = section.modules.filter(module => 
            module.modname === 'subsection'
          );
          
          // If no subsections, use regular modules instead (exclude qbank, lti)
          const itemsToShow = subsections.length > 0 
            ? subsections 
            : section.modules.filter(module => 
                module.modname !== 'qbank' && 
                module.modname !== 'lti' &&
                module.uservisible !== false
              );
          
          itemsToShow.forEach(item => {
            const itemCompletion = completionStatuses.find(
              (c: any) => c.cmid === item.id
            );
            const isCompleted = itemCompletion?.state === 1;
            
            pathData.push({
              id: item.id,
              title: item.name,
              status: isCompleted ? "completed" : "locked",
              score: isCompleted ? Math.floor(Math.random() * 20) + 80 : 0,
              sectionName: section.name, // Store parent section name
            });
          });
        });
        
        // Find first incomplete item and mark as in-progress
        const firstIncompleteIndex = pathData.findIndex(item => item.status === "locked");
        if (firstIncompleteIndex !== -1) {
          pathData[firstIncompleteIndex].status = "in-progress";
        }

        if (pathData.length > 0) {
          setLearningPath(pathData);
        }

        // Generate skills data based on completion
        const skillsPerformance = [
          { skill: "Reading", value: Math.min(progress.overall + 10, 100) },
          { skill: "Practice", value: Math.min(progress.overall + 15, 100) },
          { skill: "Tests", value: Math.max(progress.overall - 5, 0) },
          { skill: "Projects", value: Math.min(progress.overall + 8, 100) },
          { skill: "Quizzes", value: Math.min(progress.overall + 18, 100) },
        ];
        setSkillsData(skillsPerformance);
      }

      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      setError("Không thể tải dữ liệu từ Moodle. Hiển thị dữ liệu mẫu.");
      setLoading(false);
      // Keep mock data as fallback
    }
  }

  const userName = userData?.fullname || "Hoàng Sinh";
  const userInitials = userName
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const courseName = currentCourse?.fullname || "Python Programming";
  const nextLesson = learningPath.find(l => l.status === "in-progress") || learningPath[0];

  if (loading) {
    return (
      <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
        <div className="space-y-4">
          <div className="h-32 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="h-64 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
            <div className="h-64 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="h-80 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
            <div className="h-80 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Error Alert */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="border-yellow-400 bg-yellow-50 dark:bg-yellow-950">
            <CardContent className="p-4 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <p className="text-sm text-yellow-800 dark:text-yellow-200">{error}</p>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Profile Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="border border-green-400/30 rounded-2xl">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
              <Avatar className="h-20 w-20 sm:h-24 sm:w-24 border-4 border-green-400/40 shadow-md">
                <AvatarImage src={userData?.userpictureurl || ""} alt={userName} />
                <AvatarFallback className="bg-green-200 text-green-900 text-2xl font-semibold">
                  {userInitials}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 text-slate-100 w-full sm:w-auto">
                <h2 className="text-xl sm:text-2xl font-semibold mb-1 text-green-700 text-center sm:text-left">
                  {userName}
                </h2>
                <p className="text-slate-700 mb-4 text-center sm:text-left text-sm sm:text-base">
                  {courseName}
                </p>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm text-slate-700">
                    <span>Tiến độ</span>
                    <span className="text-green-700 font-medium">{overallProgress}%</span>
                  </div>
                  <Progress value={overallProgress} className="h-2 bg-gray-200! [&>div]:bg-green-400" />
                  {totalLessons > 0 && (
                    <p className="text-xs text-slate-600">
                      {completedLessons} / {totalLessons} modules completed
                    </p>
                  )}
                </div>
              </div>

              <div className="hidden lg:flex flex-col gap-3">
                <Badge className="bg-green-100 text-green-800 border-0 px-4 py-2 font-medium shadow-sm">
                  <Award className="h-4 w-4 mr-2 text-green-700" />
                  12 Danh hiệu
                </Badge>
                <Badge className="bg-blue-100 text-blue-800 border-0 px-4 py-2 font-medium shadow-sm">
                  <TrendingUp className="h-4 w-4 mr-2 text-blue-700" />
                  Hạng #2 trong lớp
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* AI Feedback */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                Phản hồi từ AI
              </CardTitle>
              <CardDescription>Gợi ý cá nhân hóa cho bạn</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950 p-3 sm:p-4 rounded-xl border border-primary/20">
                <div className="flex gap-2 sm:gap-3">
                  <div className="text-xl sm:text-2xl flex-shrink-0">💬</div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm mb-2">
                      <strong>Excellent progress!</strong> Bạn đang học rất tốt phần <strong>Probability</strong>.
                    </p>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      Nên ôn lại <strong>Bayes' Theorem</strong> trước khi chuyển sang chương mới để nắm vững kiến thức nhé.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-950 dark:to-amber-950 p-3 sm:p-4 rounded-xl border border-accent/20">
                <div className="flex gap-2 sm:gap-3">
                  <div className="text-xl sm:text-2xl flex-shrink-0">💡</div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm">
                      <strong>Suggestion:</strong> Thời gian học tốt nhất của bạn là buổi chiều. Hãy sắp xếp các bài khó vào thời điểm này!
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>Updated 5 minutes ago</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Next Lesson */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                Bài học tiếp theo
              </CardTitle>
              <CardDescription>Đề xuất từ AI cho bạn</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-secondary p-3 sm:p-4 rounded-xl mb-4">
                <h3 className="mb-2 text-sm sm:text-base">{nextLesson.title}</h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  {nextLesson.status === "in-progress" 
                    ? "Tiếp tục hành trình học tập với mô-đun này."
                    : "Phù hợp với trình độ hiện tại của bạn!"}
                </p>
                <div className="flex flex-wrap items-center gap-2 text-xs mb-4">
                  <Badge variant="outline" className="border-primary text-primary text-xs">
                    {nextLesson.status === "in-progress" ? "Tiếp tục" : "Bắt đầu"}
                  </Badge>
                  <Badge variant="outline" className="text-xs">⏱️ 45 phút</Badge>
                  {nextLesson.status === "completed" && (
                    <Badge variant="outline" className="text-xs">✓ Đã hoàn thành: {nextLesson.score}%</Badge>
                  )}
                </div>
                <Button className="w-full rounded-xl bg-primary hover:bg-primary/90 text-sm sm:text-base">
                  {nextLesson.status === "in-progress" ? "Tiếp tục học →" : "Bắt đầu học ngay →"}
                </Button>
              </div>

              <div className="space-y-2">
                <p className="text-xs sm:text-sm text-muted-foreground">Mục tiêu học tập:</p>
                <ul className="text-xs sm:text-sm space-y-1 ml-4">
                  <li>✓ Hiểu logic điều kiện</li>
                  <li>✓ Sử dụng câu lệnh if, elif và else</li>
                  <li>✓ Áp dụng điều kiện trong tình huống thực tế</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Progress Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Tiến độ học tập</CardTitle>
              <CardDescription>Điểm số của bạn trong 6 tuần qua</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="week" stroke="#64748B" fontSize={12} />
                  <YAxis stroke="#64748B" fontSize={12} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#16A34A"
                    strokeWidth={3}
                    dot={{ fill: "#16A34A", r: 5 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Skills Radar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Phân tích kỹ năng</CardTitle>
              <CardDescription>Hiệu suất qua các lĩnh vực khác nhau</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <RadarChart data={skillsData}>
                  <PolarGrid stroke="#E2E8F0" />
                  <PolarAngleAxis dataKey="skill" stroke="#64748B" fontSize={12} />
                  <PolarRadiusAxis stroke="#64748B" fontSize={12} />
                  <Radar
                    name="Performance"
                    dataKey="value"
                    stroke="#16A34A"
                    fill="#16A34A"
                    fillOpacity={0.3}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Activity Heatmap & Learning Path */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Activity Heatmap */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Hoạt động hàng tuần</CardTitle>
              <CardDescription>Số giờ học mỗi ngày</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 justify-between">
                {activityHeatmap.map((day) => (
                  <div key={day.day} className="flex-1">
                    <div
                      className="rounded-lg mb-2 flex items-end justify-center transition-all hover:scale-105"
                      style={{
                        height: `${Math.max(day.hours * 30, 20)}px`,
                        backgroundColor: `rgba(22, 163, 74, ${day.hours / 5})`,
                        minHeight: "20px",
                      }}
                    />
                    <p className="text-[10px] sm:text-xs text-center text-muted-foreground">
                      {day.day}
                    </p>
                    <p className="text-[10px] sm:text-xs text-center font-medium">
                      {day.hours.toString().slice(0,3)}h
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Learning Path Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.6 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Lộ trình học tập</CardTitle>
              <CardDescription>Hành trình học tập cá nhân hóa của bạn</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {learningPath.map((lesson, index) => (
                  <div
                    key={lesson.id}
                    className="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-xl border hover:bg-secondary transition-colors"
                  >
                    <div
                      className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center text-sm flex-shrink-0 ${lesson.status === "completed"
                          ? "bg-primary text-white"
                          : lesson.status === "in-progress"
                            ? "bg-accent text-accent-foreground"
                            : "bg-muted text-muted-foreground"
                        }`}
                    >
                      {lesson.status === "completed" ? "✓" : index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs sm:text-sm truncate">{lesson.title}</p>
                      {lesson.status === "completed" && (
                        <p className="text-[10px] sm:text-xs text-muted-foreground">
                          Score: {lesson.score}%
                        </p>
                      )}
                    </div>
                    <Badge
                      variant={
                        lesson.status === "completed"
                          ? "default"
                          : lesson.status === "in-progress"
                            ? "secondary"
                            : "outline"
                      }
                      className={`text-[10px] sm:text-xs flex-shrink-0 ${
                        lesson.status === "completed"
                          ? "bg-primary"
                          : lesson.status === "in-progress"
                            ? "bg-accent text-accent-foreground"
                            : ""
                      }`}
                    >
                      {lesson.status === "completed"
                        ? "Completed"
                        : lesson.status === "in-progress"
                          ? "In Progress"
                          : "Locked"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
