# System Architecture

## Overview

This is a React-based adaptive learning frontend that integrates with Moodle LMS via LTI (Learning Tools Interoperability) and provides personalized learning paths using AI/ML services.

## Technology Stack

### Frontend
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **Routing**: React Router DOM v6
- **Styling**: Tailwind CSS (via inline classes)
- **HTTP Client**: Fetch API
- **State Management**: React Hooks (useState, useEffect, useContext)

### Backend Services
- **API Gateway**: Kong Gateway
- **User Service**: Spring Boot (Java)
- **Course Service**: Spring Boot (Java)
- **ML Service**: Python (Flask/FastAPI)
- **AI Service**: Google Gemini API

### Integration
- **LMS**: Moodle with LTI 1.3
- **Authentication**: JWT via Kong Gateway
- **Database**: PostgreSQL (via backend services)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Moodle LMS                            │
│                  (Learning Platform)                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ LTI Launch (POST with LTI params)
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│        React Frontend (Port 5173)                       │
│                                                          │
│  ┌────────────────┐  ┌──────────────────────────┐      │
│  │  LTI Service   │  │  Kong API Service        │      │
│  │  - Parse LTI   │  │  - JWT Management        │      │
│  │  - Auth        │  │  - API Calls             │      │
│  └────────────────┘  └──────────────────────────┘      │
│                                                          │
│  ┌────────────────┐  ┌──────────────────────────┐      │
│  │  Learning      │  │  Moodle                  │      │
│  │  Path Service  │  │  API Service             │      │
│  │  - Get Action  │  │  - Grades                │      │
│  │  - Get Explain │  │  - Completion            │      │
│  └────────────────┘  └──────────────────────────┘      │
│                                                          │
│  ┌───────────────────────────────────────────────┐      │
│  │          Dashboard Components                  │      │
│  │  - StudentDashboard                           │      │
│  │  - InstructorDashboard                        │      │
│  │  - AdminDashboard                             │      │
│  └───────────────────────────────────────────────┘      │
└────────┬────────────────────────────────────────────────┘
         │
         │ HTTP/REST API
         │ JWT Bearer Token
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         Kong Gateway (Port 8000)                        │
│    - Request Routing                                    │
│    - JWT Validation                                     │
│    - Rate Limiting                                      │
│    - Load Balancing                                     │
└────────┬────────────────────────────────────────────────┘
         │
    ┌────┴──────────────────────────┐
    │                               │
    ▼                               ▼
┌──────────┐                   ┌──────────────┐
│   User   │                   │  ML/AI       │
│  Service │                   │  Service     │
│  :8080   │                   │  - Q-Learning│
│          │                   │  - AI Explain│
│ - Auth   │                   │  - Analytics │
│ - Users  │                   │              │
└──────────┘                   └──────────────┘
```

## Component Structure

```
src/
├── components/
│   ├── auth/                    # Authentication components
│   │   └── index.tsx
│   ├── lti/                     # LTI-specific components
│   │   └── index.tsx            # useLTIAuth hook, LTILoader, LTIError
│   ├── Header.tsx               # App header with user menu
│   ├── Navigation.tsx            # Sidebar navigation (role-based)
│   ├── DashboardAnalytics.tsx   # Moodle integration analytics
│   └── StudentsLearningPaths.tsx
├── pages/
│   ├── StudentDashboard.tsx      # Student learning path & progress
│   ├── InstructorDashboard.tsx  # Student monitoring & analytics
│   ├── TeacherDashboard.tsx     # Alias for InstructorDashboard
│   ├── AdminDashboard.tsx       # System administration
│   └── Profile.tsx              # User profile management
├── services/
│   ├── kongApiService.ts        # Kong Gateway API integration
│   ├── ltiService.ts            # LTI parameter handling
│   ├── ltiServiceFixed.ts       # Fixed LTI implementation
│   ├── learningPathService.ts   # ML recommendation API
│   ├── learningPathExplanationService.ts # AI explanation API
│   └── moodleApiService.ts      # Moodle web services
├── types/
│   └── index.ts                 # TypeScript type definitions
├── data/
│   └── mockData.ts              # Mock data for development
├── assets/
│   └── react.svg                # Static assets
├── App.tsx                       # Main app component
├── AppLTI.tsx                    # LTI-specific app variant
├── main.tsx                      # Entry point
├── index.css                     # Global styles
└── vite-env.d.ts                 # Vite type definitions
```

## Data Flow

### LTI Launch Flow

```
1. User clicks LTI tool in Moodle
   ↓
2. Moodle sends POST request with LTI parameters
   ↓
