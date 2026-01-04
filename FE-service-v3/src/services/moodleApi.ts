import type {
  MoodleUser,
  MoodleCourse,
  MoodleEnrolledUser,
  MoodleCompletion,
  MoodleCourseModule,
  MoodleUserGrade,
  MoodleLogEntry,
  MoodleCourseContent,
} from "../types/moodle";
import type { ClusteringOverview, ClusteringResults } from "../types/clustering";

const MOODLE_URL = import.meta.env.VITE_MOODLE_URL || "";
const MOODLE_TOKEN = import.meta.env.VITE_MOODLE_TOKEN || "";
const CLUSTERING_API_URL = import.meta.env.VITE_CLUSTERING_API_URL || "http://139.99.103.223:8089";

interface MoodleApiParams {
  [key: string]: string | number | boolean | undefined;
}

/**
 * Generic function to call Moodle Web Services
 */
async function callMoodleApi<T>(
  wsfunction: string,
  params: MoodleApiParams = {}
): Promise<T> {
  const url = new URL(`${MOODLE_URL}/webservice/rest/server.php`);
  url.searchParams.append("wstoken", MOODLE_TOKEN);
  url.searchParams.append("wsfunction", wsfunction);
  url.searchParams.append("moodlewsrestformat", "json");

  // Add additional parameters
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value));
    }
  });

  try {
    const response = await fetch(url.toString());
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Check for Moodle error
    if (data.exception || data.errorcode) {
      throw new Error(data.message || "Moodle API Error");
    }

    return data as T;
  } catch (error) {
    console.error(`Error calling Moodle API (${wsfunction}):`, error);
    throw error;
  }
}

/**
 * Get site info and current user
 */
export async function getSiteInfo(): Promise<{
  sitename: string;
  username: string;
  userid: number;
  userfullname: string;
  userpictureurl: string;
}> {
  return callMoodleApi("core_webservice_get_site_info");
}

/**
 * Get user by ID
 */
export async function getUserById(userId: number): Promise<MoodleUser[]> {
  return callMoodleApi<MoodleUser[]>("core_user_get_users_by_field", {
    field: "id",
    "values[0]": userId,
  });
}

/**
 * Get courses where user is enrolled
 */
export async function getUserCourses(userId: number): Promise<MoodleCourse[]> {
  return callMoodleApi<MoodleCourse[]>("core_enrol_get_users_courses", {
    userid: userId,
  });
}

/**
 * Get enrolled users in a course
 */
export async function getEnrolledUsers(
  courseId: number
): Promise<MoodleEnrolledUser[]> {
  return callMoodleApi<MoodleEnrolledUser[]>(
    "core_enrol_get_enrolled_users",
    {
      courseid: courseId,
    }
  );
}

/**
 * Get course content (modules, sections)
 */
export async function getCourseContent(
  courseId: number
): Promise<MoodleCourseContent[]> {
  return callMoodleApi<MoodleCourseContent[]>(
    "core_course_get_contents",
    {
      courseid: courseId,
    }
  );
}

/**
 * Get completion status for a course
 */
export async function getCourseCompletion(
  courseId: number,
  userId: number
): Promise<MoodleCompletion> {
  return callMoodleApi<MoodleCompletion>(
    "core_completion_get_activities_completion_status",
    {
      courseid: courseId,
      userid: userId,
    }
  );
}

/**
 * Get grades for a user in a course
 */
export async function getUserGrades(
  courseId: number,
  userId: number
): Promise<MoodleUserGrade[]> {
  return callMoodleApi<MoodleUserGrade[]>(
    "gradereport_user_get_grade_items",
    {
      courseid: courseId,
      userid: userId,
    }
  );
}

/**
 * Get course grades for all users (teacher view)
 */
export async function getCourseGrades(courseId: number): Promise<{
  usergrades: MoodleUserGrade[];
}> {
  return callMoodleApi("gradereport_user_get_grade_items", {
    courseid: courseId,
  });
}

/**
 * Get recent activity logs
 */
export async function getRecentLogs(
  courseId: number,
  limitFrom: number = 0,
  limitNum: number = 100
): Promise<{ events: MoodleLogEntry[] }> {
  return callMoodleApi("core_course_get_recent_courses", {
    courseid: courseId,
    limitfrom: limitFrom,
    limitnum: limitNum,
  });
}

/**
 * Get course statistics
 */
export async function getCourseStats(courseId: number): Promise<{
  totalstudents: number;
  activetoday: number;
  avgcompletion: number;
}> {
  try {
    const enrolledUsers = await getEnrolledUsers(courseId);
    
    // Filter students (role shortname 'student')
    const students = enrolledUsers.filter(user => 
      user.roles?.some(role => role.shortname === 'student')
    );

    // Count active students today
    const oneDayAgo = Math.floor(Date.now() / 1000) - 86400;
    const activeToday = students.filter(
      student => student.lastaccess && student.lastaccess > oneDayAgo
    ).length;

    return {
      totalstudents: students.length,
      activetoday: activeToday,
      avgcompletion: 0, // Will be calculated separately
    };
  } catch (error) {
    console.error("Error fetching course stats:", error);
    throw error;
  }
}

