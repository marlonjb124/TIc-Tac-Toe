"""
Authentication endpoints.
Handles user login and token validation following OAuth2 standards.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.security import security
from app.models import Token, UserPublic
from app.services.user_service import user_service

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login.

    Get an access token for future requests using email/password.
    The username field should contain the user's email.

    Args:
        session: Database session
        form_data: OAuth2 form with username (email) and password

    Returns:
        Access token and token type

    Raises:
        HTTPException: 400 if credentials are invalid or user is inactive
    """
    # Authenticate using email (form_data.username is the email)
    user = await user_service.authenticate(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create access token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return Token(access_token=access_token)


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser) -> UserPublic:
    """
    Test access token validity.

    Use this endpoint to verify if your access token is valid.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return current_user
