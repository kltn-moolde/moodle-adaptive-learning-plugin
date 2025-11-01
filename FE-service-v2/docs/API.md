# API Documentation

## Base URLs

- **Kong Gateway**: `http://localhost:8000`
- **User Service**: `http://localhost:8080`
- **Moodle**: `https://your-moodle-instance.com`

## Authentication

All API requests (except auth endpoints) require JWT Bearer token:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

## Endpoints

### LTI Authentication

**POST** `/auth/lti`

Authenticate user with LTI parameters from Moodle.

**Request Body:**
```json
{
  "name": "Student Name",
  "email": "student@example.com",
  "roleName": "STUDENT",
  "courseId": 1,
  "ltiUserId": "moodle_123"
}
```

**Response:**
```json
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "name": "Student Name",
    "email": "student@example.com",
    "roleName": "STUDENT"
  }
}
```

### Learning Path - Suggest Action

**POST** `/api/suggest-action`

Get suggested next learning action for user.

**Request Body:**
```json
{
  "userid": 4,
  "courseid": 3
}
```

**Response:**
```json
{
  "user_id": 4,
  "course_id": 3,
  "suggested_action": "watch_video",
  "q_value": 0.95,
  "source_state": {
    "section_id": 2,
    "lesson_name": "Introduction",
    "quiz_level": "medium",
    "complete_rate_bin": 0.5,
    "score_bin": 7
  }
}
```

### Learning Path - AI Explanation

**POST** `/api/learning-path/explain`

Get AI-powered explanation for learning path recommendation.

**Request Body:**
```json
{
  "user_id": "4",
  "course_id": "3",
  "learning_path": {
    "suggested_action": "watch_video",
    "q_value": 0.95,
    "source_state": {
      "section_id": 2,
      "lesson_name": "Introduction",
      "quiz_level": "medium",
      "complete_rate_bin": 0.5,
      "score_bin": 7
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "reason": "AI explanation reason...",
    "current_status": "Your current status...",
    "benefit": "Benefits of this action...",
    "motivation": "Motivational message...",
    "next_steps": ["Step 1", "Step 2", "Step 3"]
  },
  "from_cache": false
}
```

### User Management

**GET** `/api/users?skip=0&limit=100`

Get list of users.

**GET** `/api/users/:id`

Get user by ID.

**GET** `/auth/me`

Get current authenticated user.

### Course Management

**GET** `/api/courses?skip=0&limit=100`

Get list of courses.

**GET** `/api/courses/:id`

Get course by ID.

**POST** `/api/courses`

Create new course.

**Request Body:**
```json
{
  "name": "Course Name",
  "description": "Course Description",
  "instructorId": 1
}
```

**PUT** `/api/courses/:id`

Update course.

**DELETE** `/api/courses/:id`

Delete course.

### Health Check

**GET** `/auth/health`

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "user-service",
  "timestamp": 1234567890
}
```

### LTI Launches

**GET** `/api/lti/launches?skip=0&limit=100`

Get list of LTI launches.

**GET** `/api/lti/user/:userId/launches`

Get LTI launches for specific user.

**GET** `/api/lti/config`

Get LTI configuration.

## Moodle Web Service Integration

### Course Completion

**POST** `/webservice/rest/server.php`

Get course completion status.

**Parameters:**
- `wstoken`: Moodle web service token
- `wsfunction`: `core_completion_get_course_completion_status`
- `courseid`: Course ID
- `userid`: User ID

### Activities Completion

**POST** `/webservice/rest/server.php`

Get activities completion status.

**Parameters:**
- `wstoken`: Moodle web service token
- `wsfunction`: `core_completion_get_activities_completion_status`
- `courseid`: Course ID
- `userid`: User ID

### Grades

**POST** `/webservice/rest/server.php`

Get grade items for user.

**Parameters:**
- `wstoken`: Moodle web service token
- `wsfunction`: `gradereport_user_get_grade_items`
- `courseid`: Course ID
- `userid`: User ID

### Enrolled Users

**POST** `/webservice/rest/server.php`

Get enrolled users in course (for instructors).

**Parameters:**
- `wstoken`: Moodle web service token
- `wsfunction`: `core_enrol_get_enrolled_users`
- `courseid`: Course ID

## Error Responses

All endpoints may return error responses:

**401 Unauthorized:**
```json
{
  "error": "Unauthorized",
  "message": "JWT token missing or invalid"
}
```

**404 Not Found:**
```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

- Standard endpoints: 100 requests/minute
- Auth endpoints: 10 requests/minute
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Pagination

List endpoints support pagination:

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

Example:
```
GET /api/users?skip=0&limit=50
```

