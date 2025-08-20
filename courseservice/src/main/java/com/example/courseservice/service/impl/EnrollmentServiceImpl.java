package com.example.courseservice.service.impl;

import com.example.courseservice.dto.EnrollmentRequestDTO;
import com.example.courseservice.dto.EnrollmentResponseDTO;
import com.example.courseservice.dto.EnrollmentUpdateRequestDTO;
import com.example.courseservice.entity.Enrollment;
import com.example.courseservice.mapper.EnrollmentMapper;
import com.example.courseservice.repository.EnrollmentRepository;
import com.example.courseservice.service.EnrollmentService;
import com.mongodb.DuplicateKeyException;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class EnrollmentServiceImpl implements EnrollmentService {

    private final EnrollmentRepository repository;

    @Override
    public EnrollmentResponseDTO create(EnrollmentRequestDTO request) {
        Enrollment entity = EnrollmentMapper.toEntity(request);
        try {
            entity = repository.save(entity);
        } catch (DuplicateKeyException e) {
            // vi phạm unique index (courseId + userId)
            throw new IllegalStateException("User is already enrolled in this course");
        }
        return EnrollmentMapper.toResponse(entity);
    }

    @Override
    @Transactional(readOnly = true)
    public EnrollmentResponseDTO getById(ObjectId id) {
        Enrollment e = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Enrollment not found"));
        return EnrollmentMapper.toResponse(e);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<EnrollmentResponseDTO> listByCourse(ObjectId courseId, Pageable pageable) {
        return repository.findByCourseId(courseId, pageable)
                .map(EnrollmentMapper::toResponse);
    }

    @Override
    public EnrollmentResponseDTO update(ObjectId id, EnrollmentUpdateRequestDTO request) {
        Enrollment e = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Enrollment not found"));
        EnrollmentMapper.applyUpdate(e, request);
        return EnrollmentMapper.toResponse(repository.save(e));
    }

    @Override
    public void delete(ObjectId id) {
        if (!repository.existsById(id)) {
            throw new IllegalArgumentException("Enrollment not found");
        }
        repository.deleteById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public EnrollmentResponseDTO getByCourseAndUser(ObjectId courseId, String userId) {
        Enrollment e = repository.findByCourseIdAndUserId(courseId, userId)
                .orElseThrow(() -> new IllegalArgumentException("Enrollment not found"));
        return EnrollmentMapper.toResponse(e);
    }

    @Override
    public void unenrollByCourseAndUser(ObjectId courseId, String userId) {
        long count = repository.deleteByCourseIdAndUserId(courseId, userId);
        if (count == 0) {
            throw new IllegalArgumentException("Enrollment not found");
        }
    }
}
