# NGINX Gateway for Microservices

NGINX-based API Gateway thay thế cho Spring Cloud Gateway, nhẹ hơn và hiệu suất cao hơn.

## Cấu trúc thư mục

```
nginx-gateway/
├── conf/
│   ├── nginx.conf          # Cấu hình chính
│   ├── routes.conf         # Định tuyến API
│   ├── cors.conf           # Cấu hình CORS
│   ├── security.conf       # Bảo mật
│   ├── load-balancing.conf # Load balancing
│   └── monitoring.conf     # Monitoring & logging
├── ssl/                    # SSL certificates
├── logs/                   # Log files
├── errors/                 # Custom error pages
├── docker-compose.yml      # Docker deployment
├── Dockerfile             # Docker image
└── scripts/               # Start/stop scripts
```

## Tính năng

### ✅ Đã hoàn thành
- **Load Balancing**: Phân tải với health checks
- **CORS**: Hỗ trợ Cross-Origin requests
- **Security Headers**: XSS, CSRF protection
- **Rate Limiting**: Giới hạn request rate
- **Monitoring**: Health checks và status endpoints
- **Logging**: JSON format logs cho ELK stack
- **Docker Support**: Container deployment
- **Windows Scripts**: Easy start/stop

### 🚀 Ưu điểm so với Spring Cloud Gateway
- **Hiệu suất cao**: ~10x faster, ít RAM hơn
- **Đơn giản**: Configuration file thay vì code
- **Ổn định**: Battle-tested trong production
- **Monitoring**: Built-in metrics và logging
- **Caching**: Static file caching
- **SSL Termination**: HTTPS support

## Cài đặt và chạy

### Option 1: Windows Native

1. **Cài đặt NGINX**:
   ```bash
   # Download từ http://nginx.org/en/download.html
   # Hoặc dùng Chocolatey
   choco install nginx
   ```

2. **Khởi động**:
   ```cmd
   start-nginx.bat
   ```

3. **Dừng**:
   ```cmd
   stop-nginx.bat
   ```

### Option 2: Docker (Recommended)

1. **Khởi động**:
   ```cmd
   start-docker.bat
   ```

2. **Dừng**:
   ```cmd
   stop-docker.bat
   ```

## Endpoints

### API Gateway
- **Base URL**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **Eureka**: http://localhost:8080/eureka/

### Microservices Routes
- **User Service**: http://localhost:8080/api/users/
- **Course Service**: http://localhost:8080/api/courses/
- **Common Service**: http://localhost:8080/api/common/
- **LTI Service**: http://localhost:8080/lti/

### Monitoring
- **NGINX Status**: http://localhost:8081/nginx_status
- **Detailed Health**: http://localhost:8081/health/detailed
- **Prometheus Metrics**: http://localhost:9113/metrics

## Cấu hình

### 1. Thay đổi upstream servers
Chỉnh sửa `conf/nginx.conf`:
```nginx
upstream user-service {
    server 127.0.0.1:8086;
    server 127.0.0.1:8186;  # Thêm instance
}
```

### 2. Rate limiting
Chỉnh sửa `conf/nginx.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### 3. CORS domains
Chỉnh sửa `conf/cors.conf`:
```nginx
~^https?://yourdomain\.com$ $http_origin;
```

### 4. SSL/HTTPS
1. Đặt certificates vào `ssl/`
2. Uncomment SSL config trong `routes.conf`

## Load Balancing

### Phương pháp
- **least_conn**: Ít connection nhất
- **ip_hash**: Sticky sessions
- **hash**: Custom hash key
- **random**: Random selection

### Health Checks
- **max_fails**: 3 (số lần fail tối đa)
- **fail_timeout**: 30s (thời gian chờ)
- **weight**: Load balancing weight

## Monitoring & Logging

### Log Files
- **Access Log**: `logs/access.log`
- **Error Log**: `logs/error.log`
- **JSON Log**: `logs/access.json` (ELK compatible)

### Metrics
- Response times
- Error rates
- Upstream status
- Connection counts

### Alerts
Có thể tích hợp với:
- Prometheus + Grafana
- ELK Stack
- Datadog, New Relic

## Troubleshooting

### 1. NGINX không start
```bash
# Check config
nginx -t -c conf/nginx.conf

# Check ports
netstat -an | find "8080"
```

### 2. Microservice connection fails
```bash
# Test upstream
curl http://localhost:8086/health

# Check NGINX error log
tail -f logs/error.log
```

### 3. CORS issues
- Kiểm tra `cors.conf`
- Check browser dev tools
- Verify allowed origins

### 4. Rate limiting
- Adjust rate in `nginx.conf`
- Check client IP
- Monitor rate limit logs

## Performance Tuning

### Worker Processes
```nginx
worker_processes auto;  # = CPU cores
worker_connections 1024;
```

### Keepalive
```nginx
keepalive 32;
keepalive_requests 100;
keepalive_timeout 60s;
```

### Caching
```nginx
proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone=my_cache:10m;
proxy_cache my_cache;
```

## So sánh với Spring Cloud Gateway

| Feature | NGINX | Spring Cloud Gateway |
|---------|--------|---------------------|
| Memory | ~10MB | ~500MB |
| Startup | <1s | ~30s |
| Throughput | 50k RPS | 5k RPS |
| Config | Files | Code + Rebuild |
| Hot Reload | ✅ | ❌ |
| Caching | ✅ | Limited |
| SSL Termination | ✅ | ✅ |
| Service Discovery | Manual/Script | Auto |

## Migration từ Spring Cloud Gateway

1. **Backup** gatewayservice hiện tại
2. **Map routes** từ Java sang NGINX config
3. **Test** từng route riêng lẻ
4. **Deploy** NGINX gateway
5. **Switch** traffic dần dần
6. **Monitor** và adjust performance

## Next Steps

1. **Service Discovery Integration**: Script auto-update upstreams từ Eureka
2. **SSL/HTTPS**: Production SSL setup
3. **Caching Layer**: Redis/Memcached integration
4. **Monitoring**: Prometheus metrics export
5. **Security**: WAF rules, DDoS protection
