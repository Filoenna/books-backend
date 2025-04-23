from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    description: str

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
    description: str | None = None

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True  # Allows ORM models to be converted to Pydantic models