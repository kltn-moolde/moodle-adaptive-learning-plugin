# Microservices với Spring Cloud Eureka

## Cấu trúc Microservices

### 1. Discovery Service (Eureka Server)
- **Port**: 8761
- **URL**: http://localhost:8761
- **Mô tả**: Service discovery cho toàn bộ hệ thống

### 2. Gateway Service (Spring Cloud Gateway)
- **Port**: 8080
- **URL**: http://localhost:8080
- **Mô tả**: API Gateway định tuyến requests tới các microservices

### 3. Các Microservices
- **User Service**: 8086 (đã cấu hình Eureka)
- **Course Service**: 8084 (cần cấu hình)
- **Common Service**: 8087 (cần cấu hình)
- **LTI Service**: 8082 (cần cấu hình)

## Hướng dẫn Setup

### Bước 1: Khởi động theo thứ tự
1. **Discovery Service** (phải khởi động trước)
2. **Gateway Service**
3. **Các microservices khác**

### Bước 2: Sử dụng script tự động
```bash
# Khởi động tất cả services
./start-services.bat

# Dừng tất cả services
./stop-services.bat
```

### Bước 3: Cấu hình từng service để đăng ký với Eureka

#### Cho các service còn lại, thêm vào `pom.xml`:
```xml
<properties>
    <spring-cloud.version>2025.0.0</spring-cloud.version>
</properties>

<dependencies>
    <!-- Thêm dependency này -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
    </dependency>
</dependencies>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

#### Thêm vào Main Application class:
```java
@SpringBootApplication
@EnableDiscoveryClient
public class YourServiceApplication {
    // ...
}
```

#### Cấu hình `application.yml`:
```yaml
spring:
  application:
    name: your-service-name # Đặt tên service

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
    register-with-eureka: true
    fetch-registry: true
  instance:
    prefer-ip-address: true
```

## Tên Services trong Eureka
- `user-service`
- `course-service`
- `common-service`
- `lti-service`
- `gatewayservice`

## Kiểm tra hệ thống

1. **Eureka Dashboard**: http://localhost:8761
2. **Gateway Health**: http://localhost:8080/actuator/health (nếu có actuator)
3. **API qua Gateway**: http://localhost:8080/api/users/... (ví dụ)

## Load Balancing

Gateway sử dụng `lb://service-name` để tự động load balance giữa các instances của cùng một service.

## Troubleshooting

### Service không đăng ký với Eureka
1. Kiểm tra Discovery Service đã khởi động chưa
2. Kiểm tra cấu hình `eureka.client.service-url.defaultZone`
3. Kiểm tra annotation `@EnableDiscoveryClient`

### Gateway không tìm thấy service
1. Kiểm tra service đã đăng ký thành công trong Eureka Dashboard
2. Kiểm tra tên service trong route configuration
3. Kiểm tra URL pattern trong Gateway routes

### CORS Issues
- Gateway đã được cấu hình CORS cho tất cả origins
- Nếu cần custom, chỉnh sửa trong `GatewayConfig.java`
