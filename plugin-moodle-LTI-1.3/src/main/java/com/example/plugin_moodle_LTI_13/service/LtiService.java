package com.example.plugin_moodle_LTI_13.service;

import com.example.plugin_moodle_LTI_13.model.LtiLaunch;
import com.example.plugin_moodle_LTI_13.repository.LtiLaunchRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Date;
import java.util.List;
import java.util.Map;

@Service
public class LtiService {

    @Autowired
    private LtiLaunchRepository ltiLaunchRepository;

    @Value("${jwt.secret}")
    private String jwtSecret;

    @Value("${jwt.expiration}")
    private int jwtExpiration;

    public LtiLaunch processLaunch(Map<String, Object> launchData) {
        System.out.println("launchData: " + launchData);

        // Extract JWT token from launchData
        String idToken = (String) launchData.get("id_token");
        if (idToken == null) {
            throw new RuntimeException("ID token not found in launch data");
        }

        // Decode JWT token to get actual payload
        Map<String, Object> tokenPayload = decodeJwtToken(idToken);
        System.out.println("Decoded token payload: " + tokenPayload);

        // Extract user information from decoded token
        String userId = (String) tokenPayload.get("sub");

        // Extract context information properly
        Map<String, Object> context = (Map<String, Object>) tokenPayload.get("https://purl.imsglobal.org/spec/lti/claim/context");
        String contextId = context != null ? (String) context.get("id") : null;

        // Extract resource link information properly
        Map<String, Object> resourceLink = (Map<String, Object>) tokenPayload.get("https://purl.imsglobal.org/spec/lti/claim/resource_link");
        String resourceLinkId = resourceLink != null ? (String) resourceLink.get("id") : null;

        // Extract user information
        String userName = (String) tokenPayload.get("name");
        String userEmail = (String) tokenPayload.get("email");

        // Extract course information
        String courseId = contextId;
        String courseTitle = context != null ? (String) context.get("title") : null;

        // Extract additional information
        String givenName = (String) tokenPayload.get("given_name");
        String familyName = (String) tokenPayload.get("family_name");
        String resourceTitle = resourceLink != null ? (String) resourceLink.get("title") : null;

        // Extract roles
        List<String> roles = (List<String>) tokenPayload.get("https://purl.imsglobal.org/spec/lti/claim/roles");

        System.out.println("User Id: " + userId);
        System.out.println("Context Id: " + contextId);
        System.out.println("Resource Link Id: " + resourceLinkId);
        System.out.println("User Name: " + userName);
        System.out.println("User Email: " + userEmail);
        System.out.println("Course Id: " + courseId);

        // Create LtiLaunch object
        LtiLaunch launch = new LtiLaunch(userId, contextId, resourceLinkId, userName, userEmail, courseId);

        return ltiLaunchRepository.save(launch);
    }

    // Helper method to decode JWT token
    private Map<String, Object> decodeJwtToken(String idToken) {
        try {
            // Split JWT token into parts
            String[] tokenParts = idToken.split("\\.");
            if (tokenParts.length != 3) {
                throw new RuntimeException("Invalid JWT token format");
            }

            // Decode payload (second part)
            String payload = tokenParts[1];

            // Add padding if needed
            switch (payload.length() % 4) {
                case 2: payload += "=="; break;
                case 3: payload += "="; break;
            }

            // Decode base64
            byte[] decodedBytes = Base64.getDecoder().decode(payload);
            String decodedPayload = new String(decodedBytes, StandardCharsets.UTF_8);

            // Parse JSON
            ObjectMapper objectMapper = new ObjectMapper();
            return objectMapper.readValue(decodedPayload, Map.class);

        } catch (Exception e) {
            throw new RuntimeException("Error decoding JWT token", e);
        }
    }

    public String generateJwtToken(String userId, String courseId) {
        Date expiryDate = new Date(System.currentTimeMillis() + jwtExpiration);

        return Jwts.builder()
                .setSubject(userId)
                .setIssuedAt(new Date())
                .setExpiration(expiryDate)
                .claim("courseId", courseId)
                .signWith(SignatureAlgorithm.HS512, jwtSecret)
                .compact();
    }


    public String getUserIdFromToken(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(jwtSecret)
                .parseClaimsJws(token)
                .getBody();

        return claims.getSubject();
    }

    public String getCourseIdFromToken(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(jwtSecret)
                .parseClaimsJws(token)
                .getBody();

        String courseId = claims.get("courseId", String.class);
        if (courseId == null) {
            throw new RuntimeException("Course ID not found in token");
        }
        return courseId;
    }



    public boolean validateToken(String token) {
        try {
            Jwts.parser().setSigningKey(jwtSecret).parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}