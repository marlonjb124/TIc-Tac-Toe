"""
Script to create initial superuser.
Run this after starting the application for the first time.
"""

import asyncio
import logging

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models import UserCreate
from app.services.user_service import user_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_superuser() -> None:
    """Create initial superuser."""
    async with AsyncSessionLocal() as session:
        # Check if superuser already exists
        existing_user = await user_service.get_by_email(
            session=session, email=settings.FIRST_SUPERUSER
        )

        if existing_user:
            logger.warning("Superuser already exists!")
            logger.info(f"Email: {existing_user.email}")
            return

        # Create superuser
        superuser_data = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin User",
            is_superuser=True,
        )

        user = await user_service.create(
            session=session, user_create=superuser_data
        )

        logger.info("✅ Superuser created successfully!")
        logger.info(f"Email: {user.email}")
        logger.info(f"Password: {settings.FIRST_SUPERUSER_PASSWORD}")
        logger.warning("Please change the password immediately!")


if __name__ == "__main__":
    logger.info("🚀 Creating superuser...")
    asyncio.run(create_superuser())
