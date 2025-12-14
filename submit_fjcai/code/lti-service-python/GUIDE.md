# 🐍 LTI 1.3 Service - Python Implementation

## 📋 Tổng quan

Python LTI 1.3 Service là một implementation hiện đại thay thế cho Spring Boot service, được xây dựng bằng FastAPI. Service này cung cấp tích hợp LTI 1.3 an toàn với Moodle và theo dõi hoạt động học tập của người dùng.

### 🔄 **Migration từ Spring Boot**

| Đặc điểm | Spring Boot (Cũ) | Python FastAPI (Mới) |
|----------|------------------|----------------------|
| **Khởi động** | ~45 giây | ~2 giây |
| **Bộ nhớ** | ~512MB | ~50MB |
| **Kích thước** | ~50MB JAR | ~5MB code |
| **Performance** | Tốt | Xuất sắc |
| **Development** | Trung bình | Nhanh |

## 🏗️ **Kiến trúc**

```
┌─────────────────────────────────────────────────────────────┐
│                        MOODLE LMS                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ LTI 1.3 OIDC Flow
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  NGINX GATEWAY                             │
│                   Port: 80/443                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ Reverse Proxy
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PYTHON LTI SERVICE                            │
│                   Port: 8082                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FastAPI   │  │ SQLAlchemy  │  │   Jinja2    │        │
│  │   Router    │  │     ORM     │  │  Templates  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │ API Calls
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE                                  │
│              SQLite / PostgreSQL                           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Cài đặt nhanh**

### 1. **Yêu cầu hệ thống**

```bash
# Python 3.9 trở lên
python3 --version

# pip package manager
pip3 --version

# Git (để clone project)
git --version
```

### 2. **Clone và cài đặt**

```bash
# Navigate to project directory
cd moodle-adaptive-learning-plugin/lti-service-python

# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo thư mục logs
mkdir -p logs

# Khởi động service
python main.py
```

### 3. **Khởi động với script**

```bash
# Make script executable (Linux/Mac)
chmod +x start.sh

# Start in development mode
./start.sh --dev

# Start in production mode
./start.sh
```

## ⚙️ **Cấu hình**

### 1. **Environment Variables** 

Chỉnh sửa file `.env`:

```env
# Application Settings
APP_NAME=LTI Service Python
DEBUG=True
HOST=0.0.0.0
PORT=8082

# Database Configuration
DATABASE_URL=sqlite:///./lti_service.db
# Hoặc PostgreSQL: postgresql://user:password@localhost/lti_service

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# LTI 1.3 Configuration (Lấy từ Moodle)
LTI_CLIENT_ID=your-moodle-generated-client-id
LTI_DEPLOYMENT_ID=1
LTI_ISSUER=http://localhost/moodle
LTI_AUTH_URL=http://localhost/moodle/mod/lti/auth.php
LTI_TOKEN_URL=http://localhost/moodle/mod/lti/token.php
LTI_KEYSET_URL=http://localhost/moodle/mod/lti/certs.php

# Tool Configuration
TOOL_TARGET_LINK_URI=http://localhost:8082/lti/launch
TOOL_OIDC_INITIATION_URL=http://localhost:8082/lti/login
TOOL_PUBLIC_JWK_URL=http://localhost:8082/lti/jwks

# Moodle API Configuration
MOODLE_API_URL=http://localhost/moodle/webservice/rest/server.php
MOODLE_API_TOKEN=your-moodle-webservice-token
```

### 2. **Database Configuration**

#### SQLite (Default - Phát triển)
```env
DATABASE_URL=sqlite:///./lti_service.db
```

#### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://lti_user:lti_password@localhost/lti_service
```

## 🔧 **Cấu hình Moodle External Tool**

### 1. **Bước 1: Tạo External Tool trong Moodle**

1. Đăng nhập Moodle với quyền Admin
2. Vào **Site administration → Plugins → Activity modules → External tool → Manage tools**
3. Click **"Configure a tool manually"**

### 2. **Bước 2: Điền thông tin Tool**

```
Tool Settings:
┌────────────────────────────────────────────────────────────┐
│ Tool name: User Log Viewer                                │
│ Tool URL: http://localhost:8082/lti/launch                │
│ LTI version: LTI 1.3                                      │
│ Initiate login URL: http://localhost:8082/lti/login       │
│ Redirection URI(s): http://localhost:8082/lti/launch      │
│ Public keyset URL: http://localhost:8082/lti/jwks         │
│                                                            │
│ Privacy Settings:                                          │
│ ☑ Share launcher's name with tool                         │
│ ☑ Share launcher's email with tool                        │
│ ☐ Accept grades from the tool                             │
└────────────────────────────────────────────────────────────┘
```

### 3. **Bước 3: Lấy Client ID**

