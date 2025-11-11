from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

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
        
class BookBase(BaseModel):
    isbn: str
    title: str
    author: str | None = None
    year: int | None = None
    publisher: str | None = None
    image_url_s: str | None = None
    image_url_m: str | None = None
    image_url_l: str | None = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    
    class Config:
        from_attributes = True