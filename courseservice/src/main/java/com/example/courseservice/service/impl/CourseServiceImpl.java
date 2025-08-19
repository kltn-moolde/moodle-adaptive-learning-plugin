package com.example.courseservice.service.impl;

import java.util.List;
import java.util.stream.Collectors;

import com.example.courseservice.mapper.CourseMapper;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;

import com.example.courseservice.dto.CourseDTO;
import com.example.courseservice.entity.Course;
import com.example.courseservice.repository.CourseRepository;
import com.example.courseservice.service.CourseService;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CourseServiceImpl implements CourseService {

    private final CourseRepository courseRepository;

    @Override
    public List<CourseDTO> getAllCourses() {
        return courseRepository.findAll()
                .stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public CourseDTO getCourseById(ObjectId id) {
        Course course = courseRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Course not found with id: " + id));
        return mapToDTO(course);
    }

    @Override
    public CourseDTO createCourse(CourseDTO courseDTO) {
        Course course = mapToEntity(courseDTO);
        Course saved = courseRepository.save(course);
        return mapToDTO(saved);
    }

    @Override
    public CourseDTO updateCourse(ObjectId id, CourseDTO courseDTO) {
        Course existing = courseRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Course not found with id: " + id));

        existing.setCourseCode(courseDTO.getCourseCode());
        existing.setTitle(courseDTO.getTitle());
        existing.setSections(mapToEntity(courseDTO).getSections());

        Course saved = courseRepository.save(existing);
        return mapToDTO(saved);
    }

    @Override
    public void deleteCourse(ObjectId id) {
        courseRepository.deleteById(id);
    }

    // ------------ Mapper methods ------------

    private CourseDTO mapToDTO(Course course) {
        return CourseMapper.toDTO(course);
    }

    private Course mapToEntity(CourseDTO dto) {
        return CourseMapper.toEntity(dto);
    }
}