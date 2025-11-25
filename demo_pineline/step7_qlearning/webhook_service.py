#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook Service - Receive Moodle events and generate recommendations
====================================================================
Receives events from Moodle observer.php and processes asynchronously
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import existing services
from pipeline.log_processing_pipeline import LogProcessingPipeline
from services.repository.state_repository import StateRepository
from services.business.recommendation import RecommendationService
from services.model.loader import ModelLoader

# =============================================================================
# Configuration
# =============================================================================

MODEL_PATH = HERE / 'models' / 'qtable.pkl'
COURSE_PATH = HERE / 'data' / 'course_structure.json'
CLUSTER_PROFILES_PATH = HERE / 'data' / 'cluster_profiles.json'

# Global services (initialized on startup)
pipeline: Optional[LogProcessingPipeline] = None
recommendation_service: Optional[RecommendationService] = None
state_repository: Optional[StateRepository] = None
model_loader: Optional[ModelLoader] = None

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global pipeline, recommendation_service, state_repository, model_loader
    
    print("\n" + "="*70)
    print("🚀 Initializing Webhook Service")
    print("="*70)
    
    # Load model
    print("\n1. Loading Q-Learning model...")
    model_loader = ModelLoader(
        model_path=MODEL_PATH,
        course_path=COURSE_PATH,
        cluster_profiles_path=CLUSTER_PROFILES_PATH
    )
    model_loader.load_all(verbose=False)
    print("  ✓ Model loaded")
    
    # Initialize pipeline
    print("\n2. Initializing log processing pipeline...")
    pipeline = LogProcessingPipeline(
        cluster_profiles_path=str(CLUSTER_PROFILES_PATH),
        course_structure_path=str(COURSE_PATH),
        enable_qtable_updates=False  # Don't update Q-table from webhook events
    )
    print("  ✓ Pipeline ready")
    
    # Initialize recommendation service
    print("\n3. Initializing recommendation service...")
    recommendation_service = RecommendationService(
        agent=model_loader.agent,
        action_space=model_loader.action_space,
        state_builder=model_loader.state_builder,
        course_structure_path=str(COURSE_PATH)
    )
    print("  ✓ Recommendation service ready")
    
    # Initialize state repository
    print("\n4. Connecting to MongoDB...")
    state_repository = StateRepository()
    print("  ✓ MongoDB connected")
    
    print("\n" + "="*70)
    print("✅ Webhook Service Ready")
    print("="*70 + "\n")
    
    yield
    
    # Cleanup on shutdown
    print("\n🛑 Shutting down Webhook Service...")

# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title='Adaptive Learning Webhook Service',
    version='1.0',
    description='Receives Moodle events and generates Q-Learning recommendations',
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Request/Response Models
# =============================================================================

class MoodleLogEvent(BaseModel):
    """Single Moodle log event"""
    userid: int
    courseid: int
    eventname: str
    component: str
    action: str
    target: str
    objectid: Optional[int] = None
    crud: str
    edulevel: int
    contextinstanceid: int
    timecreated: int
    grade: Optional[float] = None
    success: Optional[int] = None


class WebhookPayload(BaseModel):
    """Webhook payload from Moodle observer"""
    logs: List[MoodleLogEvent]
    event_id: Optional[str] = None  # For idempotency
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))


class RecommendationResponse(BaseModel):
    """Recommendation response"""
    user_id: int
    module_id: int
    recommendations: List[Dict[str, Any]]
    state: List[float]
    timestamp: str


class WebhookResponse(BaseModel):
    """Webhook response"""
    status: str
    message: str
    events_received: int
    processing_started: bool
    event_id: Optional[str] = None


# =============================================================================
# Background Task Processing
# =============================================================================

