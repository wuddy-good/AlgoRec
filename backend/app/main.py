from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.auth import hash_password, verify_password, create_access_token
from app.utils import verify_password
from app.models import User 
from app.schemas import UserCreate, UserResponse, UserLogin
from app.database import get_db

app = FastAPI("Movie Site API")

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