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
import { BookOpen, Brain, TrendingUp, Award, Clock } from "lucide-react";

const progressData = [
  { week: "Week 1", score: 65 },
  { week: "Week 2", score: 72 },
  { week: "Week 3", score: 78 },
  { week: "Week 4", score: 85 },
  { week: "Week 5", score: 88 },
  { week: "Week 6", score: 92 },
];

const skillsData = [
  { skill: "Reading", value: 85 },
  { skill: "Practice", value: 92 },
  { skill: "Tests", value: 78 },
  { skill: "Projects", value: 88 },
  { skill: "Quizzes", value: 95 },
];

const activityHeatmap = [
  { day: "Mon", hours: 2.5 },
  { day: "Tue", hours: 3.2 },
  { day: "Wed", hours: 1.8 },
  { day: "Thu", hours: 4.1 },
  { day: "Fri", hours: 2.9 },
  { day: "Sat", hours: 1.2 },
  { day: "Sun", hours: 0.5 },
];

const learningPath = [
  { id: 1, title: "Introduction to Python", status: "completed", score: 95 },
  { id: 2, title: "Data Types & Variables", status: "completed", score: 88 },
  { id: 3, title: "Control Flow", status: "in-progress", score: 0 },
  { id: 4, title: "Functions", status: "locked", score: 0 },
  { id: 5, title: "Object-Oriented Programming", status: "locked", score: 0 },
];

export function StudentDashboard() {
  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
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
                <AvatarImage src="" alt="Student" />
                <AvatarFallback className="bg-green-200 text-green-900 text-2xl font-semibold">
                  HS
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 text-slate-100 w-full sm:w-auto">
                <h2 className="text-xl sm:text-2xl font-semibold mb-1 text-green-700 text-center sm:text-left">Hoàng Sinh</h2>
                <p className="text-slate-700 mb-4 text-center sm:text-left text-sm sm:text-base">Lớp 12A1 — Python Programming</p>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm text-slate-700">
                    <span>Overall Progress</span>
                    <span className="text-green-700 font-medium">75%</span>
                  </div>
                  <Progress value={75} className="h-2 bg-gray-200! [&>div]:bg-green-400" />
                </div>
              </div>

              <div className="hidden lg:flex flex-col gap-3">
                <Badge className="bg-green-100 text-green-800 border-0 px-4 py-2 font-medium shadow-sm">
                  <Award className="h-4 w-4 mr-2 text-green-700" />
                  12 Achievements
                </Badge>
                <Badge className="bg-blue-100 text-blue-800 border-0 px-4 py-2 font-medium shadow-sm">
                  <TrendingUp className="h-4 w-4 mr-2 text-blue-700" />
                  Rank #3 in Class
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
                AI Feedback
              </CardTitle>
              <CardDescription>Personalized insights for you</CardDescription>
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
                Next Lesson
              </CardTitle>
              <CardDescription>AI recommended for you</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-secondary p-3 sm:p-4 rounded-xl mb-4">
                <h3 className="mb-2 text-sm sm:text-base">Control Flow: If-Else Statements</h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Learn how to make decisions in your code using conditional statements. Perfect for your current level!
                </p>
                <div className="flex flex-wrap items-center gap-2 text-xs mb-4">
                  <Badge variant="outline" className="border-primary text-primary text-xs">
                    Difficulty: Medium
                  </Badge>
                  <Badge variant="outline" className="text-xs">⏱️ 45 min</Badge>
                  <Badge variant="outline" className="text-xs">📊 85% success rate</Badge>
                </div>
                <Button className="w-full rounded-xl bg-primary hover:bg-primary/90 text-sm sm:text-base">
                  Start Learning Now →
                </Button>
              </div>

              <div className="space-y-2">
                <p className="text-xs sm:text-sm text-muted-foreground">Learning objectives:</p>
                <ul className="text-xs sm:text-sm space-y-1 ml-4">
                  <li>✓ Understand conditional logic</li>
                  <li>✓ Use if, elif, and else statements</li>
                  <li>✓ Apply conditions in real scenarios</li>
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
              <CardTitle>Learning Progress</CardTitle>
              <CardDescription>Your score over the past 6 weeks</CardDescription>
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
              <CardTitle>Skills Analysis</CardTitle>
              <CardDescription>Performance across different areas</CardDescription>
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
              <CardTitle>Weekly Activity</CardTitle>
              <CardDescription>Study hours per day</CardDescription>
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
                      {day.hours}h
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
              <CardTitle>Learning Path</CardTitle>
              <CardDescription>Your personalized journey</CardDescription>
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
