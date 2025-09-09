# 🚀 Hướng dẫn Deploy Hệ thống Microservices lên Server Linux

## 📋 Tổng quan

Hướng dẫn này sẽ giúp bạn deploy toàn bộ hệ thống **Adaptive Learning Platform** lên server Linux mới từ con số 0, bao gồm:

- Kong Gateway (API Gateway)
- User Service (Spring Boot + JWT)
- Course Service (Spring Boot)
- LTI Service (Python FastAPI)
- Frontend Service (React)
- PostgreSQL Database
- Monitoring & Logging

## 🏗️ **Kiến trúc Hệ thống**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERNET                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/HTTP
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 REVERSE PROXY                               │
│              Nginx (Port 80/443)                           │
│                 SSL Termination                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 KONG GATEWAY                               │
│                  Port: 8000                                │
│           JWT Auth + Rate Limiting                         │
└─────────────────────┬───────────────────────────────────────┘
                      │ Load Balancing
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 MICROSERVICES                              │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │User Service │ │Course Svc   │ │LTI Service  │            │
│ │   :8080     │ │   :8081     │ │   :8082     │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
│ ┌─────────────┐ ┌─────────────┐                           │
│ │Frontend     │ │PostgreSQL   │                           │
│ │   :3000     │ │   :5432     │                           │
│ └─────────────┘ └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **PHẦN 1: CẤU HÌNH SERVER**

### 1.1 **Thông tin Server yêu cầu**

```bash
# Minimum Requirements
OS: Ubuntu 20.04 LTS hoặc CentOS 8+
CPU: 2 cores
RAM: 4GB (8GB recommended)
Storage: 20GB SSD
Network: Public IP với port 80, 443, 8000-8002 mở

# Recommended for Production
CPU: 4+ cores
RAM: 8GB+
Storage: 50GB+ SSD
```

### 1.2 **Kết nối Server**

```bash
# SSH vào server với user có quyền sudo
ssh username@your-server-ip

# Hoặc với key file
ssh -i your-key.pem username@your-server-ip
```

### 1.3 **Cập nhật hệ thống**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# hoặc với CentOS 8+
sudo dnf update -y
```

### 1.4 **Cài đặt các package cần thiết**

```bash
# Ubuntu/Debian
sudo apt install -y curl wget git unzip nano htop net-tools

# CentOS/RHEL
sudo yum install -y curl wget git unzip nano htop net-tools
```

---

## 🐳 **PHẦN 2: CÀI ĐẶT DOCKER**

### 2.1 **Cài đặt Docker Engine**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Thêm user vào docker group
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2.2 **Cài đặt Docker Compose**

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Cấp quyền thực thi
sudo chmod +x /usr/local/bin/docker-compose

# Tạo symbolic link
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Kiểm tra version
docker-compose --version
```

### 2.3 **Khởi động lại và kiểm tra**

```bash
# Logout và login lại để docker group có hiệu lực
exit
ssh username@your-server-ip

# Kiểm tra Docker
docker --version
docker run hello-world
```

---

## 📁 **PHẦN 3: CLONE VÀ SETUP PROJECT**

### 3.1 **Clone repository**

```bash
# Tạo thư mục project
mkdir -p ~/projects
cd ~/projects

# Clone repository
git clone https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin.git
cd moodle-adaptive-learning-plugin

# Xem cấu trúc project
ls -la
```

### 3.2 **Cấu hình environment variables**

```bash
# Copy file environment mẫu
cd kong-gateway
cp .env .env.production

# Chỉnh sửa cấu hình cho production
nano .env.production
```

**Nội dung file `.env.production`:**