/**
 * Get average completion percentage for a course
 */
export async function getAverageCompletion(courseId: number): Promise<number> {
  try {
    const enrolledUsers = await getEnrolledUsers(courseId);
    const students = enrolledUsers.filter(user => 
      user.roles?.some(role => role.shortname === 'student')
    );

    if (students.length === 0) return 0;

    const completionPromises = students.map(student =>
      getCourseCompletion(courseId, student.id).catch(() => null)
    );

    const completions = await Promise.all(completionPromises);
    const validCompletions = completions.filter(c => c !== null);

    if (validCompletions.length === 0) return 0;

    const totalPercentage = validCompletions.reduce((sum, completion) => {
      if (!completion) return sum;
      // Handle both 'statuses' and 'completions' response formats
      const statuses = (completion as any)?.statuses || (completion as any)?.completions || [];
      const completed = statuses.filter((c: any) => c.state === 1).length;
      const total = statuses.length;
      return sum + (total > 0 ? (completed / total) * 100 : 0);
    }, 0);

    return Math.round(totalPercentage / validCompletions.length);
  } catch (error) {
    console.error("Error calculating average completion:", error);
    return 0;
  }
}

/**
 * Get student progress data for charts
 */
export async function getStudentProgress(
  courseId: number,
  userId: number
): Promise<{
  overall: number;
  completedLessons: number;
  totalLessons: number;
  grades: { week: string; score: number }[];
}> {
  try {
    const [completion, content] = await Promise.all([
      getCourseCompletion(courseId, userId).catch(() => ({ statuses: [] })),
      getCourseContent(courseId).catch(() => []),
    ]);

    // Handle case where Moodle API returns 'statuses' or 'completions'
    const completionStatuses = (completion as any)?.statuses || (completion as any)?.completions || [];
    const totalModules = completionStatuses.length;
    const completedModules = completionStatuses.filter(
      (c: any) => c.state === 1
    ).length;

    const overall = totalModules > 0
      ? Math.round((completedModules / totalModules) * 100)
      : 0;

    // Generate mock weekly grades based on completion trend
    const grades = Array.from({ length: 6 }, (_, i) => ({
      week: `Week ${i + 1}`,
      score: Math.min(overall, 65 + i * 5 + Math.random() * 5),
    }));

    return {
      overall,
      completedLessons: completedModules,
      totalLessons: totalModules,
      grades,
    };
  } catch (error) {
    console.error("Error fetching student progress:", error);
    // Return default values instead of throwing
    return {
      overall: 0,
      completedLessons: 0,
      totalLessons: 0,
      grades: Array.from({ length: 6 }, (_, i) => ({
        week: `Week ${i + 1}`,
        score: 65 + i * 5,
      })),
    };
  }
}

/**
 * Get activity heatmap data
 */
export async function getActivityHeatmap(
  courseId: number,
  userId: number
): Promise<{ day: string; hours: number }[]> {
  try {
    // Moodle doesn't have direct API for this, so we'll return mock data
    // In production, you'd analyze log entries
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    return days.map(day => ({
      day,
      hours: Math.random() * 4 + 0.5,
    }));
  } catch (error) {
    console.error("Error fetching activity heatmap:", error);
    return [];
  }
}

/**
 * Get module view counts (for teacher analytics)
 */
export async function getModuleViews(
  courseId: number
): Promise<{ name: string; views: number }[]> {
  try {
    const content = await getCourseContent(courseId);
    
    const modules = content.flatMap(section => section.modules);
    
    return modules.map(module => ({
      name: module.name,
      views: module.viewcount || Math.floor(Math.random() * 200) + 50,
    }));
  } catch (error) {
    console.error("Error fetching module views:", error);
    return [];
  }
}

/**
 * Get struggling topics (modules with low completion)
 */