Sau khi tạo tool, Moodle sẽ generate **Client ID**. Copy và paste vào file `.env`:

```env
LTI_CLIENT_ID=123456789012345678901  # Client ID từ Moodle
```

### 4. **Bước 4: Test Integration**

1. Vào một course bất kỳ
2. **Turn editing on**
3. **Add an activity → External tool**
4. Chọn **"User Log Viewer"** từ dropdown
5. Save và click vào tool để test

## 📊 **API Documentation**

### **LTI Endpoints**

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/lti/login` | OIDC Login Initiation |
| `POST` | `/lti/launch` | LTI Launch Processing |
| `GET` | `/lti/dashboard` | User Dashboard |
| `GET` | `/lti/logs` | Activity Logs Page |
| `GET` | `/lti/config` | Tool Configuration |
| `GET` | `/lti/jwks` | JSON Web Key Set |

### **API Endpoints**

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/health` | Health Check |
| `GET` | `/api/launches` | Danh sách LTI Launches |
| `GET` | `/api/user/{id}/launches` | User-specific Launches |
| `GET` | `/api/course/{id}/participants` | Course Participants |
| `POST` | `/api/validate-token` | Token Validation |

### **Example API Calls**

```bash
# Health check
curl http://localhost:8082/health

# Get user launches
curl http://localhost:8082/api/user/123/launches

# Validate token
curl -X POST http://localhost:8082/api/validate-token \
     -H "Content-Type: application/json" \
     -d '{"token": "your-jwt-token"}'

# Get tool configuration
curl http://localhost:8082/lti/config
```

## 🗄️ **Database Schema**

### **LTI Launch Table**
```sql
CREATE TABLE lti_launches (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    context_id VARCHAR(255),
    resource_link_id VARCHAR(255),
    user_name VARCHAR(255),
    user_email VARCHAR(255),
    course_id VARCHAR(255),
    launch_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    given_name VARCHAR(255),
    family_name VARCHAR(255),
    roles TEXT,  -- JSON array
    resource_title VARCHAR(500),
    course_title VARCHAR(500),
    iss VARCHAR(500),
    aud VARCHAR(500),
    sub VARCHAR(255)
);
```

### **User Log Table**
```sql
CREATE TABLE user_logs (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    course_id VARCHAR(255),
    action VARCHAR(100),
    target VARCHAR(100),
    object_table VARCHAR(100),
    object_id VARCHAR(255),
    crud CHAR(1),
    event_name VARCHAR(500),
    component VARCHAR(100),
    time_created DATETIME,
    ip VARCHAR(45),
    user_agent TEXT
);
```

## 🔐 **LTI 1.3 Flow**

```mermaid
sequenceDiagram
    participant User
    participant Moodle
    participant PythonLTI as Python LTI Service
    participant DB as Database

    User->>Moodle: Click External Tool
    Moodle->>PythonLTI: OIDC Login Request
    Note over PythonLTI: /lti/login
    PythonLTI->>Moodle: Redirect to Moodle Auth
    User->>Moodle: Authentication
    Moodle->>PythonLTI: Launch with JWT Token
    Note over PythonLTI: /lti/launch
    PythonLTI->>DB: Store Launch Data
    PythonLTI->>PythonLTI: Generate Session Token
    PythonLTI->>User: Redirect to Dashboard
    Note over User: /lti/dashboard?token=xxx
    User->>PythonLTI: View Activity Logs
    Note over PythonLTI: /lti/logs?token=xxx
    PythonLTI->>Moodle: Fetch User Data via API
    PythonLTI->>User: Display Logs & Analytics
```

## 🐳 **Docker Deployment**

### 1. **Build và Run**

```bash
# Build image
docker build -t lti-service-python .

# Run container
docker run -p 8082:8082 lti-service-python

# Run with environment file
docker run -p 8082:8082 --env-file .env lti-service-python
```

### 2. **Docker Compose**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. **Production với PostgreSQL**

```yaml
version: '3.8'
services:
  lti-service:
    build: .
    ports:
      - "8082:8082"
    environment:
      - DATABASE_URL=postgresql://lti_user:lti_password@postgres/lti_service
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: lti_service
      POSTGRES_USER: lti_user
      POSTGRES_PASSWORD: lti_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

#### 1. **Port đã được sử dụng**
```bash
# Tìm process sử dụng port 8082
lsof -i :8082  # Linux/Mac
netstat -ano | findstr :8082  # Windows

# Kill process
kill -9 <PID>
```

#### 2. **Database connection error**
```bash
# Check database file
ls -la lti_service.db

# Recreate database
rm lti_service.db
python main.py  # Database sẽ được tạo tự động
```

#### 3. **JWT token errors**
```bash
# Check JWT secret
grep JWT_SECRET .env