```bash
# Kong Database Configuration
KONG_DATABASE=postgres
KONG_PG_HOST=kong-database
KONG_PG_PORT=5432
KONG_PG_USER=kong
KONG_PG_PASSWORD=StrongKongPassword123!
KONG_PG_DATABASE=kong

# Kong Gateway Configuration
KONG_PROXY_ACCESS_LOG=/dev/stdout
KONG_ADMIN_ACCESS_LOG=/dev/stdout
KONG_PROXY_ERROR_LOG=/dev/stderr
KONG_ADMIN_ERROR_LOG=/dev/stderr
KONG_ADMIN_LISTEN=0.0.0.0:8001
KONG_PROXY_LISTEN=0.0.0.0:8000, 0.0.0.0:8443 ssl
KONG_ADMIN_GUI_LISTEN=0.0.0.0:8002
KONG_PLUGINS=bundled,jwt,cors,rate-limiting,file-log
KONG_LOG_LEVEL=info

# JWT Configuration (Đổi secret cho production!)
JWT_SECRET=your-super-strong-production-jwt-secret-key-2024
JWT_ISSUER=adaptive-learning-issuer
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400000

# Service URLs (Internal Docker Network)
USER_SERVICE_URL=http://user-service:8080
COURSE_SERVICE_URL=http://course-service:8081
LTI_SERVICE_URL=http://lti-service:8082
FRONTEND_SERVICE_URL=http://frontend-service:3000

# External URLs (Thay YOUR_DOMAIN bằng domain thật)
DOMAIN_NAME=your-domain.com
KONG_GATEWAY_URL=https://your-domain.com
KONG_ADMIN_URL=http://your-domain.com:8001
FRONTEND_URL=https://your-domain.com

# Database URLs for Services
USER_SERVICE_DB_URL=jdbc:postgresql://kong-database:5432/userservice
COURSE_SERVICE_DB_URL=jdbc:postgresql://kong-database:5432/courseservice
LTI_SERVICE_DB_URL=postgresql://kong:StrongKongPassword123!@kong-database:5432/lti_service

# Security Settings
ENABLE_RATE_LIMITING=true
RATE_LIMIT_MINUTE=100
RATE_LIMIT_HOUR=1000
RATE_LIMIT_DAY=10000

# Performance Settings
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=4096
MEM_CACHE_SIZE=512m
```

### 3.3 **Cấu hình SSL/TLS (Tùy chọn)**

```bash
# Tạo thư mục cho SSL certificates
sudo mkdir -p /etc/ssl/certs/adaptive-learning
cd /etc/ssl/certs/adaptive-learning

# Option 1: Tự tạo self-signed certificate (Development)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout private.key \
    -out certificate.crt \
    -subj "/C=VN/ST=HCM/L=HCMC/O=AdaptiveLearning/CN=your-domain.com"

# Option 2: Sử dụng Let's Encrypt (Production)
sudo apt install -y certbot
sudo certbot certonly --standalone -d your-domain.com
```

---

## 🔧 **PHẦN 4: CẤU HÌNH DOCKER COMPOSE CHO PRODUCTION**

### 4.1 **Tạo Docker Compose Production**

```bash
cd ~/projects/moodle-adaptive-learning-plugin/kong-gateway
nano docker-compose.production.yml
```

**Nội dung file `docker-compose.production.yml`:**

