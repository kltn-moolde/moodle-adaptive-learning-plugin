package com.example.courseservice.service;

import com.example.courseservice.dto.EnrollmentRequestDTO;
import com.example.courseservice.dto.EnrollmentResponseDTO;
import com.example.courseservice.dto.EnrollmentUpdateRequestDTO;
import org.bson.types.ObjectId;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface EnrollmentService {
    EnrollmentResponseDTO create(EnrollmentRequestDTO request);
    EnrollmentResponseDTO getById(ObjectId id);
    Page<EnrollmentResponseDTO> listByCourse(ObjectId courseId, Pageable pageable);
    EnrollmentResponseDTO update(ObjectId id, EnrollmentUpdateRequestDTO request);
    void delete(ObjectId id);

    // tiện ích
    EnrollmentResponseDTO getByCourseAndUser(ObjectId courseId, String userId);
    void unenrollByCourseAndUser(ObjectId courseId, String userId);
}