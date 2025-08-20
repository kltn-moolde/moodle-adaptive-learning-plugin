package com.example.courseservice.dto;
import lombok.*;

import java.time.Instant;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnrollmentResponseDTO {
    private String id;
    private String courseId;
    private String userId;
    private String fullname;
    private String email;
    private String role;
    private String status;
    private Instant enrolledAt;
}