async def process_events_async(
    logs: List[Dict],
    event_id: Optional[str] = None
):
    """
    Process events asynchronously
    
    Steps:
    1. Use pipeline to update states in MongoDB
    2. For each affected (user_id, module_id), generate recommendations
    3. Save recommendations to MongoDB
    """
    try:
        print(f"\n{'='*70}")
        print(f"🔄 Background Processing Started (event_id: {event_id})")
        print(f"{'='*70}")
        
        # Step 1: Process logs with pipeline → Update states in MongoDB
        print(f"\n📊 Step 1: Processing {len(logs)} events with pipeline...")
        result = pipeline.process_logs_from_dict(
            raw_logs=logs,
            save_to_db=True,
            save_logs=True
        )
        
        affected_users = result['unique_users']
        affected_modules = result['unique_modules']
        
        print(f"  ✓ States updated for {affected_users} users across {affected_modules} modules")
        
        # Step 2: Generate recommendations for affected users/modules
        print(f"\n🎯 Step 2: Generating recommendations...")
        
        # Get list of affected (user_id, module_id) pairs
        affected_pairs = set()
        for log in logs:
            user_id = log['userid']
            # Extract module_id from contextinstanceid or objectid
            module_id = log.get('contextinstanceid', 1)
            affected_pairs.add((user_id, module_id))
        
        recommendations_saved = 0
        for user_id, module_id in affected_pairs:
            try:
                # Get current state from MongoDB
                state_doc = state_repository.get_state(user_id, module_id)
                
                if state_doc is None:
                    print(f"  ⚠️  No state found for user {user_id}, module {module_id}")
                    continue
                
                state = state_doc['state']
                cluster_id = int(state[0])
                
                # Generate recommendations using Q-Learning
                recommendations = recommendation_service.get_recommendations(
                    state=tuple(state),
                    cluster_id=cluster_id,
                    top_k=3,
                    exclude_action_ids=None,
                    lo_mastery=None,  # Use default
                    module_idx=int(state[1]) if len(state) > 1 else 0
                )
                
                # Save recommendations to MongoDB
                state_repository.save_recommendations(
                    user_id=user_id,
                    module_id=module_id,
                    recommendations=recommendations,
                    state=state
                )
                
                recommendations_saved += 1
                print(f"  ✓ Recommendations saved for user {user_id}, module {module_id}")
                
            except Exception as e:
                print(f"  ✗ Error generating recommendations for user {user_id}, module {module_id}: {e}")
        
        print(f"\n{'='*70}")
        print(f"✅ Background Processing Complete")
        print(f"{'='*70}")
        print(f"  - Events processed: {len(logs)}")
        print(f"  - States updated: {result['states_saved']}")
        print(f"  - Recommendations generated: {recommendations_saved}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Background processing error: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# Webhook Endpoints
# =============================================================================

@app.post('/webhook/moodle-events', response_model=WebhookResponse)
async def receive_moodle_events(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks
):
    """
    Receive events from Moodle observer.php
    
    This endpoint:
    1. Accepts the webhook payload
    2. Returns immediately (non-blocking)
    3. Processes events in background task
    
    Args:
        payload: Webhook payload with logs
        background_tasks: FastAPI background tasks
        
    Returns:
        Immediate acknowledgment response
    """
    if not payload.logs:
        raise HTTPException(status_code=400, detail="No logs provided")
    
    # Convert Pydantic models to dicts for processing
    logs_dict = [log.dict() for log in payload.logs]
    
    # Add to background task queue (non-blocking)
    background_tasks.add_task(
        process_events_async,
        logs=logs_dict,
        event_id=payload.event_id
    )
    
    # Return immediately
    return WebhookResponse(
        status='accepted',
        message='Events received and queued for processing',
        events_received=len(payload.logs),
        processing_started=True,
        event_id=payload.event_id
    )


@app.get('/api/recommendations/{user_id}/{module_id}')
async def get_recommendations(
    user_id: int,
    module_id: int
):
    """
    Get recommendations for a user/module
    
    This endpoint is called by Moodle to retrieve recommendations
    after they've been generated by the webhook.
    
    Args:
        user_id: User ID
        module_id: Module ID
        
    Returns:
        Recommendations from MongoDB
    """
    try:
        # Get recommendations from MongoDB
        rec_doc = state_repository.get_recommendations(user_id, module_id)
        
        if rec_doc is None:
            # No recommendations yet - return empty
            return {
                'user_id': user_id,
                'module_id': module_id,
                'recommendations': [],
                'state': None,
                'message': 'No recommendations available yet',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return RecommendationResponse(
            user_id=user_id,
            module_id=module_id,
            recommendations=rec_doc['recommendations'],
            state=rec_doc.get('state', []),
            timestamp=rec_doc.get('timestamp', datetime.utcnow().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'service': 'webhook',
        'pipeline_ready': pipeline is not None,
        'recommendation_service_ready': recommendation_service is not None,
        'mongodb_connected': state_repository is not None,
        'model_loaded': model_loader is not None and model_loader.agent is not None,
        'timestamp': datetime.utcnow().isoformat()
    }


@app.get('/')
def root():
    """Root endpoint"""
    return {
        'service': 'Adaptive Learning Webhook Service',
        'version': '1.0',
        'endpoints': {
            'webhook': 'POST /webhook/moodle-events',
            'recommendations': 'GET /api/recommendations/{user_id}/{module_id}',
            'health': 'GET /health'
        },
        'description': 'Receives Moodle events and generates Q-Learning recommendations asynchronously'
    }


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 Starting Webhook Service")
    print("="*70)
    print(f"📊 Model: {MODEL_PATH}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📖 Docs: http://localhost:8000/docs")
    print(f"🔗 Webhook: http://localhost:8000/webhook/moodle-events")
    print("="*70 + "\n")
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
