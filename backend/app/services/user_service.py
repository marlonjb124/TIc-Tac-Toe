"""
User service for business logic.
Handles all user operations following the Service Layer pattern.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import security
from app.models import User, UserCreate, UserUpdate


class UserService:
    """
    Service for user operations.
    Encapsulates business logic for user management.
    """

    async def get_by_id(
        self, session: AsyncSession, user_id: int
    ) -> Optional[User]:
        """
        Get user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User or None if not found
        """
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(
        self, session: AsyncSession, email: str
    ) -> Optional[User]:
        """
        Get user by email.

        Args:
            session: Database session
            email: User email

        Returns:
            User or None if not found
        """
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        user_create: UserCreate,
    ) -> User:
        """
        Create new user.

        Args:
            session: Database session
            user_create: User creation data

        Returns:
            Created user
        """
        hashed_password = security.get_password_hash(user_create.password)

        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_superuser=user_create.is_superuser,
            is_active=user_create.is_active,
        )

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        return db_user

    async def update(
        self,
        session: AsyncSession,
        db_user: User,
        user_update: UserUpdate,
    ) -> User:
        """
        Update user information.

        Args:
            session: Database session
            db_user: User to update
            user_update: Update data

        Returns:
            Updated user
        """
        update_data = user_update.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            hashed_password = security.get_password_hash(
                update_data["password"]
            )
            update_data["hashed_password"] = hashed_password
            del update_data["password"]

        # Update fields
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await session.commit()
        await session.refresh(db_user)

        return db_user

    async def authenticate(
        self, session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            session: Database session
            email: User email
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_by_email(session, email)

        if not user:
            return None

        if not security.verify_password(password, user.hashed_password):
            return None

        return user


# Singleton instance
user_service = UserService()
