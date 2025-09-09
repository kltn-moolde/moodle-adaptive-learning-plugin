# 🔗 LTI Integration Flow - Python Service ↔ React Frontend ↔ Kong Gateway

## 📋 **Tóm tắt tình trạng tích hợp**

### ✅ **ĐÃ KHỚP - Flow chính xác:**
- **Python LTI Service**: Validate LTI 1.3 từ Moodle → Extract user info → Redirect React với params
- **React Frontend**: Parse LTI params → Call User Service qua Kong → Get JWT → Display dashboard
- **Kong Gateway**: Protect APIs với JWT validation
- **User Service**: Nhận LTI user data → Create/update user → Return JWT token

### 🔄 **CORRECT FLOW:**
```
1. Moodle LTI Launch 
   ↓ POST to Python LTI Service (8002)
2. Python LTI Service
   ↓ Validate LTI 1.3 token, extract user info
   ↓ Redirect to React Frontend với LTI parameters
3. React Frontend (5173)
   ↓ Parse LTI params từ URL
   ↓ Call User Service qua Kong Gateway  
4. Kong Gateway (8000) → User Service (8080)
   ↓ Create/update user từ LTI data
   ↓ Return JWT token
5. React Frontend
   ↓ Store JWT token, display dashboard theo role
   ↓ All future API calls use JWT qua Kong
```

---

## 🌊 **Flow hoạt động hoàn chỉnh:**

### **Step 1: Moodle → Python LTI Service**
```python
# Python nhận LTI 1.3 launch từ Moodle
@router.post("/launch")
async def lti_launch(id_token: str = Form(...)):
    # Validate LTI token
    launch_data = lti_service.decode_token(id_token)
    
    # Extract user info từ LTI token
    user_id = launch_data.get("sub")
    user_name = launch_data.get("name")
    user_email = launch_data.get("email")
    roles = launch_data.get("roles")
    
    # Redirect to React với LTI parameters
    redirect_url = f"{frontend_url}?user_id={user_id}&lis_person_name_full={user_name}..."
```

### **Step 2: React Frontend Parse & Authenticate**
```typescript
// React parse LTI parameters từ URL
const ltiParams = parseLTILaunch(); // từ URL parameters

// Call User Service qua Kong để get JWT
const authResponse = await kongApi.authenticateWithLTI({
    name: ltiParams.lis_person_name_full,
    email: ltiParams.lis_person_contact_email_primary,
    role: mapLTIRoleToSystemRole(ltiParams.roles)
});

// Store JWT token cho future API calls
localStorage.setItem('auth_token', authResponse.token);
```

### **Step 3: User Service Create/Update User**
```java
@PostMapping("/auth/lti")
public ResponseEntity<?> ltiAuthentication(@RequestBody Map<String, Object> ltiData) {
    // Create or update user từ LTI data
    UserDTO user = userService.createLTIUser(name, email, role, ltiUserId, courseId);
    
    // Generate JWT token compatible với Kong
    String token = jwtUtil.generateToken(user);
    
    return AuthResponse.builder()
        .token(token)
        .user(user)
        .build();
}
```

---

## 🏗️ **Kiến trúc Services:**

### **Python LTI Service (Port 8002)**
```python
# Main Endpoints
/login          # LTI 1.3 login initiation
/launch         # LTI 1.3 launch handler → Redirect to React
/dashboard      # HTML dashboard (backup)
/config         # Tool configuration for Moodle
/jwks          # JWT keys

# API Endpoints for React
/api/validate-token    # Validate session token
/api/user-info        # Get user information
/api/session-info     # Get full session data
/api/logs            # Get user logs
```

### **React Frontend (Port 5173)**
```typescript
# Routes
/lti-dashboard/*     # LTI launched from Python service
/*                  # Regular access (fallback)

# Services
ltiService.ts        # Handle Python LTI integration
kongApiService.ts    # Kong Gateway integration

# Components
useLTIAuth()        # React hook for LTI authentication
LTIContext          # Display LTI context info
```

