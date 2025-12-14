# Kong Gateway Documentation

## 🏗️ Kong Gateway Architecture

Kong Gateway thay thế NGINX Gateway với các tính năng mạnh mẽ hơn:

### 🎯 **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                    React App :3000                         │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Requests với JWT
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   KONG GATEWAY                             │
│                     Port: 8000                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ JWT Plugin  │  │ CORS Plugin │  │Rate Limiting│        │
│  │ Validation  │  │   Support   │  │    Plugin   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │ Load Balancing & Routing
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   MICROSERVICES                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │USER SERVICE │  │COURSE SVC   │  │ LTI SERVICE │        │
│  │   :8080     │  │   :8081     │  │    :8082    │        │
│  │(Auth & JWT) │  │(Protected)  │  │  (Mixed)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                │
│               PostgreSQL :5432                             │
└─────────────────────────────────────────────────────────────┘
```

### 🚀 **Quick Start**

#### 1. **Start Kong Gateway**

```powershell
# Navigate to kong-gateway directory
cd kong-gateway

# Start all services
.\start-kong.ps1

# Or manually
docker-compose up -d
.\configure-kong.ps1
```

#### 2. **Verify Services**

```powershell
# Check Kong Gateway
Invoke-RestMethod http://localhost:8000/auth/health

# Check Admin API
Invoke-RestMethod http://localhost:8001

# Access Admin UI
# Open browser: http://localhost:8002

# Access Konga UI
# Open browser: http://localhost:1337
```

### 🔐 **JWT Authentication Flow**

#### 1. **User Login**

```typescript
// Frontend login
const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
});

