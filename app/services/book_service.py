from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException
from ..db.models import Book as BookModel
from ..schemas.book import BookCreate, BookUpdate

class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_books(self) -> list[BookModel]:
        result = await self.db.execute(select(BookModel).order_by(BookModel.author))
        books = result.scalars().all()
        return books

    async def read_book(self, book_id: int) -> BookModel:
        result = await self.db.execute(select(BookModel).where(BookModel.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    async def create_book(self, book: BookCreate) -> BookModel:
        new_book = BookModel(**book.model_dump())
        self.db.add(new_book)
        await self.db.commit()
        await self.db.refresh(new_book)
        return new_book

    async def delete_book(self, book_id: int) -> None:
        result = await self.db.execute(select(BookModel).where(BookModel.id == book_id))
        book = result.scalars().first()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        await self.db.delete(book)
        await self.db.commit()

    async def update_book(self, book_id: int, book_data: BookUpdate) -> BookModel:
        result = await self.db.execute(select(BookModel).where(BookModel.id == book_id))
        existing_book = result.scalar_one_or_none()
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book not found")
        update_data = book_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_book, key, value)
        await self.db.commit()
        await self.db.refresh(existing_book)
        return existing_book