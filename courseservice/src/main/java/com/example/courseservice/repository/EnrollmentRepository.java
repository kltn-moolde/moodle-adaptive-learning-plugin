package com.example.courseservice.repository;

import com.example.courseservice.entity.Enrollment;
import org.bson.types.ObjectId;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface EnrollmentRepository extends MongoRepository<Enrollment, ObjectId> {
    Page<Enrollment> findByCourseId(ObjectId courseId, Pageable pageable);
    Optional<Enrollment> findByCourseIdAndUserId(ObjectId courseId, String userId);
    long deleteByCourseIdAndUserId(ObjectId courseId, String userId);
}
