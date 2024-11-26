import logging
from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL: str = settings.DATABASE_URL
engine: AsyncEngine = create_async_engine(settings.DATABASE_URL)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while initializing the database: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


class Base(DeclarativeBase):
    pass
