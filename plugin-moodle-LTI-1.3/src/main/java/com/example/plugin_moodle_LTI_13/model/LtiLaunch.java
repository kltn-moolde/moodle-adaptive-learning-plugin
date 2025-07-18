package com.example.plugin_moodle_LTI_13.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "lti_launches")
public class LtiLaunch {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private String userId;

    @Column(name = "context_id")
    private String contextId;

    @Column(name = "resource_link_id")
    private String resourceLinkId;

    @Column(name = "launch_time")
    private LocalDateTime launchTime;

    @Column(name = "user_name")
    private String userName;

    @Column(name = "user_email")
    private String userEmail;

    @Column(name = "course_id")
    private String courseId;

    // Constructors
    public LtiLaunch() {}

    public LtiLaunch(String userId, String contextId, String resourceLinkId,
                     String userName, String userEmail, String courseId) {
        this.userId = userId;
        this.contextId = contextId;
        this.resourceLinkId = resourceLinkId;
        this.userName = userName;
        this.userEmail = userEmail;
        this.courseId = courseId;
        this.launchTime = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getContextId() { return contextId; }
    public void setContextId(String contextId) { this.contextId = contextId; }

    public String getResourceLinkId() { return resourceLinkId; }
    public void setResourceLinkId(String resourceLinkId) { this.resourceLinkId = resourceLinkId; }

    public LocalDateTime getLaunchTime() { return launchTime; }
    public void setLaunchTime(LocalDateTime launchTime) { this.launchTime = launchTime; }

    public String getUserName() { return userName; }
    public void setUserName(String userName) { this.userName = userName; }

    public String getUserEmail() { return userEmail; }
    public void setUserEmail(String userEmail) { this.userEmail = userEmail; }

    public String getCourseId() { return courseId; }
    public void setCourseId(String courseId) { this.courseId = courseId; }
}