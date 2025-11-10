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
import { Eye, FileText, CheckSquare, Video, Award } from "lucide-react";
import { Badge } from "../ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

const moduleViews = [
  { name: "Introduction", views: 245, icon: Video },
  { name: "Variables", views: 198, icon: FileText },
  { name: "Control Flow", views: 167, icon: FileText },
  { name: "Functions", views: 142, icon: FileText },
  { name: "Loops", views: 189, icon: Video },
  { name: "OOP Basics", views: 98, icon: FileText },
  { name: "Final Quiz", views: 76, icon: CheckSquare },
];

const resourceTypes = [
  { name: "Video Lectures", value: 45, color: "#16A34A" },
  { name: "Reading Materials", value: 30, color: "#22C55E" },
  { name: "Quizzes", value: 15, color: "#FACC15" },
  { name: "Assignments", value: 10, color: "#4ADE80" },
];

const topPerformers = [
  { rank: 1, name: "Hoàng Văn Em", score: 95, badge: "🥇" },
  { rank: 2, name: "Nguyễn Văn An", score: 92, badge: "🥈" },
  { rank: 3, name: "Trần Thị Bình", score: 88, badge: "🥉" },
  { rank: 4, name: "Võ Thị Phương", score: 82, badge: "" },
  { rank: 5, name: "Lê Văn Cường", score: 75, badge: "" },
];

const weeklyEngagement = [
  { day: "Mon", lectures: 85, quizzes: 45, assignments: 20 },
  { day: "Tue", lectures: 92, quizzes: 52, assignments: 28 },
  { day: "Wed", lectures: 78, quizzes: 38, assignments: 15 },
  { day: "Thu", lectures: 105, quizzes: 68, assignments: 35 },
  { day: "Fri", lectures: 88, quizzes: 55, assignments: 22 },
  { day: "Sat", lectures: 42, quizzes: 28, assignments: 12 },
  { day: "Sun", lectures: 25, quizzes: 15, assignments: 5 },
];

export function CourseAnalytics() {
  return (
    <div className="p-6 space-y-6">
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
                <p className="text-sm text-muted-foreground">Total Views</p>
                <h3 className="text-3xl mt-1">1,115</h3>
                <p className="text-xs text-primary mt-1">All modules</p>
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
                <p className="text-sm text-muted-foreground">Avg. View Time</p>
                <h3 className="text-3xl mt-1">42m</h3>
                <p className="text-xs text-primary mt-1">Per student</p>
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
                <p className="text-sm text-muted-foreground">Assignments</p>
                <h3 className="text-3xl mt-1">28</h3>
                <p className="text-xs text-primary mt-1">Submitted today</p>
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
                <p className="text-sm text-muted-foreground">Quiz Pass Rate</p>
                <h3 className="text-3xl mt-1">87%</h3>
                <p className="text-xs text-primary mt-1">Above threshold</p>
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
              <CardTitle>Module Popularity</CardTitle>
              <CardDescription>Views per course component</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={moduleViews} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis type="number" stroke="#64748B" />
                  <YAxis dataKey="name" type="category" stroke="#64748B" width={100} />
                  <Tooltip />
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
              <CardTitle>Resource Distribution</CardTitle>
              <CardDescription>Types of learning materials</CardDescription>
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
            <CardTitle>Weekly Engagement Pattern</CardTitle>
            <CardDescription>Activity breakdown by resource type</CardDescription>
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
                Top Performers
              </CardTitle>
              <CardDescription>Students with highest scores</CardDescription>
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
              <CardTitle>AI Course Summary</CardTitle>
              <CardDescription>Key insights and recommendations</CardDescription>
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
