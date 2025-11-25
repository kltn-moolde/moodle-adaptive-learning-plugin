"""
Pydantic request/response models for API
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """Request model for recommendations"""
    student_id: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    state: Optional[List[float]] = None
    top_k: int = 3
    exclude_action_ids: Optional[List[int]] = None
    lo_mastery: Optional[Dict[str, float]] = None  # LO mastery scores for activity recommendation


class RecommendResponse(BaseModel):
    """Response model for recommendations"""
    success: bool
    student_id: Optional[int]
    cluster_id: Optional[int]
    cluster_name: Optional[str]
    state_vector: List[float]
    state_description: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    model_info: Dict[str, Any]


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
    event_id: Optional[str] = None
    timestamp: Optional[int] = Field(default_factory=lambda: int(__import__('datetime').datetime.utcnow().timestamp()))


class WebhookResponse(BaseModel):
    """Webhook response"""
    status: str
    message: str
    events_received: int
    processing_started: bool
    event_id: Optional[str] = None

