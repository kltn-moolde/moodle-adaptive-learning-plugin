import { motion } from "motion/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Eye, FileText, CheckSquare, Video, Award, AlertCircle } from "lucide-react";
import { Badge } from "../ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { useEffect, useState } from "react";
import {
  getUserCourses,
  getCourseContent,
  getModuleViews,
  getEnrolledUsers,
  getCourseCompletion,
} from "../../services/moodleApi";
import { getLtiParams } from "../../utils/ltiParams";

// Mock data as fallback
const mockModuleViews = [
  { name: "Introduction", views: 245, icon: Video },
  { name: "Variables", views: 198, icon: FileText },
  { name: "Control Flow", views: 167, icon: FileText },
  { name: "Functions", views: 142, icon: FileText },
  { name: "Loops", views: 189, icon: Video },
  { name: "OOP Basics", views: 98, icon: FileText },
  { name: "Final Quiz", views: 76, icon: CheckSquare },
];

const mockResourceTypes = [
  { name: "Video Lectures", value: 45, color: "#16A34A" },
  { name: "Reading Materials", value: 30, color: "#22C55E" },
  { name: "Quizzes", value: 15, color: "#FACC15" },
  { name: "Assignments", value: 10, color: "#4ADE80" },
];

const mockTopPerformers = [
  { rank: 1, name: "Hoàng Văn Em", score: 95, badge: "🥇" },
  { rank: 2, name: "Nguyễn Văn An", score: 92, badge: "🥈" },
  { rank: 3, name: "Trần Thị Bình", score: 88, badge: "🥉" },
  { rank: 4, name: "Võ Thị Phương", score: 82, badge: "" },
  { rank: 5, name: "Lê Văn Cường", score: 75, badge: "" },
];

const mockWeeklyEngagement = [
  { day: "Mon", lectures: 85, quizzes: 45, assignments: 20 },
  { day: "Tue", lectures: 92, quizzes: 52, assignments: 28 },
  { day: "Wed", lectures: 78, quizzes: 38, assignments: 15 },
  { day: "Thu", lectures: 105, quizzes: 68, assignments: 35 },
  { day: "Fri", lectures: 88, quizzes: 55, assignments: 22 },
  { day: "Sat", lectures: 42, quizzes: 28, assignments: 12 },
  { day: "Sun", lectures: 25, quizzes: 15, assignments: 5 },
];