### **Kong Gateway (Port 8000)**
```
# Future API routing through Kong
/users/*    → User Service (8080)
/courses/*  → Course Service (8081)
# All protected by JWT validation
```

---

## 🔐 **Authentication Flow:**

### **LTI Session Token (Python → React)**
```python
# Python creates session token
session_token = lti_service.create_session_token({
    "user_id": user_id,
    "course_id": course_id,
    "launch_id": launch_id,
    "role": roles
})
```

```typescript
// React validates and uses token
const sessionData = parseLTISession();
const isValid = await validateSessionToken(sessionData.token);
const userInfo = await getUserInfoFromSession(sessionData);
```

### **Kong JWT (Future API calls)**
```typescript
// After LTI auth, get Kong JWT for API calls
const authResponse = await kongApi.authenticateWithLTI(ltiUserData);
// All subsequent API calls use Kong JWT
```

---

## 📁 **File Structure Summary:**

```
lti-service-python/
├── app/routers/lti.py           # ✅ Updated with API endpoints
├── app/models/lti_launch.py     # ✅ Database model
└── app/services/lti_service.py  # ✅ LTI logic

FE-service-v2/
├── src/services/
│   ├── ltiService.ts           # ✅ Updated for Python integration
│   └── kongApiService.ts       # ✅ Kong Gateway integration
├── src/components/lti/         # ✅ LTI React components
├── src/AppLTI.tsx             # ✅ Router-based app
├── .env                       # ✅ Environment variables
└── public/lti-test.html       # ✅ Test LTI launch

userservice/
└── Controller/AuthController.java  # ✅ LTI auth endpoint added
```

---

## 🚀 **Cách chạy và test:**

### **1. Start All Services**
```bash
# Python LTI Service
cd lti-service-python
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002

# Kong Gateway
cd kong-gateway
./start-kong.ps1

# User Service  
cd userservice
./mvnw spring-boot:run

# React Frontend
cd FE-service-v2
npm install
npm run dev
```

### **2. Test LTI Flow**
```bash
# Option 1: Use test HTML
Open: http://localhost:5173/lti-test.html
Click "Launch LTI Tool"

# Option 2: Simulate Moodle POST
curl -X POST http://localhost:8002/login \
  -d "login_hint=user123&target_link_uri=http://localhost:8002/launch"
```

### **3. Verify Integration**
```bash
# Check Python LTI service
curl http://localhost:8002/config

# Check React frontend (should redirect to LTI dashboard)
curl http://localhost:5173/lti-dashboard?token=xxx&user_id=123&course_id=456

# Test API endpoints
curl http://localhost:8002/api/validate-token -d '{"token":"xxx"}'
curl http://localhost:8002/api/user-info?token=xxx
```

---

## 🔧 **Còn cần làm:**

### **Immediate Fixes:**
1. ✅ Fix Python imports (LTILaunch model, logger)
2. ✅ Update React to use session token flow
3. ✅ Add API endpoints to Python service
4. ✅ Create Router-based React app

### **Next Steps:**
1. 🔄 Test end-to-end LTI flow
2. 🔄 Connect Kong Gateway for API calls
3. 🔄 Add proper error handling
4. 🔄 Add user role management
5. 🔄 Production deployment testing

---

## 📞 **Debug Commands:**

```bash
# Check Python service logs
tail -f lti-service-python/logs/app.log

# Check React console
Open Browser Developer Tools → Console

# Check Kong Gateway
curl http://localhost:8001/services

# Test database
# Connect to PostgreSQL and check lti_launches table
```

---

**✅ HIỆN TẠI**: LTI service Python và React frontend đã được cấu hình để hoạt động cùng nhau thông qua session token flow.

**🎯 MỤC TIÊU**: Tạo ra một hệ thống LTI hoàn chỉnh cho phép Moodle launch external tool một cách seamless với authentication qua Kong Gateway.
