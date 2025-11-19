from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.auth import hash_password, verify_password, create_access_token
from app.utils import verify_password
from app.models import User, Book, Rating
from app.schemas import UserCreate, UserResponse, UserLogin, RatingCreate, BookResponse
from app.database import get_db
from typing import List, Optional
from sqlalchemy import func, desc

app = FastAPI()

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )
    if not db_user or not verify_password(
        user.password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": str(db_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

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
            detail="Користувач з таким email вже існує"
        )
    
    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
        , location=user_data.location
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при створенні користувача: {str(e)}"
        )

    return new_user


@app.post("/api/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email или пароль"
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email или пароль"
        )

    access_token = create_access_token(data={"user_id": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "location": user.location
        }
    }


@app.get("/api/popular_books_detailed")
def get_popular_books_detailed(
    limit: int = 10,
    db: Session = Depends(get_db)
):  
    popular_books = (
        db.query(
            Book,
            func.count(Rating.id).label('rating_count'),
            func.avg(Rating.rating).label('avg_rating')
        )
        .join(Rating, Book.id == Rating.book_id)
        .group_by(Book.id)
        .order_by(desc('rating_count'))
        .limit(limit)
        .all()
    )
    
    if not popular_books:
        return {"message": "Не знайдено популярних книг. Додайте оцінки."}

    result = []
    for book, rating_count, avg_rating in popular_books:
        result.append({
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "publisher": book.publisher,
            "image_url_s": book.image_url_s, 
            "image_url_m": book.image_url_m, 
            "image_url_l": book.image_url_l, 
            "rating_count": rating_count,
            "avg_rating": round(float(avg_rating), 2)
        })
    
    return result

@app.get("/books", response_model=List[BookResponse])
def get_all_books(
    skip: int = Query(0, description="Кількість пропущених книг"),
    limit: int = Query(100, description="Максимальна кількість книг для отримання"),
    db: Session = Depends(get_db)
):
    
    try:
        books = db.query(Book).offset(skip).limit(limit).all()
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні книг: {str(e)}")
    
