# Deployment Guide

## Production Deployment

This guide covers deploying the Adaptive Learning Frontend to production environments.

## Prerequisites

- Node.js 20+ installed
- Docker installed (optional)
- Kubernetes cluster configured (for K8s deployment)
- Access to production environment
- Backend services configured

## Build Process

### Local Build

```bash
# Install dependencies
npm ci

# Run tests (if available)
npm test

# Build production bundle
npm run build

# Output in dist/ directory
# Verify: ls -la dist/
```

### Build Verification

Check build output:

```bash
# Check dist directory
ls -la dist/

# Should contain:
# - index.html
# - assets/ (JS, CSS files)
# - vite.svg
```

## Docker Deployment

### Build Docker Image

```bash
# Build image
docker build -t adaptive-learning-frontend:latest .

# Tag for registry
docker tag adaptive-learning-frontend:latest your-registry/adaptive-learning-frontend:latest

# Push to registry
docker push your-registry/adaptive-learning-frontend:latest
```

### Run Docker Container

```bash
# Run container
docker run -d \
  --name adaptive-learning-frontend \
  -p 5173:5173 \
  -e VITE_KONG_GATEWAY_URL=https://api.yourdomain.com \
  -e VITE_MOODLE_URL=https://moodle.yourdomain.com \
  -e VITE_MOODLE_TOKEN=your_token_here \
  adaptive-learning-frontend:latest

# Check logs
docker logs -f adaptive-learning-frontend
```

### Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    image: adaptive-learning-frontend:latest
    ports:
      - "5173:5173"
    environment:
      - VITE_KONG_GATEWAY_URL=https://api.yourdomain.com
      - VITE_MOODLE_URL=https://moodle.yourdomain.com
      - VITE_MOODLE_TOKEN=${MOODLE_TOKEN}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5173"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Deploy:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### Create Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adaptive-learning-frontend
  labels:
    app: adaptive-learning-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adaptive-learning-frontend
  template:
    metadata:
      labels:
        app: adaptive-learning-frontend
    spec:
      containers:
      - name: frontend
        image: adaptive-learning-frontend:latest
        ports:
        - containerPort: 5173
        env:
        - name: VITE_KONG_GATEWAY_URL
          value: "https://api.yourdomain.com"
        - name: VITE_MOODLE_URL
          value: "https://moodle.yourdomain.com"
        - name: VITE_MOODLE_TOKEN
          valueFrom:
            secretKeyRef:
              name: adaptive-learning-secrets
              key: moodle-token
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 5173
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 5173
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: adaptive-learning-frontend-svc
spec:
  selector:
    app: adaptive-learning-frontend
  ports:
  - port: 80
    targetPort: 5173
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: adaptive-learning-secrets
type: Opaque
data:
  moodle-token: <base64-encoded-token>
```

### Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -l app=adaptive-learning-frontend

# Check logs
kubectl logs -f deployment/adaptive-learning-frontend

# Get service URL
kubectl get svc adaptive-learning-frontend-svc
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| VITE_KONG_GATEWAY_URL | Kong API Gateway URL | https://api.yourdomain.com |
| VITE_MOODLE_URL | Moodle instance URL | https://moodle.yourdomain.com |
| VITE_MOODLE_TOKEN | Moodle web service token | abc123... |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_APP_NAME | Application name | Adaptive Learning Frontend |
| VITE_APP_ENV | Environment | production |
| VITE_ENABLE_ANALYTICS | Enable analytics | true |
| VITE_ENABLE_LTI | Enable LTI | true |

### Setting Variables

**Docker:**
```bash
docker run -e VITE_KONG_GATEWAY_URL=https://api.domain.com ...
```

**Kubernetes:**
```yaml
env:
- name: VITE_KONG_GATEWAY_URL
  value: "https://api.yourdomain.com"
```

**Build time:**
```bash
export VITE_KONG_GATEWAY_URL=https://api.yourdomain.com
npm run build
```

## Health Checks

### Application Health

Endpoint: `http://localhost:5173/`

Expected: HTML page loads

### Backend Health

