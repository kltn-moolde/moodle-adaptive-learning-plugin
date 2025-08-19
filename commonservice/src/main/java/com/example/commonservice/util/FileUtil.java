package com.example.commonservice.util;

import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.List;

public class FileUtil {
    
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    private static final List<String> ALLOWED_EXTENSIONS = List.of(
        "jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "xls", "xlsx", "txt", "csv"
    );
    
    /**
     * Check if file extension is allowed
     */
    public static boolean isAllowedExtension(String filename) {
        if (ValidationUtil.isEmpty(filename)) return false;
        
        String extension = getFileExtension(filename).toLowerCase();
        return ALLOWED_EXTENSIONS.contains(extension);
    }
    
    /**
     * Get file extension from filename
     */
    public static String getFileExtension(String filename) {
        if (ValidationUtil.isEmpty(filename)) return "";
        
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == filename.length() - 1) {
            return "";
        }
        
        return filename.substring(lastDotIndex + 1);
    }
    
    /**
     * Get filename without extension
     */
    public static String getFilenameWithoutExtension(String filename) {
        if (ValidationUtil.isEmpty(filename)) return "";
        
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1) {
            return filename;
        }
        
        return filename.substring(0, lastDotIndex);
    }
    
    /**
     * Validate uploaded file
     */
    public static boolean isValidFile(MultipartFile file) {
        if (file == null || file.isEmpty()) return false;
        
        // Check file size
        if (file.getSize() > MAX_FILE_SIZE) return false;
        
        // Check file extension
        return isAllowedExtension(file.getOriginalFilename());
    }
    
    /**
     * Generate unique filename
     */
    public static String generateUniqueFilename(String originalFilename) {
        String extension = getFileExtension(originalFilename);
        String nameWithoutExt = getFilenameWithoutExtension(originalFilename);
        String timestamp = String.valueOf(System.currentTimeMillis());
        
        return nameWithoutExt + "_" + timestamp + "." + extension;
    }
    
    /**
     * Save uploaded file to directory
     */
    public static String saveFile(MultipartFile file, String uploadDir) throws IOException {
        if (!isValidFile(file)) {
            throw new IllegalArgumentException("Invalid file");
        }
        
        // Create directory if not exists
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }
        
        // Generate unique filename
        String filename = generateUniqueFilename(file.getOriginalFilename());
        Path filePath = uploadPath.resolve(filename);
        
        // Save file
        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
        
        return filename;
    }
    
    /**
     * Delete file
     */
    public static boolean deleteFile(String filePath) {
        try {
            Path path = Paths.get(filePath);
            return Files.deleteIfExists(path);
        } catch (IOException e) {
            return false;
        }
    }
    
    /**
     * Read file content as string
     */
    public static String readFileAsString(String filePath) throws IOException {
        return Files.readString(Paths.get(filePath));
    }
    
    /**
     * Write string to file
     */
    public static void writeStringToFile(String content, String filePath) throws IOException {
        Files.write(Paths.get(filePath), content.getBytes());
    }
    
    /**
     * Get file size in bytes
     */
    public static long getFileSize(String filePath) throws IOException {
        return Files.size(Paths.get(filePath));
    }
    
    /**
     * Check if file exists
     */
    public static boolean fileExists(String filePath) {
        return Files.exists(Paths.get(filePath));
    }
    
    /**
     * List files in directory
     */
    public static List<String> listFiles(String directoryPath) throws IOException {
        List<String> fileList = new ArrayList<>();
        
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get(directoryPath))) {
            for (Path entry : stream) {
                if (Files.isRegularFile(entry)) {
                    fileList.add(entry.getFileName().toString());
                }
            }
        }
        
        return fileList;
    }
    
    /**
     * Format file size for display
     */
    public static String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.1f GB", bytes / (1024.0 * 1024 * 1024));
    }
}
