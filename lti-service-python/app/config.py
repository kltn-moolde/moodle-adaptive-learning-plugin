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
    FRONTEND_URL: str = "http://51.68.124.207:5173"  # React Frontend URL
    
    # Database
    DATABASE_URL: str = "sqlite:///./lti_service.db"
    
    # JWT
    JWT_SECRET: str = "384E3C37BFF4B95EE7CC16BED39A5"
    JWT_ALGORITHM: str = "RS256"
    JWT_EXPIRATION: int = 3600
    
    # LTI 1.3
    LTI_CLIENT_ID: str = "8gSjDiDrD4x2ZpS"
    LTI_DEPLOYMENT_ID: str = "1"
    LTI_ISSUER: str = "http://51.68.124.207:9090"
    LTI_AUTH_URL: str = "http://51.68.124.207:9090/mod/lti/auth.php"
    LTI_TOKEN_URL: str = "http://51.68.124.207:9090/mod/lti/token.php"
    LTI_KEYSET_URL: str = "http://moodle502:8080/mod/lti/certs.php"
    
    # Tool Configuration
    TOOL_TITLE: str = "User Log Viewer"
    TOOL_DESCRIPTION: str = "View user activity logs from Moodle"
    TOOL_TARGET_LINK_URI: str = "http://51.68.124.207:8082/lti/launch"
    TOOL_OIDC_INITIATION_URL: str = "http://51.68.124.207:8082/lti/login"
    TOOL_PUBLIC_JWK_URL: str = "http://51.68.124.207:8082/lti/jwks"
    
    # Moodle API
    MOODLE_API_URL: str = "http://51.68.124.207:9090/webservice/rest/server.php"
    MOODLE_API_TOKEN: str = "9b13f135bae7ba27d67e609c414b70df"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "51.68.124.207"]
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8085", "http://51.68.124.207:5173", "http://51.68.124.207:8085"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/lti_service.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
