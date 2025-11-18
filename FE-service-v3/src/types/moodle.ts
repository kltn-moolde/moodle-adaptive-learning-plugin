// Moodle API Response Types

export interface MoodleUser {
  id: number;
  username: string;
  firstname: string;
  lastname: string;
  fullname: string;
  email: string;
  profileimageurl?: string;
}

export interface MoodleCourse {
  id: number;
  shortname: string;
  fullname: string;
  displayname: string;
  enrolledusercount?: number;
  idnumber?: string;
  visible?: number;
  summary?: string;
  summaryformat?: number;
  format?: string;
  startdate?: number;
  enddate?: number;
  progress?: number;
}

export interface MoodleGrade {
  courseid: number;
  userid: number;
  grade: number;
  grademax: number;
  grademin: number;
  gradeformatted: string;
  feedback?: string;
}

export interface MoodleCourseModule {
  id: number;
  course: number;
  module: number;
  name: string;
  modname: string;
  instance: number;
  section: number;
  visible: number;
  uservisible?: boolean;
  completion: number;
  completiondata?: {
    state: number;
    timecompleted: number;
  };
  viewcount?: number;
}

export interface MoodleCompletion {
  userid: number;
  courseid: number;
  completions: {
    cmid: number;
    modname: string;
    instance: number;
    state: number;
    timecompleted: number;
    tracking: number;
  }[];
}

export interface MoodleEnrolledUser extends MoodleUser {
  courseid?: number;
  roles?: {
    roleid: number;
    name: string;
    shortname: string;
  }[];
  lastaccess?: number;
  enrolledcourses?: {
    id: number;
    fullname: string;
    shortname: string;
  }[];
}

export interface MoodleLogEntry {
  id: number;
  eventname: string;
  component: string;
  action: string;
  target: string;
  objecttable: string;
  userid: number;
  timecreated: number;
  courseid: number;
  contextid: number;
  contextlevel: number;
}

export interface MoodleGradeItem {
  id: number;
  courseid: number;
  categoryid: number;
  itemname: string;
  itemtype: string;
  itemmodule: string;
  iteminstance: number;
  grademax: number;
  grademin: number;
  gradepass: number;
}

export interface MoodleUserGrade {
  userid: number;
  courseid: number;
  userfullname: string;
  maxdepth: number;
  gradeitems: {
    id: number;
    itemname: string;
    itemtype: string;
    graderaw: number;
    gradeformatted: string;
    grademax: number;
    grademin: number;
    percentageformatted: string;
  }[];
}

export interface MoodleCourseContent {
  id: number;
  name: string;
  visible: number;
  summary: string;
  summaryformat: number;
  section: number;
  hiddenbynumsections: number;
  uservisible: boolean;
  modules: MoodleCourseModule[];
}

export interface MoodleQuizAttempt {
  id: number;
  quiz: number;
  userid: number;
  attempt: number;
  uniqueid: number;
  state: string;
  timestart: number;
  timefinish: number;
  timemodified: number;
  sumgrades: number;
}
