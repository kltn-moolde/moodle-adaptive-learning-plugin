package com.example.courseservice.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.*;


@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnrollmentRequestDTO {
    @NotBlank
    private String courseId; // ObjectId dạng string

    @NotBlank
    private String userId;

    @NotBlank
    private String fullname;

    @Email
    @NotBlank
    private String email;

    @NotBlank
    private String role; // student, editingteacher, ...
}
