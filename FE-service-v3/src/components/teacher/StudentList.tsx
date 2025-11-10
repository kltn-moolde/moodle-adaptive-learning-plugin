import { motion } from "motion/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Search, Eye, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Progress } from "../ui/progress";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";

const students = [
  {
    id: 1,
    name: "Nguyễn Văn An",
    email: "an.nguyen@student.edu",
    progress: 92,
    activity: "high",
    trend: "up",
    lastActive: "2 hours ago",
    aiInsight: "Đang học rất tốt, nên thử thách với bài nâng cao",
    completedLessons: 18,
    totalLessons: 20,
  },
  {
    id: 2,
    name: "Trần Thị Bình",
    email: "binh.tran@student.edu",
    progress: 88,
    activity: "high",
    trend: "up",
    lastActive: "1 hour ago",
    aiInsight: "Tiến bộ ổn định, có thể tăng tốc độ học",
    completedLessons: 17,
    totalLessons: 20,
  },
  {
    id: 3,
    name: "Lê Văn Cường",
    email: "cuong.le@student.edu",
    progress: 75,
    activity: "medium",
    trend: "stable",
    lastActive: "5 hours ago",
    aiInsight: "Cần ôn lại phần Functions",
    completedLessons: 15,
    totalLessons: 20,
  },
  {
    id: 4,
    name: "Phạm Thị Dung",
    email: "dung.pham@student.edu",
    progress: 65,
    activity: "low",
    trend: "down",
    lastActive: "2 days ago",
    aiInsight: "Nguy cơ bỏ học - cần hỗ trợ ngay",
    completedLessons: 13,
    totalLessons: 20,
  },
  {
    id: 5,
    name: "Hoàng Văn Em",
    email: "em.hoang@student.edu",
    progress: 95,
    activity: "high",
    trend: "up",
    lastActive: "30 minutes ago",
    aiInsight: "Học sinh xuất sắc, nên giao thêm project",
    completedLessons: 19,
    totalLessons: 20,
  },
  {
    id: 6,
    name: "Võ Thị Phương",
    email: "phuong.vo@student.edu",
    progress: 82,
    activity: "medium",
    trend: "up",
    lastActive: "3 hours ago",
    aiInsight: "Tiến bộ tốt trong tuần qua",
    completedLessons: 16,
    totalLessons: 20,
  },
];

export function StudentList() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterActivity, setFilterActivity] = useState("all");
  const [selectedStudent, setSelectedStudent] = useState<typeof students[0] | null>(null);

  const filteredStudents = students.filter((student) => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesActivity = filterActivity === "all" || student.activity === filterActivity;
    return matchesSearch && matchesActivity;
  });

  const getActivityBadge = (activity: string) => {
    switch (activity) {
      case "high":
        return <Badge className="bg-primary">High</Badge>;
      case "medium":
        return <Badge variant="secondary">Medium</Badge>;
      case "low":
        return <Badge variant="destructive">Low</Badge>;
      default:
        return null;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-primary" />;
      case "down":
        return <TrendingDown className="h-4 w-4 text-destructive" />;
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="rounded-2xl">
          <CardHeader>
            <CardTitle>Student Management</CardTitle>
            <CardDescription>
              Monitor and manage individual student progress
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name or email..."
                  className="pl-10 rounded-xl"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select value={filterActivity} onValueChange={setFilterActivity}>
                <SelectTrigger className="w-full md:w-[200px] rounded-xl">
                  <SelectValue placeholder="Filter by activity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Activity Levels</SelectItem>
                  <SelectItem value="high">High Activity</SelectItem>
                  <SelectItem value="medium">Medium Activity</SelectItem>
                  <SelectItem value="low">Low Activity</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Student Table */}
            <div className="border rounded-xl overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Student</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Activity</TableHead>
                    <TableHead>Trend</TableHead>
                    <TableHead>Last Active</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredStudents.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src="" alt={student.name} />
                            <AvatarFallback className="bg-primary text-primary-foreground">
                              {student.name
                                .split(" ")
                                .map((n) => n[0])
                                .join("")
                                .slice(0, 2)
                                .toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-sm">{student.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {student.email}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="w-32">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs">{student.progress}%</span>
                          </div>
                          <Progress value={student.progress} className="h-2" />
                          <p className="text-xs text-muted-foreground mt-1">
                            {student.completedLessons}/{student.totalLessons} lessons
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>{getActivityBadge(student.activity)}</TableCell>
                      <TableCell>{getTrendIcon(student.trend)}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {student.lastActive}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="rounded-xl"
                          onClick={() => setSelectedStudent(student)}
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {filteredStudents.length === 0 && (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  No students found matching your criteria
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Student Detail Modal */}
      <Dialog open={!!selectedStudent} onOpenChange={() => setSelectedStudent(null)}>
        <DialogContent className="max-w-2xl rounded-2xl">
          <DialogHeader>
            <DialogTitle>Student Details</DialogTitle>
            <DialogDescription>
              Detailed overview and AI insights
            </DialogDescription>
          </DialogHeader>
          {selectedStudent && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarImage src="" alt={selectedStudent.name} />
                  <AvatarFallback className="bg-primary text-primary-foreground text-xl">
                    {selectedStudent.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <h3 className="text-lg">{selectedStudent.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedStudent.email}
                  </p>
                </div>
                {getActivityBadge(selectedStudent.activity)}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground">Progress</p>
                    <p className="text-2xl mt-1">{selectedStudent.progress}%</p>
                    <Progress value={selectedStudent.progress} className="mt-2 h-2" />
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground">Completed</p>
                    <p className="text-2xl mt-1">
                      {selectedStudent.completedLessons}/{selectedStudent.totalLessons}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">lessons</p>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950 border-primary/20">
                <CardHeader>
                  <CardTitle className="text-base">AI Insight</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-3">
                    <div className="text-2xl">💡</div>
                    <p className="text-sm">{selectedStudent.aiInsight}</p>
                  </div>
                </CardContent>
              </Card>

              <div className="flex justify-end gap-2">
                <Button variant="outline" className="rounded-xl">
                  Send Message
                </Button>
                <Button className="rounded-xl bg-primary">
                  View Full Dashboard
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