```bash
# Check Kong Gateway
curl https://api.yourdomain.com/auth/health

# Check User Service
curl https://api.yourdomain.com/users/health

# Expected response:
# {"status": "healthy", "timestamp": 1234567890}
```

## Monitoring

### Application Metrics

Monitor:
- Response times
- Error rates
- Request volumes
- User sessions

### Log Monitoring

**Docker:**
```bash
docker logs -f adaptive-learning-frontend
```

**Kubernetes:**
```bash
kubectl logs -f deployment/adaptive-learning-frontend
```

**Application Logs:**
- Browser console errors
- Network request failures
- Authentication errors

### Performance Monitoring

Monitor:
- Page load times
- API response times
- Bundle sizes
- User engagement metrics

## Rollback Strategy

### Docker Rollback

```bash
# Rollback to previous image
docker pull adaptive-learning-frontend:previous
docker stop adaptive-learning-frontend
docker run -d adaptive-learning-frontend:previous
```

### Kubernetes Rollback

```bash
# Check deployment history
kubectl rollout history deployment/adaptive-learning-frontend

# Rollback to previous version
kubectl rollout undo deployment/adaptive-learning-frontend

# Rollback to specific revision
kubectl rollout undo deployment/adaptive-learning-frontend --to-revision=2
```

## Scaling

### Horizontal Scaling

**Kubernetes:**
```bash
# Scale to 5 replicas
kubectl scale deployment adaptive-learning-frontend --replicas=5

# Auto-scaling
kubectl autoscale deployment adaptive-learning-frontend --min=3 --max=10
```

**Docker Compose:**
```yaml
services:
  frontend:
    deploy:
      replicas: 5
```

### Load Balancing

Configure load balancer to:
- Distribute traffic across replicas
- Handle SSL termination
- Set up sticky sessions if needed

## Security

### HTTPS/SSL

Ensure all production deployments use HTTPS:

```nginx
server {
  listen 443 ssl;
  server_name yourdomain.com;
  
  ssl_certificate /path/to/cert.pem;
  ssl_certificate_key /path/to/key.pem;
  
  location / {
    proxy_pass http://frontend:5173;
  }
}
```

### Security Headers

Add security headers:

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";
```

### CORS Configuration

Ensure backend services allow your domain:

```
Access-Control-Allow-Origin: https://yourdomain.com
Access-Control-Allow-Credentials: true
```

## Troubleshooting

### Deployment Issues

**Issue**: Build fails

**Solution**:
```bash
# Clear cache
rm -rf node_modules dist .vite
npm ci
npm run build
```

**Issue**: Container won't start

**Solution**:
```bash
# Check logs
docker logs adaptive-learning-frontend

# Check environment variables
docker exec adaptive-learning-frontend env
```

**Issue**: Kubernetes pods crashing

**Solution**:
```bash
# Describe pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events
```

### Performance Issues

**Issue**: Slow page loads

**Solutions**:
- Enable CDN for static assets
- Enable gzip compression
- Optimize images
- Reduce bundle size

**Issue**: High memory usage

**Solutions**:
- Increase container memory limits
- Scale horizontally
- Optimize code

### Connectivity Issues

**Issue**: Can't reach backend

**Solutions**:
1. Verify network connectivity
2. Check firewall rules
3. Verify backend services are running
4. Check service endpoints

## Maintenance

### Regular Updates

```bash
# Update dependencies
npm update

# Rebuild image
docker build -t adaptive-learning-frontend:latest .

# Deploy updated image
docker push your-registry/adaptive-learning-frontend:latest
```

### Backup Strategy

Backup:
- Environment configuration
- Secrets and tokens
- Deployment configurations

### Monitoring Checklist

- [ ] Application health checks passing
- [ ] Backend services accessible
- [ ] No error logs
- [ ] Performance metrics normal
- [ ] User sessions stable
- [ ] API response times acceptable

## Post-Deployment

After deployment, verify:

1. ✅ Application accessible
2. ✅ No console errors
3. ✅ API calls working
4. ✅ Authentication working
5. ✅ LTI launch working
6. ✅ Role-based access working
7. ✅ All features functional

## Support

For issues or questions:
- Check application logs
- Review backend service logs
- Consult documentation
- Contact development team

