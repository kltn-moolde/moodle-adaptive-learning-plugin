# Common Service - Utilities for Adaptive Learning System

## Mô tả
Common Service cung cấp các utilities và functions chung cho hệ thống microservice học tăng cường, bao gồm:

- **String Utilities**: Xử lý chuỗi, slug, mask data, tên viết hoa, v.v.
- **Validation Utilities**: Validate email, phone, password, username, v.v.
- **DateTime Utilities**: Xử lý ngày tháng, format, parse, timezone
- **Encryption Utilities**: Hash, encrypt/decrypt, random generation
- **JSON Utilities**: Parse, validate, format JSON
- **File Utilities**: Validate file, generate filename, format size
- **Collection Utilities**: Xử lý collections, set operations, partitioning

## Cấu trúc dự án

```
src/main/java/com/example/commonservice/
├── config/                 # Cấu hình Spring
├── controller/             # REST controllers để expose utilities
├── dto/                    # Data Transfer Objects
├── exception/              # Exception handlers
├── model/                  # Entity models
└── util/                   # Utility classes (chính)
    ├── StringUtil.java     # String processing utilities
    ├── ValidationUtil.java # Validation utilities
    ├── DateTimeUtil.java   # DateTime utilities
    ├── EncryptionUtil.java # Encryption & security utilities
    ├── JsonUtil.java       # JSON processing utilities
    ├── FileUtil.java       # File processing utilities
    ├── CollectionUtil.java # Collection utilities
    └── JwtUtil.java        # JWT utilities
```

## API Endpoints

### Health Check
- `GET /api/common/health` - Health check

### String Utilities
- `POST /api/common/string/to-slug` - Convert string to URL-friendly slug
- `POST /api/common/string/to-title-case` - Convert to title case
- `POST /api/common/string/mask-email` - Mask email for privacy
- `POST /api/common/string/get-initials` - Get initials from full name

### Validation Utilities
- `POST /api/common/validate/email` - Validate email format
- `POST /api/common/validate/phone` - Validate phone number
- `POST /api/common/validate/password` - Validate password strength

### DateTime Utilities
- `GET /api/common/datetime/current` - Get current datetime
- `POST /api/common/datetime/format` - Format datetime with custom pattern

### Encryption Utilities
- `POST /api/common/encryption/hash` - Hash string using SHA-256
- `POST /api/common/encryption/generate-random` - Generate random string

### JSON Utilities
- `POST /api/common/json/validate` - Validate JSON format
- `POST /api/common/json/pretty` - Format JSON with pretty print

### File Utilities
- `POST /api/common/file/validate` - Validate uploaded file
- `POST /api/common/file/generate-filename` - Generate unique filename
- `GET /api/common/file/format-size` - Format file size for display

## Utility Classes

### 1. StringUtil
```java
// Chuyển thành slug URL-friendly
String slug = StringUtil.toSlug("Học Tăng Cường"); // "hoc-tang-cuong"

// Viết hoa chữ cái đầu
String title = StringUtil.toTitleCase("nguyễn văn a"); // "Nguyễn Văn A"

// Mask email
String masked = StringUtil.maskEmail("user@example.com"); // "u**r@example.com"

// Lấy initials
String initials = StringUtil.getInitials("Nguyễn Văn A"); // "NVA"
```

### 2. ValidationUtil
```java
// Validate email
boolean isValid = ValidationUtil.isValidEmail("user@example.com");

// Validate password (min 8 chars, có chữ và số)
boolean isStrong = ValidationUtil.isValidPassword("password123");

// Check empty
boolean isEmpty = ValidationUtil.isEmpty(someString);
```

### 3. DateTimeUtil
```java
// Current datetime
String now = DateTimeUtil.getCurrentDateTimeString();

// Format datetime
String formatted = DateTimeUtil.formatDateTime(dateTime, "dd/MM/yyyy HH:mm");

// Parse datetime
LocalDateTime parsed = DateTimeUtil.parseDateTime("2025-08-19 10:30:00");
```

### 4. EncryptionUtil
```java
// Hash string
String hash = EncryptionUtil.hash("password");

// Generate random string
String random = EncryptionUtil.generateRandomString(10);

// Encrypt/Decrypt
SecretKey key = EncryptionUtil.generateKey();
String encrypted = EncryptionUtil.encrypt("text", key);
String decrypted = EncryptionUtil.decrypt(encrypted, key);
```

### 5. JsonUtil
```java
// Object to JSON
String json = JsonUtil.toJson(object);

// JSON to Object
User user = JsonUtil.fromJson(json, User.class);

// Pretty JSON
String pretty = JsonUtil.toPrettyJson(object);

// Validate JSON
boolean isValid = JsonUtil.isValidJson(jsonString);
```

### 6. FileUtil
```java
// Validate file
boolean isValid = FileUtil.isValidFile(multipartFile);

// Generate unique filename
String filename = FileUtil.generateUniqueFilename("document.pdf");

// Format file size
String size = FileUtil.formatFileSize(1024000); // "1.0 MB"
```

### 7. CollectionUtil
```java
// Remove duplicates
List<String> unique = CollectionUtil.removeDuplicates(list);

// Get random elements
List<String> random = CollectionUtil.getRandomElements(collection, 5);

// Set operations
Set<String> intersection = CollectionUtil.intersection(set1, set2);
Set<String> union = CollectionUtil.union(set1, set2);
```

## Cấu hình

### Database (Optional)
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/adaptive_learning_common
spring.datasource.username=your_username
spring.datasource.password=your_password
```

### Common Settings
```properties
common.date.format=yyyy-MM-dd HH:mm:ss
common.timezone=Asia/Ho_Chi_Minh
common.file.upload.max-size=10MB
common.encryption.algorithm=AES
```

## Chạy ứng dụng

```bash
./mvnw spring-boot:run
```

Service sẽ chạy trên port 8080.

## Sử dụng trong các microservice khác

Các microservice khác có thể:
1. **Gọi qua HTTP API**: Sử dụng REST API endpoints
2. **Import utilities trực tiếp**: Copy các util classes vào project
3. **Dependency injection**: Include as library dependency

## Dependencies chính

- Spring Boot 3.5.4
- Spring Boot Starter Web
- Spring Boot Starter Data JPA
- Spring Boot Starter Validation
- MySQL Connector
- Jackson (JSON processing)

## Best Practices

- Tất cả utilities đều static methods, không cần instantiate
- Error handling được xử lý trong từng method
- Support Vietnamese characters (diacritics)
- Thread-safe implementations
- Null-safe operations
- Comprehensive validation

## Mở rộng

Có thể dễ dàng thêm các utility classes mới:
- **EmailUtil**: Gửi email
- **CacheUtil**: Cache operations
- **LogUtil**: Logging utilities
- **ConfigUtil**: Configuration management
