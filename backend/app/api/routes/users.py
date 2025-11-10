"""
User management endpoints.
Provides CRUD operations for users following REST best practices.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import User, UserCreate, UserPublic, UsersPublic, UserUpdate
from app.services.user_service import user_service

router = APIRouter()


@router.get("/", response_model=UsersPublic)
async def list_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    skip: int = 0,
    limit: int = 100,
) -> UsersPublic:
    """
    List all users (superuser only).
    """
    # Get users with pagination
    statement = select(User).offset(skip).limit(limit)
    result = await session.exec(statement)
    users = result.all()

    count_statement = select(func.count()).select_from(User)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    return UsersPublic(data=list(users), count=count)


@router.get("/me", response_model=UserPublic)
async def read_current_user(current_user: CurrentUser) -> User:
    """
    Get current user.

    Retrieve information about the currently authenticated user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_current_user(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdate,
) -> User:
    """
    Update current user.

    Update information for the currently authenticated user.

    Args:
        session: Database session
        current_user: Current authenticated user
        user_in: User update data

    Returns:
        Updated user data

    Raises:
        HTTPException: 409 if email is already taken by another user
    """
    # Check if email is being changed and is already taken
    if user_in.email:
        existing_user = await user_service.get_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    # Update user
    updated_user = await user_service.update(
        session=session, db_user=current_user, user_update=user_in
    )

    return updated_user


@router.post(
    "/", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def create_user(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_in: UserCreate,
) -> User:
    """
    Create new user (superuser only).

    Create a new user in the system. Only accessible to superusers.

    Args:
        session: Database session
        current_user: Current authenticated superuser
        user_in: User creation data

    Returns:
        Created user data

    Raises:
        HTTPException: 403 if user is not a superuser
        HTTPException: 409 if user with email already exists
    """
    # Check if user already exists
    existing_user = await user_service.get_by_email(
        session=session, email=user_in.email
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Create user
    user = await user_service.create(session=session, user_create=user_in)

    return user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_id: int,
) -> User:
    """
    Get user by ID (superuser only).

    Retrieve a specific user by their ID. Only accessible to superusers.

    Args:
        session: Database session
        current_user: Current authenticated superuser
        user_id: ID of the user to retrieve

    Returns:
        User data

    Raises:
        HTTPException: 403 if user is not a superuser
        HTTPException: 404 if user is not found
    """
    user = await user_service.get_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
