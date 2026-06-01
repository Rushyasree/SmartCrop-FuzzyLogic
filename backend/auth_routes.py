"""
Authentication Routes
Flask endpoints for user registration, login, and token management
"""

import logging
from functools import wraps

from flask import request, jsonify

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    extract_token_from_header,
    verify_token
)
from database import get_db_context
from models import User, UserRole
from schemas.auth_schema import UserLogin, UserRegister, UserResponse
from security import rate_limit, revoke_token_id

logger = logging.getLogger(__name__)

# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

def token_required(f):
    """Decorator to require valid JWT token in Authorization header"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("Request missing Authorization header")
            return jsonify({
                "status": "error",
                "message": "Missing authorization header"
            }), 401
        
        token = extract_token_from_header(auth_header)
        if not token:
            logger.warning("Invalid Authorization header format")
            return jsonify({
                "status": "error",
                "message": "Invalid authorization header format. Use: Bearer {token}"
            }), 401
        
        user_id = verify_token(token)
        if not user_id:
            logger.warning("Invalid or expired token")
            return jsonify({
                "status": "error",
                "message": "Invalid or expired token"
            }), 401
        
        # Get user from database to verify still active
        try:
            with get_db_context() as db:
                user = db.query(User).filter_by(id=user_id).first()
                if not user or not user.is_active:
                    logger.warning(f"User {user_id} not found or inactive")
                    return jsonify({
                        "status": "error",
                        "message": "User not found or inactive"
                    }), 401
        except Exception as e:
            logger.error(f"Database error during token verification: {e}")
            return jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500
        
        # Pass user_id to the route
        request.user_id = user_id
        request.user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

def register_user_routes(app):
    """Register authentication routes with Flask app"""
    
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    @rate_limit(max_requests=8, window_seconds=60)
    def register():
        """
        Register a new user account
        
        POST Parameters:
            - email (str): User email address
            - password (str): Password (min 8 chars)
            - first_name (str): First name
            - last_name (str): Last name
            - phone (str, optional): Phone number
        
        Returns:
            JSON with user data and tokens
        """
        try:
            logger.info("Received user registration request")
            
            # Handle CORS preflight
            if request.method == 'OPTIONS':
                return '', 200
            
            # Parse and validate request data
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "status": "error",
                        "message": "Request body is empty"
                    }), 400
                
                user_data = UserRegister(**data)
            except ValueError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({
                    "status": "error",
                    "message": f"Validation failed: {str(e)}"
                }), 400
            
            # Check if user already exists
            with get_db_context() as db:
                existing_user = db.query(User).filter_by(email=user_data.email).first()
                if existing_user:
                    logger.warning(f"Registration attempt with existing email: {user_data.email}")
                    return jsonify({
                        "status": "error",
                        "message": "Email already registered"
                    }), 409
                
                # Create new user
                try:
                    hashed_password = hash_password(user_data.password)
                    
                    new_user = User(
                        email=user_data.email,
                        password_hash=hashed_password,
                        first_name=user_data.first_name,
                        last_name=user_data.last_name,
                        phone=user_data.phone,
                        role=UserRole.FARMER,
                        is_active=True
                    )
                    
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    
                    logger.info(f"User registered successfully: {user_data.email}")
                    
                    # Generate tokens
                    access_token = create_access_token({
                        "user_id": new_user.id,
                        "email": new_user.email
                    })
                    refresh_token = create_refresh_token({
                        "user_id": new_user.id,
                        "email": new_user.email
                    })
                    
                    return jsonify({
                        "status": "success",
                        "message": "User registered successfully",
                        "data": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "Bearer",
                            "user": UserResponse.from_user(new_user).model_dump()
                        }
                    }), 201
                
                except ValueError as e:
                    logger.error(f"Error during registration: {e}")
                    return jsonify({
                        "status": "error",
                        "message": f"Registration failed: {str(e)}"
                    }), 400
        
        except Exception as e:
            logger.error(f"Unexpected error in register endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500
    
    
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    @rate_limit(max_requests=10, window_seconds=60)
    def login():
        """
        User login endpoint
        
        POST Parameters:
            - email (str): User email address
            - password (str): Password
        
        Returns:
            JSON with tokens and user data
        """
        try:
            logger.info("Received login request")
            
            # Handle CORS preflight
            if request.method == 'OPTIONS':
                return '', 200
            
            # Parse and validate request data
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "status": "error",
                        "message": "Request body is empty"
                    }), 400
                
                login_data = UserLogin(**data)
            except ValueError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({
                    "status": "error",
                    "message": f"Validation failed: {str(e)}"
                }), 400
            
            # Find user and verify password
            with get_db_context() as db:
                user = db.query(User).filter_by(email=login_data.email).first()
                
                if not user:
                    logger.warning(f"Login attempt with non-existent email: {login_data.email}")
                    return jsonify({
                        "status": "error",
                        "message": "Invalid email or password"
                    }), 401
                
                if not user.is_active:
                    logger.warning(f"Login attempt for inactive user: {login_data.email}")
                    return jsonify({
                        "status": "error",
                        "message": "User account is inactive"
                    }), 401
                
                if not verify_password(login_data.password, user.password_hash):
                    logger.warning(f"Failed login attempt for user: {login_data.email}")
                    return jsonify({
                        "status": "error",
                        "message": "Invalid email or password"
                    }), 401
                
                logger.info(f"User logged in successfully: {login_data.email}")
                
                # Generate tokens
                access_token = create_access_token({
                    "user_id": user.id,
                    "email": user.email
                })
                refresh_token = create_refresh_token({
                    "user_id": user.id,
                    "email": user.email
                })
                
                return jsonify({
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "Bearer",
                        "user": UserResponse.from_user(user).model_dump()
                    }
                }), 200
        
        except Exception as e:
            logger.error(f"Unexpected error in login endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500
    
    
    @app.route('/api/auth/refresh-token', methods=['POST', 'OPTIONS'])
    @rate_limit(max_requests=20, window_seconds=60)
    def refresh():
        """
        Refresh access token using refresh token
        
        POST Parameters:
            - refresh_token (str): Valid refresh token
        
        Returns:
            JSON with new access token
        """
        try:
            logger.info("Received token refresh request")
            
            # Handle CORS preflight
            if request.method == 'OPTIONS':
                return '', 200
            
            try:
                data = request.get_json()
                if not data or 'refresh_token' not in data:
                    return jsonify({
                        "status": "error",
                        "message": "Missing refresh_token in request body"
                    }), 400
                
                refresh_token = data.get('refresh_token')
            except Exception as e:
                logger.warning(f"Invalid request data: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Invalid request data"
                }), 400
            
            # Verify refresh token
            payload = decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                logger.warning("Invalid or expired refresh token")
                return jsonify({
                    "status": "error",
                    "message": "Invalid or expired refresh token"
                }), 401
            
            user_id = payload.get("user_id")
            email = payload.get("email")
            
            if not user_id:
                return jsonify({
                    "status": "error",
                    "message": "Invalid token payload"
                }), 401
            
            # Verify user still exists and is active
            with get_db_context() as db:
                user = db.query(User).filter_by(id=user_id).first()
                if not user or not user.is_active:
                    logger.warning(f"Refresh attempt for non-existent or inactive user: {user_id}")
                    return jsonify({
                        "status": "error",
                        "message": "User not found or inactive"
                    }), 401
            
            # Generate new access token
            revoke_token_id(payload.get("jti"))
            new_access_token = create_access_token({
                "user_id": user_id,
                "email": email
            })
            new_refresh_token = create_refresh_token({
                "user_id": user_id,
                "email": email
            })
            
            logger.info(f"Token refreshed for user: {user_id}")
            
            return jsonify({
                "status": "success",
                "message": "Token refreshed successfully",
                "data": {
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                    "token_type": "Bearer"
                }
            }), 200
        
        except Exception as e:
            logger.error(f"Unexpected error in refresh endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500
    
    
    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def get_current_user():
        """
        Get current authenticated user info
        
        Headers:
            - Authorization: Bearer {access_token}
        
        Returns:
            JSON with user data
        """
        try:
            logger.info(f"Retrieving user info for user: {request.user_id}")
            
            return jsonify({
                "status": "success",
                "data": UserResponse.from_user(request.user).model_dump()
            }), 200
        
        except Exception as e:
            logger.error(f"Error retrieving user info: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500

    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    @token_required
    def logout():
        """Revoke the current access token for this process."""
        if request.method == 'OPTIONS':
            return '', 200

        auth_header = request.headers.get('Authorization')
        token = extract_token_from_header(auth_header)
        payload = decode_token(token) if token else None
        if payload:
            revoke_token_id(payload.get("jti"))

        return jsonify({
            "status": "success",
            "message": "Logged out successfully"
        }), 200
