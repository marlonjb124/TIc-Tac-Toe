"""
Initial data creation script.
Creates the first superuser if it doesn't exist.
"""

import asyncio
import logging

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models import UserCreate
from app.services.user_service import user_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize database with initial data."""
    async with AsyncSessionLocal() as session:
        # Check if superuser exists
        user = await user_service.get_by_email(
            session=session, email=settings.FIRST_SUPERUSER
        )

        if not user:
            logger.info("Creating first superuser")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                full_name="Admin User",
            )
            user = await user_service.create(
                session=session, user_create=user_in
            )
            logger.info(f"Superuser created: {user.email}")
        else:
            logger.info("Superuser already exists")


async def main() -> None:
    """Main function."""
    logger.info("Creating initial data")
    await init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
