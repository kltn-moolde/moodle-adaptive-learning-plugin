# Chat Service CRUD API

Simple REST API for DIFY workflows to store/retrieve chat conversations and messages.

## Features

- ✅ CRUD operations for conversations and messages
- ✅ MongoDB storage with indexes
- ✅ Analyzed context support (for LLM keyword extraction)
- ✅ Aggregation API for teacher analytics
- ✅ FastAPI with async/await
- ✅ Swagger UI documentation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your MongoDB URI

# Run
python main.py
```

API docs: http://localhost:5557/docs

## API Endpoints

### Conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations` - List conversations (with filters)
- `GET /api/conversations/{id}` - Get one conversation
- `DELETE /api/conversations/{id}` - Delete conversation

### Messages
- `POST /api/messages` - Create message
- `GET /api/messages?conversation_id={id}` - List messages
- `GET /api/messages/{id}` - Get one message
- `DELETE /api/messages/{id}` - Delete message

### Analyzed Context (LLM keywords)
- `POST /api/analyzed-context` - Save LLM analysis
- `GET /api/analyzed-context?user_id={id}&course_id={id}` - List contexts
- `GET /api/analyzed-context/summary?user_id={id}&course_id={id}` - Aggregated summary

## MongoDB Schema

### chat_conversations
```json
{
  "conversation_id": "uuid",
  "user_id": 10,
  "course_id": 5,
  "user_type": "student|teacher",
  "created_at": "datetime",
  "updated_at": "datetime",
  "metadata": {}
}
```

### chat_messages
```json
{
  "message_id": "uuid",
  "conversation_id": "uuid",
  "role": "user|assistant",
  "content": "message text",
  "timestamp": "datetime",
  "metadata": {}
}
```

### chat_analyzed_context
```json
{
  "context_id": "uuid",
  "user_id": 10,
  "course_id": 5,
  "message_id": "uuid",
  "keywords": [
    {"keyword": "hàm bậc 2", "category": "topic", "confidence": 0.95}
  ],
  "intent": "general_qa",
  "sentiment": "neutral",
  "learning_indicators": {
    "understanding_level": 0.7,
    "engagement_score": 0.8,
    "help_needed": false
  },
  "extracted_at": "datetime"
}
```

## Environment Variables

```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=chat_db
PORT=5557
```

## DIFY Integration

This service is designed to work with DIFY workflows:

1. DIFY HTTP Request nodes call these endpoints
2. Store conversations persistently
3. Enable teacher analytics via aggregation

See `SETUP_GUIDE.md` for complete integration instructions.

## License

MIT
