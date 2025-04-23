import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ------------------------
# 🌱 Load Environment Vars
# ------------------------
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# ----------------------------------
# 🛠️ Build the Database URL Dynamically
# ----------------------------------
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
