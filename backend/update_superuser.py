"""
Script to update superuser email and password.
"""

import asyncio
import sys

from sqlmodel import select

from app.core.db import AsyncSessionLocal
from app.core.security import security
from app.models import User


async def update_superuser(new_email: str, new_password: str) -> None:
    """Update the first user to be superuser with new credentials."""
    async with AsyncSessionLocal() as session:
        # Get first user (ID=1)
        statement = select(User).where(User.id == 1)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if user:
            print(f"Usuario encontrado: {user.email}")
            user.email = new_email
            user.hashed_password = security.get_password_hash(new_password)
            user.is_superuser = True
            user.is_active = True

            session.add(user)
            await session.commit()
            await session.refresh(user)

            print("✅ Usuario actualizado:")
            print(f"   Email: {user.email}")
            print(f"   Superuser: {user.is_superuser}")
            print(f"   Active: {user.is_active}")
        else:
            print("❌ No se encontró usuario con ID=1")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python update_superuser.py <email> <password>")
        print(
            "Ejemplo: python update_superuser.py "
            "admin@tictactoe.com changethis123"
        )
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    asyncio.run(update_superuser(email, password))
