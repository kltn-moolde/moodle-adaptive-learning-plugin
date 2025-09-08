# NGINX Gateway for Linux Deployment

## Overview

NGINX Gateway được thiết kế để chạy trên Linux server với hard-coded IPs thay vì Eureka service discovery. Hệ thống này cung cấp high-performance reverse proxy cho microservices architecture.

## Architecture

```
Internet → NGINX Gateway (Linux) → Backend Services
    ↓
- User Service (192.168.1.100:8086)
- Course Service (192.168.1.100:8084)  
- Common Service (192.168.1.100:8087)
- LTI Service (192.168.1.100:8082)
- Frontend (192.168.1.200:3000)
```

## Quick Start

### 1. Prerequisites

- Linux server (Ubuntu 20.04+ hoặc CentOS 8+)
- Docker và Docker Compose
- Root access hoặc sudo privileges
- Minimum 2GB RAM, 10GB disk space

### 2. Deploy NGINX Gateway

```bash
# Clone project và navigate to nginx-gateway folder
cd nginx-gateway

# Make scripts executable
chmod +x deploy-linux.sh manage.sh update-ips.sh

# Run deployment
sudo ./deploy-linux.sh
```

### 3. Configure Service IPs

```bash
# Update IPs interactively
./update-ips.sh update

# Or set specific service
./update-ips.sh set user-service 192.168.1.101 8086

# Apply configuration
./update-ips.sh apply

# Restart gateway
./manage.sh restart
```

## Configuration Files

### Main Configuration
- `conf/nginx.conf` - Main NGINX configuration
- `conf.d/routes.conf` - Route definitions
- `conf.d/cors.conf` - CORS settings
- `conf.d/security.conf` - Security headers
- `conf.d/monitoring.conf` - Monitoring endpoints

### Environment
- `config.env` - IP và port configuration
- `docker-compose.yml` - Docker services
- `.env` - Environment variables

## Service Management

### Basic Commands

```bash
# Start gateway
./manage.sh start

# Stop gateway  
./manage.sh stop

# Restart gateway
./manage.sh restart

# Check status
./manage.sh status

# View logs
./manage.sh logs

# Follow logs
./manage.sh logs -f

# Check health
./manage.sh health

# Reload NGINX config
./manage.sh reload
```

### System Service

```bash
# Start with systemd
sudo systemctl start nginx-gateway

# Enable auto-start
sudo systemctl enable nginx-gateway

# Check status
sudo systemctl status nginx-gateway
```

## IP Configuration

### Default IPs

| Service | Default IP:Port | Purpose |
|---------|----------------|---------|
| User Service | 192.168.1.100:8086 | User management |
| Course Service | 192.168.1.100:8084 | Course management |
| Common Service | 192.168.1.100:8087 | Common utilities |
| LTI Service | 192.168.1.100:8082 | LTI integration |
| Frontend | 192.168.1.200:3000 | React frontend |
| Gateway | 192.168.1.50:80/443 | NGINX Gateway |

### Updating IPs

1. **Interactive Update:**
   ```bash
   ./update-ips.sh update
   ```

2. **Auto Detection:**
   ```bash
   ./update-ips.sh auto
   ```

3. **Manual Setting:**
   ```bash
   ./update-ips.sh set user-service 10.0.0.10 8086
   ./update-ips.sh apply
   ```

4. **View Current Config:**
   ```bash
   ./update-ips.sh show
   ```

## SSL Configuration

### Self-Signed Certificates (Default)
Deployment script tự động tạo self-signed certificates:
- Certificate: `/etc/ssl/certs/nginx-selfsigned.crt`
- Private Key: `/etc/ssl/private/nginx-selfsigned.key`

### Production Certificates
Để sử dụng production certificates:

1. **Let's Encrypt:**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot --nginx -d your-domain.com
   ```

2. **Manual Certificates:**
   ```bash
   # Copy your certificates
   sudo cp your-cert.crt /etc/ssl/certs/nginx-selfsigned.crt
   sudo cp your-key.key /etc/ssl/private/nginx-selfsigned.key
   
   # Restart gateway
   ./manage.sh restart
   ```

## Monitoring

### Prometheus Metrics
- URL: `http://your-server:9090`
- Metrics endpoint: `http://your-server/nginx_status`

