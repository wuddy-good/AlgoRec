from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, 
        max_length=100,
        description="Мінімум 8 символів"
    )
    confirm_password: str = Field(
        min_length=8,
        max_length=100,
        description="Підтвердження пароля"
    )
    location: str = Field(  
        min_length=2,
        max_length=255,
        description="Місце розташування користувача"
    )
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Паролі не співпадають')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    location: str 
    created_at: datetime
    
    class Config:
        from_attributes = True 

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    isbn: Optional[str] = None
    title: str
    author: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    image_url_s: Optional[str] = None
    image_url_m: Optional[str] = None
    image_url_l: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    
    class Config:
        from_attributes = True

class BotUserBase(BaseModel):
    location: Optional[str] = None
    age: Optional[int] = None

class BotUserCreate(BotUserBase):
    id: int

class BotUserResponse(BotUserBase):
    id: int
    
    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    user_id: int
    book_id: int
    rating: int = Field(ge=0, le=10, description="Рейтинг від 0 до 10")
    is_bot: bool = False

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WatchlistCreate(BaseModel):
    book_id: int

class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    added_at: datetime
    
    class Config:
        from_attributes = True

class WatchlistWithBook(BaseModel):
    id: int
    book_id: int
    added_at: datetime
    book: BookResponse
    
    class Config:
        from_attributes = True