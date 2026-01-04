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
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { 
  Search, 
  Eye, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Award,
  Target,
  Activity,
  TrendingUp as TrendUp
} from "lucide-react";
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
  syncStudentMastery,
  getStudentMastery,
  type LOMasteryData,
} from "../../services/moodleApi";
import { getLtiParams } from "../../utils/ltiParams";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface Student {
  id: number;
  name: string;
  email: string;
  progress: number;
  activity: string;
  trend: string;
  lastActive: string;
  completedLessons: number;
  totalLessons: number;
  profileImageUrl?: string;
}

// Mock students from temp_students.json (real data from Moodle)
const mockStudents: Student[] = [
  {
    id: 3,
    name: "Văn Kiệt",
    email: "vankiet@gmail.com",
    progress: 30,
    activity: "low",
    trend: "down",
    lastActive: "Lâu rồi",
    completedLessons: 6,
    totalLessons: 20,
    profileImageUrl: "http://139.99.103.223:9090/theme/image.php/boost/core/1766677854/u/f1",
  },
  {
    id: 206,
    name: "Nguyễn Bình An",
    email: "abcz@gmail.com",
    progress: 30,
    activity: "low",
    trend: "down",
    lastActive: "Lâu rồi",
    completedLessons: 6,
    totalLessons: 20,
    profileImageUrl: "http://139.99.103.223:9090/theme/image.php/boost/core/1766677854/u/f1",
  },
];

// Mock LO/PO mastery data based on actual API response
const mockMasteryData: LOMasteryData = {
  course_id: 5,
  user_id: 2,
  last_sync: "2025-12-12T16:43:45.145000",
  lo_mastery: {
    "LO1.1": 0.4,
    "LO1.2": 0.4,
    "LO1.3": 0.4,
    "LO1.4": 0.4,
    "LO1.5": 0.4,
    "LO2.1": 0.4,
    "LO2.2": 0.4,
    "LO2.3": 0.0,
    "LO2.4": 0.0,
    "LO3.1": 0.0,
    "LO3.2": 0.4,
    "LO4.1": 0.4,
    "LO4.2": 0.0,
    "LO5.1": 0.0,
    "LO5.2": 0.0,
  },
  metadata: {
    total_activities_completed: 22,
    total_quizzes_taken: 22,
    avg_quiz_score: 0.09090909090909091,
    activities_by_lo: {
      "LO1.1": [54, 98],
      "LO1.2": [56, 57, 58],
      "LO1.3": [92],
      "LO1.4": [60, 99],
      "LO1.5": [62, 63, 64],
      "LO2.1": [67, 100],
      "LO2.2": [68, 69, 70],
      "LO2.3": [73, 101, 79, 103],
      "LO2.4": [74, 75, 76, 80, 81, 82, 95],
      "LO3.1": [85, 104],
      "LO3.2": [86, 87, 88, 93],
      "LO4.1": [96],
      "LO4.2": [105],
      "LO5.1": [107, 109, 110, 111],
      "LO5.2": [112, 91],
    },
  },
  po_progress: {
    "PO1": 0.3333333333333333,
    "PO2": 0.16,
    "PO3": 0.2,
    "PO4": 0.2,
    "PO5": 0.24000000000000005,
  },
};

