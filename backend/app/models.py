"""
User model following SQLModel pattern.
Centralizes all user-related models and schemas.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    """Base user properties shared across schemas."""

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for user creation via API."""

    password: str = Field(min_length=8, max_length=100)


# Properties to receive via API on update
class UserUpdate(SQLModel):
    """Schema for user update via API. All fields are optional."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=100)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    """User database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    # Use timezone-aware datetimes for compatibility with recent versions
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# Properties to return via API
class UserPublic(UserBase):
    """Public user properties returned via API."""

    id: int
    created_at: datetime


class UsersPublic(SQLModel):
    """Paginated list of users."""

    data: list[UserPublic]
    count: int


# Token models
class Token(SQLModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """JWT token payload."""

    sub: Optional[int] = None  # User ID
    exp: Optional[int] = None  # Expiration timestamp
