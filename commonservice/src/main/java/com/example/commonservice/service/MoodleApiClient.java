package com.example.commonservice.service;



import com.example.commonservice.enums.TokenType;

import java.util.List;
import java.util.Map;

/**
 * Interface for Moodle API Client.
 * Defines the contract for interacting with the Moodle Web Service.
 */
public interface MoodleApiClient {
    <T> T callMoodleApi(String wsfunction, Map<String, Object> params, Class<T> responseType, TokenType tokenType) throws Exception;
}