"""
User Log Model
Represents user activity logs from Moodle
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime


class UserLog(Base):
    """User Log model for storing Moodle user activity"""
    
    __tablename__ = "user_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    course_id = Column(String(255), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    target = Column(String(255), nullable=True)
    object_table = Column(String(100), nullable=True)
    object_id = Column(String(255), nullable=True)
    crud = Column(String(10), nullable=True)  # Create, Read, Update, Delete
    event_name = Column(String(500), nullable=True)
    component = Column(String(255), nullable=True)
    time_created = Column(DateTime, nullable=False)
    ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<UserLog(id={self.id}, user_id='{self.user_id}', action='{self.action}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "action": self.action,
            "target": self.target,
            "object_table": self.object_table,
            "object_id": self.object_id,
            "crud": self.crud,
            "event_name": self.event_name,
            "component": self.component,
            "time_created": self.time_created.isoformat() if self.time_created else None,
            "ip": self.ip,
            "user_agent": self.user_agent
        }
