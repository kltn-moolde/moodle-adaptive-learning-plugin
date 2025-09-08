"""
Configuration module for LTI 1.3 Service
Handles all application settings and environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "LTI Service Python"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8082
    
    # Frontend Configuration
    FRONTEND_URL: str = "http://localhost:3000"  # React Frontend URL
    
    # Database
    DATABASE_URL: str = "sqlite:///./lti_service.db"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600
    
    # LTI 1.3
    LTI_CLIENT_ID: str = "your-client-id"
    LTI_DEPLOYMENT_ID: str = "your-deployment-id"
    LTI_ISSUER: str = "https://your-moodle-instance.com"
    LTI_AUTH_URL: str = "https://your-moodle-instance.com/mod/lti/auth.php"
    LTI_TOKEN_URL: str = "https://your-moodle-instance.com/mod/lti/token.php"
    LTI_KEYSET_URL: str = "https://your-moodle-instance.com/mod/lti/certs.php"
    
    # Tool Configuration
    TOOL_TITLE: str = "User Log Viewer"
    TOOL_DESCRIPTION: str = "View user activity logs from Moodle"
    TOOL_TARGET_LINK_URI: str = "http://localhost:8082/lti/launch"
    TOOL_OIDC_INITIATION_URL: str = "http://localhost:8082/lti/login"
    TOOL_PUBLIC_JWK_URL: str = "http://localhost:8082/lti/jwks"
    
    # Moodle API
    MOODLE_API_URL: str = "https://your-moodle-instance.com/webservice/rest/server.php"
    MOODLE_API_TOKEN: str = "your-moodle-api-token"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/lti_service.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
