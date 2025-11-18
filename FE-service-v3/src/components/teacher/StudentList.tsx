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
import { Search, Eye, TrendingUp, TrendingDown, Minus, AlertCircle } from "lucide-react";
import { Progress } from "../ui/progress";
import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import {
  getUserCourses,
  getEnrolledUsers,
  getCourseCompletion,
} from "../../services/moodleApi";

interface Student {
  id: number;
  name: string;
  email: string;
  progress: number;
  activity: string;
  trend: string;
  lastActive: string;
  aiInsight: string;
  completedLessons: number;
  totalLessons: number;
  profileImageUrl?: string;
}

// Mock students as fallback
const mockStudents: Student[] = [
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
];

export function StudentList() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterActivity, setFilterActivity] = useState("all");
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [students, setStudents] = useState<Student[]>(mockStudents);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStudentData();
  }, []);

  async function fetchStudentData() {
    try {
      setLoading(true);
      setError(null);

      // Get teacher's courses
      const courses = await getUserCourses(5); // Use actual user ID
      console.log("Fetched courses:", courses);
      if (courses.length > 0) {
        const course = courses[0];
        
        // Get enrolled users
        const enrolledUsers = await getEnrolledUsers(course.id);
        console.log("Enrolled users:", enrolledUsers);
        const studentsData = enrolledUsers.filter(user =>
          user.roles?.some(role => role.shortname === 'student')
        );
        console.log("Filtered students:", studentsData);

        // Get completion for each student
        const studentPromises = studentsData.map(async (user) => {
          try {
            const completion = await getCourseCompletion(course.id, user.id);
            console.log(`Completion for user ${user.id}:`, completion);
            // Handle case where Moodle API returns 'statuses' or 'completions'
            const completionStatuses = (completion as any)?.statuses || (completion as any)?.completions || [];
            const totalModules = completionStatuses.length;
            const completedModules = completionStatuses.filter((c: any) => c.state === 1).length;
            const progress = totalModules > 0 
              ? Math.round((completedModules / totalModules) * 100)
              : 0;

            // Determine activity level based on last access
            const now = Math.floor(Date.now() / 1000);
            const daysSinceAccess = user.lastaccess 
              ? (now - user.lastaccess) / 86400
              : 999;
            
            let activity = "low";
            let lastActive = "Never";
            
            if (user.lastaccess) {
              if (daysSinceAccess < 1) {
                activity = "high";
                lastActive = `${Math.floor(daysSinceAccess * 24)} hours ago`;
              } else if (daysSinceAccess < 3) {
                activity = "medium";
                lastActive = `${Math.floor(daysSinceAccess)} days ago`;
              } else {
                activity = "low";
                lastActive = `${Math.floor(daysSinceAccess)} days ago`;
              }
            }

            // Determine trend based on progress
            const trend = progress > 80 ? "up" : progress > 50 ? "stable" : "down";

            return {
              id: user.id,
              name: user.fullname,
              email: user.email,
              progress,
              activity,
              trend,
              lastActive,
              aiInsight: progress > 80 
                ? "Đang học rất tốt, nên thử thách với bài nâng cao"
                : progress > 50
                ? "Tiến bộ ổn định, tiếp tục duy trì"
                : "Cần hỗ trợ thêm để cải thiện",
              completedLessons: completedModules,
              totalLessons: totalModules,
              profileImageUrl: user.profileimageurl,
            };
          } catch (err) {
            console.error(`Error fetching data for student ${user.id}:`, err);
            return null;
          }
        });

        const studentsWithData = (await Promise.all(studentPromises)).filter(
          (s) => s !== null
        ) as Student[];

        if (studentsWithData.length > 0) {
          setStudents(studentsWithData);
        }
      }

      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch student data:", err);
      setError("Unable to load students from Moodle. Showing demo data.");
      setLoading(false);
    }
  }

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

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <Card className="rounded-2xl">
          <CardHeader>
            <div className="h-8 w-48 bg-gray-200 dark:bg-gray-800 rounded animate-pulse" />
            <div className="h-4 w-64 bg-gray-200 dark:bg-gray-800 rounded animate-pulse mt-2" />
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-6">
              <div className="flex-1 h-10 bg-gray-200 dark:bg-gray-800 rounded-xl animate-pulse" />
              <div className="w-48 h-10 bg-gray-200 dark:bg-gray-800 rounded-xl animate-pulse" />
            </div>
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-20 bg-gray-200 dark:bg-gray-800 rounded-xl animate-pulse" />
              ))}
            </div>
          </CardContent>
        </Card>
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
                            <AvatarImage src={student.profileImageUrl || ""} alt={student.name} />
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
        <DialogContent className="relative max-w-2xl rounded-2xl max-h-[85vh] overflow-y-auto translate-x-[-25%]">
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
