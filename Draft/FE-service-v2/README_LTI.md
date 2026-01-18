# 🚀 Moodle LTI Integration - Kong Gateway Authentication

Hệ thống này tích hợp với Moodle thông qua LTI (Learning Tools Interoperability) và sử dụng Kong Gateway để xác thực và phân quyền.

## 🏗️ Kiến trúc hệ thống

```
Moodle → LTI Launch → React Frontend → Kong Gateway → User Service → Database
```

## 🔧 Cách hoạt động

### 1. **LTI Launch từ Moodle**
- Người dùng click vào external tool trong Moodle
- Moodle gửi POST request với các tham số LTI
- Frontend nhận và parse các tham số LTI

### 2. **Xác thực qua Kong Gateway**
- Frontend gọi User Service để lấy JWT token
- User Service tạo/cập nhật user từ dữ liệu LTI
- Trả về JWT token tương thích với Kong

### 3. **Phân quyền theo Role**
- **Student**: Truy cập dashboard học sinh
- **Instructor**: Truy cập dashboard giáo viên  
- **Admin**: Truy cập dashboard quản trị

## 📁 Cấu trúc thư mục

```
FE-service-v2/
├── src/
│   ├── services/
│   │   ├── ltiService.ts      # Xử lý LTI parameters
│   │   └── kongApiService.ts  # Tích hợp Kong Gateway
│   ├── components/
│   │   ├── lti/               # LTI components
│   │   └── auth/              # Kong auth components
│   └── App.tsx                # Main app với LTI integration
├── public/
│   └── lti-test.html          # Test LTI launch
```

## 🚀 Chạy hệ thống

### 1. Khởi động Backend Services

```bash
# Kong Gateway (PostgreSQL + Kong + Konga)
cd kong-gateway
./start-kong.ps1

# User Service
cd userservice
./mvnw spring-boot:run

# Course Service  
cd courseservice
./mvnw spring-boot:run
```

### 2. Khởi động Frontend

```bash
cd FE-service-v2
npm install
npm run dev
```

### 3. Test LTI Integration

1. Mở: `http://localhost:5173/lti-test.html`
2. Chọn role (Student/Instructor/Admin)
3. Click "Launch LTI Tool"
4. Ứng dụng sẽ mở với role tương ứng

## 🔗 LTI Parameters

### Required Parameters từ Moodle:
- `user_id`: ID người dùng trong Moodle
- `lis_person_name_full`: Tên đầy đủ
- `lis_person_contact_email_primary`: Email
- `roles`: Role trong Moodle (Student/Instructor/Administrator)
- `context_id`: ID khóa học
- `context_title`: Tên khóa học
- `resource_link_id`: ID resource
- `tool_consumer_instance_guid`: GUID của Moodle

### Optional Parameters:
- `custom_course_id`: ID khóa học tùy chỉnh
- `custom_user_role`: Role hệ thống (STUDENT/INSTRUCTOR/ADMIN)

## 🔐 JWT Authentication Flow

1. **Frontend nhận LTI params** → Parse và validate
2. **Gọi User Service** → `/auth/lti` endpoint  
3. **User Service**:
   - Tạo user mới nếu chưa tồn tại
   - Cập nhật thông tin nếu đã tồn tại
   - Generate JWT token với issuer "adaptive-learning-issuer"
4. **Kong Gateway validate JWT** → Cho phép truy cập API

## 🎯 Role Mapping

| Moodle Role | System Role | Dashboard Access |
|-------------|-------------|------------------|
| Student | STUDENT | Student Dashboard |
| Instructor/Teacher | INSTRUCTOR | Instructor Dashboard |
| Administrator | ADMIN | Admin Dashboard |

## 🔧 Cấu hình Moodle

### 1. Tạo External Tool
1. Vào **Site administration** → **Plugins** → **Activity modules** → **External tool** → **Manage tools**
2. Click **Configure a tool manually**
3. Điền thông tin:
   - **Tool name**: Adaptive Learning Plugin
   - **Tool URL**: `http://localhost:5173/`
   - **Consumer key**: `moodle_consumer`
   - **Shared secret**: `your_secret_key`

### 2. Custom Parameters (Optional)
```
custom_course_id=$CourseID
custom_user_role=STUDENT
```

### 3. Privacy Settings
- ✅ Share launcher's name with tool
- ✅ Share launcher's email with tool  
- ✅ Accept grades from the tool

## 🐛 Debug & Testing

### 1. Check LTI Parameters
```javascript
// Console trong browser
console.log(sessionStorage.getItem('lti_launch_params'));
```

### 2. Test Kong Gateway
```bash
# Check Kong services
curl http://localhost:8001/services

# Test with JWT
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/users/profile
```

### 3. Check User Service
```bash
# Health check
curl http://localhost:8080/auth/health

# Test LTI auth
curl -X POST http://localhost:8080/auth/lti \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","role":"STUDENT"}'
```

## 📝 Logs

### Frontend Logs
- Browser Developer Tools → Console
- LTI parameter parsing
- Kong API calls

### Backend Logs  
- User Service: `logs/userservice.log`
- Kong Gateway: `docker logs kong-gateway`

## 🚨 Troubleshooting

### Lỗi thường gặp:

1. **"No LTI parameters found"**
   - Kiểm tra Moodle configuration
   - Đảm bảo POST request đúng format

2. **"JWT validation failed"**
   - Kiểm tra Kong Gateway configuration
   - Verify JWT issuer = "adaptive-learning-issuer"

3. **"User creation failed"**
   - Kiểm tra database connection
   - Verify role mapping

### Debug Steps:
1. Check Kong Gateway status
2. Verify User Service connection
3. Test LTI parameters manually
4. Check database records

## 🔄 Production Deployment

Xem file: `PRODUCTION_DEPLOYMENT.md` để biết chi tiết deploy production.

## 📞 Support

- **Frontend Issues**: Check browser console logs
- **Backend Issues**: Check service logs
- **Kong Gateway**: Check admin UI at `http://localhost:1337`
- **Database**: Check PostgreSQL logs