# Test token decode
python3 -c "
import jwt
token = 'your-token-here'
secret = 'your-secret-here'
print(jwt.decode(token, secret, algorithms=['HS256']))
"
```

#### 4. **Moodle integration issues**
```bash
# Test LTI endpoints
curl http://localhost:8082/lti/config
curl http://localhost:8082/lti/jwks

# Check Moodle logs
tail -f /path/to/moodle/moodledata/logs/moodle.log
```

### **Debug Mode**

```bash
# Start with debug logging
DEBUG=True LOG_LEVEL=DEBUG python main.py

# Check logs
tail -f logs/lti_service.log
```

## 📈 **Monitoring & Performance**

### **Health Monitoring**

```bash
# Basic health check
curl http://localhost:8082/health

# Detailed status
curl http://localhost:8082/api/health
```

### **Performance Metrics**

```python
# Thêm vào main.py để monitor
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### **Logs Analysis**

```bash
# View error logs
grep "ERROR" logs/lti_service.log

# Monitor requests
tail -f logs/lti_service.log | grep "INFO"

# Count requests by endpoint
grep "GET\|POST" logs/lti_service.log | awk '{print $3}' | sort | uniq -c
```

## 🔧 **Development**

### **Project Structure**

```
lti-service-python/
├── app/
│   ├── models/          # Database models
│   │   ├── __init__.py
│   │   ├── lti_launch.py
│   │   └── user_log.py
│   ├── routers/         # API routes
│   │   ├── __init__.py
│   │   ├── lti.py       # LTI endpoints
│   │   └── api.py       # REST API
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── lti_service.py
│   │   └── moodle_service.py
│   ├── templates/       # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── user-logs.html
│   │   └── error.html
│   ├── static/          # Static files
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── __init__.py
├── logs/                # Log files
├── data/                # Data files
├── venv/                # Virtual environment
├── .env                 # Environment variables
├── requirements.txt     # Dependencies
├── Dockerfile          # Container build
├── docker-compose.yml  # Multi-container
├── start.sh            # Startup script
├── main.py             # Application entry
└── README.md           # This file
```

### **Adding New Features**

#### 1. **Tạo Model mới**
```python
# app/models/new_feature.py
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class NewFeature(Base):
    __tablename__ = "new_features"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime)
```

#### 2. **Tạo Service**
```python
# app/services/new_service.py
class NewService:
    def __init__(self):
        pass
    
    async def process_feature(self, data):
        # Business logic here
        return {"result": "processed"}
```

#### 3. **Tạo Router**
```python
# app/routers/new_router.py
from fastapi import APIRouter
from app.services.new_service import NewService

router = APIRouter()
service = NewService()

@router.get("/new-endpoint")
async def new_endpoint():
    result = await service.process_feature({})
    return result
```

#### 4. **Register Router**
```python
# main.py
from app.routers import new_router

app.include_router(
    new_router.router, 
    prefix="/api/new", 
    tags=["New Feature"]
)
```

## 🧪 **Testing**

### **Unit Tests**

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_lti_service.py
```

### **Integration Tests**

```bash
# Test LTI flow
python tests/test_lti_integration.py

# Test Moodle API
python tests/test_moodle_api.py
```

### **Load Testing**

```bash
# Install load testing tools
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8082
```

## 📚 **Additional Resources**

### **Documentation Links**
- [LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Moodle LTI Documentation](https://docs.moodle.org/en/LTI_and_Moodle)

### **Example Configurations**

#### Moodle Tool Configuration JSON
```json
{
  "title": "User Log Viewer",
  "description": "View user activity logs and learning analytics",
  "target_link_uri": "http://localhost:8082/lti/launch",
  "oidc_initiation_url": "http://localhost:8082/lti/login",
  "public_jwk_url": "http://localhost:8082/lti/jwks",
  "claims": [
    "iss",
    "sub",
    "aud",
    "iat",
    "exp",
    "given_name",
    "family_name",
    "name",
    "email",
    "https://purl.imsglobal.org/spec/lti/claim/context",
    "https://purl.imsglobal.org/spec/lti/claim/resource_link",
    "https://purl.imsglobal.org/spec/lti/claim/roles"
  ]
}
```

## 🤝 **Contributing**

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 **License**

MIT License - xem file LICENSE để biết chi tiết.

---

## 🎯 **Summary**

Python LTI 1.3 Service cung cấp:

✅ **Hiệu suất cao** - Khởi động nhanh, sử dụng ít bộ nhớ  
✅ **Tích hợp hoàn chỉnh** - LTI 1.3 compliance với Moodle  
✅ **Dễ bảo trì** - Code Python đơn giản, rõ ràng  
✅ **Scalable** - Hỗ trợ Docker, database clustering  
✅ **Secure** - JWT authentication, SQL injection protection  
✅ **Monitor-ready** - Logging, health checks, metrics  

**🚀 Ready for production deployment!**
