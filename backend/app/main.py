from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app import schemas
from app.auth import hash_password, create_access_token, verify_password, get_current_user
from app.models import User, Book, Rating, Watchlist
from app.schemas import UserCreate, UserResponse, UserLogin
from app.database import get_db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Movie Site API")

origins = [
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Movie Site API працює!"}


@app.post(
    "/api/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація нового користувача",
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким email вже існує"
        )
    
    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        location=user_data.location
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
            detail="Невірний email або пароль"
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль"
        )

    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "location": user.location
        }
    }


@app.get("/api/popular_books")
def get_popular_books(limit: int = 10, db: Session = Depends(get_db)):
    popular_books = (
        db.query(
            Book,
            func.avg(Rating.rating).label('avg_rating'),
            func.count(Rating.id).label('rating_count')
        )
        .join(Rating, Book.id == Rating.book_id)
        .group_by(Book.id)
        .having(func.count(Rating.id) >= 5)
        .order_by(desc('avg_rating'))
        .limit(limit)
        .all()
    )
    
    if not popular_books:
        return {"message": "Немає книг з рейтингами"}
    
    result = []
    for book, avg_rating, rating_count in popular_books:
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
            "avg_rating": round(float(avg_rating), 2),
            "rating_count": rating_count
        })
    
    return result


@app.get("/api/all_books")
def get_all_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    total = db.query(Book).count()
    books = db.query(Book).offset(skip).limit(limit).all()
    
    result = []
    for book in books:
        result.append({
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "publisher": book.publisher,
            "image_url_s": book.image_url_s,
            "image_url_m": book.image_url_m,
            "image_url_l": book.image_url_l
        })
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "books": result
    }


@app.post("/api/watchlist", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    watchlist_data: schemas.WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    
    book = db.query(Book).filter(Book.id == watchlist_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книгу не знайдено"
        )
    
    existing = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == user_id,
            Watchlist.book_id == watchlist_data.book_id
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Книга вже у watchlist"
        )
    
    new_item = Watchlist(
        user_id=user_id,
        book_id=watchlist_data.book_id
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {
        "message": "Книгу додано до watchlist",
        "watchlist_id": new_item.id
    }


@app.get("/api/watchlist")
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    
    watchlist_items = (
        db.query(Watchlist, Book)
        .join(Book, Watchlist.book_id == Book.id)
        .filter(Watchlist.user_id == user_id)
        .order_by(Watchlist.added_at.desc())
        .all()
    )
    
    if not watchlist_items:
        return {"message": "Ваш watchlist порожній", "books": []}
    
    result = []
    for watchlist, book in watchlist_items:
        result.append({
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
                "image_url_l": book.image_url_l
            }
        })
    
    return {
        "total": len(result),
        "books": result
    }


@app.delete("/api/watchlist/{book_id}")
def remove_from_watchlist(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    
    item = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == user_id,
            Watchlist.book_id == book_id
        )
        .first()
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книгу не знайдено у watchlist"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Книгу видалено з watchlist"}


@app.get("/api/user")
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "location": current_user.location,
        "created_at": current_user.created_at
    }


@app.put("/api/user")
def update_user_profile(
    location: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.location = location
    
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при оновленні профілю: {str(e)}"
        )
    
    return {
        "message": "Профіль оновлено",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "location": current_user.location,
            "created_at": current_user.created_at
        }
    }