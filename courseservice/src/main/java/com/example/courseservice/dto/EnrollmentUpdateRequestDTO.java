package com.example.courseservice.dto;

import jakarta.validation.constraints.Email;
import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnrollmentUpdateRequestDTO {
    private String fullname;
    @Email
    private String email;
    private String role;
    private String status; // active|suspended|completed
}
