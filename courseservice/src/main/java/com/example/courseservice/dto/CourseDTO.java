package com.example.courseservice.dto;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CourseDTO {
    private String id;
    private String courseCode;
    private String title;
    private List<SectionDTO> sections;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SectionDTO {
        private Integer sectionId;
        private Integer sectionIdOld;
        private Integer sectionIdNew;
        private String name;
        private List<LessonDTO> lessons;
        private List<ResourceDTO> resources;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonDTO {
        private Integer sectionIdOld;
        private Integer sectionIdNew;
        private String name;
        private List<ResourceDTO> resources;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResourceDTO {
        private Integer id;
        private String name;
        private String modname; // giữ kiểu String để dễ map
    }
}