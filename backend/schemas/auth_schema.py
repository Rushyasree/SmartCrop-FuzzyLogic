"""Schemas for authentication requests and responses."""

from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from models import User


class UserRegister(BaseModel):
    """User registration request schema."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        if not v or len(v) > 50:
            raise ValueError('Names must be 1-50 characters')
        return v


class UserLogin(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema without password data."""

    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: str

    @classmethod
    def from_user(cls, user: User):
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role.value if user.role else "farmer",
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse
