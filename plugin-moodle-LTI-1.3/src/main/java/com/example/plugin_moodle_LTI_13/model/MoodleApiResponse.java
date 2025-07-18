package com.example.plugin_moodle_LTI_13.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class MoodleApiResponse {
    @JsonProperty("logs")
    private List<UserLog> logs;

    @JsonProperty("exception")
    private String exception;

    @JsonProperty("errorcode")
    private String errorCode;

    @JsonProperty("message")
    private String message;

    // Constructors
    public MoodleApiResponse() {}

    // Getters and Setters
    public List<UserLog> getLogs() { return logs; }
    public void setLogs(List<UserLog> logs) { this.logs = logs; }

    public String getException() { return exception; }
    public void setException(String exception) { this.exception = exception; }

    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}