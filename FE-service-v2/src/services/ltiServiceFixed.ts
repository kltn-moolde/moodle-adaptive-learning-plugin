// LTI Integration Service for Moodle External Tool
import { kongApi, type UserData } from "./kongApiService";

// LTI Launch Parameters from Python LTI Service redirect
export interface LTILaunchParams {
  user_id: string;
  lis_person_name_full: string;
  lis_person_contact_email_primary: string;
  roles: string;
  context_id: string;
  context_title: string;
  resource_link_id: string;
  tool_consumer_instance_guid: string;
  custom_course_id?: string;
  custom_user_role?: string;
}

// LTI Role mapping to our system roles
export type UserRole = "STUDENT" | "INSTRUCTOR" | "ADMIN";

export interface LTIUserData extends UserData {
  ltiUserId: string;
  courseId: string;
  contextTitle: string;
  resourceLinkId: string;
}

class LTIService {
  private static instance: LTIService;
  private ltiParams: LTILaunchParams | null = null;

  static getInstance(): LTIService {
    if (!LTIService.instance) {
      LTIService.instance = new LTIService();
    }
    return LTIService.instance;
  }

  // Parse LTI parameters from Python LTI Service redirect
  parseLTILaunch(): LTILaunchParams | null {
    try {
      console.log("🔍 [LTI DEBUG] Đang parse LTI launch...");
      const urlParams = new URLSearchParams(window.location.search);
      console.log(
        "🔍 [LTI DEBUG] URL params:",
        Object.fromEntries(urlParams.entries())
      );    

      // Nếu có thông tin từ redirect Python service
      if (urlParams.has("user_id") || urlParams.has("lis_person_name_full")) {
        console.log("✅ [LTI DEBUG] Phát hiện LTI params trong URL.");

        const params: LTILaunchParams = {
          user_id: urlParams.get("user_id") || "",
          lis_person_name_full: urlParams.get("lis_person_name_full") || "",
          lis_person_contact_email_primary:
            urlParams.get("lis_person_contact_email_primary") || "",
          roles: urlParams.get("roles") || "",
          context_id: urlParams.get("context_id") || "",
          context_title: urlParams.get("context_title") || "",
          resource_link_id: urlParams.get("resource_link_id") || "",
          tool_consumer_instance_guid:
            urlParams.get("tool_consumer_instance_guid") || "",
          custom_course_id: urlParams.get("custom_course_id") || undefined,
          custom_user_role: urlParams.get("custom_user_role") || undefined,
        };

        console.log("✅ [LTI DEBUG] LTI launch params parsed:", params);

        // Lưu lại vào sessionStorage
        sessionStorage.setItem("lti_launch_params", JSON.stringify(params));
        this.ltiParams = params;
        return params;
      }

      // Nếu không có trên URL, kiểm tra sessionStorage
      console.log(
        "ℹ️ [LTI DEBUG] Không thấy params trong URL, kiểm tra sessionStorage..."
      );
      const sessionLTI = sessionStorage.getItem("lti_launch_params");
      if (sessionLTI) {
        const params = JSON.parse(sessionLTI) as LTILaunchParams;
        console.log("✅ [LTI DEBUG] Lấy từ sessionStorage:", params);
        this.ltiParams = params;
        return params;
      }

      console.warn(
        "⚠️ [LTI DEBUG] Không tìm thấy LTI launch params ở URL hoặc sessionStorage."
      );
      return null;
    } catch (error) {
      console.error(
        "❌ [LTI DEBUG] Lỗi khi parse LTI launch parameters:",
        error
      );
      return null;
    }
  }

  // Map LTI roles to our system roles
  mapLTIRoleToSystemRole(ltiRoles: string): UserRole {
    const roles = ltiRoles.toLowerCase();

    if (
      roles.includes("instructor") ||
      roles.includes("teacher") ||
      roles.includes("contentdeveloper")
    ) {
      return "INSTRUCTOR";
    }

    if (roles.includes("administrator") || roles.includes("admin")) {
      return "ADMIN";
    }

    // Default to student
    return "STUDENT";
  }

  // Authenticate user with LTI parameters from Python service → Call User Service via Kong
  async authenticateWithLTI(): Promise<LTIUserData | null> {
    try {
        console.log("🔍 [LTI DEBUG] Bắt đầu authenticateWithLTI()...");

        const ltiParams = this.ltiParams || this.parseLTILaunch();
        console.log("🧩 [LTI DEBUG] LTI Params:", ltiParams);

        if (!ltiParams) {
        console.error("❌ [LTI DEBUG] Không tìm thấy LTI launch parameters");
        throw new Error("No LTI launch parameters found");
        }

        // Map LTI role to system role
        const systemRole = this.mapLTIRoleToSystemRole(ltiParams.roles);
        console.log("🧭 [LTI DEBUG] Mapped LTI role → system role:", systemRole);

        // Create user data from LTI parameters for User Service
        const ltiUserData: Partial<UserData> = {
        name: ltiParams.lis_person_name_full,
        email: ltiParams.lis_person_contact_email_primary,
        roleName: systemRole,
        };
        console.log("📦 [LTI DEBUG] User data gửi sang Kong:", ltiUserData);

        // Call User Service via Kong Gateway to get JWT token
        const authResponse = await kongApi.authenticateWithLTI(ltiUserData);
        console.log("📥 [LTI DEBUG] Phản hồi từ Kong:", authResponse);

        if (!authResponse || !authResponse.user) {
        console.error("❌ [LTI DEBUG] Kong không trả về user hợp lệ:", authResponse);
        return null;
        }

        // Combine auth response with LTI data
        const userData: LTIUserData = {
        ...authResponse.user,
        ltiUserId: ltiParams.user_id,
        courseId: ltiParams.custom_course_id || ltiParams.context_id,
        contextTitle: ltiParams.context_title,
        resourceLinkId: ltiParams.resource_link_id,
        };

        console.log("✅ [LTI DEBUG] Tạo user thành công:", userData);

        return userData;
    } catch (error) {
        console.error("🔥 [LTI DEBUG] LTI authentication failed:", error);
        throw error;
    }
    }

  // Get current LTI parameters
  getLTIParams(): LTILaunchParams | null {
    return this.ltiParams;
  }

  // Check if this is an LTI launch
  isLTILaunch(): boolean {
    const params = this.parseLTILaunch();
    return params !== null && params.user_id !== "";
  }

  // Get course context
  getCourseContext(): { courseId: string; courseTitle: string } | null {
    if (!this.ltiParams) return null;

    return {
      courseId: this.ltiParams.custom_course_id || this.ltiParams.context_id,
      courseTitle: this.ltiParams.context_title,
    };
  }

  // Clear LTI session data
  clearLTISession(): void {
    this.ltiParams = null;
    sessionStorage.removeItem("lti_launch_params");
  }
}

// Export singleton instance
export const ltiService = LTIService.getInstance();

// Helper function to check if running in LTI context
export const isLTIContext = (): boolean => {
  return ltiService.isLTILaunch();
};

// Helper function to get LTI user info
export const getLTIUserInfo = async (): Promise<LTIUserData | null> => {
  try {
    return await ltiService.authenticateWithLTI();
  } catch (error) {
    console.error("Failed to get LTI user info:", error);
    return null;
  }
};
