# 🚀 Hướng Dẫn Deployment Adaptive Learning Platform

## 📋 Tổng Quan

Hệ thống bao gồm:
- **User Service** (Spring Boot): Xử lý authentication và user management
- **LTI Service** (Python FastAPI): Xử lý LTI 1.3 integration với Moodle
- **Frontend Service** (React + Vite): Giao diện người dùng
- **Kong Gateway**: API Gateway với DB-less mode
- **Docker Compose**: Orchestration cho production

## 🔧 Chuẩn Bị

### 1. Yêu Cầu Server
- Ubuntu 20.04+ hoặc Debian 11+
- 4GB RAM, 20GB disk space
- Docker và Docker Compose đã cài đặt
- Domain name (khuyến khích)

### 2. Chuẩn Bị Docker Hub
```bash
# Tạo repositories trên Docker Hub:
# - your-username/adaptive-learning-user-service
# - your-username/adaptive-learning-lti-service  
# - your-username/adaptive-learning-frontend
```

### 3. Chuẩn Bị GitHub Secrets
Vào GitHub Repository Settings > Secrets and variables > Actions, thêm:
```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password
SERVER_HOST=your-server-ip
SERVER_USER=your-server-username
SERVER_SSH_KEY=your-private-ssh-key
SERVER_PORT=22 (optional)
```

## 🏗️ Bước 1: Setup Server

### Tự Động (Khuyến nghị)
```bash
# Trên server
wget https://raw.githubusercontent.com/LocNguyenSGU/moodle-adaptive-learning-plugin/main/deploy/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

### Thủ Công
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
sudo mkdir -p /opt/adaptive-learning
sudo chown $USER:$USER /opt/adaptive-learning
cd /opt/adaptive-learning
git clone https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin.git .
```

## ⚙️ Bước 2: Cấu Hình

### 1. Cập nhật Environment Variables
```bash
cd /opt/adaptive-learning
cp .env.production .env

# Sửa file .env với editor
nano .env
```

**Các giá trị quan trọng cần thay đổi:**
```bash
# Docker Registry
DOCKER_REGISTRY=your-dockerhub-username

# Domain URLs
API_BASE_URL=https://your-domain.com
FRONTEND_URL=https://your-domain.com
LTI_SERVICE_URL=https://your-domain.com/lti
USER_SERVICE_URL=https://your-domain.com/auth

# Security (QUAN TRỌNG!)
JWT_SECRET=your-super-secret-jwt-key-change-this

# Database (Production)
DATABASE_URL=jdbc:postgresql://your-db-host:5432/adaptive_learning

# Moodle Integration
LTI_ISSUER=https://your-moodle-domain/moodle
LTI_AUTH_URL=https://your-moodle-domain/moodle/mod/lti/auth.php
LTI_TOKEN_URL=https://your-moodle-domain/moodle/mod/lti/token.php
LTI_KEYSET_URL=https://your-moodle-domain/moodle/mod/lti/certs.php
MOODLE_API_URL=https://your-moodle-domain/moodle/webservice/rest/server.php
MOODLE_API_TOKEN=your-moodle-api-token
```

### 2. Cập nhật Nginx Configuration
```bash
# Sửa domain trong nginx config
sudo nano /etc/nginx/sites-available/adaptive-learning

# Thay your-domain.com bằng domain thật
# Restart nginx
sudo systemctl restart nginx
```

## 🚀 Bước 3: Deploy

### Phương Pháp 1: CI/CD với GitHub Actions (Khuyến nghị)

1. **Push code lên GitHub**:
   ```bash
   git add .
   git commit -m "Setup production deployment"
   git push origin main
   ```

2. **GitHub Actions sẽ tự động**:
   - Build Docker images
   - Push lên Docker Hub
   - Deploy lên server

### Phương Pháp 2: Deploy Thủ Công

```bash
# Trên server
cd /opt/adaptive-learning

# Pull latest code
git pull origin main

# Pull Docker images từ Docker Hub
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🔒 Bước 4: Setup SSL

```bash
# Install Certbot SSL
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Thêm dòng:
0 12 * * * /usr/bin/certbot renew --quiet
```

## ✅ Bước 5: Verification

### Health Checks
```bash
# Kong Gateway
curl https://your-domain.com/api/

# User Service
curl https://your-domain.com/auth/health

# LTI Service
curl https://your-domain.com/lti/health

# Frontend
curl https://your-domain.com/
```

### Service Status
```bash
# Check containers
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# System service
sudo systemctl status adaptive-learning
```

## 🛠️ Maintenance

### Update Application
```bash
# Automatic via GitHub Actions (push to main)
git push origin main

# Manual update
cd /opt/adaptive-learning
./deploy/deploy.sh
```

### Backup
```bash
# Backup configuration
tar -czf adaptive-learning-backup-$(date +%Y%m%d).tar.gz /opt/adaptive-learning/.env /opt/adaptive-learning/kong-gateway/config

# Restore
tar -xzf adaptive-learning-backup-YYYYMMDD.tar.gz -C /
```

### Monitoring
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Cleanup
docker system prune -f
```

## 🔧 Troubleshooting

### Containers không start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check available ports
sudo netstat -tulpn | grep :8000

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Kong Gateway lỗi
```bash
# Check Kong config
docker exec -it adaptive-learning-kong-gateway-1 kong config parse /kong/declarative/kong.yml

# Reload Kong config
docker exec -it adaptive-learning-kong-gateway-1 kong reload
```

### SSL Issues
```bash
# Renew SSL manually
sudo certbot renew

# Check SSL status
sudo certbot certificates
```

## 📞 Support

- **Repository**: https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin
- **Issues**: https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin/issues
- **Documentation**: https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin/wiki

## 📝 Checklist Deploy

- [ ] Server có Docker và Docker Compose
- [ ] Clone repository về `/opt/adaptive-learning`
- [ ] Cập nhật `.env` với giá trị production
- [ ] Setup Docker Hub repositories
- [ ] Configure GitHub Secrets
- [ ] Setup Nginx reverse proxy
- [ ] Chạy deployment (CI/CD hoặc manual)
- [ ] Setup SSL với Certbot
- [ ] Verify tất cả services
- [ ] Test LTI integration với Moodle
- [ ] Setup monitoring và backup

**🎉 Chúc mừng! Hệ thống đã sẵn sàng production!**