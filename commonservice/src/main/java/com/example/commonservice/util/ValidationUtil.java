package com.example.commonservice.util;

import java.util.Collection;
import java.util.Map;
import java.util.regex.Pattern;

public class ValidationUtil {
    
    private static final String EMAIL_REGEX = "^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\\.[A-Za-z]{2,})$";
    private static final Pattern EMAIL_PATTERN = Pattern.compile(EMAIL_REGEX);
    
    private static final String PHONE_REGEX = "^[0-9+\\-\\s()]+$";
    private static final Pattern PHONE_PATTERN = Pattern.compile(PHONE_REGEX);
    
    /**
     * Check if string is null or empty
     */
    public static boolean isEmpty(String str) {
        return str == null || str.trim().isEmpty();
    }
    
    /**
     * Check if string is not null and not empty
     */
    public static boolean isNotEmpty(String str) {
        return !isEmpty(str);
    }
    
    /**
     * Check if collection is null or empty
     */
    public static boolean isEmpty(Collection<?> collection) {
        return collection == null || collection.isEmpty();
    }
    
    /**
     * Check if collection is not null and not empty
     */
    public static boolean isNotEmpty(Collection<?> collection) {
        return !isEmpty(collection);
    }
    
    /**
     * Check if map is null or empty
     */
    public static boolean isEmpty(Map<?, ?> map) {
        return map == null || map.isEmpty();
    }
    
    /**
     * Check if map is not null and not empty
     */
    public static boolean isNotEmpty(Map<?, ?> map) {
        return !isEmpty(map);
    }
    
    /**
     * Validate email format
     */
    public static boolean isValidEmail(String email) {
        if (isEmpty(email)) return false;
        return EMAIL_PATTERN.matcher(email).matches();
    }
    
    /**
     * Validate phone number format
     */
    public static boolean isValidPhone(String phone) {
        if (isEmpty(phone)) return false;
        return PHONE_PATTERN.matcher(phone).matches();
    }
    
    /**
     * Check if string contains only letters and spaces
     */
    public static boolean isValidName(String name) {
        if (isEmpty(name)) return false;
        return name.matches("^[a-zA-ZÀ-ỹ\\s]+$");
    }
    
    /**
     * Check if string is a valid username (alphanumeric and underscore)
     */
    public static boolean isValidUsername(String username) {
        if (isEmpty(username)) return false;
        return username.matches("^[a-zA-Z0-9_]{3,20}$");
    }
    
    /**
     * Check if password meets minimum requirements
     */
    public static boolean isValidPassword(String password) {
        if (isEmpty(password)) return false;
        // At least 8 characters, contains letter and number
        return password.length() >= 8 && 
               password.matches(".*[a-zA-Z].*") && 
               password.matches(".*\\d.*");
    }
    
    /**
     * Check if string is a valid positive number
     */
    public static boolean isPositiveNumber(String str) {
        if (isEmpty(str)) return false;
        try {
            double number = Double.parseDouble(str);
            return number > 0;
        } catch (NumberFormatException e) {
            return false;
        }
    }
    
    /**
     * Check if string is a valid integer
     */
    public static boolean isValidInteger(String str) {
        if (isEmpty(str)) return false;
        try {
            Integer.parseInt(str);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }
    
    /**
     * Validate if ID is valid (positive long)
     */
    public static boolean isValidId(Long id) {
        return id != null && id > 0;
    }
}