### Grafana Dashboard
- URL: `http://your-server:3001`
- Default login: `admin/admin123`

### Health Check
- Gateway health: `http://your-server/health`
- Service health: `./manage.sh health`

## Load Balancing

### Multiple Backend Instances

Edit `conf/nginx.conf` để thêm multiple servers:

```nginx
upstream user-service {
    server 192.168.1.100:8086 weight=1;
    server 192.168.1.101:8086 weight=1;
    server 192.168.1.102:8086 weight=1;
    keepalive 32;
}
```

### Health Checks

```nginx
upstream user-service {
    server 192.168.1.100:8086 max_fails=3 fail_timeout=30s;
    server 192.168.1.101:8086 max_fails=3 fail_timeout=30s backup;
    keepalive 32;
}
```

## Performance Tuning

### NGINX Optimization

Edit `conf/nginx.conf`:

```nginx
worker_processes auto;
worker_connections 2048;

# For high traffic
client_max_body_size 500M;
keepalive_timeout 65;
keepalive_requests 1000;

# Buffer sizes
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;
```

### System Optimization

```bash
# Increase file limits
echo "fs.file-max = 65535" >> /etc/sysctl.conf

# TCP optimization
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf

# Apply changes
sysctl -p
```

## Troubleshooting

### Common Issues

1. **Service Unreachable:**
   ```bash
   # Check service connectivity
   curl -I http://192.168.1.100:8086/actuator/health
   
   # Update IPs
   ./update-ips.sh show
   ./update-ips.sh update
   ```

2. **SSL Certificate Errors:**
   ```bash
   # Check certificates
   openssl x509 -in /etc/ssl/certs/nginx-selfsigned.crt -text -noout
   
   # Regenerate if needed
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout /etc/ssl/private/nginx-selfsigned.key \
     -out /etc/ssl/certs/nginx-selfsigned.crt
   ```

3. **Configuration Errors:**
   ```bash
   # Test NGINX config
   ./manage.sh test
   
   # View detailed logs
   ./manage.sh logs
   ```

### Log Locations

- NGINX logs: `/opt/nginx-gateway/logs/`
- Docker logs: `docker logs nginx-gateway`
- System logs: `journalctl -u nginx-gateway`

### Performance Issues

```bash
# Check resource usage
./manage.sh status

# Monitor real-time metrics
docker stats

# Check connection count
ss -tuln | grep :80
```

## Backup và Recovery

### Configuration Backup

```bash
# Create backup
./manage.sh backup

# Manual backup
sudo cp -r /opt/nginx-gateway /opt/nginx-gateway-backup-$(date +%Y%m%d)
```

### Recovery

```bash
# Stop services
./manage.sh stop

# Restore configuration
sudo cp -r /opt/nginx-gateway-backup-20240101 /opt/nginx-gateway

# Start services
./manage.sh start
```

## Security

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Rate Limiting

Edit `conf.d/routes.conf`:

```nginx
# Adjust rate limits
limit_req zone=api_limit burst=50 nodelay;
limit_req zone=auth_limit burst=20 nodelay;
```

### Security Headers

Configured in `conf.d/security.conf`:
- HSTS
- XSS Protection
- Content Security Policy
- Frame Options

## Migration from Spring Cloud Gateway

### Performance Comparison

| Metric | Spring Cloud Gateway | NGINX Gateway |
|--------|---------------------|---------------|
| Memory Usage | ~512MB | ~10MB |
| Startup Time | ~45s | ~2s |
| Throughput | ~2K RPS | ~20K RPS |
| Latency | ~50ms | ~5ms |

### Migration Steps

1. Deploy NGINX Gateway alongside existing gateway
2. Update frontend to use NGINX endpoints
3. Monitor performance và stability
4. Gradually migrate traffic
5. Decommission Spring Cloud Gateway

## Support

### Documentation
- NGINX Documentation: https://nginx.org/en/docs/
- Docker Documentation: https://docs.docker.com/

### Contact
- Project Repository: [Your repo URL]
- Issues: [Your issues URL]

---

*Last updated: $(date)*