```yaml
version: '3.8'

services:
  # Reverse Proxy (Nginx)
  nginx-proxy:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/ssl/certs/adaptive-learning:/etc/ssl/certs:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - kong-gateway
    networks:
      - kong-net

  # Kong Database
  kong-database:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: ${KONG_PG_PASSWORD}
      POSTGRES_DB: kong
      POSTGRES_MULTIPLE_DATABASES: userservice,courseservice,lti_service,konga
    volumes:
      - kong-db-data:/var/lib/postgresql/data
      - ./init-databases.sql:/docker-entrypoint-initdb.d/init-databases.sql:ro
    networks:
      - kong-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kong"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Kong Migration
  kong-migration:
    image: kong/kong-gateway:3.7.1.1
    command: "kong migrations bootstrap"
    restart: "no"
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_PG_PASSWORD}
      KONG_PG_DATABASE: kong
    networks:
      - kong-net
    depends_on:
      kong-database:
        condition: service_healthy

  # Kong Gateway
  kong-gateway:
    image: kong/kong-gateway:3.7.1.1
    restart: unless-stopped
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_PG_PASSWORD}
      KONG_PG_DATABASE: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
      KONG_PROXY_LISTEN: "0.0.0.0:8000"
      KONG_ADMIN_GUI_LISTEN: "0.0.0.0:8002"
      KONG_PLUGINS: "bundled,jwt,cors,rate-limiting,file-log"
      KONG_LOG_LEVEL: info
      KONG_NGINX_WORKER_PROCESSES: ${NGINX_WORKER_PROCESSES}
      KONG_MEM_CACHE_SIZE: ${MEM_CACHE_SIZE}
    expose:
      - "8000"
      - "8001"
      - "8002"
    volumes:
      - kong-logs:/tmp
    networks:
      - kong-net
    depends_on:
      kong-migration:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "kong", "health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # User Service
  user-service:
    build: 
      context: ../userservice
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SPRING_PROFILES_ACTIVE: production
      SPRING_DATASOURCE_URL: ${USER_SERVICE_DB_URL}
      SPRING_DATASOURCE_USERNAME: kong
      SPRING_DATASOURCE_PASSWORD: ${KONG_PG_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      JWT_EXPIRATION: ${JWT_EXPIRATION}
      LOGGING_LEVEL_ROOT: INFO
    expose:
      - "8080"
    volumes:
      - user-service-logs:/app/logs
    networks:
      - kong-net
    depends_on:
      kong-database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Course Service
  course-service:
    build: 
      context: ../courseservice
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SPRING_PROFILES_ACTIVE: production
      SPRING_DATASOURCE_URL: ${COURSE_SERVICE_DB_URL}
      SPRING_DATASOURCE_USERNAME: kong
      SPRING_DATASOURCE_PASSWORD: ${KONG_PG_PASSWORD}
      LOGGING_LEVEL_ROOT: INFO
    expose:
      - "8081"
    volumes:
      - course-service-logs:/app/logs
    networks:
      - kong-net
    depends_on:
      kong-database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # LTI Service Python
  lti-service:
    build: 
      context: ../lti-service-python
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      DATABASE_URL: ${LTI_SERVICE_DB_URL}
      JWT_SECRET: ${JWT_SECRET}
      FRONTEND_URL: ${FRONTEND_URL}
      DEBUG: "False"
      LOG_LEVEL: INFO
    expose:
      - "8082"
    volumes:
      - lti-service-logs:/app/logs
    networks:
      - kong-net
    depends_on:
      kong-database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Service
  frontend-service:
    build: 
      context: ../FE-service
      dockerfile: Dockerfile
      args:
        REACT_APP_API_BASE_URL: ${KONG_GATEWAY_URL}
        REACT_APP_AUTH_URL: ${KONG_GATEWAY_URL}/auth
    restart: unless-stopped
    expose:
      - "3000"
    volumes:
      - frontend-logs:/var/log/nginx
    networks:
      - kong-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Konga (Kong Admin UI)
  konga:
    image: pantsel/konga:latest
    restart: unless-stopped
    environment:
      DB_ADAPTER: postgres
      DB_HOST: kong-database
      DB_USER: kong
      DB_PASSWORD: ${KONG_PG_PASSWORD}
      DB_DATABASE: konga
      NODE_ENV: production
      KONGA_HOOK_TIMEOUT: 120000
    expose:
      - "1337"
    networks:
      - kong-net
    depends_on:
      kong-database:
        condition: service_healthy

networks:
  kong-net:
    driver: bridge

volumes:
  kong-db-data:
    driver: local
  kong-logs:
    driver: local
  nginx-logs:
    driver: local
  user-service-logs:
    driver: local
  course-service-logs:
    driver: local
  lti-service-logs:
    driver: local
  frontend-logs:
    driver: local
```

### 4.2 **Tạo Nginx Configuration**

```bash
nano nginx.conf
```

