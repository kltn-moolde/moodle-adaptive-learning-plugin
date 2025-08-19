package com.example.commonservice.util;

import java.text.Normalizer;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class StringUtil {
    
    private static final Pattern DIACRITICS_PATTERN = Pattern.compile("\\p{InCombiningDiacriticalMarks}+");
    
    /**
     * Convert string to slug (URL friendly)
     */
    public static String toSlug(String input) {
        if (ValidationUtil.isEmpty(input)) return "";
        
        // Normalize Vietnamese characters
        String normalized = Normalizer.normalize(input, Normalizer.Form.NFD);
        String withoutDiacritics = DIACRITICS_PATTERN.matcher(normalized).replaceAll("");
        
        // Replace special characters and spaces with hyphens
        return withoutDiacritics.toLowerCase()
                .replaceAll("[^a-z0-9\\s-]", "")
                .replaceAll("\\s+", "-")
                .replaceAll("-+", "-")
                .replaceAll("^-|-$", "");
    }
    
    /**
     * Capitalize first letter of each word
     */
    public static String toTitleCase(String input) {
        if (ValidationUtil.isEmpty(input)) return "";
        
        return Arrays.stream(input.split("\\s+"))
                .map(word -> word.substring(0, 1).toUpperCase() + word.substring(1).toLowerCase())
                .collect(Collectors.joining(" "));
    }
    
    /**
     * Capitalize first letter only
     */
    public static String capitalize(String input) {
        if (ValidationUtil.isEmpty(input)) return "";
        
        return input.substring(0, 1).toUpperCase() + input.substring(1).toLowerCase();
    }
    
    /**
     * Remove Vietnamese diacritics
     */
    public static String removeDiacritics(String input) {
        if (ValidationUtil.isEmpty(input)) return "";
        
        String normalized = Normalizer.normalize(input, Normalizer.Form.NFD);
        return DIACRITICS_PATTERN.matcher(normalized).replaceAll("");
    }
    
    /**
     * Truncate string to specified length with ellipsis
     */
    public static String truncate(String input, int maxLength) {
        if (ValidationUtil.isEmpty(input) || maxLength <= 0) return "";
        if (input.length() <= maxLength) return input;
        
        return input.substring(0, maxLength - 3) + "...";
    }
    
    /**
     * Mask sensitive information (like email, phone)
     */
    public static String maskEmail(String email) {
        if (!ValidationUtil.isValidEmail(email)) return email;
        
        String[] parts = email.split("@");
        String username = parts[0];
        String domain = parts[1];
        
        if (username.length() <= 2) {
            return "*".repeat(username.length()) + "@" + domain;
        }
        
        return username.charAt(0) + "*".repeat(username.length() - 2) + 
               username.charAt(username.length() - 1) + "@" + domain;
    }
    
    /**
     * Mask phone number
     */
    public static String maskPhone(String phone) {
        if (ValidationUtil.isEmpty(phone) || phone.length() < 4) return phone;
        
        int visibleDigits = 2;
        int maskedLength = phone.length() - (visibleDigits * 2);
        
        return phone.substring(0, visibleDigits) + 
               "*".repeat(maskedLength) + 
               phone.substring(phone.length() - visibleDigits);
    }
    
    /**
     * Generate initials from full name
     */
    public static String getInitials(String fullName) {
        if (ValidationUtil.isEmpty(fullName)) return "";
        
        return Arrays.stream(fullName.split("\\s+"))
                .filter(word -> !word.isEmpty())
                .map(word -> word.substring(0, 1).toUpperCase())
                .collect(Collectors.joining());
    }
    
    /**
     * Count words in text
     */
    public static int countWords(String text) {
        if (ValidationUtil.isEmpty(text)) return 0;
        
        return text.trim().split("\\s+").length;
    }
    
    /**
     * Extract numbers from string
     */
    public static List<String> extractNumbers(String input) {
        if (ValidationUtil.isEmpty(input)) return List.of();
        
        return Arrays.stream(input.split("\\D+"))
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList());
    }
    
    /**
     * Check if string contains only digits
     */
    public static boolean isNumeric(String input) {
        if (ValidationUtil.isEmpty(input)) return false;
        return input.matches("\\d+");
    }
    
    /**
     * Reverse string
     */
    public static String reverse(String input) {
        if (ValidationUtil.isEmpty(input)) return "";
        return new StringBuilder(input).reverse().toString();
    }
    
    /**
     * Generate random string with specified length and characters
     */
    public static String generateRandom(int length, String characters) {
        if (length <= 0 || ValidationUtil.isEmpty(characters)) return "";
        
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < length; i++) {
            int index = (int) (Math.random() * characters.length());
            result.append(characters.charAt(index));
        }
        return result.toString();
    }
    
    /**
     * Join collection with delimiter
     */
    public static String join(Iterable<?> elements, String delimiter) {
        if (elements == null) return "";
        
        return elements.toString().replaceAll("^\\[|\\]$", "").replace(", ", delimiter);
    }
    
    /**
     * Pad string to specified length
     */
    public static String padLeft(String input, int length, char padChar) {
        if (input == null) input = "";
        if (input.length() >= length) return input;
        
        return String.valueOf(padChar).repeat(length - input.length()) + input;
    }
    
    public static String padRight(String input, int length, char padChar) {
        if (input == null) input = "";
        if (input.length() >= length) return input;
        
        return input + String.valueOf(padChar).repeat(length - input.length());
    }
}
