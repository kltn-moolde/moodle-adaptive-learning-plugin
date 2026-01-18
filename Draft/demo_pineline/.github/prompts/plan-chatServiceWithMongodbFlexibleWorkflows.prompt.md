# Plan: Chat Service with MongoDB & Flexible Workflows

Build a FastAPI-based chat service following clustering_service patterns, replacing hardcoded YAML workflows with dynamic, database-driven conversations. Store chat history in MongoDB for AI-powered student analysis via keyword extraction and intent classification.

## Steps

### 1. Create service structure
Initialize chat_service/ folder with main.py, config.py, requirements.txt following clustering_service/main.py async lifespan pattern and clustering_service/config.py environment variables structure

### 2. Build MongoDB models
Create models/conversation.py, models/message.py, models/analyzed_context.py with async Motor client, indexed by `(user_id, course_id, timestamp)`, storing conversations, messages with role/content, and AI-extracted keywords/intents for student analysis

### 3. Implement Moodle API client
Create moodle_api/chat_api_client.py extending clustering_service/moodle_api/custom_api_client.py with methods: `get_quiz_attempt(attempt_id)`, `get_user_grades(user_id, course_id)`, `get_course_activities(course_id)`, `get_user_info(user_id)` - all using dynamic parameters from conversation context instead of hardcoded `attemptid=387`, `course_id=5`

### 4. Build core services layer
Implement services/conversation_service.py for CRUD operations, services/intent_classifier.py using Gemini LLM to replace keyword matching ("Review", "xem kiến thức") with semantic intent detection (`quiz_review`, `view_knowledge`, `generate_quiz`, `general_qa`), services/keyword_extractor.py to analyze messages and extract learning-related keywords ("hàm bậc 2", "đạo hàm", "tích phân") for student strength/weakness profiling

### 5. Create REST API endpoints
Define FastAPI routes in main.py: `POST /api/chat/student/message`, `POST /api/chat/teacher/message`, `GET /api/chat/conversations/{conversation_id}/history`, `GET /api/chat/students/{student_id}/analysis`, `POST /api/chat/teacher/quiz-generate` (calls existing API with dynamic `course_id`, `topic`, `difficulty` from context), all accepting `user_id`, `course_id`, `conversation_id` as parameters

### 6. Implement student features
Build handlers in handlers/student_handler.py: `handle_general_qa()` with RAG from course content, `handle_quiz_review(attempt_id)` dynamically fetching from Moodle API, `handle_view_grades(user_id, course_id)` showing personal performance, all storing messages with extracted keywords to models/analyzed_context.py

### 7. Implement teacher features
Build handlers in handlers/teacher_handler.py: `handle_class_overview(course_id)` aggregating student data, `handle_student_analysis(student_id)` querying analyzed keywords from chat history to identify strengths/weaknesses, `handle_quiz_generation()` calling existing quiz API `http://139.99.103.223:5003/api/ai/generate-and-import` with teacher-specified parameters, `handle_general_teacher_qa()` for class management questions

## Further Considerations

### 1. Keyword constraint strategy
Should keyword extraction focus on specific learning objectives (e.g., "quadratic functions", "derivatives") or be broad? Recommend defining a taxonomy of allowed keywords per course in config.py or fetching from course metadata

### 2. Context window management
For conversation history, use sliding window (last N messages) or relevance-based retrieval? Suggest implementing both: recent 20 messages for immediate context + semantic search across full history for deep analysis

### 3. Migration from YAML workflows
The Dify workflows can call this service via HTTP Request nodes: replace inline LLM+code logic with `POST http://localhost:5000/api/chat/student/message` passing `user_id`, `course_id`, `message`. Keep Dify for UI/orchestration, move business logic to this service

## Database Schema

### Collection 1: `chat_conversations`
```python
{
    "_id": ObjectId,
    "conversation_id": str,  # UUID
    "user_id": int,          # Moodle user ID
    "course_id": int,        # Moodle course ID
    "user_type": str,        # "student" or "teacher"
    "created_at": datetime,
    "updated_at": datetime,
    "metadata": {
        "session_id": str,   # Dify session ID
        "user_agent": str,
        "ip_address": str
    }
}

# Indexes:
# - (user_id, course_id, user_type)
# - (conversation_id) unique
# - (updated_at) descending
```

### Collection 2: `chat_messages`
```python
{
    "_id": ObjectId,
    "conversation_id": str,  # FK to chat_conversations
    "message_id": str,       # UUID
    "role": str,             # "user" or "assistant"
    "content": str,          # Message text
    "timestamp": datetime,
    "metadata": {
        "intent": str,       # "general_qa", "review_quiz", "view_knowledge", "generate_quiz"
        "context": dict,     # Intent-specific data
        "llm_model": str,    # "gemini-2.5-flash"
        "tokens_used": int,
        "latency_ms": int
    }
}

# Indexes:
# - (conversation_id, timestamp)
# - (timestamp) descending for recent queries
```

