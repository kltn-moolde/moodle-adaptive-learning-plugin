/**
 * LTI 1.3 Parameter Utilities
 * Extract and parse LTI parameters from URL
 */

export interface LtiParams {
  userId: number;
  userFullName: string;
  userEmail: string;
  roles: string[];
  userRole: 'STUDENT' | 'INSTRUCTOR' | 'ADMINISTRATOR' | 'UNKNOWN';
  courseId: number;
  courseTitle: string;
  resourceLinkId: number;
  toolConsumerInstanceGuid: string;
}

/**
 * Parse LTI parameters from URL search params
 */
export function getLtiParams(): LtiParams | null {
  if (typeof window === 'undefined') return null;

  const searchParams = new URLSearchParams(window.location.search);

  // Extract user_id
  const userIdStr = searchParams.get('user_id');
  const userId = userIdStr ? parseInt(userIdStr, 10) : null;

  // Extract course/context ID
  const contextIdStr = searchParams.get('context_id');
  const courseId = contextIdStr ? parseInt(contextIdStr, 10) : null;

  // If essential params are missing, return null
  if (!userId || !courseId) {
    console.warn('Missing essential LTI parameters (user_id or context_id)');
    return null;
  }

  // Extract other parameters
  const userFullName = searchParams.get('lis_person_name_full') || 'Unknown User';
  const userEmail = searchParams.get('lis_person_contact_email_primary') || '';
  const rolesStr = searchParams.get('roles') || '';
  const customUserRole = searchParams.get('custom_user_role') || 'UNKNOWN';
  const courseTitle = searchParams.get('context_title') || 'Untitled Course';
  const resourceLinkIdStr = searchParams.get('resource_link_id');
  const resourceLinkId = resourceLinkIdStr ? parseInt(resourceLinkIdStr, 10) : 0;
  const toolConsumerInstanceGuid = searchParams.get('tool_consumer_instance_guid') || '';

  // Parse roles array
  const roles = rolesStr
    .split(',')
    .map(role => decodeURIComponent(role.trim()))
    .filter(role => role.length > 0);

  // Determine user role
  let userRole: 'STUDENT' | 'INSTRUCTOR' | 'ADMINISTRATOR' | 'UNKNOWN' = 'UNKNOWN';
  if (customUserRole === 'INSTRUCTOR') {
    userRole = 'INSTRUCTOR';
  } else if (customUserRole === 'STUDENT') {
    userRole = 'STUDENT';
  } else if (customUserRole === 'ADMINISTRATOR') {
    userRole = 'ADMINISTRATOR';
  } else {
    // Fallback: parse from roles string
    const rolesLower = rolesStr.toLowerCase();
    if (rolesLower.includes('instructor')) {
      userRole = 'INSTRUCTOR';
    } else if (rolesLower.includes('administrator')) {
      userRole = 'ADMINISTRATOR';
    } else if (rolesLower.includes('learner') || rolesLower.includes('student')) {
      userRole = 'STUDENT';
    }
  }

  return {
    userId,
    userFullName: decodeURIComponent(userFullName),
    userEmail: decodeURIComponent(userEmail),
    roles,
    userRole,
    courseId,
    courseTitle: decodeURIComponent(courseTitle),
    resourceLinkId,
    toolConsumerInstanceGuid,
  };
}

/**
 * Check if user is instructor/teacher
 */
export function isInstructor(ltiParams: LtiParams | null): boolean {
  if (!ltiParams) return false;
  return ltiParams.userRole === 'INSTRUCTOR' || ltiParams.userRole === 'ADMINISTRATOR';
}

/**
 * Check if user is student
 */
export function isStudent(ltiParams: LtiParams | null): boolean {
  if (!ltiParams) return false;
  return ltiParams.userRole === 'STUDENT';
}

/**
 * Get user ID from LTI params or fallback
 */
export function getUserId(ltiParams: LtiParams | null, fallback: number = 5): number {
  return ltiParams?.userId || fallback;
}

/**
 * Get course ID from LTI params or fallback
 */
export function getCourseId(ltiParams: LtiParams | null, fallback: number = 2): number {
  return ltiParams?.courseId || fallback;
}
