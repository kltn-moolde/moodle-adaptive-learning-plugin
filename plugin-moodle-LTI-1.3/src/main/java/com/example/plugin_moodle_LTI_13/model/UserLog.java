package com.example.plugin_moodle_LTI_13.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;

@JsonIgnoreProperties(ignoreUnknown = true)
public class UserLog {

    @JsonProperty("id")
    private Long id;

    @JsonProperty("userid")
    private Long userId;

    @JsonProperty("username")
    private String username;

    @JsonProperty("eventname")
    private String eventName;

    @JsonProperty("action")
    private String action;

    @JsonProperty("target")
    private String target;

    @JsonProperty("component")
    private String component;

    @JsonProperty("timecreated")
    private Long timeCreated;

    // Constructors
    public UserLog() {}

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEventName() { return eventName; }
    public void setEventName(String eventName) { this.eventName = eventName; }

    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }

    public String getTarget() { return target; }
    public void setTarget(String target) { this.target = target; }

    public String getComponent() { return component; }
    public void setComponent(String component) { this.component = component; }

    public Long getTimeCreated() { return timeCreated; }
    public void setTimeCreated(Long timeCreated) { this.timeCreated = timeCreated; }

    public LocalDateTime getDateTime() {
        return timeCreated != null ? LocalDateTime.ofEpochSecond(timeCreated, 0, java.time.ZoneOffset.UTC) : null;
    }
}
