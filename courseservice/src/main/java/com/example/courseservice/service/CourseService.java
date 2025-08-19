package com.example.courseservice.service;

import java.util.List;

import org.bson.types.ObjectId;

import com.example.courseservice.dto.CourseDTO;

public interface CourseService {
    List<CourseDTO> getAllCourses();
    CourseDTO getCourseById(ObjectId id);
    CourseDTO createCourse(CourseDTO courseDTO);
    CourseDTO updateCourse(ObjectId id, CourseDTO courseDTO);
    void deleteCourse(ObjectId id);
}