3. Frontend receives and parses LTI params
   ↓
4. Frontend calls POST /auth/lti with user data
   ↓
5. User Service creates/updates user, returns JWT
   ↓
6. Frontend stores JWT in localStorage
   ↓
7. Frontend redirects to appropriate dashboard
```

### Learning Path Flow

```
1. Student opens Student Dashboard
   ↓
2. Frontend calls GET /api/suggest-action
   ↓
3. ML Service analyzes student performance
   ↓
4. ML Service returns recommended action
   ↓
5. Frontend displays recommendation
   ↓
6. (Optional) User requests AI explanation
   ↓
7. Frontend calls POST /api/learning-path/explain
   ↓
8. AI Service generates personalized explanation
   ↓
9. Frontend displays AI explanation
```

### Role-Based Access Flow

```
User Role Detection (from LTI)
   ↓
   ├─→ STUDENT → StudentDashboard
   │       ├─ Learning Paths
   │       ├─ Progress Tracking
   │       └─ AI Explanations
   │
   ├─→ INSTRUCTOR → InstructorDashboard
   │       ├─ Student Analytics
   │       ├─ Video Analytics
   │       └─ Action Analytics
   │
   └─→ ADMIN → AdminDashboard
           ├─ User Management
           ├─ System Metrics
           └─ System Settings
```

## Service Integration

### Kong Gateway

**Purpose**: API Gateway for routing and authentication

**Responsibilities**:
- JWT token validation
- Request routing to backend services
- Rate limiting and throttling
- CORS handling

**Configuration**:
- Admin port: `1337`
- Gateway port: `8000`

### User Service

**Purpose**: User authentication and management

**Endpoints**:
- `POST /auth/lti` - LTI authentication
- `POST /auth/login` - Standard login
- `GET /auth/me` - Current user
- `GET /api/users` - List users

### ML/AI Service

**Purpose**: Learning path recommendations and AI explanations

**Endpoints**:
- `POST /api/suggest-action` - Get next action
- `POST /api/learning-path/explain` - AI explanation
- `GET /api/learning-path/teacher-recommendations` - Class analytics

### Moodle Integration

**Purpose**: Synchronize grades and completion data

**Web Services**:
- Course completion status
- Activities completion
- Grade items
- Enrolled users
- Competency reports

## State Management

### Local State
- Component-specific state via `useState`
- Form data, UI toggles, loading states

### Global State
- User authentication via React Context
- Session data in `localStorage`
- LTI parameters in `sessionStorage`

### Cache Strategy
- API responses cached in memory
- JWT tokens in `localStorage`
- User data in `localStorage`

## Security

### Authentication
- JWT tokens via Kong Gateway
- Token validation on every request
- Automatic token refresh
- Logout on 401 errors

### Authorization
- Role-based access control
- Protected routes
- Permission checks before actions
- LTI parameter validation

### Data Protection
- HTTPS in production
- No sensitive data in logs
- Input validation
- XSS prevention

## Performance Optimization

### Code Splitting
- Route-based code splitting
- Lazy loading of heavy components
- Dynamic imports for large modules

### Bundle Optimization
- Tree shaking
- Minification
- Asset optimization
- CDN for static assets

### API Optimization
- Request caching
- Debouncing user input
- Pagination for lists
- Lazy loading images

## Error Handling

### API Errors
- Network errors: Retry mechanism
- 401 errors: Redirect to login
- 404 errors: Show not found
- 500 errors: Show error message

### LTI Errors
- Missing parameters: Show error
- Invalid signature: Reject launch
- Service unavailable: Fallback UI

### User Feedback
- Loading spinners
- Error messages
- Success notifications
- Progress indicators

## Testing Strategy

### Unit Tests
- Service functions
- Utility functions
- Component logic

### Integration Tests
- API service integration
- LTI flow
- Authentication flow

### E2E Tests
- Complete user flows
- Role-based access
- Cross-browser testing

## Deployment

### Development
- Vite dev server
- Hot module replacement
- Development tools

### Staging
- Production build
- Docker container
- Environment variables

### Production
- CDN deployment
- Load balancing
- Monitoring and logging

## Monitoring & Logging

### Client-Side
- Console logs for debugging
- Error tracking
- User analytics
- Performance metrics

### Server-Side
- Kong access logs
- Backend service logs
- Database logs
- Error tracking

## Scalability Considerations

### Frontend
- Code splitting for smaller bundles
- Lazy loading for performance
- CDN for static assets
- Caching strategy

### Backend
- API gateway load balancing
- Database connection pooling
- Caching frequent queries
- Horizontal scaling

