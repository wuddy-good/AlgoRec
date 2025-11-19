from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String(255), nullable=True)

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), unique=True, index=True, nullable=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), index=True)
    year = Column(Integer)
    publisher = Column(String(255))
    image_url_s = Column(String(500))
    image_url_m = Column(String(500))
    image_url_l = Column(String(500))
    
    def __repr__(self):
        return f"<Book {self.title}>"

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False) 
    book_id = Column(Integer, nullable=False) 
    rating = Column(Integer, nullable=False)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BotUser(Base):
    __tablename__ = "bot_users"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<BotUser {self.id}>"