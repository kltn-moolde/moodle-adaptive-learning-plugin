package com.example.plugin_moodle_LTI_13.controller;
import com.example.plugin_moodle_LTI_13.model.LtiLaunch;
import com.example.plugin_moodle_LTI_13.model.UserLog;
import com.example.plugin_moodle_LTI_13.service.LtiService;
import com.example.plugin_moodle_LTI_13.service.MoodleApiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Controller
@RequestMapping("/lti")
public class LtiController {

    @Autowired
    private LtiService ltiService;

    @Autowired
    private MoodleApiService moodleApiService;

    @Value("${lti.tool.client-id}")
    private String clientId;

    @Value("${lti.tool.deployment-id}")
    private String deploymentId;

    @Value("${lti.tool.issuer}")
    private String issuer;

    @Value("${lti.tool.auth-url}")
    private String authUrl;

    @Value("${lti.tool.token-url}")
    private String tokenUrl;

    @Value("${lti.tool.keyset-url}")
    private String keysetUrl;

    // LTI 1.3 Login Initiation
    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestParam Map<String, String> params) {

        System.out.println("=== LOGIN METHOD CALLED ===");

        String loginHint = params.get("login_hint");
        String targetLinkUri = params.get("target_link_uri");
        String ltiMessageHint = params.get("lti_message_hint");

        System.out.println("login_hint: " + loginHint);
        System.out.println("target_link_uri: " + targetLinkUri);
        System.out.println("lti_message_hint: " + ltiMessageHint);

        // Generate state and nonce for security
        String state = UUID.randomUUID().toString();
        String nonce = UUID.randomUUID().toString();

        try {
            // Build authorization URL
            StringBuilder authUrlBuilder = new StringBuilder(authUrl);
            authUrlBuilder.append("?response_type=id_token");
            authUrlBuilder.append("&client_id=").append(URLEncoder.encode(clientId, StandardCharsets.UTF_8));
            authUrlBuilder.append("&redirect_uri=").append(URLEncoder.encode(targetLinkUri, StandardCharsets.UTF_8));
            authUrlBuilder.append("&login_hint=").append(URLEncoder.encode(loginHint, StandardCharsets.UTF_8));
            authUrlBuilder.append("&state=").append(URLEncoder.encode(state, StandardCharsets.UTF_8));
            authUrlBuilder.append("&nonce=").append(URLEncoder.encode(nonce, StandardCharsets.UTF_8));
            authUrlBuilder.append("&scope=openid");
            authUrlBuilder.append("&response_mode=form_post");

            if (ltiMessageHint != null) {
                authUrlBuilder.append("&lti_message_hint=").append(URLEncoder.encode(ltiMessageHint, StandardCharsets.UTF_8));
            }

            String authUrlString = authUrlBuilder.toString();
            System.out.println("Auth URL: " + authUrlString);

            // Return redirect response
            HttpHeaders headers = new HttpHeaders();
            headers.add("Location", authUrlString);
            return new ResponseEntity<>(headers, HttpStatus.FOUND);

        } catch (Exception e) {
            System.err.println("ERROR in login method: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error: " + e.getMessage());
        }
    }

    // LTI 1.3 Launch
    @PostMapping("/launch")
    public String launch(@RequestParam Map<String, Object> params, Model model) {
        try {
            System.out.println("=== LAUNCH METHOD CALLED ===");
            System.out.println("Received Form Params: " + params);

            String idToken = (String) params.get("id_token");
            String state = (String) params.get("state");

            // In a real implementation, you would validate the JWT token here
            // For this example, we'll simulate processing the launch data

            // Process the launch
            System.out.println("=== truoc khi chayj processLaunch ===");
            LtiLaunch launch = ltiService.processLaunch(params);
            System.out.println("=== sau khi chayj processLaunch ===");

            System.out.println("=== truoc khi chay gen token ===");
            // Generate a session token
            String sessionToken = ltiService.generateJwtToken(launch.getUserId(), launch.getCourseId());

            System.out.println("=== sau svdhsgkhi chay gen token ===");

            System.out.println("Launch object: " + launch.getUserId());
            System.out.println("Model keys: " + model.asMap().keySet());
            System.out.println("Session Token: " + sessionToken);

            model.addAttribute("launch", launch);
            model.addAttribute("sessionToken", sessionToken);

            System.out.println("redirect:/lti/dashboard?token=" + sessionToken);

            return "redirect:/lti/dashboard?token=" + sessionToken;

        } catch (Exception e) {
            System.out.println("Received Form Params: " + params);
            System.out.println("=== Loi LAUNCH METHOD ===");
            model.addAttribute("error", "Launch failed: " + e.getMessage());
            return "error";
        }
    }

    // Dashboard
    @GetMapping("/dashboard")
    public String dashboard(@RequestParam("token") String token, Model model) {
        if (!ltiService.validateToken(token)) {
            model.addAttribute("error", "Invalid or expired token");
            return "error";
        }
        System.out.println("Token validated successfully: " + token);

        String userId = ltiService.getUserIdFromToken(token);
        // You would typically get launch data from database here
        String courseId = ltiService.getCourseIdFromToken(token);
        System.out.println("courseId ID: " + courseId);

        model.addAttribute("userId", userId);
        model.addAttribute("token", token);
        model.addAttribute("courseId", courseId);

        return "dashboard";
    }

    // User Logs Page
    @GetMapping("/logs")
    public String userLogs(@RequestParam("token") String token,
                           @RequestParam(value = "courseId", required = false) String courseId,
                           Model model) {
        if (!ltiService.validateToken(token)) {
            model.addAttribute("error", "Invalid or expired token");
            return "error";
        }

        String userId = ltiService.getUserIdFromToken(token);

        List<UserLog> logs;
        if (courseId != null && !courseId.isEmpty()) {
            logs = moodleApiService.getUserLogs(courseId);
        } else {
            logs = moodleApiService.getUserLogs("1"); // Default course ID
        }

        model.addAttribute("logs", logs);
        model.addAttribute("userId", userId);
        model.addAttribute("courseId", courseId);
        model.addAttribute("token", token);

        return "user-logs";
    }

    // API endpoint to get logs as JSON
    @GetMapping("/api/logs")
    @ResponseBody
    public ResponseEntity<List<UserLog>> getLogsApi(@RequestParam("token") String token,
                                                    @RequestParam("courseId") String courseId) {
        if (!ltiService.validateToken(token)) {
            return ResponseEntity.status(401).build();
        }

        List<UserLog> logs = moodleApiService.getUserLogs(courseId);
        return ResponseEntity.ok(logs);
    }

    // Configuration endpoint for Moodle
    @GetMapping("/config")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getToolConfiguration() {
        Map<String, Object> config = Map.of(
                "title", "User Log Viewer",
                "description", "View user activity logs from Moodle",
                "target_link_uri", "/lti/launch",
                "oidc_initiation_url", "/lti/login",
                "public_jwk_url", "/lti/jwks",
                "privacy_level", "public"
        );

        return ResponseEntity.ok(config);
    }

    // JWKS endpoint (simplified - in production you'd have proper keys)
    @GetMapping("/jwks")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getJwks() {
        Map<String, Object> jwks = Map.of(
                "keys", List.of()
        );
        return ResponseEntity.ok(jwks);
    }
}