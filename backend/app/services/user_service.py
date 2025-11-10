"""User service for business logic."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logger import get_logger
from app.core.security import security
from app.models import User, UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    async def get_by_id(
        self, session: AsyncSession, user_id: int
    ) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        result = await session.exec(statement)
        return result.one_or_none()

    async def get_by_email(
        self, session: AsyncSession, email: str
    ) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.one_or_none()

    async def create(
        self, session: AsyncSession, user_create: UserCreate
    ) -> User:
        hashed_pw = security.get_password_hash(user_create.password)
        user_data = user_create.model_dump(exclude={"password"})
        new_user = User(
            **user_data,
            hashed_password=hashed_pw,
            is_superuser=False,
            is_active=True,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        logger.info(f"User created: {new_user.email} (id={new_user.id})")

        return new_user

    async def update(
        self, session: AsyncSession, db_user: User, user_update: UserUpdate
    ) -> User:
        updates = user_update.model_dump(exclude_unset=True)

        if "password" in updates:
            updates["hashed_password"] = security.get_password_hash(
                updates.pop("password")
            )

        for field, value in updates.items():
            setattr(db_user, field, value)

        await session.commit()
        await session.refresh(db_user)

        return db_user

    async def authenticate(
        self, session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(session, email)

        if not user:
            return None

        if not security.verify_password(password, user.hashed_password):
            return None

        return user


user_service = UserService()
