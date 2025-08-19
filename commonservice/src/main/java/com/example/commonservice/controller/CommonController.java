package com.example.commonservice.controller;

import com.example.commonservice.dto.ApiResponse;
import com.example.commonservice.util.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.Map;

@RestController
@RequestMapping("/api/common")
public class CommonController {
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.success("Common Service is running"));
    }
    
    // String Utilities
    @PostMapping("/string/to-slug")
    public ResponseEntity<ApiResponse<String>> toSlug(@RequestBody String input) {
        String result = StringUtil.toSlug(input);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
    
    @PostMapping("/string/to-title-case")
    public ResponseEntity<ApiResponse<String>> toTitleCase(@RequestBody String input) {
        String result = StringUtil.toTitleCase(input);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
    
    @PostMapping("/string/mask-email")
    public ResponseEntity<ApiResponse<String>> maskEmail(@RequestBody String email) {
        String result = StringUtil.maskEmail(email);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
    
    @PostMapping("/string/get-initials")
    public ResponseEntity<ApiResponse<String>> getInitials(@RequestBody String fullName) {
        String result = StringUtil.getInitials(fullName);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
    
    // Validation Utilities
    @PostMapping("/validate/email")
    public ResponseEntity<ApiResponse<Boolean>> validateEmail(@RequestBody String email) {
        boolean isValid = ValidationUtil.isValidEmail(email);
        return ResponseEntity.ok(ApiResponse.success("Email validation result", isValid));
    }
    
    @PostMapping("/validate/phone")
    public ResponseEntity<ApiResponse<Boolean>> validatePhone(@RequestBody String phone) {
        boolean isValid = ValidationUtil.isValidPhone(phone);
        return ResponseEntity.ok(ApiResponse.success("Phone validation result", isValid));
    }
    
    @PostMapping("/validate/password")
    public ResponseEntity<ApiResponse<Boolean>> validatePassword(@RequestBody String password) {
        boolean isValid = ValidationUtil.isValidPassword(password);
        return ResponseEntity.ok(ApiResponse.success("Password validation result", isValid));
    }
    
    // DateTime Utilities
    @GetMapping("/datetime/current")
    public ResponseEntity<ApiResponse<String>> getCurrentDateTime() {
        String currentDateTime = DateTimeUtil.getCurrentDateTimeString();
        return ResponseEntity.ok(ApiResponse.success(currentDateTime));
    }
    
    @PostMapping("/datetime/format")
    public ResponseEntity<ApiResponse<String>> formatDateTime(@RequestBody Map<String, String> request) {
        try {
            String dateTimeString = request.get("dateTime");
            String pattern = request.get("pattern");
            
            LocalDateTime dateTime = DateTimeUtil.parseDateTime(dateTimeString);
            String formatted = DateTimeUtil.formatDateTime(dateTime, pattern);
            
            return ResponseEntity.ok(ApiResponse.success(formatted));
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Error formatting datetime: " + e.getMessage()));
        }
    }
    
    // Encryption Utilities
    @PostMapping("/encryption/hash")
    public ResponseEntity<ApiResponse<String>> hashString(@RequestBody String input) {
        try {
            String hash = EncryptionUtil.hash(input);
            return ResponseEntity.ok(ApiResponse.success(hash));
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Error hashing string: " + e.getMessage()));
        }
    }
    
    @PostMapping("/encryption/generate-random")
    public ResponseEntity<ApiResponse<String>> generateRandomString(@RequestParam int length) {
        String randomString = EncryptionUtil.generateRandomString(length);
        return ResponseEntity.ok(ApiResponse.success(randomString));
    }
    
    // JSON Utilities
    @PostMapping("/json/validate")
    public ResponseEntity<ApiResponse<Boolean>> validateJson(@RequestBody String json) {
        boolean isValid = JsonUtil.isValidJson(json);
        return ResponseEntity.ok(ApiResponse.success("JSON validation result", isValid));
    }
    
    @PostMapping("/json/pretty")
    public ResponseEntity<ApiResponse<String>> prettyJson(@RequestBody String json) {
        try {
            Object obj = JsonUtil.jsonToMap(json);
            String prettyJson = JsonUtil.toPrettyJson(obj);
            return ResponseEntity.ok(ApiResponse.success(prettyJson));
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Error formatting JSON: " + e.getMessage()));
        }
    }
    
    // File Utilities
    @PostMapping("/file/validate")
    public ResponseEntity<ApiResponse<Boolean>> validateFile(@RequestParam("file") MultipartFile file) {
        boolean isValid = FileUtil.isValidFile(file);
        return ResponseEntity.ok(ApiResponse.success("File validation result", isValid));
    }
    
    @PostMapping("/file/generate-filename")
    public ResponseEntity<ApiResponse<String>> generateUniqueFilename(@RequestBody String originalFilename) {
        String uniqueFilename = FileUtil.generateUniqueFilename(originalFilename);
        return ResponseEntity.ok(ApiResponse.success(uniqueFilename));
    }
    
    @GetMapping("/file/format-size")
    public ResponseEntity<ApiResponse<String>> formatFileSize(@RequestParam long bytes) {
        String formattedSize = FileUtil.formatFileSize(bytes);
        return ResponseEntity.ok(ApiResponse.success(formattedSize));
    }
}
