package com.example.courseservice.controller;

import java.util.List;

import com.example.courseservice.dto.CourseDTO;
import org.bson.types.ObjectId;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.courseservice.entity.Course;
import com.example.courseservice.service.CourseService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/courses")
@RequiredArgsConstructor
public class CourseController {

    private final CourseService courseService;

    @GetMapping
    public ResponseEntity<List<CourseDTO>> getAllCourses() {
        return ResponseEntity.ok(courseService.getAllCourses());
    }

    @GetMapping("/{id}")
    public ResponseEntity<CourseDTO> getCourseById(@PathVariable ObjectId id) {
        return ResponseEntity.ok(courseService.getCourseById(id));
    }

    @PostMapping
    public ResponseEntity<CourseDTO> createCourse(@RequestBody CourseDTO course) {
        return ResponseEntity.ok(courseService.createCourse(course));
    }

    @PutMapping("/{id}")
    public ResponseEntity<CourseDTO> updateCourse(@PathVariable ObjectId id, @RequestBody CourseDTO course) {
        return ResponseEntity.ok(courseService.updateCourse(id, course));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCourse(@PathVariable ObjectId id) {
        courseService.deleteCourse(id);
        return ResponseEntity.noContent().build();
    }
}