// Moodle API Service

// Interfaces for Moodle API responses
export interface CourseCompletion {
  courseid: number;
  userid: number;
  completionstatus: number; // 0 = incomplete, 1 = complete
  progress: number; // 0-100
  timecompleted?: number;
}

export interface ActivityCompletion {
  cmid: number;
  modname: string;
  instance: number;
  state: number; // 0 = incomplete, 1 = complete, 2 = complete pass, 3 = complete fail
  timecompleted?: number;
  tracking: number;
  overrideby?: number;
  valueused?: boolean;
}

export interface GradeItem {
  id: number;
  itemname: string;
  itemtype: string;
  itemmodule?: string;
  iteminstance?: number;
  categoryid: number;
  gradetype: number;
  grademax: number;
  grademin: number;
  gradepass?: number;
  locked: boolean;
  hidden: boolean;
  weightraw?: number;
  aggregationcoef?: number;
  aggregationcoef2?: number;
  sortorder: number;
  display: number;
  decimals?: number;
  needsupdate: boolean;
  feedback?: string;
  grade?: {
    grade: number;
    str_grade: string;
    str_long_grade: string;
    dategraded: number;
    locked: boolean;
    overridden: boolean;
    feedback?: string;
  };
}

export interface CourseGrade {
  courseid: number;
  grade: string;
  rawgrade: number;
}

export interface EnrolledUser {
  id: number;
  username: string;
  firstname: string;
  lastname: string;
  fullname: string;
  email: string;
  profileimagewithlink: string;
  profileimageurl: string;
  groups: Array<{
    id: number;
    name: string;
    description: string;
  }>;
  roles: Array<{
    roleid: number;
    name: string;
    shortname: string;
    sortorder: number;
  }>;
  enrolledcourses?: Array<{
    id: number;
    fullname: string;
  }>;
}

export interface GradesTable {
  courseid: number;
  userid: number;
  userfullname: string;
  maxdepth: number;
  tabledata: Array<{
    itemname: {
      content: string;
      class: string;
      colspan: number;
      celltype: string;
      title?: string;
    };
    leader: {
      class: string;
      rowspan: number;
    };
    weight: {
      content: string;
      class: string;
      headers: string;
    };
    grade: {
      content: string;
      class: string;
      headers: string;
      title?: string;
    };
    range: {
      content: string;
      class: string;
      headers: string;
    };
    percentage: {
      content: string;
      class: string;
      headers: string;
    };
    lettergrade: {
      content: string;
      class: string;
      headers: string;
    };
    rank: {
      content: string;
      class: string;
      headers: string;
    };
    average: {
      content: string;
      class: string;
      headers: string;
    };
    feedback: {
      content: string;
      class: string;
      headers: string;
    };
    contributiontocoursetotal: {
      content: string;
      class: string;
      headers: string;
    };
  }>;
}

export interface CompetencyReport {
  userid: number;
  courseid: number;
  competencies: Array<{
    competency: {
      id: number;
      shortname: string;
      description: string;
      framework: {
        id: number;
        name: string;
      };
    };
    usercompetency?: {
      userid: number;
      competencyid: number;
      status: number;
      reviewerid?: number;
      proficiency?: boolean;
      grade?: number;
    };
    usercompetencycourse?: {
      userid: number;
      courseid: number;
      competencyid: number;
      proficiency?: boolean;
      grade?: number;
    };
  }>;
}

// Dashboard Analytics Data
export interface DashboardAnalytics {
  courseCompletion: CourseCompletion;
  activitiesCompletion: ActivityCompletion[];
  gradeItems: GradeItem[];
  courseGrades: CourseGrade[];
  gradesTable: GradesTable;
  competencyReport: CompetencyReport;
  enrolledUsers?: EnrolledUser[]; // For teacher dashboard
  gradeDistribution?: {
    ranges: string[];
    counts: number[];
    average: number;
    median: number;
  };
}

export class MoodleApiService {
  private moodleUrl: string;
  private token: string;

  constructor(
    moodleUrl: string = import.meta.env.VITE_MOODLE_URL || 'http://localhost:8100',
    token: string = import.meta.env.VITE_MOODLE_TOKEN || ''
  ) {
    this.moodleUrl = moodleUrl;
    this.token = token;
  }