const data = await response.json();
// data.token contains JWT token for Kong Gateway
```

#### 2. **API Requests with JWT**

```typescript
// Protected API call
const response = await fetch('http://localhost:8000/api/courses', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
```

#### 3. **Kong JWT Validation**

```
1. Client sends request với JWT trong Authorization header
2. Kong Gateway validates JWT signature & expiration
3. Kong extracts user info từ JWT claims
4. Kong forwards request đến backend service
5. Backend service receives validated request
```

### 🛣️ **API Routes & Protection**

| Route | Service | JWT Required | Description |
|-------|---------|--------------|-------------|
| `POST /auth/login` | User Service | ❌ | User login & JWT generation |
| `POST /auth/register` | User Service | ❌ | User registration |
| `GET /auth/validate` | User Service | ✅ | JWT token validation |
| `GET /auth/me` | User Service | ✅ | Current user info |
| `GET /api/users/*` | User Service | ✅ | User management |
| `GET /api/courses/*` | Course Service | ✅ | Course management |
| `POST /lti/login` | LTI Service | ❌ | LTI OIDC login |
| `POST /lti/launch` | LTI Service | ❌ | LTI launch (has own auth) |
| `GET /api/lti/*` | LTI Service | ✅ | LTI API endpoints |

### 🔧 **Configuration Details**

#### **Kong Services Configuration**

```json
{
  "user-service": {
    "url": "http://user-service:8080",
    "routes": ["/auth/*", "/api/users/*"],
    "plugins": ["cors"]
  },
  "course-service": {
    "url": "http://course-service:8081", 
    "routes": ["/api/courses/*"],
    "plugins": ["jwt", "cors"]
  },
  "lti-service": {
    "url": "http://lti-service:8082",
    "routes": ["/lti/*", "/api/lti/*"],
    "plugins": ["cors"]
  }
}
```

#### **JWT Consumer Configuration**

```json
{
  "username": "adaptive-learning-app",
  "key": "adaptive-learning-issuer",
  "secret": "your-super-secret-jwt-key-for-kong-gateway-2024",
  "algorithm": "HS256"
}
```

### 📊 **Management UIs**

#### 1. **Kong Manager (Built-in)**
- URL: http://localhost:8002
- Features: Service & Route management, Plugin configuration
- Authentication: None (development)

#### 2. **Konga (Third-party)**
- URL: http://localhost:1337
- Features: Advanced UI, Dashboard, Monitoring
- Setup: Auto-configured in docker-compose

#### 3. **Admin API**
- URL: http://localhost:8001
- Features: RESTful API for Kong configuration
- Documentation: Kong Admin API docs

### 🔍 **Monitoring & Debugging**

#### **Health Checks**

```powershell
# Kong Gateway status
curl http://localhost:8001/status

# Service health checks
curl http://localhost:8000/auth/health
curl http://localhost:8000/api/courses/health
curl http://localhost:8000/lti/config
```

#### **Kong Admin API Examples**

```powershell
# List all services
Invoke-RestMethod http://localhost:8001/services

# List all routes  
Invoke-RestMethod http://localhost:8001/routes

# List all consumers
Invoke-RestMethod http://localhost:8001/consumers

# List plugins
Invoke-RestMethod http://localhost:8001/plugins
```

#### **Debug JWT Issues**

```powershell
# Test JWT validation directly
$headers = @{
    'Authorization' = 'Bearer your-jwt-token-here'
    'Content-Type' = 'application/json'
}

Invoke-RestMethod -Uri 'http://localhost:8000/api/courses' -Headers $headers
```

### 🔧 **Advanced Configuration**

#### **Rate Limiting Plugin**

```powershell
# Add rate limiting to course service
curl -X POST http://localhost:8001/services/course-service/plugins \
  -d "name=rate-limiting" \
  -d "config.minute=100" \
  -d "config.hour=1000"
```

#### **Request Logging Plugin**

```powershell
# Enable request logging
curl -X POST http://localhost:8001/services/user-service/plugins \
  -d "name=file-log" \
  -d "config.path=/tmp/kong-logs.log"
```

#### **API Key Authentication (Alternative to JWT)**

```powershell
# Enable API key auth for specific route
curl -X POST http://localhost:8001/routes/courses-route/plugins \
  -d "name=key-auth"
```

### 🚨 **Troubleshooting**

#### **Common Issues**

1. **Kong won't start**
   ```powershell
   # Check database connection
   docker-compose logs kong-database
   
   # Check Kong logs
   docker-compose logs kong-gateway
   ```

2. **JWT validation failing**
   ```powershell
   # Check JWT consumer configuration
   curl http://localhost:8001/consumers/adaptive-learning-app/jwt
   
   # Verify JWT secret matches between Kong and User Service
   ```

3. **Service not reachable**
   ```powershell
   # Check service registration
   curl http://localhost:8001/services/user-service
   
   # Check route configuration
   curl http://localhost:8001/services/user-service/routes
   ```

4. **CORS issues**
   ```powershell
   # Check CORS plugin configuration
   curl http://localhost:8001/services/user-service/plugins
   ```

#### **Reset Kong Configuration**

```powershell
# Stop services
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Restart and reconfigure
.\start-kong.ps1
```

### 🔄 **Migration from NGINX Gateway**

#### **Key Differences**

| Feature | NGINX Gateway | Kong Gateway |
|---------|---------------|--------------|
| **Configuration** | Static files | Dynamic API |
| **JWT Validation** | Manual/Custom | Built-in plugin |
| **Load Balancing** | Basic | Advanced algorithms |
| **Rate Limiting** | Manual/Custom | Built-in plugin |
| **Monitoring** | Basic logs | Advanced metrics |
| **Plugin Ecosystem** | Limited | 300+ plugins |

#### **Migration Steps**

1. **Stop NGINX Gateway**
   ```powershell
   cd nginx-gateway
   docker-compose down
   ```

2. **Start Kong Gateway**
   ```powershell
   cd kong-gateway
   .\start-kong.ps1
   ```

3. **Update Frontend Configuration**
   ```typescript
   // Change base URL from NGINX to Kong
   const API_BASE_URL = 'http://localhost:8000'; // Kong Gateway
   ```

4. **Update Service Configurations**
   - Remove NGINX-specific configurations
   - Ensure services are accessible from Kong network
   - Update health check endpoints

### 📈 **Performance Optimization**

#### **Kong Tuning**

```yaml
# docker-compose.yml Kong environment
KONG_NGINX_WORKER_PROCESSES: 4
KONG_NGINX_WORKER_CONNECTIONS: 4096
KONG_MEM_CACHE_SIZE: 256m
```

#### **Database Connection Pooling**

```yaml
# PostgreSQL configuration
KONG_PG_MAX_CONCURRENT_QUERIES: 50
KONG_PG_SEMAPHORE_TIMEOUT: 60000
```

#### **Caching Configuration**

```powershell
# Enable response caching
curl -X POST http://localhost:8001/services/course-service/plugins \
  -d "name=proxy-cache" \
  -d "config.content_type=application/json" \
  -d "config.cache_ttl=300"
```

### 🎯 **Best Practices**

1. **Security**
   - Always use HTTPS in production
   - Rotate JWT secrets regularly
   - Implement rate limiting
   - Enable request logging

2. **Performance**
   - Use connection pooling
   - Enable response caching
   - Monitor service health
   - Implement circuit breakers

3. **Development**
   - Use consistent naming conventions
   - Document all routes and plugins
   - Test JWT flows thoroughly
   - Monitor Kong metrics

4. **Production**
   - Use Kong Enterprise for advanced features
   - Implement proper logging and monitoring
   - Use database clustering
   - Configure backup strategies

---

## 🎉 **Summary**

Kong Gateway provides:

✅ **Advanced API Management** - Dynamic configuration, plugin ecosystem  
✅ **Built-in JWT Authentication** - No custom implementation needed  
✅ **Enhanced Security** - Rate limiting, CORS, authentication plugins  
✅ **Better Monitoring** - Admin UI, metrics, logging  
✅ **Scalability** - Load balancing, circuit breakers  
✅ **Developer Experience** - Easy configuration, debugging tools  

**🚀 Ready for enterprise-grade API management!**