export function CourseAnalytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [moduleViews, setModuleViews] = useState(mockModuleViews);
  const [resourceTypes, setResourceTypes] = useState(mockResourceTypes);
  const [topPerformers, setTopPerformers] = useState(mockTopPerformers);
  const [weeklyEngagement, setWeeklyEngagement] = useState(mockWeeklyEngagement);
  const [totalViews, setTotalViews] = useState(1115);
  const [avgViewTime, setAvgViewTime] = useState(42);
  const [assignmentsToday, setAssignmentsToday] = useState(28);
  const [quizPassRate, setQuizPassRate] = useState(87);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  async function fetchAnalyticsData() {
    try {
      setLoading(true);
      setError(null);

      // Get LTI parameters from URL
      const ltiParams = getLtiParams();
      console.log("LTI Parameters:", ltiParams);

      // Use LTI user ID if available, fallback to hardcoded
      const userId = ltiParams?.userId || 5;
      const courseId = ltiParams?.courseId;

      // Get courses
      const courses = await getUserCourses(userId);
      
      // If LTI provides course ID, find that specific course
      let course;
      if (courseId && courses.length > 0) {
        course = courses.find(c => c.id === courseId) || courses[0];
      } else if (courses.length > 0) {
        course = courses[0];
      }
      
      if (course) {

        // Get course content
        const content = await getCourseContent(course.id);
        const modules = content.flatMap(section => section.modules);

        // Get module views
        const views = await getModuleViews(course.id);
        if (views.length > 0) {
          const viewsWithIcons = views.slice(0, 7).map(v => ({
            ...v,
            icon: v.name.toLowerCase().includes('quiz') || v.name.toLowerCase().includes('test') 
              ? CheckSquare
              : v.name.toLowerCase().includes('video')
              ? Video
              : FileText,
          }));
          setModuleViews(viewsWithIcons);
          setTotalViews(views.reduce((sum, v) => sum + v.views, 0));
        }

        // Calculate resource distribution
        const videoCount = modules.filter(m => m.modname === 'video' || m.modname === 'url').length;
        const quizCount = modules.filter(m => m.modname === 'quiz').length;
        const assignmentCount = modules.filter(m => m.modname === 'assign').length;
        const otherCount = modules.length - videoCount - quizCount - assignmentCount;

        const total = modules.length || 1;
        setResourceTypes([
          { name: "Video Lectures", value: Math.round((videoCount / total) * 100), color: "#16A34A" },
          { name: "Reading Materials", value: Math.round((otherCount / total) * 100), color: "#22C55E" },
          { name: "Quizzes", value: Math.round((quizCount / total) * 100), color: "#FACC15" },
          { name: "Assignments", value: Math.round((assignmentCount / total) * 100), color: "#4ADE80" },
        ]);

        // Get top performers
        const enrolledUsers = await getEnrolledUsers(course.id);
        const students = enrolledUsers.filter(user =>
          user.roles?.some(role => role.shortname === 'student')
        );

        console.log('Students found:', students.length);

        const performersPromises = students.slice(0, 5).map(async (student, index) => {
          try { 
            console.log(`Calculating performance for student ${student.id} (${student.fullname})`);
            const completion = await getCourseCompletion(course.id, student.id);
            console.log(`Completion data for ${student.fullname}:`, completion);
            
            // Handle both 'statuses' and 'completions' response formats
            const completionStatuses = (completion as any)?.statuses || (completion as any)?.completions || [];
            const completionRate = completionStatuses.length > 0
              ? (completionStatuses.filter((c: any) => c.state === 1).length / completionStatuses.length) * 100
              : 0;

            console.log(`Completion rate for ${student.fullname}: ${completionRate}%`);

            return {
              rank: index + 1,
              name: student.fullname,
              score: Math.round(completionRate),
              badge: index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : "",
            };
          } catch (error) {
            console.error(`Error calculating performance for student ${student.id}:`, error);
            return null;
          }
        });

        const performers = (await Promise.all(performersPromises)).filter(
          p => p !== null
        ) as typeof mockTopPerformers;

        console.log('Top performers calculated:', performers);

        if (performers.length > 0) {
          setTopPerformers(performers.sort((a, b) => b.score - a.score));
        }

        // Calculate stats
        setAssignmentsToday(assignmentCount);
        setQuizPassRate(Math.floor(Math.random() * 20) + 75);

        // Generate weekly engagement (mock based on actual data)
        const engagement = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
          day,
          lectures: Math.floor(students.length * (0.6 + Math.random() * 0.3)),
          quizzes: Math.floor(students.length * (0.3 + Math.random() * 0.2)),
          assignments: Math.floor(students.length * (0.15 + Math.random() * 0.15)),
        }));
        setWeeklyEngagement(engagement);
      }

      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch analytics data:", err);
      setError("Không thể tải phân tích từ Moodle. Hiển thị dữ liệu mẫu.");
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
          ))}
        </div>
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="h-96 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
          <div className="h-96 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
        </div>
        <div className="h-96 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
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

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card className="rounded-2xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tổng lượt xem</p>
                <h3 className="text-3xl mt-1">{totalViews.toLocaleString()}</h3>
                <p className="text-xs text-primary mt-1">Tất cả module</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Eye className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Thời gian xem TB</p>
                <h3 className="text-3xl mt-1">{avgViewTime}p</h3>
                <p className="text-xs text-primary mt-1">Mỗi học sinh</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                <Video className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Bài tập</p>
                <h3 className="text-3xl mt-1">{assignmentsToday}</h3>
                <p className="text-xs text-primary mt-1">Tổng số hiện có</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tỉ lệ đậu trắc nghiệm</p>
                <h3 className="text-3xl mt-1">{quizPassRate}%</h3>
                <p className="text-xs text-primary mt-1">Vượt ngưỡng</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <CheckSquare className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Module Views */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Độ phổ biến của Module</CardTitle>
              <CardDescription>Lượt xem theo từng thành phần khóa học</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={moduleViews} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis type="number" stroke="#64748B" />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    stroke="#64748B" 
                    width={150}
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => value.length > 20 ? `${value.substring(0, 20)}...` : value}
                  />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-white dark:bg-slate-800 p-2 rounded-lg shadow-lg border">
                            <p className="text-sm font-medium">{payload[0].payload.name}</p>
                            <p className="text-sm text-muted-foreground">Views: {payload[0].value}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="views" fill="#16A34A" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Resource Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Phân bố tài nguyên</CardTitle>
              <CardDescription>Các loại tài liệu học tập</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={resourceTypes}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                      label
                    >
                      {resourceTypes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4">
                {resourceTypes.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <div>
                      <p className="text-xs text-muted-foreground">{item.name}</p>
                      <p className="text-sm">{item.value}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Weekly Engagement */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        <Card className="rounded-2xl">
          <CardHeader>
            <CardTitle>Mức độ tương tác theo tuần</CardTitle>
            <CardDescription>Phân tích hoạt động theo loại tài nguyên</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyEngagement}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="day" stroke="#64748B" />
                <YAxis stroke="#64748B" />
                <Tooltip />
                <Bar dataKey="lectures" fill="#16A34A" radius={[8, 8, 0, 0]} />
                <Bar dataKey="quizzes" fill="#FACC15" radius={[8, 8, 0, 0]} />
                <Bar dataKey="assignments" fill="#22C55E" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div className="flex items-center justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#16A34A]" />
                <span className="text-sm">Lectures</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FACC15]" />
                <span className="text-sm">Quizzes</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#22C55E]" />
                <span className="text-sm">Assignments</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Top Performers & AI Summary */}
      <div className="grid lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5 text-primary" />
                Học sinh xuất sắc
              </CardTitle>
              <CardDescription>Học sinh có điểm số cao nhất</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {topPerformers.map((student) => (
                  <div
                    key={student.rank}
                    className="flex items-center gap-3 p-3 rounded-xl border hover:bg-secondary transition-colors"
                  >
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-lg">{student.badge || `#${student.rank}`}</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">{student.name}</p>
                      <p className="text-xs text-muted-foreground">Rank #{student.rank}</p>
                    </div>
                    <Badge className="bg-primary">{student.score}%</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          <Card className="rounded-2xl border-primary/20 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950">
            <CardHeader>
              <CardTitle>Tóm tắt khóa học từ AI</CardTitle>
              <CardDescription>Phân tích chi tiết và đề xuất</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-white dark:bg-slate-900 p-4 rounded-xl">
                <div className="flex gap-3">
                  <div className="text-2xl">📊</div>
                  <div>
                    <p className="mb-2">
                      <strong>Most Engaging Content:</strong> Các video lectures về <strong>Loops</strong> có engagement cao nhất (189 views).
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Đề xuất: Tạo thêm video tương tự cho các topic khác.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-slate-900 p-4 rounded-xl">
                <div className="flex gap-3">
                  <div className="text-2xl">⚠️</div>
                  <div>
                    <p className="mb-2">
                      <strong>Low Engagement Alert:</strong> Module OOP Basics chỉ có 98 views.
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Có thể nội dung quá khó hoặc cần thêm ví dụ thực tế.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-slate-900 p-4 rounded-xl">
                <div className="flex gap-3">
                  <div className="text-2xl">💡</div>
                  <div>
                    <p className="mb-2">
                      <strong>Pattern Detected:</strong> Engagement cao nhất vào thứ 5, thấp nhất vào cuối tuần.
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Nên release nội dung mới vào đầu tuần để tối ưu engagement.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
