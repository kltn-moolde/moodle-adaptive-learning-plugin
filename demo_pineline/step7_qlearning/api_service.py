#!/usr/bin/env python3
"""
Adaptive Learning API Service
Clean and modular FastAPI service with business logic separated into services

Endpoints:
 - GET  /api/health      : Health check and model status
 - GET  /api/model-info  : Model metadata and training statistics
 - POST /api/recommend   : Get top-K learning recommendations

Run: uvicorn api_service:app --reload --port 8080
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import dependencies to initialize services
from api import dependencies  # noqa: F401

# Import routes
from api.routes import health, qtable, recommendations, webhook, po_lo, midterm_weights

# Import config for startup message
from api.config import MODEL_PATH

# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(
    title='Adaptive Learning API',
    version='2.0',
    description='Q-Learning based adaptive learning path recommendation system'
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Register Routes
# =============================================================================

app.include_router(health.router)
app.include_router(qtable.router)
app.include_router(recommendations.router)
app.include_router(webhook.router)
app.include_router(po_lo.router)
app.include_router(midterm_weights.router)

# =============================================================================
# Root Endpoint
# =============================================================================

@app.get('/')
def root():
    """Root endpoint"""
    return {
        'service': 'Adaptive Learning API',
        'version': '2.0',
        'endpoints': {
            'health': '/api/health',
            'model_info': '/api/model-info',
            'recommend': '/api/recommend (POST)',
            'top_states': '/api/qtable/states/positive?top_n=N',
            'webhook': '/webhook/moodle-events (POST) - NEW',
            'get_recommendations': '/api/recommendations/{user_id}/{module_id} (GET) - NEW',
            'po_lo': '/api/po-lo',
            'midterm_weights': '/api/midterm-weights'
        }
    }


# =============================================================================
# Startup Message
# =============================================================================

if __name__ == '__main__':
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Adaptive Learning API Server (with Webhook)")
    print("="*70)
    print(f"📊 Model: {MODEL_PATH}")
    print(f"🎯 Q-table states: {len(dependencies.model_loader.agent.q_table) if dependencies.model_loader.agent else 0}")
    print(f"🌐 Server: http://localhost:8080")
    print(f"📖 Docs: http://localhost:8080/docs")
    print(f"🔗 Webhook: http://localhost:8080/webhook/moodle-events")
    print("="*70 + "\n")
    
    uvicorn.run(app, host='0.0.0.0', port=8080)
