"""
Authentication Module
JWT token generation, user authentication, and password hashing
"""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import os
import uuid
from dotenv import load_dotenv

from security import is_token_revoked

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def utc_now():
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)

# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
        
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds recommended
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password (str): Plain text password to verify
        hashed_password (str): Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        data (Dict): Data to encode in token (typically user_id, email)
        expires_delta (timedelta, optional): Token expiration time
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_access_token({"user_id": 1, "email": "user@example.com"})
        >>> # token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = data.copy()
    expire = utc_now() + expires_delta
    to_encode.update({"exp": expire, "type": "access", "jti": uuid.uuid4().hex})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """
    Create JWT refresh token (longer expiration)
    
    Args:
        data (Dict): Data to encode in token
        
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": uuid.uuid4().hex})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode JWT token and verify signature
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        Dict: Decoded token data if valid, None if invalid
        
    Example:
        >>> token = create_access_token({"user_id": 1})
        >>> data = decode_token(token)
        >>> data.get("user_id")
        1
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if is_token_revoked(payload.get("jti")):
            print("Token has been revoked")
            return None
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None


def verify_token(token: str) -> Optional[int]:
    """
    Verify token and extract user_id
    
    Args:
        token (str): JWT token
        
    Returns:
        int: user_id if token is valid, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("user_id")
    if user_id is None:
        return None
    
    return user_id

# ============================================================================
# TOKEN VALIDATION
# ============================================================================

def validate_token_format(token: str) -> bool:
    """
    Validate token format (should have 3 parts: header.payload.signature)
    
    Args:
        token (str): Token to validate
        
    Returns:
        bool: True if format is valid
    """
    if not token:
        return False
    
    parts = token.split('.')
    return len(parts) == 3


def extract_token_from_header(auth_header: str) -> Optional[str]:
    """
    Extract token from Authorization header
    
    Expected format: "Bearer {token}"
    
    Args:
        auth_header (str): Authorization header value
        
    Returns:
        str: Token if valid format, None otherwise
        
    Example:
        >>> header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> token = extract_token_from_header(header)
        >>> # token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if not auth_header:
        return None
    
    parts = auth_header.split()
    
    # Check format: "Bearer {token}"
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    token = parts[1]
    
    # Validate token format
    if not validate_token_format(token):
        return None
    
    return token

# ============================================================================
# HASHING UTILITIES
# ============================================================================

def hash_string(text: str) -> str:
    """
    Generic string hashing (for things other than passwords)
    
    Args:
        text (str): Text to hash
        
    Returns:
        str: Hashed text
    """
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def test_password_hashing():
    """Test password hashing and verification"""
    print("\n" + "=" * 60)
    print("Testing Password Hashing")
    print("=" * 60)
    
    password = "test_password_123"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed[:30]}...")
    
    # Test correct password
    if verify_password(password, hashed):
        print("Correct password verified")
    else:
        print("Failed to verify correct password")
    
    # Test wrong password
    if not verify_password("wrong_password", hashed):
        print("Wrong password correctly rejected")
    else:
        print("Wrong password incorrectly accepted")
    
    print("=" * 60 + "\n")


def test_jwt_tokens():
    """Test JWT token creation and verification"""
    print("\n" + "=" * 60)
    print("Testing JWT Tokens")
    print("=" * 60)
    
    user_data = {"user_id": 1, "email": "test@example.com"}
    
    # Create token
    token = create_access_token(user_data)
    print(f"Access Token Created: {token[:30]}...")
    
    # Decode token
    decoded = decode_token(token)
    print(f"Token Decoded: {decoded}")
    
    # Verify token
    user_id = verify_token(token)
    print(f"User ID from Token: {user_id}")
    
    # Test refresh token
    refresh_token = create_refresh_token(user_data)
    print(f"Refresh Token Created: {refresh_token[:30]}...")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_password_hashing()
    test_jwt_tokens()
