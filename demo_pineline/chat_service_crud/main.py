"""
Chat Service - Simple CRUD API for DIFY
Chỉ lưu/lấy conversations và messages - KHÔNG có LLM logic
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import os
from contextlib import asynccontextmanager

# =============================================================================
# Configuration
# =============================================================================
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "chat_db")

# Global MongoDB client
mongo_client: Optional[AsyncIOMotorClient] = None


# =============================================================================
# Pydantic Models
# =============================================================================
class ConversationCreate(BaseModel):
    user_id: int
    course_id: int
    user_type: str = Field(..., pattern="^(student|teacher)$")  # student hoặc teacher
    metadata: Optional[dict] = {}


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: int
    course_id: int
    user_type: str
    created_at: datetime
    updated_at: datetime
    metadata: dict


class MessageCreate(BaseModel):
    conversation_id: str
    role: str = Field(..., pattern="^(user|assistant)$")  # user hoặc assistant
    content: str
    metadata: Optional[dict] = {}


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: datetime
    metadata: dict


class AnalyzedKeyword(BaseModel):
    keyword: str
    category: str  # topic, concept, difficulty, emotion, action
    confidence: float


class AnalyzedContextCreate(BaseModel):
    user_id: int
    course_id: int
    message_id: str
    keywords: List[AnalyzedKeyword]
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    learning_indicators: Optional[dict] = {}


class AnalyzedContextResponse(BaseModel):
    context_id: str
    user_id: int
    course_id: int
    message_id: str
    keywords: List[AnalyzedKeyword]
    intent: Optional[str]
    sentiment: Optional[str]
    learning_indicators: dict
    extracted_at: datetime


# =============================================================================
# Lifespan - MongoDB Connection
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MongoDB connection lifecycle"""
    global mongo_client
    
    # Startup
    print(f"🔗 Connecting to MongoDB: {MONGODB_URI}")
    mongo_client = AsyncIOMotorClient(MONGODB_URI)
    
    # Test connection
    try:
        await mongo_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        
        # Create indexes
        db = mongo_client[DB_NAME]
        await db.chat_conversations.create_index([("conversation_id", 1)], unique=True)
        await db.chat_conversations.create_index([("user_id", 1), ("course_id", 1)])
        await db.chat_messages.create_index([("message_id", 1)], unique=True)
        await db.chat_messages.create_index([("conversation_id", 1), ("timestamp", -1)])
        await db.chat_analyzed_context.create_index([("user_id", 1), ("course_id", 1)])
        await db.chat_analyzed_context.create_index([("message_id", 1)])
        print("✅ MongoDB indexes created")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    if mongo_client:
        mongo_client.close()
        print("🔌 MongoDB connection closed")


