from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String(255), nullable=False)

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), index=True)
    year = Column(Integer)
    publisher = Column(String(255))
    image_url_s = Column(String(500))
    image_url_m = Column(String(500))
    image_url_l = Column(String(500))
    
    # Связи (добавишь позже, когда будут другие таблицы)
    # ratings = relationship("Rating", back_populates="book")
    # favorites = relationship("Favorite", back_populates="book")
    
    def __repr__(self):
        return f"<Book {self.title}>"
