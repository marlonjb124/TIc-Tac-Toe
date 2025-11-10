"""Authentication endpoints."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.logger import get_logger
from app.core.security import security
from app.models import Token, UserCreate, UserPublic
from app.services.user_service import user_service

router = APIRouter()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/signup", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_SIGNUP)
async def signup(
    request: Request, session: SessionDep, user: UserCreate
) -> Token:
    existing = await user_service.get_by_email(
        session=session, email=user.email
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = await user_service.create(session=session, user_create=user)

    token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        subject=new_user.id, expires_delta=token_expiry
    )

    return Token(access_token=token)


@router.post("/login/access-token", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await user_service.authenticate(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        logger.warning(f"Failed login: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning(f"Inactive user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        subject=user.id, expires_delta=token_expiry
    )

    logger.info(f"Login: {user.email} (id={user.id})")

    return Token(access_token=token)


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser) -> UserPublic:
    return current_user