# =============================================================================
# FastAPI App
# =============================================================================
app = FastAPI(
    title="Chat Service CRUD API",
    description="Simple CRUD API for DIFY workflows - No LLM logic",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Get MongoDB database"""
    return mongo_client[DB_NAME]


# =============================================================================
# Conversations CRUD
# =============================================================================
@app.post("/api/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(conv: ConversationCreate):
    """Tạo conversation mới"""
    db = get_db()
    
    conversation_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    doc = {
        "conversation_id": conversation_id,
        "user_id": conv.user_id,
        "course_id": conv.course_id,
        "user_type": conv.user_type,
        "created_at": now,
        "updated_at": now,
        "metadata": conv.metadata or {}
    }
    
    await db.chat_conversations.insert_one(doc)
    
    return ConversationResponse(**doc)


@app.get("/api/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: Optional[int] = None,
    course_id: Optional[int] = None,
    user_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Lấy danh sách conversations (có thể filter)"""
    db = get_db()
    
    query = {}
    if user_id is not None:
        query["user_id"] = user_id
    if course_id is not None:
        query["course_id"] = course_id
    if user_type:
        query["user_type"] = user_type
    
    cursor = db.chat_conversations.find(query).sort("updated_at", -1).limit(limit)
    conversations = await cursor.to_list(length=limit)
    
    # Remove _id field
    for conv in conversations:
        conv.pop("_id", None)
    
    return [ConversationResponse(**conv) for conv in conversations]


@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Lấy 1 conversation theo ID"""
    db = get_db()
    
    conv = await db.chat_conversations.find_one({"conversation_id": conversation_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv.pop("_id", None)
    return ConversationResponse(**conv)


@app.delete("/api/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    """Xóa conversation và tất cả messages liên quan"""
    db = get_db()
    
    # Delete conversation
    result = await db.chat_conversations.delete_one({"conversation_id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete all messages
    await db.chat_messages.delete_many({"conversation_id": conversation_id})
    
    return None


# =============================================================================
# Messages CRUD
# =============================================================================
@app.post("/api/messages", response_model=MessageResponse, status_code=201)
async def create_message(msg: MessageCreate):
    """Tạo message mới và cập nhật conversation updated_at"""
    db = get_db()
    
    # Check conversation exists
    conv = await db.chat_conversations.find_one({"conversation_id": msg.conversation_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    doc = {
        "message_id": message_id,
        "conversation_id": msg.conversation_id,
        "role": msg.role,
        "content": msg.content,
        "timestamp": now,
        "metadata": msg.metadata or {}
    }
    
    await db.chat_messages.insert_one(doc)
    
    # Update conversation updated_at
    await db.chat_conversations.update_one(
        {"conversation_id": msg.conversation_id},
        {"$set": {"updated_at": now}}
    )
    
    doc.pop("_id", None)
    return MessageResponse(**doc)


@app.get("/api/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """Lấy messages của 1 conversation (có phân trang)"""
    db = get_db()
    
    cursor = db.chat_messages.find({"conversation_id": conversation_id}) \
        .sort("timestamp", 1) \
        .skip(skip) \
        .limit(limit)
    
    messages = await cursor.to_list(length=limit)
    
    for msg in messages:
        msg.pop("_id", None)
    
    return [MessageResponse(**msg) for msg in messages]


@app.get("/api/messages/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str):
    """Lấy 1 message theo ID"""
    db = get_db()
    
    msg = await db.chat_messages.find_one({"message_id": message_id})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg.pop("_id", None)
    return MessageResponse(**msg)


@app.delete("/api/messages/{message_id}", status_code=204)
async def delete_message(message_id: str):
    """Xóa 1 message"""
    db = get_db()
    
    result = await db.chat_messages.delete_one({"message_id": message_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return None


# =============================================================================
# Analyzed Context CRUD (cho LLM analysis từ DIFY)
# =============================================================================
@app.post("/api/analyzed-context", response_model=AnalyzedContextResponse, status_code=201)
async def create_analyzed_context(ctx: AnalyzedContextCreate):
    """Lưu kết quả phân tích từ LLM (được gọi từ DIFY workflow)"""
    db = get_db()
    
    context_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    doc = {
        "context_id": context_id,
        "user_id": ctx.user_id,
        "course_id": ctx.course_id,
        "message_id": ctx.message_id,
        "keywords": [kw.dict() for kw in ctx.keywords],
        "intent": ctx.intent,
        "sentiment": ctx.sentiment,
        "learning_indicators": ctx.learning_indicators or {},
        "extracted_at": now
    }
    
    await db.chat_analyzed_context.insert_one(doc)
    
    doc.pop("_id", None)
    return AnalyzedContextResponse(**doc)


@app.get("/api/analyzed-context", response_model=List[AnalyzedContextResponse])
async def get_analyzed_contexts(
    user_id: int,
    course_id: int,
    limit: int = Query(50, ge=1, le=200)
):
    """Lấy analyzed contexts của user trong course (cho teacher xem phân tích)"""
    db = get_db()
    
    cursor = db.chat_analyzed_context.find({
        "user_id": user_id,
        "course_id": course_id
    }).sort("extracted_at", -1).limit(limit)
    
    contexts = await cursor.to_list(length=limit)
    
    for ctx in contexts:
        ctx.pop("_id", None)
    
    return [AnalyzedContextResponse(**ctx) for ctx in contexts]


@app.get("/api/analyzed-context/summary")
async def get_user_analysis_summary(user_id: int, course_id: int):
    """
    Tổng hợp phân tích học sinh (teacher dùng để xem overview)
    Aggregation từ analyzed_context
    """
    db = get_db()
    
    # Aggregate keywords
    keyword_pipeline = [
        {"$match": {"user_id": user_id, "course_id": course_id}},
        {"$unwind": "$keywords"},
        {"$group": {
            "_id": {
                "keyword": "$keywords.keyword",
                "category": "$keywords.category"
            },
            "count": {"$sum": 1},
            "avg_confidence": {"$avg": "$keywords.confidence"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    
    keywords = await db.chat_analyzed_context.aggregate(keyword_pipeline).to_list(length=20)
    
    # Aggregate intents
    intent_pipeline = [
        {"$match": {"user_id": user_id, "course_id": course_id}},
        {"$group": {
            "_id": "$intent",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    intents = await db.chat_analyzed_context.aggregate(intent_pipeline).to_list(length=10)
    
    # Aggregate learning indicators
    indicators_pipeline = [
        {"$match": {"user_id": user_id, "course_id": course_id}},
        {"$group": {
            "_id": None,
            "avg_understanding": {"$avg": "$learning_indicators.understanding_level"},
            "avg_engagement": {"$avg": "$learning_indicators.engagement_score"},
            "help_needed_count": {
                "$sum": {"$cond": [{"$eq": ["$learning_indicators.help_needed", True]}, 1, 0]}
            }
        }}
    ]
    
    indicators = await db.chat_analyzed_context.aggregate(indicators_pipeline).to_list(length=1)
    
    return {
        "user_id": user_id,
        "course_id": course_id,
        "top_keywords": keywords,
        "intent_distribution": intents,
        "learning_indicators": indicators[0] if indicators else {}
    }


# =============================================================================
# Health Check
# =============================================================================
@app.get("/")
async def root():
    return {
        "service": "Chat Service CRUD API",
        "status": "running",
        "version": "1.0.0",
        "description": "Simple CRUD for DIFY workflows"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Ping MongoDB
        await mongo_client.admin.command('ping')
        return {"status": "healthy", "mongodb": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 5557))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
