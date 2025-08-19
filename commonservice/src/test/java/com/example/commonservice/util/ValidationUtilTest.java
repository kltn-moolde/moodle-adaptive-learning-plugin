package com.example.commonservice.util;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ValidationUtilTest {
    
    @Test
    void testIsValidEmail() {
        assertTrue(ValidationUtil.isValidEmail("user@example.com"));
        assertTrue(ValidationUtil.isValidEmail("test.email@domain.org"));
        assertFalse(ValidationUtil.isValidEmail("invalid-email"));
        assertFalse(ValidationUtil.isValidEmail("@domain.com"));
        assertFalse(ValidationUtil.isValidEmail("user@"));
        assertFalse(ValidationUtil.isValidEmail(""));
        assertFalse(ValidationUtil.isValidEmail(null));
    }
    
    @Test
    void testIsValidPassword() {
        assertTrue(ValidationUtil.isValidPassword("password123"));
        assertTrue(ValidationUtil.isValidPassword("MyPass456"));
        assertFalse(ValidationUtil.isValidPassword("password")); // no number
        assertFalse(ValidationUtil.isValidPassword("12345678")); // no letter
        assertFalse(ValidationUtil.isValidPassword("pass1")); // too short
        assertFalse(ValidationUtil.isValidPassword(""));
        assertFalse(ValidationUtil.isValidPassword(null));
    }
    
    @Test
    void testIsEmpty() {
        assertTrue(ValidationUtil.isEmpty(""));
        assertTrue(ValidationUtil.isEmpty("   "));
        assertTrue(ValidationUtil.isEmpty(null));
        assertFalse(ValidationUtil.isEmpty("text"));
        assertFalse(ValidationUtil.isEmpty(" text "));
    }
    
    @Test
    void testIsValidUsername() {
        assertTrue(ValidationUtil.isValidUsername("user123"));
        assertTrue(ValidationUtil.isValidUsername("test_user"));
        assertFalse(ValidationUtil.isValidUsername("us")); // too short
        assertFalse(ValidationUtil.isValidUsername("user@name")); // invalid char
        assertFalse(ValidationUtil.isValidUsername(""));
        assertFalse(ValidationUtil.isValidUsername(null));
    }
}
