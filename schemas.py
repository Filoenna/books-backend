from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    description: str


class Book(BookCreate):
    id: int

    class Config:
        from_attributes = True  # Allows ORM models to be converted to Pydantic models

class User(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    disabled: bool | None = None

    class Config:
        orm_mode = True  # Allows ORM models to be converted to Pydantic models

class UserInDb(User):
    hashed_password: str