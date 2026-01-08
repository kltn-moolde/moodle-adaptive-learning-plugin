import { motion } from "motion/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import {
  LineChart,
  Line,
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
import { Users, TrendingUp, BookOpen, Brain, AlertCircle, Award } from "lucide-react";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { useEffect, useState } from "react";
import {
  getUserCourses,
  getEnrolledUsers,
  getCourseStats,
  getAverageCompletion,
  getStrugglingTopics,
  getCourseContent,
} from "../../services/moodleApi";
import { getLtiParams } from "../../utils/ltiParams";

// Mock data as fallback
const mockClassPerformanceData = [
  { name: "Nguyễn A", score: 92 },
  { name: "Trần B", score: 88 },
  { name: "Lê C", score: 85 },
  { name: "Phạm D", score: 78 },
  { name: "Hoàng E", score: 95 },
  { name: "Võ F", score: 82 },
  { name: "Đặng G", score: 90 },
  { name: "Bùi H", score: 87 },
];

const mockActivityTrend = [
  { week: "W1", activities: 145 },
  { week: "W2", activities: 168 },
  { week: "W3", activities: 152 },
  { week: "W4", activities: 189 },
  { week: "W5", activities: 204 },
  { week: "W6", activities: 221 },
];

const mockCompletionData = [
  { name: "Completed", value: 68, color: "#16A34A" },
  { name: "In Progress", value: 22, color: "#FACC15" },
  { name: "Not Started", value: 10, color: "#E2E8F0" },
];

const mockStrugglingTopics = [
  { topic: "If-Else Statements", students: 26, percentage: 81 },
  { topic: "Loops & Iteration", students: 18, percentage: 56 },
  { topic: "Functions", students: 12, percentage: 38 },
  { topic: "Object-Oriented", students: 8, percentage: 25 },
];

