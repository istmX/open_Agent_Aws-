from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from open_agent.core.config import get_settings
from open_agent.database.url import async_database_url


engine = create_async_engine(
    async_database_url(get_settings().database_url), pool_pre_ping=True
)
AsyncSessionFactory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped session; the caller owns the transaction."""
    async with AsyncSessionFactory() as session:
        yield session
