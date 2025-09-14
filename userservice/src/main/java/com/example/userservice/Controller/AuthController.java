package com.example.userservice.Controller;

import com.example.userservice.DTO.AuthRequest;
import com.example.userservice.DTO.AuthResponse;
import com.example.userservice.DTO.UserDTO;
import com.example.userservice.Service.UserService;
import com.example.userservice.Util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {
    
    private final AuthenticationManager authenticationManager;
    private final UserService userService;
    private final JwtUtil jwtUtil;
    
    @PostMapping("/auth/login")
    public ResponseEntity<?> login(@Valid @RequestBody AuthRequest authRequest) {
        try {
            // Authenticate user
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    authRequest.getEmail(),
                    authRequest.getPassword()
                )
            );
            
            // Get user details
            UserDTO user = userService.getUserByEmail(authRequest.getEmail())
                .orElseThrow(() -> new RuntimeException("User not found"));
            
            // Generate JWT token
            String token = jwtUtil.generateToken(user);
            
            // Create response
            AuthResponse response = AuthResponse.builder()
                .token(token)
                .type("Bearer")
                .user(user)
                .expiresIn(jwtUtil.getExpirationTime())
                .build();
            
            return ResponseEntity.ok(response);
            
        } catch (AuthenticationException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Invalid credentials");
            error.put("message", "Email or password is incorrect");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Authentication failed");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }
    
    @PostMapping("/auth/register")
    public ResponseEntity<?> register(@Valid @RequestBody UserDTO userDTO) {
        try {
            // Check if user already exists
            if (userService.getUserByEmail(userDTO.getEmail()).isPresent()) {
                Map<String, String> error = new HashMap<>();
                error.put("error", "User already exists");
                error.put("message", "User with this email already exists");
                return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
            }
            
            // Create new user
            UserDTO newUser = userService.createUser(userDTO);
            
            // Generate JWT token
            String token = jwtUtil.generateToken(newUser);
            
            // Create response
            AuthResponse response = AuthResponse.builder()
                .token(token)
                .type("Bearer")
                .user(newUser)
                .expiresIn(jwtUtil.getExpirationTime())
                .build();
            
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
            
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Registration failed");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }
    
    @PostMapping("/auth/validate")
    public ResponseEntity<?> validateToken(@RequestHeader("Authorization") String token) {
        try {
            // Remove "Bearer " prefix
            if (token.startsWith("Bearer ")) {
                token = token.substring(7);
            }
            
            // Validate token
            if (jwtUtil.validateToken(token)) {
                String email = jwtUtil.getEmailFromToken(token);
                UserDTO user = userService.getUserByEmail(email)
                    .orElseThrow(() -> new RuntimeException("User not found"));
                
                Map<String, Object> response = new HashMap<>();
                response.put("valid", true);
                response.put("user", user);
                response.put("email", email);
                
                return ResponseEntity.ok(response);
            } else {
                Map<String, String> error = new HashMap<>();
                error.put("valid", "false");
                error.put("error", "Invalid token");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            }
            
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("valid", "false");
            error.put("error", "Token validation failed");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        }
    }
    
    @PostMapping("/auth/refresh")
    public ResponseEntity<?> refreshToken(@RequestHeader("Authorization") String token) {
        try {
            // Remove "Bearer " prefix
            if (token.startsWith("Bearer ")) {
                token = token.substring(7);
            }
            
            // Validate and refresh token
            if (jwtUtil.validateToken(token)) {
                String email = jwtUtil.getEmailFromToken(token);
                UserDTO user = userService.getUserByEmail(email)
                    .orElseThrow(() -> new RuntimeException("User not found"));
                
                // Generate new token
                String newToken = jwtUtil.generateToken(user);
                
                AuthResponse response = AuthResponse.builder()
                    .token(newToken)
                    .type("Bearer")
                    .user(user)
                    .expiresIn(jwtUtil.getExpirationTime())
                    .build();
                
                return ResponseEntity.ok(response);
            } else {
                Map<String, String> error = new HashMap<>();
                error.put("error", "Invalid token");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            }
            
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Token refresh failed");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        }
    }
    
    @GetMapping("/auth/me")
    public ResponseEntity<?> getCurrentUser(@RequestHeader("Authorization") String token) {
        try {
            // Remove "Bearer " prefix
            if (token.startsWith("Bearer ")) {
                token = token.substring(7);
            }
            
            if (jwtUtil.validateToken(token)) {
                String email = jwtUtil.getEmailFromToken(token);
                UserDTO user = userService.getUserByEmail(email)
                    .orElseThrow(() -> new RuntimeException("User not found"));
                
                return ResponseEntity.ok(user);
            } else {
                Map<String, String> error = new HashMap<>();
                error.put("error", "Invalid token");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            }
            
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Failed to get user info");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        }
    }
    
    @PostMapping("/auth/lti")
    public ResponseEntity<?> ltiAuthentication(@RequestBody Map<String, Object> ltiData) {
        try {
            // Extract LTI user data
            String name = (String) ltiData.get("name");
            String email = (String) ltiData.get("email");
            String role = (String) ltiData.get("roleName");
            String ltiUserId = (String) ltiData.get("ltiUserId");
            String courseId = (String) ltiData.get("courseId");
            
            if (name == null || email == null || role == null) {
                Map<String, String> error = new HashMap<>();
                error.put("error", "Missing required LTI parameters");
                error.put("message", "name, email, and role are required");
                return ResponseEntity.badRequest().body(error);
            }
            
            // Check if user exists, if not create them
            UserDTO user;
            try {
                user = userService.getUserByEmail(email).orElse(null);
            } catch (Exception e) {
                user = null;
            }
            
            if (user == null) {
                // Create new user from LTI data
                user = userService.createLTIUser(name, email, role, ltiUserId, courseId);
            } else {
                // Update existing user with LTI data if needed
                user = userService.updateUserFromLTI(user, name, role, ltiUserId, courseId);
            }
            
            // Generate JWT token
            String token = jwtUtil.generateToken(user);
            
            // Create response
            AuthResponse response = AuthResponse.builder()
                .token(token)
                .type("Bearer")
                .user(user)
                .expiresIn((long)86400000) // 24 hours
                .build();
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "LTI authentication failed");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        }
    }
    
    @GetMapping("/auth/health")
    public ResponseEntity<?> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "User Authentication Service");
        health.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(health);
    }
}
