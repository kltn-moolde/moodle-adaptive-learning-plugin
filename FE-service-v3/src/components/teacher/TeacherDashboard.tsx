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

const classPerformanceData = [
  { name: "Nguyễn A", score: 92 },
  { name: "Trần B", score: 88 },
  { name: "Lê C", score: 85 },
  { name: "Phạm D", score: 78 },
  { name: "Hoàng E", score: 95 },
  { name: "Võ F", score: 82 },
  { name: "Đặng G", score: 90 },
  { name: "Bùi H", score: 87 },
];

const activityTrend = [
  { week: "W1", activities: 145 },
  { week: "W2", activities: 168 },
  { week: "W3", activities: 152 },
  { week: "W4", activities: 189 },
  { week: "W5", activities: 204 },
  { week: "W6", activities: 221 },
];

const completionData = [
  { name: "Completed", value: 68, color: "#16A34A" },
  { name: "In Progress", value: 22, color: "#FACC15" },
  { name: "Not Started", value: 10, color: "#E2E8F0" },
];

const strugglingTopics = [
  { topic: "If-Else Statements", students: 26, percentage: 81 },
  { topic: "Loops & Iteration", students: 18, percentage: 56 },
  { topic: "Functions", students: 12, percentage: 38 },
  { topic: "Object-Oriented", students: 8, percentage: 25 },
];

export function TeacherDashboard() {
  return (
    <div className="p-6 space-y-6">
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
                <p className="text-sm text-muted-foreground">Total Students</p>
                <h3 className="text-3xl mt-1">32</h3>
                <p className="text-xs text-primary mt-1">+3 from last month</p>
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
                <p className="text-sm text-muted-foreground">Today's Activity</p>
                <h3 className="text-3xl mt-1">124</h3>
                <p className="text-xs text-primary mt-1">+12% vs yesterday</p>
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
                <p className="text-sm text-muted-foreground">Avg. Completion</p>
                <h3 className="text-3xl mt-1">68%</h3>
                <p className="text-xs text-primary mt-1">+5% this week</p>
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
                <p className="text-sm text-muted-foreground">Most Popular</p>
                <h3 className="text-lg mt-1">Loops in Python</h3>
                <p className="text-xs text-primary mt-1">156 views this week</p>
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
        <Card className="rounded-2xl border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              AI Insights - Class Summary
            </CardTitle>
            <CardDescription>Personalized recommendations for your class</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="dark:bg-slate-900 p-4 rounded-xl" style={{
              backgroundColor:
                window.matchMedia("(prefers-color-scheme: dark)").matches
                  ? "#0f172a" // slate-900
                  : "#f0fdf4", // green-50
            }}>
              <div className="flex gap-3">
                <div className="text-2xl">🎯</div>
                <div className="flex-1">
                  <p className="mb-2">
                    <strong>Key Insight:</strong> 80% học sinh (26/32) đang gặp khó khăn với <strong>If-Else Statements</strong>.
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

            <div className="dark:bg-slate-900 p-4 rounded-xl" style={{
              backgroundColor:
                window.matchMedia("(prefers-color-scheme: dark)").matches
                  ? "#0f172a" // slate-900
                  : "#f0fdf4", // green-50
            }}>
              <div className="flex gap-3">
                <div className="text-2xl">📈</div>
                <div className="flex-1">
                  <p className="mb-2">
                    <strong>Positive Trend:</strong> Tỷ lệ hoàn thành bài tập đã tăng 15% so với tuần trước.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Các bài tập thực hành đang có hiệu quả tốt. Nên tiếp tục duy trì format này.
                  </p>
                </div>
              </div>
            </div>

            <div className="dark:bg-slate-900 p-4 rounded-xl" style={{
              backgroundColor:
                window.matchMedia("(prefers-color-scheme: dark)").matches
                  ? "#0f172a" // slate-900
                  : "#f0fdf4", // green-50
            }}>
              <div className="flex gap-3">
                <div className="text-2xl">👥</div>
                <div className="flex-1">
                  <p className="mb-2">
                    <strong>At-Risk Students:</strong> 3 học sinh có nguy cơ bỏ học do không hoạt động trong 7 ngày.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Đề xuất liên hệ: Nguyễn Văn A, Trần Thị B, Lê Văn C
                  </p>
                </div>
              </div>
            </div>
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
              <CardTitle>Class Performance Overview</CardTitle>
              <CardDescription>Average scores by student</CardDescription>
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
              <CardTitle>Activity Trend</CardTitle>
              <CardDescription>Student engagement over 6 weeks</CardDescription>
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
              <CardTitle>Course Completion Status</CardTitle>
              <CardDescription>Distribution of student progress</CardDescription>
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
                Topics Requiring Attention
              </CardTitle>
              <CardDescription>Where students need more help</CardDescription>
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
