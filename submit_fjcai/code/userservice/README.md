# User Service API

User Service quản lý thông tin người dùng và phân quyền trong hệ thống Moodle Adaptive Learning Plugin.

## Công nghệ sử dụng
- Spring Boot 3.5.4
- PostgreSQL (Neon Database)
- JPA/Hibernate
- Lombok
- Maven

## Cấu trúc Database

### Bảng ROLES
```sql
- id (BIGSERIAL PRIMARY KEY)
- role_name (VARCHAR(50) NOT NULL UNIQUE)
- description (VARCHAR(255))
- create_at (TIMESTAMP)
- update_at (TIMESTAMP)
- delete_at (TIMESTAMP)
```

### Bảng USERS
```sql
- id (BIGSERIAL PRIMARY KEY)
- external_id (VARCHAR(100) UNIQUE)
- email (VARCHAR(255) NOT NULL UNIQUE)
- name (VARCHAR(255) NOT NULL)
- avatar_url (VARCHAR(500))
- role_id (BIGINT NOT NULL)
- create_at (TIMESTAMP)
- update_at (TIMESTAMP)
- delete_at (TIMESTAMP)
```

## Cài đặt và Chạy

### 1. Cấu hình Database
Cập nhật file `application.properties` với thông tin Neon database của bạn:
```properties
spring.datasource.url=jdbc:postgresql://your-neon-host:5432/your-database-name
spring.datasource.username=your-username
spring.datasource.password=your-password
```

### 2. Tạo Database Schema
Chạy file `schema.sql` để tạo bảng:
```sql
-- Chạy nội dung file src/main/resources/schema.sql
```

### 3. Insert Dữ liệu mẫu
Chạy file `data.sql` để thêm dữ liệu mẫu:
```sql
-- Chạy nội dung file src/main/resources/data.sql
```

### 4. Chạy ứng dụng
```bash
mvn spring-boot:run
```

Ứng dụng sẽ chạy trên: `http://localhost:8081`

## API Endpoints

### Role APIs

#### 1. Lấy tất cả roles
```
GET /api/roles
Response: List<RoleDTO>
```

#### 2. Lấy role theo ID
```
GET /api/roles/{id}
Response: RoleDTO
```

#### 3. Lấy role theo tên
```
GET /api/roles/name/{roleName}
Response: RoleDTO
```

#### 4. Tạo role mới
```
POST /api/roles
Body: {
  "roleName": "NEW_ROLE",
  "description": "Description of new role"
}
Response: RoleDTO
```

#### 5. Cập nhật role
```
PUT /api/roles/{id}
Body: {
  "roleName": "UPDATED_ROLE",
  "description": "Updated description"
}
Response: RoleDTO
```

#### 6. Xóa role (soft delete)
```
DELETE /api/roles/{id}
Response: 204 No Content
```

#### 7. Kiểm tra role tồn tại
```
GET /api/roles/exists/{roleName}
Response: boolean
```

### User APIs

#### 1. Lấy tất cả users
```
GET /api/users
Response: List<UserDTO>
```

#### 2. Lấy user theo ID
```
GET /api/users/{id}
Response: UserDTO
```

#### 3. Lấy user theo email
```
GET /api/users/email/{email}
Response: UserDTO
```

#### 4. Lấy user theo external ID
```
GET /api/users/external/{externalId}
Response: UserDTO
```

#### 5. Lấy users theo role ID
```
GET /api/users/role/{roleId}
Response: List<UserDTO>
```

#### 6. Tạo user mới
```
POST /api/users
Body: {
  "externalId": "moodle_123",
  "email": "user@example.com",
  "name": "User Name",
  "avatarUrl": "https://example.com/avatar.jpg",
  "roleId": 3
}
Response: UserDTO
```

#### 7. Cập nhật user
```
PUT /api/users/{id}
Body: {
  "name": "Updated Name",
  "email": "updated@example.com",
  "avatarUrl": "https://example.com/new-avatar.jpg",
  "roleId": 2
}
Response: UserDTO
```

#### 8. Xóa user (soft delete)
```
DELETE /api/users/{id}
Response: 204 No Content
```

#### 9. Kiểm tra email tồn tại
```
GET /api/users/exists/email/{email}
Response: boolean
```

#### 10. Kiểm tra external ID tồn tại
```
GET /api/users/exists/external/{externalId}
Response: boolean
```

## Roles mặc định
- **ADMIN**: Quản trị viên hệ thống
- **INSTRUCTOR**: Giảng viên/Giáo viên
- **STUDENT**: Học sinh/Sinh viên

## Lưu ý
- Tất cả các thao tác xóa đều là soft delete (sử dụng trường `delete_at`)
- Email và external_id phải là duy nhất
- Role ID là bắt buộc khi tạo user
- API sử dụng validation để kiểm tra dữ liệu đầu vào
- Ứng dụng hỗ trợ CORS cho frontend integration

## Ví dụ sử dụng cURL

### Tạo role mới:
```bash
curl -X POST http://localhost:8081/api/roles \
  -H "Content-Type: application/json" \
  -d '{"roleName": "MODERATOR", "description": "Content moderator role"}'
```

### Tạo user mới:
```bash
curl -X POST http://localhost:8081/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "externalId": "moodle_999",
    "email": "newuser@example.com",
    "name": "New User",
    "roleId": 3
  }'
```