  // Get course completion status
  async getCourseCompletion(userId: number, courseId: number): Promise<CourseCompletion> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'core_completion_get_course_completion_status',
          moodlewsrestformat: 'json',
          courseid: courseId.toString(),
          userid: userId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting course completion:', error);
      // Mock data fallback
      return {
        courseid: courseId,
        userid: userId,
        completionstatus: 0,
        progress: 65,
        timecompleted: undefined,
      };
    }
  }

  // Get activities completion status
  async getActivitiesCompletion(userId: number, courseId: number): Promise<ActivityCompletion[]> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'core_completion_get_activities_completion_status',
          moodlewsrestformat: 'json',
          courseid: courseId.toString(),
          userid: userId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data.statuses || [];
    } catch (error) {
      console.error('Error getting activities completion:', error);
      // Mock data fallback
      return [
        {
          cmid: 1,
          modname: 'assign',
          instance: 1,
          state: 1,
          timecompleted: Date.now() - 86400000,
          tracking: 2,
        },
        {
          cmid: 2,
          modname: 'quiz',
          instance: 2,
          state: 2,
          timecompleted: Date.now() - 43200000,
          tracking: 2,
        },
        {
          cmid: 3,
          modname: 'resource',
          instance: 3,
          state: 0,
          tracking: 1,
        },
      ];
    }
  }

  // Get grade items
  async getGradeItems(userId: number, courseId: number): Promise<GradeItem[]> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'gradereport_user_get_grade_items',
          moodlewsrestformat: 'json',
          courseid: courseId.toString(),
          userid: userId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data.usergrades || [];
    } catch (error) {
      console.error('Error getting grade items:', error);
      // Mock data fallback
      return [
        {
          id: 1,
          itemname: 'Assignment 1',
          itemtype: 'mod',
          itemmodule: 'assign',
          iteminstance: 1,
          categoryid: 2,
          gradetype: 1,
          grademax: 100,
          grademin: 0,
          gradepass: 50,
          locked: false,
          hidden: false,
          sortorder: 1,
          display: 0,
          needsupdate: false,
          grade: {
            grade: 85,
            str_grade: '85.00',
            str_long_grade: '85.00 / 100.00',
            dategraded: Date.now() - 86400000,
            locked: false,
            overridden: false,
          },
        },
        {
          id: 2,
          itemname: 'Quiz 1',
          itemtype: 'mod',
          itemmodule: 'quiz',
          iteminstance: 2,
          categoryid: 2,
          gradetype: 1,
          grademax: 100,
          grademin: 0,
          gradepass: 60,
          locked: false,
          hidden: false,
          sortorder: 2,
          display: 0,
          needsupdate: false,
          grade: {
            grade: 78,
            str_grade: '78.00',
            str_long_grade: '78.00 / 100.00',
            dategraded: Date.now() - 43200000,
            locked: false,
            overridden: false,
          },
        },
      ];
    }
  }

  // Get course grades overview
  async getCourseGrades(userId: number): Promise<CourseGrade[]> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'gradereport_overview_get_course_grades',
          moodlewsrestformat: 'json',
          userid: userId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data.grades || [];
    } catch (error) {
      console.error('Error getting course grades:', error);
      // Mock data fallback
      return [
        {
          courseid: 5,
          grade: '81.50',
          rawgrade: 81.5,
        },
      ];
    }
  }

  // Get enrolled users (for teacher dashboard)
  async getEnrolledUsers(courseId: number): Promise<EnrolledUser[]> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'core_enrol_get_enrolled_users',
          moodlewsrestformat: 'json',
          courseid: courseId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data || [];
    } catch (error) {
      console.error('Error getting enrolled users:', error);
      // Mock data fallback
      return [
        {
          id: 4,
          username: 'student1',
          firstname: 'John',
          lastname: 'Doe',
          fullname: 'John Doe',
          email: 'john.doe@example.com',
          profileimagewithlink: '',
          profileimageurl: '',
          groups: [],
          roles: [
            {
              roleid: 5,
              name: 'Student',
              shortname: 'student',
              sortorder: 0,
            },
          ],
        },
        {
          id: 5,
          username: 'student2',
          firstname: 'Jane',
          lastname: 'Smith',
          fullname: 'Jane Smith',
          email: 'jane.smith@example.com',
          profileimagewithlink: '',
          profileimageurl: '',
          groups: [],
          roles: [
            {
              roleid: 5,
              name: 'Student',
              shortname: 'student',
              sortorder: 0,
            },
          ],
        },
      ];
    }
  }

  // Get detailed grades table
  async getGradesTable(userId: number, courseId: number): Promise<GradesTable> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'gradereport_user_get_grades_table',
          moodlewsrestformat: 'json',
          courseid: courseId.toString(),
          userid: userId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting grades table:', error);
      // Mock data fallback
      return {
        courseid: courseId,
        userid: userId,
        userfullname: 'Student User',
        maxdepth: 2,
        tabledata: [
          {
            itemname: {
              content: 'Assignment 1',
              class: 'item',
              colspan: 1,
              celltype: 'th',
            },
            leader: {
              class: 'leader',
              rowspan: 1,
            },
            weight: {
              content: '10.00 %',
              class: 'weight',
              headers: 'weight',
            },
            grade: {
              content: '85.00',
              class: 'grade',
              headers: 'grade',
              title: '85.00 / 100.00',
            },
            range: {
              content: '0–100',
              class: 'range',
              headers: 'range',
            },
            percentage: {
              content: '85.00 %',
              class: 'percentage',
              headers: 'percentage',
            },
            lettergrade: {
              content: 'B',
              class: 'lettergrade',
              headers: 'lettergrade',
            },
            rank: {
              content: '3 / 25',
              class: 'rank',
              headers: 'rank',
            },
            average: {
              content: '78.50',
              class: 'average',
              headers: 'average',
            },
            feedback: {
              content: 'Good work!',
              class: 'feedback',
              headers: 'feedback',
            },
            contributiontocoursetotal: {
              content: '8.50 %',
              class: 'contributiontocoursetotal',
              headers: 'contributiontocoursetotal',
            },
          },
        ],
      };
    }
  }

  // Get competency report
  async getCompetencyReport(userId: number, courseId: number): Promise<CompetencyReport> {
    try {
      const response = await fetch(`${this.moodleUrl}/webservice/rest/server.php`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          wstoken: this.token,
          wsfunction: 'report_competency_data_for_report',
          moodlewsrestformat: 'json',
          courseid: courseId.toString(),
          userid: userId.toString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Moodle API error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting competency report:', error);
      // Mock data fallback
      return {
        userid: userId,
        courseid: courseId,
        competencies: [
          {
            competency: {
              id: 1,
              shortname: 'Problem Solving',
              description: 'Ability to analyze and solve complex problems',
              framework: {
                id: 1,
                name: 'Core Competencies',
              },
            },
            usercompetency: {
              userid: userId,
              competencyid: 1,
              status: 1,
              proficiency: true,
              grade: 3,
            },
            usercompetencycourse: {
              userid: userId,
              courseid: courseId,
              competencyid: 1,
              proficiency: true,
              grade: 3,
            },
          },
          {
            competency: {
              id: 2,
              shortname: 'Critical Thinking',
              description: 'Ability to think critically and analytically',
              framework: {
                id: 1,
                name: 'Core Competencies',
              },
            },
            usercompetency: {
              userid: userId,
              competencyid: 2,
              status: 0,
              proficiency: false,
              grade: 2,
            },
            usercompetencycourse: {
              userid: userId,
              courseid: courseId,
              competencyid: 2,
              proficiency: false,
              grade: 2,
            },
          },
        ],
      };
    }
  }

  // Get comprehensive dashboard analytics
  async getDashboardAnalytics(userId: number, courseId: number, includeEnrolledUsers: boolean = false): Promise<DashboardAnalytics> {
    try {
      const [
        courseCompletion,
        activitiesCompletion,
        gradeItems,
        courseGrades,
        gradesTable,
        competencyReport,
        enrolledUsers,
      ] = await Promise.all([
        this.getCourseCompletion(userId, courseId),
        this.getActivitiesCompletion(userId, courseId),
        this.getGradeItems(userId, courseId),
        this.getCourseGrades(userId),
        this.getGradesTable(userId, courseId),
        this.getCompetencyReport(userId, courseId),
        includeEnrolledUsers ? this.getEnrolledUsers(courseId) : Promise.resolve(undefined),
      ]);

      // Calculate grade distribution if enrolled users available
      let gradeDistribution = undefined;
      if (enrolledUsers && enrolledUsers.length > 0) {
        const grades = gradeItems.map(item => item.grade?.grade || 0);
        gradeDistribution = this.calculateGradeDistribution(grades);
      }

      return {
        courseCompletion,
        activitiesCompletion,
        gradeItems,
        courseGrades,
        gradesTable,
        competencyReport,
        enrolledUsers,
        gradeDistribution,
      };
    } catch (error) {
      console.error('Error getting dashboard analytics:', error);
      throw error;
    }
  }

  // Calculate grade distribution
  private calculateGradeDistribution(grades: number[]): {
    ranges: string[];
    counts: number[];
    average: number;
    median: number;
  } {
    const ranges = ['0-59', '60-69', '70-79', '80-89', '90-100'];
    const counts = [0, 0, 0, 0, 0];

    grades.forEach(grade => {
      if (grade < 60) counts[0]++;
      else if (grade < 70) counts[1]++;
      else if (grade < 80) counts[2]++;
      else if (grade < 90) counts[3]++;
      else counts[4]++;
    });

    const average = grades.length > 0 ? grades.reduce((sum, grade) => sum + grade, 0) / grades.length : 0;
    const sortedGrades = [...grades].sort((a, b) => a - b);
    const median = sortedGrades.length > 0 
      ? sortedGrades.length % 2 === 0
        ? (sortedGrades[sortedGrades.length / 2 - 1] + sortedGrades[sortedGrades.length / 2]) / 2
        : sortedGrades[Math.floor(sortedGrades.length / 2)]
      : 0;

    return {
      ranges,
      counts,
      average,
      median,
    };
  }
}

// Export singleton instance
export const moodleApiService = new MoodleApiService();