package com.example.gatewayservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/gateway")
public class GatewayController {

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "Gateway Service");
        response.put("timestamp", LocalDateTime.now());
        response.put("port", 8080);
        
        Map<String, String> routes = new HashMap<>();
        routes.put("LTI Service", "http://localhost:8082");
        routes.put("Recommendation Service", "http://localhost:8083");
        routes.put("Course Service", "http://localhost:8084");
        routes.put("Analytics Service", "http://localhost:8085");
        routes.put("User Service", "http://localhost:8086");
        routes.put("React Frontend", "http://localhost:3000");
        routes.put("Discovery Service", "http://localhost:8761");
        
        response.put("configured_routes", routes);
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> info() {
        Map<String, Object> response = new HashMap<>();
        response.put("name", "Gateway Service");
        response.put("description", "API Gateway for Moodle Adaptive Learning Plugin");
        response.put("version", "1.0.0");
        response.put("routes", Map.of(
                "LTI", "/lti/**",
                "Recommendations", "/api/recommendations/**",
                "Courses", "/api/courses/**",
                "Analytics", "/api/analytics/**",
                "Users", "/api/users/**",
                "Frontend", "/** (fallback)"
        ));
        
        return ResponseEntity.ok(response);
    }
}