### Collection 3: `chat_analyzed_context`
```python
{
    "_id": ObjectId,
    "user_id": int,
    "course_id": int,
    "message_id": str,       # FK to chat_messages
    "keywords": [            # AI-extracted keywords
        {
            "keyword": str,  # e.g., "hàm bậc 2", "đạo hàm"
            "category": str, # e.g., "topic", "concept", "difficulty"
            "confidence": float
        }
    ],
    "intent": str,           # Classified intent
    "sentiment": str,        # "positive", "negative", "neutral", "confused"
    "learning_indicators": {
        "understanding_level": float,  # 0-1
        "engagement_score": float,     # 0-1
        "help_needed": bool
    },
    "extracted_at": datetime,
    "llm_model": str
}

# Indexes:
# - (user_id, course_id, extracted_at)
# - (keywords.keyword)
# - (message_id) unique
```

## Technology Stack

- **Framework**: FastAPI (async/await)
- **Database**: MongoDB with Motor (AsyncIOMotorClient)
- **HTTP Client**: httpx for Moodle API
- **LLM**: google-generativeai (Gemini 2.5 Flash)
- **Data Processing**: pandas, numpy
- **Environment**: python-dotenv, pydantic
- **Testing**: pytest, pytest-asyncio

## API Endpoints Structure

```
POST   /api/chat/conversations
       Body: {user_id, course_id, user_type}
       Response: {conversation_id}

POST   /api/chat/student/message
       Body: {conversation_id, user_id, course_id, message}
       Response: {message_id, response, intent}

POST   /api/chat/teacher/message
       Body: {conversation_id, user_id, course_id, message}
       Response: {message_id, response, intent, action_data}

GET    /api/chat/conversations/{conversation_id}/history
       Query: limit, offset
       Response: {messages: [], total_count}

GET    /api/chat/students/{student_id}/analysis
       Query: course_id, from_date, to_date
       Response: {
           strengths: [keywords],
           weaknesses: [keywords],
           engagement_score: float,
           topics_covered: [topics],
           recommendations: [str]
       }

POST   /api/chat/teacher/quiz-generate
       Body: {course_id, topic, num_questions, difficulty}
       Response: {quiz_url, questions_created}

GET    /api/chat/teacher/class-overview
       Query: course_id
       Response: {
           total_students: int,
           active_students: int,
           common_topics: [str],
           average_engagement: float,
           students_needing_help: [user_ids]
       }

DELETE /api/chat/conversations/{conversation_id}
       Response: {deleted: true}
```

## Configuration Structure (config.py)

```python
# Moodle Configuration
MOODLE_URL = os.getenv("MOODLE_URL", "http://139.99.103.223:9090")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")
MOODLE_CUSTOM_TOKEN = os.getenv("MOODLE_CUSTOM_TOKEN")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chat_service")
COLLECTION_CONVERSATIONS = "chat_conversations"
COLLECTION_MESSAGES = "chat_messages"
COLLECTION_ANALYZED_CONTEXT = "chat_analyzed_context"

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.7

# External APIs
QUIZ_GENERATION_API = os.getenv("QUIZ_GENERATION_API", "http://139.99.103.223:5003/api/ai/generate-and-import")

# Chat Service Configuration
MAX_CONVERSATION_HISTORY = 50  # messages
KEYWORD_EXTRACTION_BATCH_SIZE = 10
CONTEXT_WINDOW_SIZE = 20  # for LLM context
ANALYSIS_MIN_MESSAGES = 5  # minimum messages for student analysis

# FastAPI Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
API_TITLE = "Chat Service API"
API_VERSION = "1.0.0"
```

## Features to Remove from YAML (Hardcoded Elements)

### From Student Chatbot:
- ❌ `attemptid=387` → ✅ Dynamic from user context
- ❌ Hardcoded Moodle URLs → ✅ Config-based
- ❌ Hardcoded wstoken → ✅ Environment variable
- ❌ Case-sensitive "Review" keyword → ✅ LLM intent classification
- ❌ PhET links with IDs 162, 159 → ✅ Fetch from course structure API
- ❌ Message storage URL hardcoded → ✅ Internal MongoDB
- ❌ Fixed topic "hàm số bậc 2" → ✅ Multi-topic support

### From Teacher Chatbot:
- ❌ `course_id=5` hardcoded → ✅ From teacher context
- ❌ Keyword "xem kiến thức" → ✅ Intent classification
- ❌ Keyword "tạo bộ câu hỏi" → ✅ Intent classification
- ❌ Hardcoded PO description → ✅ Fetch from course metadata
- ❌ `limit=20` hardcoded → ✅ Configurable
- ❌ Message storage URL → ✅ Internal MongoDB
- ❌ Fixed language "vi" → ✅ Multi-language support

## Implementation Priority

### Phase 1: Core Infrastructure
1. Setup project structure
2. MongoDB models and connections
3. Basic FastAPI endpoints
4. Moodle API client

### Phase 2: Student Features
1. General Q&A handler
2. Quiz review (dynamic attempt_id)
3. View grades
4. Message storage with keyword extraction

### Phase 3: Teacher Features
1. Student analysis from chat history
2. Class overview aggregation
3. Quiz generation integration
4. General teacher Q&A

### Phase 4: Advanced Features
1. Real-time keyword extraction
2. Student strength/weakness profiling
3. Personalized recommendations
4. Multi-language support
5. Advanced analytics dashboard

## Testing Strategy

1. **Unit Tests**: Test each service, handler, model independently
2. **Integration Tests**: Test API endpoints with mock MongoDB
3. **Moodle API Tests**: Mock external Moodle API calls
4. **Load Tests**: Test with concurrent users and conversations
5. **LLM Tests**: Test intent classification and keyword extraction accuracy