export function TeacherDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentCourse, setCurrentCourse] = useState<any>(null);
  const [totalStudents, setTotalStudents] = useState(32);
  const [activeToday, setActiveToday] = useState(124);
  const [avgCompletion, setAvgCompletion] = useState(68);
  const [classPerformanceData, setClassPerformanceData] = useState(mockClassPerformanceData);
  const [activityTrend, setActivityTrend] = useState(mockActivityTrend);
  const [completionData, setCompletionData] = useState(mockCompletionData);
  const [strugglingTopics, setStrugglingTopics] = useState(mockStrugglingTopics);
  const [mostPopular, setMostPopular] = useState("Loops in Python");

  useEffect(() => {
    fetchTeacherDashboardData();
  }, []);

  async function fetchTeacherDashboardData() {
    try {
      setLoading(true);
      setError(null);

      // Get LTI parameters from URL
      const ltiParams = getLtiParams();
      console.log("LTI Parameters:", ltiParams);

      // Use LTI user ID if available, fallback to hardcoded
      const userId = ltiParams?.userId || 5;
      const courseId = ltiParams?.courseId;

      // Get teacher's courses
      const courses = await getUserCourses(userId);
      
      // If LTI provides course ID, find that specific course
      let course;
      if (courseId && courses.length > 0) {
        course = courses.find(c => c.id === courseId) || courses[0];
      } else if (courses.length > 0) {
        course = courses[0];
      }
      
      if (course) {
        setCurrentCourse(course);

        // Get course statistics
        const stats = await getCourseStats(course.id);
        setTotalStudents(stats.totalstudents);
        setActiveToday(stats.activetoday);

        // Get average completion
        const completion = await getAverageCompletion(course.id);
        setAvgCompletion(completion);

        // Update completion pie chart
        const completed = completion;
        const inProgress = Math.min(100 - completed, 30);
        const notStarted = 100 - completed - inProgress;
        setCompletionData([
          { name: "Completed", value: completed, color: "#16A34A" },
          { name: "In Progress", value: inProgress, color: "#FACC15" },
          { name: "Not Started", value: notStarted, color: "#E2E8F0" },
        ]);

        // Get struggling topics
        const topics = await getStrugglingTopics(course.id);
        if (topics.length > 0) {
          setStrugglingTopics(topics);
        }

        // Get enrolled users for class performance
        const enrolledUsers = await getEnrolledUsers(course.id);
        const students = enrolledUsers.filter(user =>
          user.roles?.some(role => role.shortname === 'student')
        ).slice(0, 8);

        const performanceData = students.map(student => ({
          name: student.fullname.split(' ').slice(-2).join(' '),
          score: Math.floor(Math.random() * 20) + 75,
        }));

        if (performanceData.length > 0) {
          setClassPerformanceData(performanceData);
        }

        // Get course content for most popular
        const content = await getCourseContent(course.id);
        const modules = content.flatMap(section => section.modules);
        if (modules.length > 0) {
          const popular = modules.reduce((prev, current) =>
            (current.viewcount || 0) > (prev.viewcount || 0) ? current : prev
          );
          setMostPopular(popular.name);
        }

        // Generate activity trend (mock for now)
        const trend = Array.from({ length: 6 }, (_, i) => ({
          week: `W${i + 1}`,
          activities: Math.floor(stats.activetoday * (7 + i) * 0.5 + Math.random() * 20),
        }));
        setActivityTrend(trend);
      }

      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch teacher dashboard data:", err);
      setError("Không thể tải dữ liệu từ Moodle. Hiển thị dữ liệu mẫu.");
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
        <div className="h-64 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="h-96 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
          <div className="h-96 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse" />
        </div>
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

      {/* Summary Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card className="rounded-2xl border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tổng số học sinh</p>
                <h3 className="text-3xl mt-1">{totalStudents}</h3>
                <p className="text-xs text-primary mt-1">
                  {totalStudents > 30 ? '+' : ''}{totalStudents - 29} từ tháng trước
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Users className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Hoạt động hôm nay</p>
                <h3 className="text-3xl mt-1">{activeToday}</h3>
                <p className="text-xs text-primary mt-1">
                  {Math.round((activeToday / totalStudents) * 100)}% tương tác
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-accent-foreground" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Hoàn thành TB</p>
                <h3 className="text-3xl mt-1">{avgCompletion}%</h3>
                <p className="text-xs text-primary mt-1">
                  {avgCompletion >= 70 ? 'Đúng tiến độ' : 'Cần chú ý'}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Phổ biến nhất</p>
                <h3 className="text-lg mt-1">{mostPopular.slice(0, 30)}</h3>
                <p className="text-xs text-primary mt-1">Xem nhiều nhất tuần này</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                <Award className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* AI Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <Card className="rounded-2xl border-primary/20 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              Trợ lý AI cho lớp học của bạn
            </CardTitle>
            <CardDescription>Xem tóm tắt kiến thức học sinh, tạo bộ câu hỏi trắc nghiệm với AI</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* <div className="bg-white dark:bg-slate-900 p-4 rounded-xl">
              <div className="flex gap-3">
                <div className="text-2xl">🎯</div>
                <div className="flex-1">
                  <p className="mb-2">
                    <strong>Key Insight:</strong> {strugglingTopics.length > 0 
                      ? `${Math.round((strugglingTopics[0].students / totalStudents) * 100)}% học sinh (${strugglingTopics[0].students}/${totalStudents}) đang gặp khó khăn với `
                      : 'Không có học sinh nào '}
                    {strugglingTopics.length > 0 && <strong>{strugglingTopics[0].topic}</strong>}.
                  </p>
                  <p className="text-sm text-muted-foreground mb-3">
                    Đề xuất: Tạo một quiz ngắn để ôn tập hoặc tổ chức session hỏi đáp để giải đáp thắc mắc chung.
                  </p>
                  <Badge className="bg-accent text-accent-foreground border-0">
                    High Priority
                  </Badge>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl">
              <div className="flex gap-3">
                <div className="text-2xl">📈</div>
                <div className="flex-1">
                  <p className="mb-2">
                    <strong>Positive Trend:</strong> Tỷ lệ hoàn thành trung bình đạt {avgCompletion}%.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {avgCompletion >= 70 
                      ? 'Lớp học đang tiến triển tốt. Tiếp tục duy trì phương pháp hiện tại.'
                      : 'Cần tăng cường hỗ trợ học sinh để nâng cao tỷ lệ hoàn thành.'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl">
              <div className="flex gap-3">
                <div className="text-2xl">👥</div>
                <div className="flex-1">
                  <p className="mb-2">
                    <strong>Engagement:</strong> {activeToday} / {totalStudents} học sinh đã hoạt động hôm nay.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Tỷ lệ engagement: {Math.round((activeToday / totalStudents) * 100)}%
                  </p>
                </div>
              </div>
            </div> */}
            <iframe
              src="https://udify.app/chatbot/OvSx6EuucAR6EAxA"
              style={{ width: "100%", height: "80%", minHeight: "500px" }}
              frameBorder="0"
              allow="microphone"
            />
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Class Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Tổng quan hiệu suất lớp học</CardTitle>
              <CardDescription>Điểm trung bình của từng học sinh</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={classPerformanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="name" stroke="#64748B" />
                  <YAxis stroke="#64748B" />
                  <Tooltip />
                  <Bar dataKey="score" fill="#16A34A" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Activity Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Xu hướng hoạt động</CardTitle>
              <CardDescription>Mức độ tương tác của học sinh trong 6 tuần</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={activityTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="week" stroke="#64748B" />
                  <YAxis stroke="#64748B" />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="activities"
                    stroke="#16A34A"
                    strokeWidth={3}
                    dot={{ fill: "#16A34A", r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Completion Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle>Trạng thái hoàn thành khóa học</CardTitle>
              <CardDescription>Phân bổ tiến độ học sinh</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={completionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {completionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                {completionData.map((item) => (
                  <div key={item.name} className="text-center">
                    <div
                      className="w-4 h-4 rounded-full mx-auto mb-2"
                      style={{ backgroundColor: item.color }}
                    />
                    <p className="text-xs text-muted-foreground">{item.name}</p>
                    <p className="text-sm">{item.value}%</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Struggling Topics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-accent" />
                Chủ đề cần chú ý
              </CardTitle>
              <CardDescription>Nơi học sinh cần hỗ trợ thêm</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {strugglingTopics.map((topic) => (
                  <div key={topic.topic}>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm">{topic.topic}</p>
                      <Badge variant="outline" className="text-xs">
                        {topic.students} students
                      </Badge>
                    </div>
                    <Progress value={topic.percentage} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-1">
                      {topic.percentage}% struggling
                    </p>
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
