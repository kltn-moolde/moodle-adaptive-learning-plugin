# Setup Guide

## Prerequisites

- **Node.js**: Version 20 or higher
- **npm**: Version 9 or higher
- **Docker**: For Kong Gateway (optional)
- **Moodle**: Instance with LTI support
- **Backend Services**: User Service, Course Service, ML Service

## Local Development Setup

### 1. Install Dependencies

```bash
# Install npm packages
npm install

# Verify installation
npm list --depth=0
```

### 2. Configure Environment

Create `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# API Gateway
VITE_KONG_GATEWAY_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000

# Moodle
VITE_MOODLE_URL=https://your-moodle-instance.com
VITE_MOODLE_TOKEN=your_moodle_webservice_token

# Application
VITE_APP_NAME=Adaptive Learning Frontend
VITE_APP_ENV=development
```

### 3. Start Backend Services

#### Option A: Docker Compose (Recommended)

```bash
cd ../kong-gateway
docker-compose up -d
```

#### Option B: Individual Services

```bash
# Terminal 1: Start Kong Gateway
cd ../kong-gateway
./start-kong.ps1

# Terminal 2: Start User Service
cd ../userservice
./mvnw spring-boot:run

# Terminal 3: Start Course Service
cd ../courseservice
./mvnw spring-boot:run

# Terminal 4: Start ML Service (if available)
cd ../ml-service
python app.py
```

### 4. Verify Backend Services

Check services are running:

```bash
# Kong Gateway
curl http://localhost:8000/auth/health

# User Service
curl http://localhost:8080/health

# Course Service
curl http://localhost:8081/health
```

### 5. Start Frontend Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

Open browser and verify:
- Application loads without errors
- No console errors
- Network tab shows API calls

### 6. Test LTI Integration

1. Open `http://localhost:5173/lti-test.html`
2. Select a role:
   - Student
   - Instructor
   - Admin
3. Click "Launch LTI Tool"
4. Verify:
   - Authentication succeeds
   - Correct dashboard loads
   - No console errors

## Moodle Configuration

### 1. Create External Tool

1. Login to Moodle as administrator
2. Navigate: **Site administration** → **Plugins** → **Activity modules** → **External tool** → **Manage tools**
3. Click **Configure a tool manually**
4. Fill in configuration:

**Basic Settings:**
- **Tool name**: `Adaptive Learning Plugin`
- **Tool URL**: `http://localhost:5173/`
- **LTI version**: `LTI 1.3`
- **Launch container**: `In new window`

**Security:**
- **Consumer key**: `moodle_consumer`
- **Shared secret**: Create a secure secret key

**Privacy:**
- ✅ Share launcher's name with tool
- ✅ Share launcher's email with tool
- ✅ Accept grades from the tool

### 2. Configure Course Tool

1. Go to your course in Moodle
2. Click **Add activity or resource**
3. Select **External tool**
4. Configure activity:

**General:**
- **Activity name**: `Adaptive Learning Dashboard`
- **Tool selection**: Select the tool created above
- **Launch URL**: `http://localhost:5173/`

**Privacy:**
- Share user data with tool ✅

**Custom Parameters (Optional):**
```
custom_course_id=$CourseID
custom_user_role=STUDENT
```

### 3. Test LTI Launch

1. Open the course in Moodle
2. Click on "Adaptive Learning Dashboard" activity
3. Verify:
   - Application launches in new window
   - User is authenticated
   - Correct role dashboard loads

## Development Tools

### VS Code Extensions (Recommended)

- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript and JavaScript Language Features

### Browser Extensions

- React Developer Tools
- Redux DevTools (if using Redux)

### Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Debug Frontend",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src",
      "sourceMaps": true
    }
  ]
}
```

## Building for Production

### 1. Build Application

```bash
# Production build
npm run build

# Output in dist/ directory
```

### 2. Preview Production Build

```bash
npm run preview
```

### 3. Verify Build

- Check `dist/` directory
- Verify all assets are bundled
- Test production build
- Check for console errors

## Docker Development

### Run with Docker

```bash
# Build image
docker build -t adaptive-learning-frontend:dev .

# Run container
docker run -p 5173:5173 \
  -e VITE_KONG_GATEWAY_URL=http://host.docker.internal:8000 \
  -e VITE_MOODLE_URL=https://your-moodle.com \
  adaptive-learning-frontend:dev
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5173
lsof -ti:5173

# Kill process
lsof -ti:5173 | xargs kill -9

# Or use different port
# Update vite.config.ts
```

### CORS Errors

**Problem**: CORS errors when calling APIs

**Solution**: Ensure backend services have proper CORS configuration:

```typescript
// Verify backend CORS settings
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Credentials: true
```

### LTI Authentication Failed

**Problem**: "No LTI parameters found"

**Solutions**:
1. Check Moodle configuration
2. Verify tool URL matches exactly
3. Check Moodle logs for errors
4. Ensure backend services are running
5. Test with `lti-test.html`

### API Connection Errors

**Problem**: "Failed to fetch" errors

**Solutions**:
1. Verify Kong Gateway is running: `curl http://localhost:8000/auth/health`
2. Check environment variables in `.env`
3. Verify backend services are accessible
4. Check browser console for detailed errors

### TypeScript Errors

**Problem**: Type errors after pull

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or update TypeScript
npm install --save-dev typescript@latest
```

### Build Errors

**Problem**: Production build fails

**Solutions**:
1. Fix TypeScript errors
2. Ensure all dependencies are installed
3. Check for circular dependencies
4. Verify all environment variables are set
5. Review build logs for specific errors

## Next Steps

After setup is complete:

1. ✅ Start backend services
2. ✅ Start frontend development server
3. ✅ Configure Moodle external tool
4. ✅ Test LTI launch
5. ✅ Verify role-based access
6. ✅ Test API integrations
7. ✅ Check browser console for errors

## Getting Help

If you encounter issues:

1. Check browser console for errors
2. Review backend service logs
3. Verify environment variables
4. Test API endpoints with curl
5. Consult project README files
6. Check GitHub issues (if applicable)