export function StudentList() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [students, setStudents] = useState<Student[]>(mockStudents);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [courseId, setCourseId] = useState<number>(2);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const studentsPerPage = 10;
  
  // Mastery detail states
  const [masteryData, setMasteryData] = useState<LOMasteryData | null>(null);
  const [masteryLoading, setMasteryLoading] = useState(false);
  const [masteryError, setMasteryError] = useState<string | null>(null);

  useEffect(() => {
    fetchStudentData();
  }, []);

  async function fetchStudentData() {
    try {
      setLoading(true);
      setError(null);

      // Get LTI parameters from URL
      const ltiParams = getLtiParams();
      console.log("LTI Parameters:", ltiParams);

      // Use LTI user ID if available, fallback to hardcoded
      const userId = ltiParams?.userId || 5;
      const ltiCourseId = ltiParams?.courseId;

      // Get teacher's courses
      const courses = await getUserCourses(userId);
      console.log("Fetched courses:", courses);
      
      // If LTI provides course ID, find that specific course
      let course;
      if (ltiCourseId && courses.length > 0) {
        course = courses.find(c => c.id === ltiCourseId) || courses[0];
      } else if (courses.length > 0) {
        course = courses[0];
      }
      
      if (course) {
        setCourseId(course.id);
        
        // Get enrolled users
        const enrolledUsers = await getEnrolledUsers(course.id);
        console.log("Enrolled users:", enrolledUsers);
        // const studentsData = enrolledUsers.filter(user =>
          // user.roles?.some(role => role.shortname === 'student')
        // );
        // console.log("Filtered students:", studentsData);

        // Get completion for each student
        const studentPromises = enrolledUsers.map(async (user) => {
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
            let lastActive = "Chưa có hoạt động";
            
            if (user.lastaccess) {
              const hoursSince = daysSinceAccess * 24;
              if (hoursSince < 1) {
                activity = "high";
                lastActive = "Vừa xong";
              } else if (hoursSince < 24) {
                activity = "high";
                const hours = Math.floor(hoursSince);
                lastActive = `${hours} giờ trước`;
              } else if (daysSinceAccess < 3) {
                activity = "medium";
                const days = Math.floor(daysSinceAccess);
                lastActive = `${days} ngày trước`;
              } else if (daysSinceAccess < 30) {
                activity = "low";
                const days = Math.floor(daysSinceAccess);
                lastActive = `${days} ngày trước`;
              } else {
                activity = "low";
                lastActive = "Hơn 30 ngày trước";
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
      
      // Fallback: Load from temp_students.json
      try {
        const response = await fetch('/temp_students.json');
        const data = await response.json();
        
        // Filter only students
        const studentsFromJson = data.filter((user: any) => 
          user.roles?.some((role: any) => role.shortname === 'student')
        );
        
        // Transform to Student format
        const now = Math.floor(Date.now() / 1000);
        const transformedStudents = studentsFromJson.map((user: any) => {
          const daysSinceAccess = user.lastaccess 
            ? (now - user.lastaccess) / 86400
            : 999;
          
          let activity = "low";
          let lastActive = "Chưa có hoạt động";
          
          if (user.lastaccess) {
            const hoursSince = daysSinceAccess * 24;
            if (hoursSince < 1) {
              activity = "high";
              lastActive = "Vừa xong";
            } else if (hoursSince < 24) {
              activity = "high";
              const hours = Math.floor(hoursSince);
              lastActive = `${hours} giờ trước`;
            } else if (daysSinceAccess < 7) {
              activity = "medium";
              const days = Math.floor(daysSinceAccess);
              lastActive = `${days} ngày trước`;
            } else if (daysSinceAccess < 30) {
              activity = "low";
              const days = Math.floor(daysSinceAccess);
              lastActive = `${days} ngày trước`;
            } else {
              activity = "low";
              lastActive = "Hơn 30 ngày trước";
            }
          }
          
          const progress = activity === "high" ? 75 : activity === "medium" ? 50 : 30;
          const trend = progress > 70 ? "up" : progress > 40 ? "stable" : "down";
          
          return {
            id: user.id,
            name: user.fullname,
            email: user.email,
            progress,
            activity,
            trend,
            lastActive,
            completedLessons: Math.floor(progress / 5),
            totalLessons: 20,
            profileImageUrl: user.profileimageurl,
          };
        });
        
        if (transformedStudents.length > 0) {
          setStudents(transformedStudents);
          setError("Không thể kết nối Moodle. Hiển thị dữ liệu từ file JSON.");
        }
      } catch (jsonErr) {
        console.error("Failed to load fallback data:", jsonErr);
        setError("Không thể tải danh sách học sinh. Hiển thị dữ liệu mẫu.");
      }
      
      setLoading(false);
    }
  }

  // Filter students based on search term
  const filteredStudents = students.filter((student) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      student.name.toLowerCase().includes(searchLower) ||
      student.email.toLowerCase().includes(searchLower)
    );
  });

  // Pagination logic
  const totalPages = Math.ceil(filteredStudents.length / studentsPerPage);
  const startIndex = (currentPage - 1) * studentsPerPage;
  const endIndex = startIndex + studentsPerPage;
  const currentStudents = filteredStudents.slice(startIndex, endIndex);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  async function handleViewDetails(student: Student) {
    setSelectedStudent(student);
    setMasteryData(null);
    setMasteryLoading(true);
    setMasteryError(null);

    try {
      // Simulate loading delay for mockup
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // console.log("Loading mock mastery data for student:", student.id);
      
      // // Use mock data instead of real API
      // setMasteryData(mockMasteryData);
      // setMasteryLoading(false);
      
      //  Real API calls - uncomment to use real data
      // Step 1: Sync student mastery first
      console.log(`Syncing mastery for student ${student.id} in course ${courseId}...`);
      const syncResult = await syncStudentMastery(courseId, student.id);
      
      if (!syncResult || !syncResult.success) {
        throw new Error("Sync failed");
      }

      console.log("Sync successful:", syncResult);

      // Step 2: Get mastery data
      console.log(`Fetching mastery data for student ${student.id}...`);
      const mastery = await getStudentMastery(student.id, courseId, false);
      
      if (!mastery) {
        throw new Error("No mastery data available");
      }

      console.log("Mastery data:", mastery);
      setMasteryData(mastery);
      setMasteryLoading(false);
    } catch (err) {
      console.error("Error loading mastery data:", err);
      setMasteryError("Không thể tải dữ liệu LO/PO mastery. Vui lòng thử lại.");
      setMasteryLoading(false);
    }
  }

  const getActivityBadge = (activity: string) => {
    switch (activity) {
      case "high":
        return <Badge className="bg-primary">Cao</Badge>;
      case "medium":
        return <Badge variant="secondary">Trung bình</Badge>;
      case "low":
        return <Badge variant="destructive">Thấp</Badge>;
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

  // Prepare radar chart data from mastery
  const prepareRadarData = () => {
    if (!masteryData) return [];
    
    return Object.entries(masteryData.lo_mastery).map(([loId, value]) => ({
      subject: loId,
      value: Math.round(value * 100),
      fullMark: 100,
    }));
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
            <CardTitle>Quản lý học sinh</CardTitle>
            <CardDescription>
              Theo dõi và quản lý tiến độ từng học sinh (Tổng: {filteredStudents.length} sinh viên)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Search */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Tìm kiếm theo tên hoặc email..."
                  className="pl-10 rounded-xl"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Student Table */}
            <div className="border rounded-xl overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Học sinh</TableHead>
                    <TableHead>Hoạt động gần nhất</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {currentStudents.map((student) => (
                    <TableRow key={student.id} className="cursor-pointer hover:bg-muted/50">
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src={student.profileImageUrl} alt={student.name} />
                            <AvatarFallback className="bg-primary/10 text-primary">
                              {student.name.split(" ").slice(-2).map(n => n[0]).join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{student.name}</p>
                            <p className="text-sm text-muted-foreground">{student.email}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {student.lastActive}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="rounded-xl"
                          onClick={() => handleViewDetails(student)}
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          Chi tiết
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex flex-col items-center gap-3 mt-6">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <div className="text-sm">
                    Trang {currentPage} / {totalPages}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-xl"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
                <div className="text-sm text-muted-foreground">
                  Hiển thị {startIndex + 1} - {Math.min(endIndex, filteredStudents.length)} của {filteredStudents.length}
                </div>
              </div>
            )}

            {filteredStudents.length === 0 && (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  Không tìm thấy học sinh nào phù hợp
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Student Detail Modal */}
      <Dialog open={!!selectedStudent} onOpenChange={() => setSelectedStudent(null)}>
        <DialogContent 
          className="max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl"
          style={{ translate: 'none', maxWidth: '80vw' }}
        >
          <DialogHeader>
            <DialogTitle>Chi tiết học sinh</DialogTitle>
            <DialogDescription>
              Thông tin LO/PO mastery và phân tích chi tiết
            </DialogDescription>
          </DialogHeader>
          {selectedStudent && (
            <div className="space-y-6">
              {/* Student Info Header */}
              <div className="flex items-center gap-4 pb-4 border-b">
                <Avatar className="h-16 w-16">
                  <AvatarImage src={selectedStudent.profileImageUrl} alt={selectedStudent.name} />
                  <AvatarFallback className="bg-primary text-primary-foreground text-xl">
                    {selectedStudent.name.split(" ").slice(-2).map(n => n[0]).join("")}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{selectedStudent.name}</h3>
                  <p className="text-sm text-muted-foreground">{selectedStudent.email}</p>
                </div>
                {getActivityBadge(selectedStudent.activity)}
              </div>

              {/* Basic Stats */}
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-primary">{selectedStudent.progress}%</div>
                    <div className="text-sm text-muted-foreground mt-1">Tiến độ</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold">{selectedStudent.completedLessons}/{selectedStudent.totalLessons}</div>
                    <div className="text-sm text-muted-foreground mt-1">Bài học</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-sm text-muted-foreground">Hoạt động</div>
                    <div className="font-semibold mt-1">{selectedStudent.lastActive}</div>
                  </CardContent>
                </Card>
              </div>

              {/* Mastery Data Loading */}
              {masteryLoading && (
                <Card className="bg-muted/50">
                  <CardContent className="p-8 flex flex-col items-center justify-center gap-3">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">Đang tải dữ liệu LO/PO mastery...</p>
                  </CardContent>
                </Card>
              )}

              {/* Mastery Error */}
              {masteryError && (
                <Card className="border-destructive bg-destructive/10">
                  <CardContent className="p-4 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <p className="text-sm text-destructive">{masteryError}</p>
                  </CardContent>
                </Card>
              )}

              {/* Mastery Data Display */}
              {masteryData && !masteryLoading && (
                <>
                  {/* Metadata Summary */}
                  <div className="grid grid-cols-3 gap-4">
                    <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-blue-500 text-white rounded-lg">
                            <Activity className="h-5 w-5" />
                          </div>
                          <div>
                            <div className="text-2xl font-bold">{masteryData.metadata.total_activities_completed}</div>
                            <div className="text-sm text-muted-foreground">Hoạt động hoàn thành</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-purple-500 text-white rounded-lg">
                            <Award className="h-5 w-5" />
                          </div>
                          <div>
                            <div className="text-2xl font-bold">{masteryData.metadata.total_quizzes_taken}</div>
                            <div className="text-sm text-muted-foreground">Bài kiểm tra</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-green-500 text-white rounded-lg">
                            <TrendUp className="h-5 w-5" />
                          </div>
                          <div>
                            <div className="text-2xl font-bold">{Math.round(masteryData.metadata.avg_quiz_score * 100)}%</div>
                            <div className="text-sm text-muted-foreground">Điểm TB Quiz</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* LO Mastery Radar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-primary" />
                        Phân tích LO Mastery
                      </CardTitle>
                      <CardDescription>
                        Mức độ thành thạo các Learning Outcomes
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={400}>
                        <RadarChart data={prepareRadarData()}>
                          <PolarGrid />
                          <PolarAngleAxis 
                            dataKey="subject" 
                            tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
                          />
                          <PolarRadiusAxis angle={90} domain={[0, 100]} />
                          <Radar
                            name="Mastery %"
                            dataKey="value"
                            stroke="hsl(var(--primary))"
                            fill="hsl(var(--primary))"
                            fillOpacity={0.6}
                          />
                          <Legend />
                        </RadarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* PO Progress */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Programme Outcomes (PO) Progress</CardTitle>
                      <CardDescription>
                        Tiến độ đạt được các PO theo LO đã hoàn thành
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {Object.entries(masteryData.po_progress).map(([poId, value]) => (
                        <div key={poId} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{poId}</span>
                            <span className="text-sm text-muted-foreground">{Math.round(value * 100)}%</span>
                          </div>
                          <Progress value={value * 100} className="h-2" />
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  {/* LO Details Table */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Chi tiết từng Learning Outcome</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {Object.entries(masteryData.lo_mastery).map(([loId, value]) => {
                          const activities = masteryData.metadata.activities_by_lo[loId] || [];
                          const percentage = Math.round(value * 100);
                          
                          return (
                            <div key={loId} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                              <div className="flex-1">
                                <div className="flex items-center gap-3">
                                  <span className="font-semibold text-lg">{loId}</span>
                                  <Badge variant={percentage >= 70 ? "default" : percentage >= 40 ? "secondary" : "destructive"}>
                                    {percentage}%
                                  </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground mt-1">
                                  {activities.length} hoạt động liên quan: {activities.join(", ")}
                                </p>
                              </div>
                              <div className="w-32">
                                <Progress value={percentage} className="h-2" />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Last Sync Info */}
                  <div className="text-xs text-muted-foreground text-center">
                    Dữ liệu đồng bộ lần cuối: {new Date(masteryData.last_sync).toLocaleString('vi-VN')}
                  </div>
                </>
              )}


            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
