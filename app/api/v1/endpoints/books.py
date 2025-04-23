from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....services.book_service import BookService
from ....schemas.book import Book, BookCreate, BookUpdate

router = APIRouter()

async def get_book_service(db: AsyncSession = Depends(get_db)) -> BookService:
    return BookService(db)

@router.get("/", response_model=list[Book])
async def read_books(book_service: BookService = Depends(get_book_service)):
    return await book_service.get_books()

@router.get("/{book_id}", response_model=Book)
async def read_book(book_id: int, book_service: BookService = Depends(get_book_service)):
    return await book_service.read_book(book_id)

@router.post("/", response_model=Book)
async def create_book(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    return await book_service.create_book(book)

@router.delete("/{book_id}")
async def delete_book(book_id: int, book_service: BookService = Depends(get_book_service)):
    await book_service.delete_book(book_id)
    return {"status": "success","message": "Book deleted successfully"}

@router.put("/{book_id}", response_model=Book)
async def update_book(book_id: int, book: BookCreate, book_service: BookService = Depends(get_book_service)):
    return await book_service.update_book(book_id, book)

@router.patch("/{book_id}", response_model=Book)
async def partial_update_book(book_id: int, book: BookUpdate, book_service: BookService = Depends(get_book_service)):
    return await book_service.update_book(book_id, book)