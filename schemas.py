from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    genre: str


class Book(BookCreate):
    id: int

    class Config:
        from_attributes = True  # Allows ORM models to be converted to Pydantic models
