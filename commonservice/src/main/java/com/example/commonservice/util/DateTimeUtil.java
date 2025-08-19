package com.example.commonservice.util;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

public class DateTimeUtil {
    
    private static final String DEFAULT_FORMAT = "yyyy-MM-dd HH:mm:ss";
    private static final String DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh";
    private static final DateTimeFormatter DEFAULT_FORMATTER = DateTimeFormatter.ofPattern(DEFAULT_FORMAT);
    
    /**
     * Format LocalDateTime to string with default format
     */
    public static String formatDateTime(LocalDateTime dateTime) {
        if (dateTime == null) return null;
        return dateTime.format(DEFAULT_FORMATTER);
    }
    
    /**
     * Format LocalDateTime to string with custom format
     */
    public static String formatDateTime(LocalDateTime dateTime, String pattern) {
        if (dateTime == null) return null;
        return dateTime.format(DateTimeFormatter.ofPattern(pattern));
    }
    
    /**
     * Parse string to LocalDateTime with default format
     */
    public static LocalDateTime parseDateTime(String dateTimeString) {
        if (dateTimeString == null || dateTimeString.trim().isEmpty()) return null;
        try {
            return LocalDateTime.parse(dateTimeString, DEFAULT_FORMATTER);
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("Invalid date format. Expected: " + DEFAULT_FORMAT, e);
        }
    }
    
    /**
     * Parse string to LocalDateTime with custom format
     */
    public static LocalDateTime parseDateTime(String dateTimeString, String pattern) {
        if (dateTimeString == null || dateTimeString.trim().isEmpty()) return null;
        try {
            return LocalDateTime.parse(dateTimeString, DateTimeFormatter.ofPattern(pattern));
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("Invalid date format. Expected: " + pattern, e);
        }
    }
    
    /**
     * Get current datetime in default timezone
     */
    public static LocalDateTime getCurrentDateTime() {
        return LocalDateTime.now(ZoneId.of(DEFAULT_TIMEZONE));
    }
    
    /**
     * Get current datetime as formatted string
     */
    public static String getCurrentDateTimeString() {
        return formatDateTime(getCurrentDateTime());
    }
    
    /**
     * Check if date is in the past
     */
    public static boolean isPast(LocalDateTime dateTime) {
        return dateTime != null && dateTime.isBefore(getCurrentDateTime());
    }
    
    /**
     * Check if date is in the future
     */
    public static boolean isFuture(LocalDateTime dateTime) {
        return dateTime != null && dateTime.isAfter(getCurrentDateTime());
    }
    
    /**
     * Calculate days between two dates
     */
    public static long daysBetween(LocalDateTime startDate, LocalDateTime endDate) {
        if (startDate == null || endDate == null) return 0;
        return java.time.Duration.between(startDate, endDate).toDays();
    }
}
