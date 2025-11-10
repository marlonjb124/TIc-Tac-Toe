"""
Initial data creation script.
Creates the first superuser if it doesn't exist.
"""

import asyncio
import logging

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.security import security
from app.models import User
from app.services.user_service import user_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with AsyncSessionLocal() as session:
        user = await user_service.get_by_email(
            session=session, email=settings.FIRST_SUPERUSER
        )

        if user:
            logger.info("Superuser already exists, skipping creation")
            return user

        logger.info("Creating first superuser")

        password = settings.FIRST_SUPERUSER_PASSWORD
        hashed_pw = security.get_password_hash(password)
        superuser = User(
            email=settings.FIRST_SUPERUSER,
            full_name="Admin User",
            hashed_password=hashed_pw,
            is_superuser=True,
            is_active=True,
        )

        session.add(superuser)
        await session.commit()
        await session.refresh(superuser)

        logger.info(
            f"Superuser created: {superuser.email} (id={superuser.id})"
        )

        return superuser


async def main() -> None:
    logger.info("Creating initial data")
    await init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
