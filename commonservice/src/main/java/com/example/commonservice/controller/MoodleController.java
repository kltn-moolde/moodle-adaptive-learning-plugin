package com.example.commonservice.controller;

import com.example.commonservice.dto.CourseResponse;
import com.example.commonservice.enums.TokenType;
import com.example.commonservice.service.MoodleApiClient;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/moodle")
public class MoodleController {

    private final MoodleApiClient moodleApiClient;

    @GetMapping("/courses")
    public List<CourseResponse> getCourses() throws Exception {
        // Gọi API Moodle
        CourseResponse[] courses = moodleApiClient.callMoodleApi(
                "core_course_get_courses",
                null,
                CourseResponse[].class,
                TokenType.SYSTEM
        );

        return Arrays.asList(courses);
    }
}