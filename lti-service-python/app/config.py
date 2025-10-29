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
    FRONTEND_URL: str = "http://localhost:5173/"  # React Frontend URL
    
    # Database
    DATABASE_URL: str = "sqlite:///./lti_service.db"
    
    # JWT
    JWT_SECRET: str = "384E3C37BFF4B95EE7CC16BED39A5"
    JWT_ALGORITHM: str = "RS256"
    JWT_EXPIRATION: int = 3600
    
    # LTI 1.3
    LTI_CLIENT_ID: str = "WCqx5MTYzULBXk3"
    LTI_DEPLOYMENT_ID: str = "4"
    # External (public) URLs used by the user's browser during LTI redirects
    LTI_ISSUER: str = "http://localhost:8100"
    LTI_AUTH_URL: str = "http://localhost:8100/mod/lti/auth.php"
    LTI_TOKEN_URL: str = "http://localhost:8100/mod/lti/token.php"
    # Internal (container) URL used by services inside the Docker network (faster, no external routing)
    # moodle502 is the Moodle container name; 8080 is its internal port
    LTI_KEYSET_URL: str = "http://localhost:8100/mod/lti/certs.php"
    
    # Tool Configuration
    TOOL_TITLE: str = "User Log Viewer"
    TOOL_DESCRIPTION: str = "View user activity logs from Moodle"
    TOOL_TARGET_LINK_URI: str = "http://localhost:8082/lti/launch"
    TOOL_OIDC_INITIATION_URL: str = "http://localhost:8082/lti/login"
    TOOL_PUBLIC_JWK_URL: str = "http://localhost:8082/lti/jwks"

    # Moodle API
    # Depending on where this service runs, you can point to the public or internal Moodle endpoint.
    # If this service is in the same Docker network as Moodle, prefer the internal DNS name for performance.
    MOODLE_API_URL: str = "http://139.99.103.223:9090/webservice/rest/server.php"  # public
    MOODLE_API_TOKEN: str = "9b13f135bae7ba27d67e609c414b70df"
    # Host header to use when calling internal Moodle endpoints (used in JWKS fetch). Should match Moodle host:port.
    ADDRESS_MOODLE: str = "http://localhost:8100"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "139.99.103.223"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:8085",
        "http://139.99.103.223:5173",
        "http://139.99.103.223:8085"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/lti_service.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
