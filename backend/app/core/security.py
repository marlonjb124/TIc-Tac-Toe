"""
Security utilities for authentication and authorization.
Implements JWT token generation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pwdlib import PasswordHash


from app.core.config import settings


# Password hashing context
password_hash = PasswordHash.recommended()


class SecurityService:
    """
    Service for handling security operations.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        """
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password for storage.
        """
        return password_hash.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT access token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None


# Singleton instance
security_service = SecurityService()
