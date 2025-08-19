package com.example.courseservice.repository;

import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.example.courseservice.entity.Course;

@Repository
public interface CourseRepository extends MongoRepository<Course, ObjectId> {
    // có thể thêm query method nếu cần, ví dụ:
    Course findByCourseCode(String courseCode);
}