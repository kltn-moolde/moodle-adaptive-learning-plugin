package com.example.commonservice.util;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.util.List;
import java.util.Map;

public class JsonUtil {
    
    private static final ObjectMapper objectMapper;
    
    static {
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }
    
    /**
     * Convert object to JSON string
     */
    public static String toJson(Object object) {
        try {
            return objectMapper.writeValueAsString(object);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting object to JSON", e);
        }
    }
    
    /**
     * Convert object to pretty JSON string
     */
    public static String toPrettyJson(Object object) {
        try {
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(object);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting object to pretty JSON", e);
        }
    }
    
    /**
     * Convert JSON string to object
     */
    public static <T> T fromJson(String json, Class<T> clazz) {
        try {
            return objectMapper.readValue(json, clazz);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting JSON to object", e);
        }
    }
    
    /**
     * Convert JSON string to object with TypeReference
     */
    public static <T> T fromJson(String json, TypeReference<T> typeReference) {
        try {
            return objectMapper.readValue(json, typeReference);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting JSON to object", e);
        }
    }
    
    /**
     * Convert JSON string to Map
     */
    public static Map<String, Object> jsonToMap(String json) {
        return fromJson(json, new TypeReference<Map<String, Object>>() {});
    }
    
    /**
     * Convert JSON string to List
     */
    public static <T> List<T> jsonToList(String json, Class<T> elementClass) {
        try {
            return objectMapper.readValue(json, 
                objectMapper.getTypeFactory().constructCollectionType(List.class, elementClass));
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting JSON to list", e);
        }
    }
    
    /**
     * Convert Map to object
     */
    public static <T> T mapToObject(Map<String, Object> map, Class<T> clazz) {
        return objectMapper.convertValue(map, clazz);
    }
    
    /**
     * Convert object to Map
     */
    public static Map<String, Object> objectToMap(Object object) {
        return objectMapper.convertValue(object, new TypeReference<Map<String, Object>>() {});
    }
    
    /**
     * Check if string is valid JSON
     */
    public static boolean isValidJson(String json) {
        try {
            objectMapper.readTree(json);
            return true;
        } catch (JsonProcessingException e) {
            return false;
        }
    }
    
    /**
     * Merge two JSON objects
     */
    public static String mergeJson(String json1, String json2) {
        try {
            Map<String, Object> map1 = jsonToMap(json1);
            Map<String, Object> map2 = jsonToMap(json2);
            map1.putAll(map2);
            return toJson(map1);
        } catch (Exception e) {
            throw new RuntimeException("Error merging JSON objects", e);
        }
    }
}
