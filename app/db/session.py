from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from typing import AsyncGenerator

from app.core.config import settings



# ----------------------------------
# 🛠️ Build the Database URL Dynamically
# ----------------------------------
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# ------------------------
# ⚙️ SQLAlchemy Async Setup
# ------------------------
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# This code creates a SQLAlchemy engine and a SQLAlchemy session class SessionLocal.
# The function get_db returns a generator that provides a new session to the dependency.

# ------------------------
# 🔁 Dependency for FastAPI
# ------------------------
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
