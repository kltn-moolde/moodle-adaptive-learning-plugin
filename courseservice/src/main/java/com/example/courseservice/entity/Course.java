package com.example.courseservice.entity;

import java.util.List;

import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
@Document(collection = "courses")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Course {

    @Id
    private ObjectId id;

    /** Optional human-readable code, e.g. "CS-12" */
    @Indexed(unique = true, sparse = true)
    @Field("courseCode")
    private String courseCode;

    /** Display title of the course */
    @Field("title")
    private String title;

    @Field("sections")
    private List<Section> sections;
    @Data
    public static class Section {
        /** Some payloads use "sectionid" (lowercase) */
        @Field("sectionid")
        private Integer sectionId; // e.g., 33 for General

        /** Legacy mapping fields present in your data */
        @Field("sectionId_old")
        private Integer sectionIdOld; // e.g., 34, 35

        @Field("sectionId_new")
        private Integer sectionIdNew; // e.g., 38, 39, 40

        @Field("name")
        private String name; // e.g., "General" or "Chủ đề 1: ..."

        @Field("lessons")
        private List<Lesson> lessons; // can be null/empty for "General"

        @Field("resources")
        private List<Resource> resources; // used directly by "General" section

    }
    @Data
    public static class Lesson {
        @Field("sectionId_old")
        private Integer sectionIdOld;

        @Field("sectionId_new")
        private Integer sectionIdNew;

        @Field("name")
        private String name;

        @Field("resources")
        private List<Resource> resources;
    }
    @Data
    public static class Resource {
        @Field("id")
        private Integer id; // e.g., 52, 60...

        @Field("name")
        private String name; // e.g., "Announcements"

        @Field("modname")
        private ModName modname; // e.g., forum, quiz, hvp
    }

    /**
     * Kept lowercase to match your JSON values so Spring stores/reads them as-is.
     */
    public enum ModName {
        forum,
        qbank,
        quiz,
        resource,
        hvp
    }
}
