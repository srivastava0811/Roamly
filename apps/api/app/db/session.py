from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger

engine_connect_args = {}
if "postgresql" in settings.database_url:
    # Supabase / PgBouncer transaction pooler compatibility
    engine_connect_args["statement_cache_size"] = 0
    engine_connect_args["prepared_statement_cache_size"] = 0

# Async engine configured from settings
engine = create_async_engine(
    settings.database_url,
    echo=(settings.roamly_env == "development"),
    future=True,
    connect_args=engine_connect_args,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for injecting an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> str:
    """Non-blocking DB connectivity check for health endpoint."""
    if not settings.database_url:
        return "unconfigured"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        logger.warning(f"Database health check failed: {exc}")
        return "degraded"
