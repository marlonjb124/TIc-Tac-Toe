"""
Backend pre-start script.
Checks database connection before starting the app.
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    """Initialize database connection check."""
    try:
        engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        async with engine.begin() as conn:
            # Try to create session to check if DB is awake
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    """Main function."""
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
