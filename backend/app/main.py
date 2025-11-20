from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app import models, schemas, database
from app.auth import hash_password, create_access_token
from app.utils import verify_password
from app.models import User, Book, Rating, Watchlist
from app.schemas import UserCreate, UserResponse, UserLogin
from app.database import get_db

app = FastAPI(title="Movie Site API")
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    payload = verify_password(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний або прострочений токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний токен"
        )

    # Знаходимо користувача в БД
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Користувача не знайдено"
        )

    return user


@app.get("/")
def root():
    return {"message": "Movie Site API is running!"}


@app.post(
    "/api/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація нового користувача",
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким email вже існує",
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        location=user_data.location,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при створенні користувача: {str(e)}",
        )

    return new_user


@app.post("/api/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний email или пароль"
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний email или пароль"
        )

    access_token = create_access_token(data={"user_id": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "location": user.location},
    }


@app.get("/api/popular_books")
def get_popular_books(limit: int = 10, db: Session = Depends(get_db)):
    popular_books = (
        db.query(
            Book,
            func.avg(Rating.rating).label("avg_rating"),
            func.count(Rating.id).label("rating_count"),
        )
        .join(Rating, Book.id == Rating.book_id)
        .group_by(Book.id)
        .having(func.count(Rating.id) >= 5)
        .order_by(desc("avg_rating"))
        .limit(limit)
        .all()
    )

    if not popular_books:
        return {"message": "Нет книг с рейтингами"}

    result = []
    for book, avg_rating, rating_count in popular_books:
        result.append(
            {
                "id": book.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "publisher": book.publisher,
                "image_url_s": book.image_url_s,
                "image_url_m": book.image_url_m,
                "image_url_l": book.image_url_l,
                "avg_rating": round(float(avg_rating), 2),
                "rating_count": rating_count,
            }
        )

    return result


@app.get("/api/all_books")
def get_all_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(Book).count()

    books = db.query(Book).offset(skip).limit(limit).all()

    result = []
    for book in books:
        result.append(
            {
                "id": book.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "publisher": book.publisher,
                "image_url_s": book.image_url_s,
                "image_url_m": book.image_url_m,
                "image_url_l": book.image_url_l,
            }
        )

    return {"total": total, "skip": skip, "limit": limit, "books": result}


@app.post("/api/watchlist", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    watchlist_data: schemas.WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Додає книгу в watchlist користувача"""

    book = db.query(Book).filter(Book.id == watchlist_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )

    existing = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == current_user.id,
            Watchlist.book_id == watchlist_data.book_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Книга уже в watchlist"
        )

    new_item = Watchlist(user_id=current_user.id, book_id=watchlist_data.book_id)

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {"message": "Книга добавлена в watchlist", "watchlist_id": new_item.id}


@app.get("/api/watchlist")
def get_watchlist(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Отримує watchlist поточного користувача"""

    watchlist_items = (
        db.query(Watchlist, Book)
        .join(Book, Watchlist.book_id == Book.id)
        .filter(Watchlist.user_id == current_user.id)
        .order_by(Watchlist.added_at.desc())
        .all()
    )

    if not watchlist_items:
        return {"message": "Ваш watchlist пуст", "books": []}

    result = []
    for watchlist, book in watchlist_items:
        result.append(
            {
                "watchlist_id": watchlist.id,
                "added_at": watchlist.added_at,
                "book": {
                    "id": book.id,
                    "isbn": book.isbn,
                    "title": book.title,
                    "author": book.author,
                    "year": book.year,
                    "publisher": book.publisher,
                    "image_url_s": book.image_url_s,
                    "image_url_m": book.image_url_m,
                    "image_url_l": book.image_url_l,
                },
            }
        )

    return {"total": len(result), "books": result}


@app.delete("/api/watchlist/{book_id}")
def remove_from_watchlist(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    item = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id, Watchlist.book_id == book_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена в watchlist"
        )

    db.delete(item)
    db.commit()

    return {"message": "Книга удалена из watchlist"}


@app.get("/api/user", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/api/user", response_model=UserResponse)
def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if user_update.email and user_update.email != current_user.email:
        existing_user = (
            db.query(User)
            .filter(User.email == user_update.email, User.id != current_user.id)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Цей email вже використовується",
            )

        current_user.email = user_update.email

    if user_update.location is not None:
        current_user.location = user_update.location

    if user_update.password:
        if len(user_update.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль має бути мінімум 8 символів",
            )
        current_user.hashed_password = hash_password(user_update.password)

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при оновленні профілю: {str(e)}",
        )

    return current_user
