package com.example.courseservice.entity;

import lombok.Builder;
import org.springframework.data.annotation.CreatedDate;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.Instant;
@Document(collection = "courses")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Enrollment {
    @Id
    private ObjectId id;

    // Tham chiếu đến Course nội bộ (Mongo _id của Course)
    private ObjectId courseId;

    // ID người dùng từ hệ thống ngoài (Moodle) hoặc user-service. Để String cho linh hoạt
    private String userId;

    private String fullname;
    private String email;

    // student | editingteacher | teacher | ta ...
    private String role;

    // active | suspended | completed (tùy nhu cầu)
    @Builder.Default
    private String status = "active";

    @CreatedDate
    private Instant enrolledAt;
}
