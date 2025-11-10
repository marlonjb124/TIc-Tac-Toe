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
from app.core.logger import get_logger
from app.core.security import security
from app.models import Token, UserCreate, UserPublic
from app.services.user_service import user_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/signup", response_model=Token)
async def signunp(session: SessionDep, user: UserCreate) -> Token:
    """Sign up and also login a new user and return access token."""
    existing_user = await user_service.get_by_email(
        session=session, email=user.email
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = await user_service.create(
        session=session,
        user_create=user,
    )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        subject=new_user.id, expires_delta=access_token_expires
    )

    return Token(access_token=access_token)


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
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning(f"Inactive user login attempt: {user.email}")
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

    logger.info(f"Successful login: {user.email} (id={user.id})")

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
