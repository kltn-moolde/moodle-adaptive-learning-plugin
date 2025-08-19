package com.example.commonservice.util;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class StringUtilTest {
    
    @Test
    void testToSlug() {
        assertEquals("hoc-tang-cuong", StringUtil.toSlug("Học Tăng Cường"));
        assertEquals("spring-boot-java", StringUtil.toSlug("Spring Boot & Java"));
        assertEquals("", StringUtil.toSlug(""));
        assertEquals("", StringUtil.toSlug(null));
    }
    
    @Test
    void testToTitleCase() {
        assertEquals("Nguyễn Văn A", StringUtil.toTitleCase("nguyễn văn a"));
        assertEquals("Spring Boot", StringUtil.toTitleCase("spring boot"));
        assertEquals("", StringUtil.toTitleCase(""));
    }
    
    @Test
    void testMaskEmail() {
        assertEquals("u**r@example.com", StringUtil.maskEmail("user@example.com"));
        assertEquals("a**n@test.org", StringUtil.maskEmail("admin@test.org"));
        assertEquals("ab@test.com", StringUtil.maskEmail("ab@test.com"));
    }
    
    @Test
    void testGetInitials() {
        assertEquals("NVA", StringUtil.getInitials("Nguyễn Văn A"));
        assertEquals("JD", StringUtil.getInitials("John Doe"));
        assertEquals("", StringUtil.getInitials(""));
        assertEquals("", StringUtil.getInitials(null));
    }
}
