package com.example.courseservice.mapper;

import com.example.courseservice.dto.CourseDTO;
import com.example.courseservice.entity.Course;
import org.bson.types.ObjectId;

import java.util.stream.Collectors;

public class CourseMapper {
    public static CourseDTO toDTO(Course course) {
        return CourseDTO.builder()
                .id(course.getId() != null ? course.getId().toHexString() : null)
                .courseCode(course.getCourseCode())
                .title(course.getTitle())
                .sections(course.getSections() != null ?
                        course.getSections().stream().map(section ->
                                CourseDTO.SectionDTO.builder()
                                        .sectionId(section.getSectionId())
                                        .sectionIdOld(section.getSectionIdOld())
                                        .sectionIdNew(section.getSectionIdNew())
                                        .name(section.getName())
                                        .lessons(section.getLessons() != null ? section.getLessons().stream().map(lesson ->
                                                CourseDTO.LessonDTO.builder()
                                                        .sectionIdOld(lesson.getSectionIdOld())
                                                        .sectionIdNew(lesson.getSectionIdNew())
                                                        .name(lesson.getName())
                                                        .resources(lesson.getResources() != null ? lesson.getResources().stream().map(resource ->
                                                                CourseDTO.ResourceDTO.builder()
                                                                        .id(resource.getId())
                                                                        .name(resource.getName())
                                                                        .modname(resource.getModname() != null ? resource.getModname().name() : null)
                                                                        .build()
                                                        ).collect(Collectors.toList()) : null)
                                                        .build()
                                        ).collect(Collectors.toList()) : null)
                                        .resources(section.getResources() != null ? section.getResources().stream().map(resource ->
                                                CourseDTO.ResourceDTO.builder()
                                                        .id(resource.getId())
                                                        .name(resource.getName())
                                                        .modname(resource.getModname() != null ? resource.getModname().name() : null)
                                                        .build()
                                        ).collect(Collectors.toList()) : null)
                                        .build()
                        ).collect(Collectors.toList())
                        : null)
                .build();
    }

    public static Course toEntity(CourseDTO dto) {
        Course course = new Course();

        if (dto.getId() != null) {
            course.setId(new ObjectId(dto.getId()));
        }

        course.setCourseCode(dto.getCourseCode());
        course.setTitle(dto.getTitle());
        course.setSections(dto.getSections() != null ?
                dto.getSections().stream().map(sectionDTO -> {
                    Course.Section section = new Course.Section();
                    section.setSectionId(sectionDTO.getSectionId());
                    section.setSectionIdOld(sectionDTO.getSectionIdOld());
                    section.setSectionIdNew(sectionDTO.getSectionIdNew());
                    section.setName(sectionDTO.getName());

                    if (sectionDTO.getLessons() != null) {
                        section.setLessons(sectionDTO.getLessons().stream().map(lessonDTO -> {
                            Course.Lesson lesson = new Course.Lesson();
                            lesson.setSectionIdOld(lessonDTO.getSectionIdOld());
                            lesson.setSectionIdNew(lessonDTO.getSectionIdNew());
                            lesson.setName(lessonDTO.getName());

                            if (lessonDTO.getResources() != null) {
                                lesson.setResources(lessonDTO.getResources().stream().map(resDTO -> {
                                    Course.Resource res = new Course.Resource();
                                    res.setId(resDTO.getId());
                                    res.setName(resDTO.getName());
                                    if (resDTO.getModname() != null) {
                                        res.setModname(Course.ModName.valueOf(resDTO.getModname().toLowerCase()));
                                    }
                                    return res;
                                }).collect(Collectors.toList()));
                            }

                            return lesson;
                        }).collect(Collectors.toList()));
                    }

                    if (sectionDTO.getResources() != null) {
                        section.setResources(sectionDTO.getResources().stream().map(resDTO -> {
                            Course.Resource res = new Course.Resource();
                            res.setId(resDTO.getId());
                            res.setName(resDTO.getName());
                            if (resDTO.getModname() != null) {
                                res.setModname(Course.ModName.valueOf(resDTO.getModname().toLowerCase()));
                            }
                            return res;
                        }).collect(Collectors.toList()));
                    }

                    return section;
                }).collect(Collectors.toList()) : null
        );

        return course;
    }
}