export async function getStrugglingTopics(
  courseId: number
): Promise<{ topic: string; students: number; percentage: number }[]> {
  try {
    const [enrolledUsers, content] = await Promise.all([
      getEnrolledUsers(courseId),
      getCourseContent(courseId),
    ]);

    const students = enrolledUsers.filter(user =>
      user.roles?.some(role => role.shortname === 'student')
    );

    const modules = content.flatMap(section => section.modules);
    const topicsData: { topic: string; students: number; percentage: number }[] = [];

    for (const module of modules.slice(0, 5)) {
      let strugglingCount = 0;

      for (const student of students) {
        try {
          const completion = await getCourseCompletion(courseId, student.id);
          if (!completion) continue;
          
          // Handle both 'statuses' and 'completions' response formats
          const statuses = (completion as any)?.statuses || (completion as any)?.completions || [];
          
          const moduleCompletion = statuses.find(
            (c: any) => c.cmid === module.id
          );
          if (!moduleCompletion || moduleCompletion.state === 0) {
            strugglingCount++;
          }
        } catch {
          continue;
        }
      }

      const percentage = students.length > 0
        ? Math.round((strugglingCount / students.length) * 100)
        : 0;

      topicsData.push({
        topic: module.name,
        students: strugglingCount,
        percentage,
      });
    }

    return topicsData.sort((a, b) => b.percentage - a.percentage);
  } catch (error) {
    console.error("Error fetching struggling topics:", error);
    return [];
  }
}

/**
 * Get AI recommendations for student
 */
export async function getAIRecommendations(userId: number, courseId: number): Promise<any> {
  try {
    const RECOMMEND_API_URL = "http://139.99.103.223:8088";
    const response = await fetch(`${RECOMMEND_API_URL}/api/recommend/user_id/${userId}/course_id/${courseId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error("Recommendation API returned unsuccessful response");
    }

    return data;
  } catch (error) {
    console.error("Error fetching AI recommendations:", error);
    return null;
  }
}

/**
 * Get PO-LO mapping for a course
 */
export async function getPOLOMapping(courseId: number): Promise<any> {
  const RECOMMEND_API_URL = "http://139.99.103.223:8088";
  
  try {
    const response = await fetch(`${RECOMMEND_API_URL}/api/po-lo/${courseId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error("PO-LO API returned unsuccessful response");
    }

    return data;
  } catch (error) {
    console.error("Error fetching PO-LO mapping:", error);
    return null;
  }
}

/**
 * Get LO mastery for a user in a course
 */
export async function getLOMastery(userId: number, courseId: number): Promise<any> {
  const RECOMMEND_API_URL = "http://139.99.103.223:8088";
  
  try {
    const response = await fetch(`${RECOMMEND_API_URL}/api/lo-mastery/${userId}/${courseId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error("LO Mastery API returned unsuccessful response");
    }

    return data;
  } catch (error) {
    console.error("Error fetching LO mastery:", error);
    return null;
  }
}

// ==================== CLUSTERING API ====================

/**
 * Get clustering overview for a course
 */
export async function getClusteringOverview(courseId: number): Promise<ClusteringOverview | null> {
  try {
    const response = await fetch(
      `${CLUSTERING_API_URL}/api/clustering/courses/${courseId}/overview`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching clustering overview:", error);
    return null;
  }
}

/**
 * Get detailed clustering results for a course
 */
export async function getClusteringResults(courseId: number): Promise<ClusteringResults | null> {
  try {
    const response = await fetch(
      `${CLUSTERING_API_URL}/api/clustering/courses/${courseId}/results`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching clustering results:", error);
    return null;
  }
}

// ===================================================================
// LO/PO Mastery API
// ===================================================================

const LO_MASTERY_API_URL = import.meta.env.VITE_LO_MASTERY_API_URL || "http://139.99.103.223:8088";

export interface LOMasteryData {
  course_id: number;
  user_id: number;
  last_sync: string;
  lo_mastery: { [key: string]: number };
  po_progress: { [key: string]: number };
  metadata: {
    total_activities_completed: number;
    total_quizzes_taken: number;
    avg_quiz_score: number;
    activities_by_lo: { [key: string]: number[] };
  };
}

export interface SyncResult {
  success: boolean;
  course_id: number;
  user_id: number;
  result?: {
    success: boolean;
    user_id: number;
    course_id: number;
    elapsed_time: number;
    lo_count: number;
    po_count: number;
    avg_lo_mastery: number;
  };
  error?: string;
}

/**
 * Sync student mastery data (call before getting mastery)
 */
export async function syncStudentMastery(
  courseId: number,
  userId: number
): Promise<SyncResult | null> {
  try {
    const response = await fetch(
      `${LO_MASTERY_API_URL}/api/lo-mastery/sync/${courseId}?user_id=${userId}`,
      { method: 'POST' }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error syncing student mastery:", error);
    return null;
  }
}

/**
 * Get student LO/PO mastery data
 */
export async function getStudentMastery(
  userId: number,
  courseId: number,
  useCache: boolean = true
): Promise<LOMasteryData | null> {
  try {
    const response = await fetch(
      `${LO_MASTERY_API_URL}/api/lo-mastery/${userId}/${courseId}?use_cache=${useCache}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // API returns { success, user_id, course_id, data }
    if (result.success && result.data) {
      return result.data;
    }
    
    return null;
  } catch (error) {
    console.error("Error fetching student mastery:", error);
    return null;
  }
}
