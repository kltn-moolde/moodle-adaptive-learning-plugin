"""
LTI 1.3 Service Implementation
Handles LTI authentication, token validation, and launch processing
"""

import jwt
import json
import uuid
import base64
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from urllib.parse import urlencode, quote_plus
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from jose import jwt as jose_jwt
from jose.utils import base64url_decode

from app.config import settings
from app.database import get_db
from app.models.lti_launch import LTILaunch
from loguru import logger


class LTIService:
    """LTI 1.3 Service for handling authentication and launches"""
    
    def __init__(self):
        self.client_id = settings.LTI_CLIENT_ID
        self.deployment_id = settings.LTI_DEPLOYMENT_ID
        self.issuer = settings.LTI_ISSUER
        self.auth_url = settings.LTI_AUTH_URL
        self.token_url = settings.LTI_TOKEN_URL
        self.keyset_url = settings.LTI_KEYSET_URL
        
    def initiate_login(self, login_hint: str, target_link_uri: str, 
                      lti_message_hint: Optional[str] = None) -> str:
        """
        Initiate LTI 1.3 login process
        """
        logger.info("=== LOGIN METHOD CALLED ===")
        logger.info(f"login_hint: {login_hint}")
        logger.info(f"target_link_uri: {target_link_uri}")
        logger.info(f"lti_message_hint: {lti_message_hint}")
        
        # Generate state and nonce for security
        state = str(uuid.uuid4())
        nonce = str(uuid.uuid4())
        
        # Build authorization URL parameters
        auth_params = {
            "response_type": "id_token",
            "client_id": self.client_id,
            "redirect_uri": target_link_uri,
            "login_hint": login_hint,
            "state": state,
            "nonce": nonce,
            "scope": "openid",
            "response_mode": "form_post"
        }
        
        if lti_message_hint:
            auth_params["lti_message_hint"] = lti_message_hint
            
        # Build the complete authorization URL
        auth_url = f"{self.auth_url}?{urlencode(auth_params, quote_via=quote_plus)}"
        
        logger.info(f"Auth URL: {auth_url}")
        return auth_url
    
    def process_launch(self, launch_data: Dict[str, Any], 
                      db: Session = Depends(get_db)) -> LTILaunch:
        """
        Process LTI 1.3 launch and extract user information
        """
        logger.info("====== Running processLaunch ========")
        logger.info(f"launchData: {launch_data}")
        
        # Extract JWT token from launch data
        id_token = launch_data.get("id_token")
        if not id_token:
            raise HTTPException(status_code=400, detail="ID token not found in launch data")
        
        # Decode JWT token to get actual payload
        token_payload = self._decode_jwt_token(id_token)
        logger.info(f"Decoded token payload: {token_payload}")
        
        # Extract user information from decoded token
        user_id = token_payload.get("sub")
        
        # Extract context information
        context_claim = "https://purl.imsglobal.org/spec/lti/claim/context"
        context = token_payload.get(context_claim, {})
        context_id = context.get("id") if context else None
        course_title = context.get("title") if context else None
        
        # Extract resource link information
        resource_link_claim = "https://purl.imsglobal.org/spec/lti/claim/resource_link"
        resource_link = token_payload.get(resource_link_claim, {})
        resource_link_id = resource_link.get("id") if resource_link else None
        resource_title = resource_link.get("title") if resource_link else None
        
        # Extract user information
        user_name = token_payload.get("name")
        user_email = token_payload.get("email")
        given_name = token_payload.get("given_name")
        family_name = token_payload.get("family_name")
        
        # Extract course information
        course_id = context_id
        
        # Extract roles
        roles_claim = "https://purl.imsglobal.org/spec/lti/claim/roles"
        roles = token_payload.get(roles_claim, [])
        
        # Extract issuer and audience
        iss = token_payload.get("iss")
        aud = token_payload.get("aud")
        
        logger.info(f"User Id: {user_id}")
        logger.info(f"Context Id: {context_id}")
        logger.info(f"Resource Link Id: {resource_link_id}")
        logger.info(f"User Name: {user_name}")
        logger.info(f"User Email: {user_email}")
        logger.info(f"Course Id: {course_id}")
        
        # Create LTI Launch object
        launch = LTILaunch(
            user_id=user_id,
            context_id=context_id,
            resource_link_id=resource_link_id,
            user_name=user_name,
            user_email=user_email,
            course_id=course_id,
            given_name=given_name,
            family_name=family_name,
            roles=json.dumps(roles) if roles else None,
            resource_title=resource_title,
            course_title=course_title,
            iss=iss,
            aud=aud if isinstance(aud, str) else json.dumps(aud),
            sub=user_id,
            launch_time=datetime.utcnow()
        )
        
        # Save to database
        db.add(launch)
        db.commit()
        db.refresh(launch)
        
        return launch
    
    def _decode_jwt_token(self, id_token: str) -> Dict[str, Any]:
        """
        Decode JWT token without verification (for development)
        In production, you should verify the signature
        """
        try:
            logger.info("=== decodeJwtToken METHOD CALLED ===")
            
            # Split JWT token into parts
            token_parts = id_token.split(".")
            if len(token_parts) != 3:
                raise ValueError("Invalid JWT token format")
            
            # Get payload (second part)
            payload = token_parts[1]
            
            # Add padding if needed
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += '=' * (4 - missing_padding)
            
            # Decode base64 URL
            decoded_bytes = base64.urlsafe_b64decode(payload)
            decoded_payload = decoded_bytes.decode('utf-8')
            
            # Parse JSON
            return json.loads(decoded_payload)
            
        except Exception as e:
            logger.error(f"Error decoding JWT token: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error decoding JWT token: {str(e)}")
    
    def generate_jwt_token(self, user_id: str, course_id: str, launch_data: Dict[str, Any] = None) -> str:
        """
        Generate JWT session token after successful LTI launch
        """
        expiry_date = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION)
        
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": expiry_date,
            "course_id": course_id,
            "iss": "lti-service-python",
            "aud": "frontend-app"
        }
        
        # Add LTI-specific claims if provided
        if launch_data:
            payload.update({
                "name": launch_data.get("name"),
                "email": launch_data.get("email"),
                "roles": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/roles", []),
                "context_title": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context", {}).get("title")
            })
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm="HS256"  # Use HS256 for session tokens (different from LTI tokens)
        )
    
    def get_jwks(self) -> Dict[str, Any]:
        """
        Get JWKS (JSON Web Key Set) from Moodle
        """
        try:
            response = requests.get(self.keyset_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching JWKS: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
    
    def get_public_key_from_jwks(self, jwks: Dict[str, Any], kid: str) -> Dict[str, Any]:
        """
        Extract JWK from JWKS for given key ID
        """
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        raise ValueError(f"Key with kid '{kid}' not found in JWKS")
    
    def validate_token(self, token: str) -> bool:
        """
        Validate LTI id_token from Moodle (RS256)
        """
        try:
            # Decode header to get key ID
            header = jose_jwt.get_unverified_header(token)
            kid = header.get("kid")
            
            if not kid:
                logger.warning("No kid in token header")
                return False
            
            # Get JWKS and extract public key
            jwks = self.get_jwks()
            jwk = self.get_public_key_from_jwks(jwks, kid)
            
            # Verify token using python-jose
            payload = jose_jwt.decode(
                token,
                jwk,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer
            )
            
            logger.info("Token validation successful")
            return True
            
        except jose_jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return False
        except jose_jwt.JWTError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode LTI id_token and return payload
        """
        try:
            # Decode header to get key ID
            header = jose_jwt.get_unverified_header(token)
            kid = header.get("kid")
            
            if not kid:
                raise ValueError("No kid in token header")
            
            # Get JWKS and extract public key
            jwks = self.get_jwks()
            jwk = self.get_public_key_from_jwks(jwks, kid)
            
            # Decode token
            payload = jose_jwt.decode(
                token,
                jwk,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer
            )
            
            return payload
            
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Failed to decode token: {str(e)}")
    
    def validate_session_token(self, token: str) -> bool:
        """
        Validate JWT session token (HS256) - for app sessions after LTI launch
        """
        try:
            jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            logger.warning("Session token has expired")
            return False
        except jwt.InvalidTokenError:
            logger.warning("Invalid session token")
            return False
        except Exception as e:
            logger.error(f"Error validating session token: {str(e)}")
            return False
    
    def decode_session_token(self, token: str) -> Dict[str, Any]:
        """
        Decode session token and return payload
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload
        except Exception as e:
            logger.error(f"Error decoding session token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid session token")
    
    def get_user_id_from_token(self, token: str) -> str:
        """
        Extract user ID from JWT session token
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload.get("sub")
        except Exception as e:
            logger.error(f"Error extracting user ID from token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def get_course_id_from_token(self, token: str) -> str:
        """
        Extract course ID from JWT session token
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            course_id = payload.get("course_id")
            if not course_id:
                raise HTTPException(status_code=400, detail="Course ID not found in token")
            return course_id
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error extracting course ID from token: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error extracting course ID: {str(e)}")


# Global service instance
lti_service = LTIService()
