package com.example.commonservice.util;

import java.util.HashMap;
import java.util.Map;

public class MoodleParams {
    private final Map<String, Object> params = new HashMap<>();
    private int criteriaIndex = 0;

    public static MoodleParams create() {
        return new MoodleParams();
    }

    public MoodleParams criteria(String key, String value) {
        params.put("criteria[" + criteriaIndex + "][key]", key);
        params.put("criteria[" + criteriaIndex + "][value]", value);
        criteriaIndex++;
        return this;
    }

    public MoodleParams add(String key, Object value) {
        params.put(key, value);
        return this;
    }

    public Map<String, Object> build() {
        return params;
    }
}