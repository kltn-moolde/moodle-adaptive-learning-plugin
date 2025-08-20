package com.example.courseservice.mapper;

import com.example.courseservice.dto.EnrollmentRequestDTO;
import com.example.courseservice.dto.EnrollmentResponseDTO;
import com.example.courseservice.dto.EnrollmentUpdateRequestDTO;
import com.example.courseservice.entity.Enrollment;
import org.bson.types.ObjectId;

public class EnrollmentMapper {
    public static Enrollment toEntity(EnrollmentRequestDTO req) {
        return Enrollment.builder()
                .courseId(new ObjectId(req.getCourseId()))
                .userId(req.getUserId())
                .fullname(req.getFullname())
                .email(req.getEmail())
                .role(req.getRole())
                .build();
    }

    public static void applyUpdate(Enrollment entity, EnrollmentUpdateRequestDTO req) {
        if (req.getFullname() != null) entity.setFullname(req.getFullname());
        if (req.getEmail() != null) entity.setEmail(req.getEmail());
        if (req.getRole() != null) entity.setRole(req.getRole());
        if (req.getStatus() != null) entity.setStatus(req.getStatus());
    }

    public static EnrollmentResponseDTO toResponse(Enrollment e) {
        return EnrollmentResponseDTO.builder()
                .id(e.getId() != null ? e.getId().toHexString() : null)
                .courseId(e.getCourseId() != null ? e.getCourseId().toHexString() : null)
                .userId(e.getUserId())
                .fullname(e.getFullname())
                .email(e.getEmail())
                .role(e.getRole())
                .status(e.getStatus())
                .enrolledAt(e.getEnrolledAt())
                .build();
    }
}
