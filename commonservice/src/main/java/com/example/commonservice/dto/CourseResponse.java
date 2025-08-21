package com.example.commonservice.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class CourseResponse {
    private int id;
    private String shortname;
    private String fullname;
    private String displayname;
    private String idnumber;

    private int categoryid;
    private String format;

    private long startdate;
    private long enddate;

    private int visible;
    private int numsections;

    private long timecreated;
    private long timemodified;

    private int enablecompletion;

    private List<CourseFormatOption> courseformatoptions;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CourseFormatOption {
        private String name;
        private Object value;
    }
}