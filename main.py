import os

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from openai import OpenAI
from dotenv import load_dotenv

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from datetime import datetime
from typing import Annotated

from contextlib import asynccontextmanager

from database import engine, get_db, Base
from models import Book as BookModel
from schemas import BookCreate, Book, User, UserInDb

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

api_calls = 0
daily_tokens = 0
last_reset = datetime.now()

def reset_daily_counters():
    global api_calls, daily_tokens, last_reset
    if (datetime.now() - last_reset).days >= 1:
        api_calls = 0
        daily_tokens = 0
        last_reset = datetime.now()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Add any cleanup code here if needed

os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

config = Config('.env')
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # Automatically builds /auth URL
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = await oauth.google.parse_id_token(request, token)
        return JSONResponse(content=user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/api/books")
async def read_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookModel).order_by(BookModel.author))
    books = result.scalars().all()
    return books

@app.get("/api/books/{book_id}", response_model=Book)
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookModel).where(BookModel.id == book_id))
    book = result.scalars().first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    new_book = BookModel(**book.model_dump())
    print('New book!')
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookModel).where(BookModel.id == book_id))
    book = result.scalars().first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.delete(book)
    await db.commit()

@app.put("/api/books/{book_id}", status_code=status.HTTP_200_OK )
async def update_book(book_id: int, book: BookCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookModel).where(BookModel.id == book_id))
    existing_book = result.scalars().first()
    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.model_dump().items():
        setattr(existing_book, key, value)
    await db.commit()
    await db.refresh(existing_book)

@app.post("/api/summarize")
def summarize_text(text: str):
    global api_calls, daily_tokens
    reset_daily_counters()
    estimated_tokens = len(text.split()) // 4 + 1  # Rough estimate of tokens used
    if estimated_tokens > 4000:
        raise HTTPException(status_code=400, detail="Text too long. Please reduce length or split into smaller parts.")
    try:
        if api_calls >= 100:
            raise HTTPException(status_code=429, detail="Daily API call limit reached.")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Create a concise summary of the following text:"},
                    {"role": "user", "content": text}], max_tokens=500)
        api_calls += 1
        daily_tokens += response.usage.total_tokens
        summary = response.choices[0].message.content
        return {"summary": summary, "usage": { "calls_today": api_calls, "tokens_today": daily_tokens }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))