**Nội dung file `nginx.conf`:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream kong_gateway {
        server kong-gateway:8000;
    }

    upstream kong_admin {
        server kong-gateway:8001;
    }

    upstream konga_ui {
        server konga:1337;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Main API Gateway (HTTPS)
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/certs/certificate.crt;
        ssl_certificate_key /etc/ssl/certs/private.key;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://kong_gateway;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # Timeouts
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Kong Admin API (restricted access)
        location /admin/ {
            limit_req zone=admin burst=10 nodelay;
            
            # Restrict access by IP (uncomment and set your IP)
            # allow YOUR_ADMIN_IP;
            # deny all;
            
            proxy_pass http://kong_admin/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Konga UI (restricted access)
        location /konga/ {
            limit_req zone=admin burst=10 nodelay;
            
            # Restrict access by IP (uncomment and set your IP)
            # allow YOUR_ADMIN_IP;
            # deny all;
            
            proxy_pass http://konga_ui/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # Default server (catch-all)
    server {
        listen 80 default_server;
        listen 443 ssl default_server;
        server_name _;
        ssl_certificate /etc/ssl/certs/certificate.crt;
        ssl_certificate_key /etc/ssl/certs/private.key;
        return 444;
    }
}
```

### 4.3 **Tạo Database Initialization Script**

```bash
nano init-databases.sql
```

**Nội dung file `init-databases.sql`:**

```sql
-- Create databases for microservices
CREATE DATABASE IF NOT EXISTS userservice;
CREATE DATABASE IF NOT EXISTS courseservice;
CREATE DATABASE IF NOT EXISTS lti_service;
CREATE DATABASE IF NOT EXISTS konga;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE userservice TO kong;
GRANT ALL PRIVILEGES ON DATABASE courseservice TO kong;
GRANT ALL PRIVILEGES ON DATABASE lti_service TO kong;
GRANT ALL PRIVILEGES ON DATABASE konga TO kong;
```

---

## 🔨 **PHẦN 5: BUILD VÀ DEPLOY SERVICES**

### 5.1 **Chuẩn bị Dockerfiles cho các services**

#### **User Service Dockerfile**

```bash
cd ../userservice
nano Dockerfile
```

```dockerfile
FROM openjdk:21-jdk-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Maven wrapper and pom.xml
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Download dependencies
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src src

# Build application
RUN ./mvnw clean package -DskipTests

# Create logs directory
RUN mkdir -p /app/logs

# Run application
EXPOSE 8080
CMD ["java", "-jar", "target/userservice-0.0.1-SNAPSHOT.jar"]
```

#### **Course Service Dockerfile**

```bash
cd ../courseservice
nano Dockerfile
```

```dockerfile
FROM openjdk:21-jdk-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Maven wrapper and pom.xml
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Download dependencies
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src src

# Build application
RUN ./mvnw clean package -DskipTests

# Create logs directory
RUN mkdir -p /app/logs

# Run application
EXPOSE 8081
CMD ["java", "-jar", "target/courseservice-0.0.1-SNAPSHOT.jar"]
```

#### **LTI Service Dockerfile**

```bash
cd ../lti-service-python
nano Dockerfile
```

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8082/health || exit 1

# Run application
EXPOSE 8082
CMD ["python", "main.py"]
```

#### **Frontend Service Dockerfile**

```bash
cd ../FE-service
nano Dockerfile
```

```dockerfile
# Multi-stage build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build arguments
ARG REACT_APP_API_BASE_URL
ARG REACT_APP_AUTH_URL

# Set environment variables for build
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL
ENV REACT_APP_AUTH_URL=$REACT_APP_AUTH_URL

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create logs directory
RUN mkdir -p /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Run nginx
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

**Frontend nginx.conf:**

```bash
nano nginx.conf
```

```nginx
server {
    listen 3000;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html index.htm;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Handle client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

### 5.2 **Build và Start Services**

```bash
# Quay về thư mục kong-gateway
cd ~/projects/moodle-adaptive-learning-plugin/kong-gateway

# Load environment variables
export $(cat .env.production | xargs)

# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Kiểm tra status
docker-compose -f docker-compose.production.yml ps
```

### 5.3 **Chờ services khởi động**

```bash
# Monitor logs
docker-compose -f docker-compose.production.yml logs -f

# Hoặc xem logs từng service
docker-compose -f docker-compose.production.yml logs kong-gateway
docker-compose -f docker-compose.production.yml logs user-service
docker-compose -f docker-compose.production.yml logs kong-database

# Chờ khoảng 2-3 phút để tất cả services khởi động
```

---

## ⚙️ **PHẦN 6: CẤU HÌNH KONG GATEWAY**

### 6.1 **Chạy Kong Configuration Script**

```bash
# Đợi Kong Gateway sẵn sàng
sleep 60

# Chạy script cấu hình Kong
chmod +x configure-kong.sh
./configure-kong.sh

# Hoặc trên Windows PowerShell (nếu có)
# powershell -ExecutionPolicy Bypass -File configure-kong.ps1
```

### 6.2 **Kiểm tra Kong Configuration**

```bash
# Kiểm tra Kong services
curl http://localhost:8001/services

# Kiểm tra Kong routes
curl http://localhost:8001/routes

# Kiểm tra Kong consumers
curl http://localhost:8001/consumers

# Kiểm tra JWT credential
curl http://localhost:8001/consumers/adaptive-learning-app/jwt
```

### 6.3 **Test API endpoints**

```bash
# Test health checks
curl http://localhost:8000/auth/health
curl http://localhost:8000/api/courses/health
curl http://localhost:8000/lti/config

# Test JWT authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}'
```

---

## 🔐 **PHẦN 7: CẤU HÌNH BẢO MẬT**

### 7.1 **Firewall Configuration**

```bash
# Ubuntu UFW
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Cho phép SSH
sudo ufw allow ssh

# Cho phép HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Cho phép Kong Admin (chỉ từ IP cụ thể)
sudo ufw allow from YOUR_ADMIN_IP to any port 8001

# Kiểm tra status
sudo ufw status

# CentOS/RHEL FirewallD
sudo systemctl enable firewalld
sudo systemctl start firewalld

sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=8001/tcp --source=YOUR_ADMIN_IP
sudo firewall-cmd --reload
```

### 7.2 **SSL Certificate (Let's Encrypt)**

```bash
# Cài đặt Certbot
sudo apt install -y certbot

# Dừng Nginx tạm thời
docker-compose -f docker-compose.production.yml stop nginx-proxy

# Tạo SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/ssl/certs/adaptive-learning/certificate.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/ssl/certs/adaptive-learning/private.key

# Khởi động lại Nginx
docker-compose -f docker-compose.production.yml start nginx-proxy

# Setup auto-renewal
sudo crontab -e
# Thêm dòng sau:
# 0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f /home/username/projects/moodle-adaptive-learning-plugin/kong-gateway/docker-compose.production.yml restart nginx-proxy
```

### 7.3 **Database Security**

```bash
# Backup database
docker exec kong-gateway_kong-database_1 pg_dump -U kong kong > kong_backup.sql

# Create backup script
nano backup-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup Kong database
docker exec kong-gateway_kong-database_1 pg_dump -U kong kong > $BACKUP_DIR/kong_$DATE.sql

# Backup application databases
docker exec kong-gateway_kong-database_1 pg_dump -U kong userservice > $BACKUP_DIR/userservice_$DATE.sql
docker exec kong-gateway_kong-database_1 pg_dump -U kong courseservice > $BACKUP_DIR/courseservice_$DATE.sql
docker exec kong-gateway_kong-database_1 pg_dump -U kong lti_service > $BACKUP_DIR/lti_service_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Database backup completed: $DATE"
```

```bash
chmod +x backup-db.sh

# Schedule daily backup
crontab -e
# Thêm: 0 2 * * * /home/username/projects/moodle-adaptive-learning-plugin/kong-gateway/backup-db.sh
```

---

## 📊 **PHẦN 8: MONITORING VÀ LOGGING**

### 8.1 **Setup Logging**

```bash
# Tạo log rotation
sudo nano /etc/logrotate.d/adaptive-learning
```

```
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 root root
    postrotate
        docker kill --signal="USR1" $(docker ps -q) 2>/dev/null || true
    endscript
}
```

### 8.2 **Health Monitoring Script**

```bash
nano health-check.sh
```

```bash
#!/bin/bash

SERVICES=("nginx-proxy" "kong-gateway" "user-service" "course-service" "lti-service" "frontend-service" "kong-database")
FAILED_SERVICES=""

echo "=== Health Check Report $(date) ==="

for service in "${SERVICES[@]}"; do
    status=$(docker-compose -f docker-compose.production.yml ps $service | grep "Up" | wc -l)
    if [ $status -eq 1 ]; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Down"
        FAILED_SERVICES="$FAILED_SERVICES $service"
    fi
done

# Test API endpoints
echo ""
echo "=== API Health Check ==="

endpoints=(
    "https://your-domain.com/auth/health"
    "https://your-domain.com/lti/config"
    "https://your-domain.com/"
)

for endpoint in "${endpoints[@]}"; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 $endpoint)
    if [ $status_code -eq 200 ]; then
        echo "✅ $endpoint: OK ($status_code)"
    else
        echo "❌ $endpoint: Failed ($status_code)"
    fi
done

# Restart failed services
if [ ! -z "$FAILED_SERVICES" ]; then
    echo ""
    echo "🔄 Restarting failed services: $FAILED_SERVICES"
    for service in $FAILED_SERVICES; do
        docker-compose -f docker-compose.production.yml restart $service
    done
fi

echo "=== End Health Check ==="
```

```bash
chmod +x health-check.sh

# Schedule health check every 5 minutes
crontab -e
# Thêm: */5 * * * * /home/username/projects/moodle-adaptive-learning-plugin/kong-gateway/health-check.sh >> /var/log/health-check.log 2>&1
```

### 8.3 **Performance Monitoring**

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor Docker resources
docker stats

# Monitor system resources
htop

# Monitor network
sudo nethogs

# Check disk usage
df -h
du -sh /var/lib/docker/
```

---

## 🧪 **PHẦN 9: TESTING VÀ VALIDATION**

### 9.1 **Functional Testing**

```bash
# Test user registration
curl -X POST https://your-domain.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "roleId": 1
  }'

# Test user login
curl -X POST https://your-domain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Test protected endpoint (replace TOKEN with actual JWT)
curl -H "Authorization: Bearer TOKEN" \
  https://your-domain.com/api/users
```

### 9.2 **Load Testing**

```bash
# Install Apache Bench
sudo apt install -y apache2-utils

# Test load
ab -n 1000 -c 10 https://your-domain.com/auth/health

# Install wrk for advanced testing
sudo apt install -y wrk

# Load test
wrk -t12 -c400 -d30s https://your-domain.com/
```

### 9.3 **Security Testing**

```bash
# Test SSL
curl -I https://your-domain.com

# Test security headers
curl -I https://your-domain.com | grep -E "(X-Frame-Options|X-Content-Type-Options|X-XSS-Protection|Strict-Transport-Security)"

# Test rate limiting
for i in {1..20}; do curl https://your-domain.com/auth/health; done
```

---

## 🔄 **PHẦN 10: DEPLOYMENT AUTOMATION**

### 10.1 **Deployment Script**

```bash
nano deploy.sh
```

```bash
#!/bin/bash

set -e

REPO_URL="https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin.git"
DEPLOY_DIR="/home/deploy"
BACKUP_DIR="/home/backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🚀 Starting deployment: $DATE"

# Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
docker-compose -f docker-compose.production.yml down
cp -r $DEPLOY_DIR $BACKUP_DIR/backup_$DATE

# Update code
echo "📥 Updating code..."
cd $DEPLOY_DIR
git fetch origin
git reset --hard origin/main

# Update environment
echo "⚙️ Updating environment..."
cd kong-gateway
source .env.production

# Build and deploy
echo "🔨 Building and deploying..."
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 60

# Configure Kong
echo "🔧 Configuring Kong..."
./configure-kong.sh

# Health check
echo "🏥 Health checking..."
./health-check.sh

# Cleanup old images
echo "🧹 Cleaning up..."
docker system prune -f

echo "✅ Deployment completed: $DATE"
```

```bash
chmod +x deploy.sh
```

### 10.2 **CI/CD Integration**

**GitHub Actions Workflow:**

```bash
mkdir -p .github/workflows
nano .github/workflows/deploy.yml
```

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /home/deploy/moodle-adaptive-learning-plugin
          ./deploy.sh
```

---

## 🆘 **PHẦN 11: TROUBLESHOOTING**

### 11.1 **Common Issues**

#### **Services không khởi động**

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs service-name

# Check resource usage
docker stats

# Check disk space
df -h

# Restart service
docker-compose -f docker-compose.production.yml restart service-name
```

#### **Database connection issues**

```bash
# Check database logs
docker-compose -f docker-compose.production.yml logs kong-database

# Connect to database
docker exec -it kong-gateway_kong-database_1 psql -U kong

# Check connections
\l
\c kong
\dt
```

#### **Kong configuration issues**

```bash
# Check Kong status
curl http://localhost:8001/status

# Reset Kong configuration
curl -X DELETE http://localhost:8001/services/user-service
./configure-kong.sh
```

#### **SSL issues**

```bash
# Test SSL certificate
openssl s_client -connect your-domain.com:443

# Renew SSL certificate
sudo certbot renew --force-renewal
```

### 11.2 **Emergency Recovery**

```bash
# Stop all services
docker-compose -f docker-compose.production.yml down

# Restore from backup
cp -r /home/backup/backup_YYYYMMDD_HHMMSS/* /home/deploy/

# Start services
docker-compose -f docker-compose.production.yml up -d
```

### 11.3 **Performance Issues**

```bash
# Check resource usage
htop
docker stats

# Optimize Docker
docker system prune -a

# Increase memory limits in docker-compose.yml
# Add to services:
#   deploy:
#     resources:
#       limits:
#         memory: 1G
#       reservations:
#         memory: 512M
```

---

## 📋 **PHẦN 12: MAINTENANCE**

### 12.1 **Daily Tasks**

```bash
# Check system health
./health-check.sh

# Check disk usage
df -h

# Check logs for errors
docker-compose -f docker-compose.production.yml logs --tail=100 | grep ERROR
```

### 12.2 **Weekly Tasks**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean Docker
docker system prune -a

# Rotate logs
sudo logrotate /etc/logrotate.d/adaptive-learning

# Check SSL expiry
sudo certbot certificates
```

### 12.3 **Monthly Tasks**

```bash
# Security updates
sudo unattended-upgrades

# Backup verification
# Restore backup to test environment and verify

# Performance review
# Check metrics and optimize if needed

# Update Docker images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

---

## 🎯 **CHECKLIST DEPLOYMENT**

### ✅ **Pre-deployment**
- [ ] Server requirements met
- [ ] Domain DNS pointing to server
- [ ] SSL certificate ready
- [ ] Environment variables configured
- [ ] Database backup strategy planned

### ✅ **Deployment**
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] Environment files configured
- [ ] Docker images built successfully
- [ ] All services running
- [ ] Kong Gateway configured
- [ ] SSL/TLS working
- [ ] Firewall configured

### ✅ **Post-deployment**
- [ ] All health checks passing
- [ ] API endpoints responding
- [ ] User registration/login working
- [ ] Monitoring setup
- [ ] Backup automation configured
- [ ] Security headers present
- [ ] Performance acceptable

### ✅ **Production Ready**
- [ ] Load testing completed
- [ ] Security testing passed
- [ ] Documentation updated
- [ ] Team trained on operations
- [ ] Incident response plan ready

---

## 🎉 **SUMMARY**

Sau khi hoàn thành tất cả các bước trên, bạn sẽ có:

✅ **Complete Microservices Platform** running on production Linux server  
✅ **Kong Gateway** với JWT authentication và rate limiting  
✅ **Auto-scaling** và health monitoring  
✅ **SSL/TLS** encryption với Let's Encrypt  
✅ **Automated backup** và disaster recovery  
✅ **CI/CD pipeline** cho continuous deployment  
✅ **Security hardening** với firewall và security headers  
✅ **Performance optimization** với caching và compression  

**🚀 Your adaptive learning platform is now production-ready!**

---

## 📞 **Support**

Nếu gặp vấn đề trong quá trình deployment:

1. **Check logs**: `docker-compose logs service-name`
2. **Run health check**: `./health-check.sh`
3. **Check documentation**: Refer to service-specific READMEs
4. **Contact team**: Create issue on GitHub repository

**Happy Deploying! 🎊**
