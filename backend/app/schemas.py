from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

# Схема для входа пользователя
class UserLogin(BaseModel):
    email: str
    password: str

# Схема для регистрации пользователя
class UserCreate(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    password: str = Field(
        min_length=8, 
        max_length=100,
        description="Минимум 8 символов"
    )
    confirm_password: str = Field(
        min_length=8,
        max_length=100,
        description="Подтверждение пароля"
    )
    location: str = Field(  
        min_length=2,
        max_length=255,
        description="Местоположение пользователя"
    )
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        """Проверка совпадения паролей"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return v


class UserResponse(BaseModel):
    """Схема для ответа (без пароля!)"""
    id: int
    email: str
    location: str 
    created_at: datetime
    
    class Config:
        from_attributes = True  # для роботи з sqlalchemy моделями