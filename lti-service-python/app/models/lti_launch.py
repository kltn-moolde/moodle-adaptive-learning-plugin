"""
LTI Launch Model
Represents LTI launch data in the database
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class LTILaunch(Base):
    """LTI Launch model for storing launch information"""
    
    __tablename__ = "lti_launches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    context_id = Column(String(255), nullable=True)
    resource_link_id = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)
    user_email = Column(String(255), nullable=True)
    course_id = Column(String(255), nullable=True, index=True)
    launch_time = Column(DateTime, default=func.now())
    
    # Additional LTI claims
    given_name = Column(String(255), nullable=True)
    family_name = Column(String(255), nullable=True)
    roles = Column(Text, nullable=True)  # JSON string of roles
    resource_title = Column(String(500), nullable=True)
    course_title = Column(String(500), nullable=True)
    
    # JWT token information
    iss = Column(String(500), nullable=True)  # Issuer
    aud = Column(String(500), nullable=True)  # Audience
    sub = Column(String(255), nullable=True)  # Subject
    
    def __repr__(self):
        return f"<LTILaunch(id={self.id}, user_id='{self.user_id}', course_id='{self.course_id}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "context_id": self.context_id,
            "resource_link_id": self.resource_link_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "course_id": self.course_id,
            "launch_time": self.launch_time.isoformat() if self.launch_time else None,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "roles": self.roles,
            "resource_title": self.resource_title,
            "course_title": self.course_title,
            "iss": self.iss,
            "aud": self.aud,
            "sub": self.sub
        }
