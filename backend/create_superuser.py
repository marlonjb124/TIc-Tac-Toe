"""
Script to create initial superuser.
Run this after starting the application for the first time.
"""

import asyncio

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models import UserCreate
from app.services.user_service import user_service


async def create_superuser() -> None:
    """Create initial superuser."""
    async with AsyncSessionLocal() as session:
        # Check if superuser already exists
        existing_user = await user_service.get_by_email(
            session=session, email=settings.FIRST_SUPERUSER
        )

        if existing_user:
            print("⚠ Superuser already exists!")
            print(f"   Email: {existing_user.email}")
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

        print("✅ Superuser created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: {settings.FIRST_SUPERUSER_PASSWORD}")
        print("⚠ Please change the password immediately!")


if __name__ == "__main__":
    print("🚀 Creating superuser...")
    asyncio.run(create_superuser())
