import os

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"Connecting to database at: {SQLALCHEMY_DATABASE_URL}")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# This code creates a SQLAlchemy engine and a SQLAlchemy session class SessionLocal.
# The function get_db returns a generator that provides a new session to the dependency.


async def get_db():
    async with SessionLocal() as session:
        print(SQLALCHEMY_DATABASE_URL)
        yield session


from models import Book
