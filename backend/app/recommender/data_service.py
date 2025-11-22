"""
Модуль data_service.py - Завантаження даних з БД для рекомендаційної системи
Адаптовано під реальну структуру БД (таблиця books замість items)
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User, Book, Rating
import logging

logger = logging.getLogger(__name__)


def load_users_df(db: Session) -> pd.DataFrame:
    """
    Завантажує всіх користувачів з бази даних у Pandas DataFrame.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: DataFrame з колонками: user_id, username, created_at
    """
    logger.info("Завантаження даних з таблиці users...")
    
    query = select(User)
    users = db.execute(query).scalars().all()
    
    # Перетворюємо список об'єктів SQLAlchemy в DataFrame
    users_data = [
        {
            'user_id': user.id,
            'username': user.email.split('@')[0] if user.email else f"user_{user.id}",
            'created_at': user.created_at
        }
        for user in users
    ]
    
    expected_columns = ['user_id', 'username', 'created_at']
    
    if not users_data:
        logger.warning("Таблиця users порожня!")
        return pd.DataFrame(columns=expected_columns)
    
    df = pd.DataFrame(users_data)
    logger.info(f"Завантажено {len(df)} користувачів з БД")
    
    return df


def load_items_df(db: Session) -> pd.DataFrame:
    """
    Завантажує всі книги з бази даних у Pandas DataFrame.
    Адаптує структуру Book до очікуваного формату items для алгоритму.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: DataFrame з колонками: item_id, item_type, title, genres, 
             release_year, author_director, actors, description
    """
    logger.info("Завантаження даних з таблиці books...")
    
    query = select(Book)
    books = db.execute(query).scalars().all()
    
    # Адаптуємо дані Book під очікуваний формат items
    items_data = []
    for book in books:
        # Створюємо штучний опис для TF-IDF (склеюємо доступні текстові поля)
        description_parts = []
        if book.title:
            description_parts.append(book.title)
        if book.author:
            description_parts.append(book.author)
        if book.publisher:
            description_parts.append(book.publisher)
        
        synthetic_description = " ".join(description_parts) if description_parts else ""
        
        items_data.append({
            'item_id': book.id,  # id -> item_id
            'item_type': 'book',  # Всі записи - книги
            'title': book.title if book.title else "Unknown Title",
            'genres': '',  # Немає в БД, залишаємо порожнім
            'release_year': book.year if book.year else 2000,  # year -> release_year
            'author_director': book.author if book.author else "Unknown Author",  # author -> author_director
            'actors': '',  # Немає для книг
            'description': synthetic_description  # Штучний опис
        })
    
    expected_columns = [
        'item_id', 'item_type', 'title', 'genres', 
        'release_year', 'author_director', 'actors', 'description'
    ]
    
    if not items_data:
        logger.warning("Таблиця books порожня!")
        return pd.DataFrame(columns=expected_columns)
    
    df = pd.DataFrame(items_data)
    logger.info(f"Завантажено {len(df)} книг з БД")
    
    return df


def load_ratings_df(db: Session) -> pd.DataFrame:
    """
    Завантажує всі оцінки з бази даних у Pandas DataFrame.
    Адаптує book_id до item_id для сумісності з алгоритмом.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: DataFrame з колонками: rating_id, user_id, item_id, rating, rating_date
    """
    logger.info("Завантаження даних з таблиці ratings...")
    
    query = select(Rating)
    ratings = db.execute(query).scalars().all()
    
    ratings_data = []
    for rating in ratings:
        ratings_data.append({
            'rating_id': rating.id,
            'user_id': rating.user_id,
            'item_id': rating.book_id,  # book_id -> item_id (критична адаптація!)
            'rating': rating.rating,
            'rating_date': rating.created_at
        })
    
    expected_columns = ['rating_id', 'user_id', 'item_id', 'rating', 'rating_date']
    
    if not ratings_data:
        logger.warning("Таблиця ratings порожня!")
        return pd.DataFrame(columns=expected_columns)
    
    df = pd.DataFrame(ratings_data)
    logger.info(f"Завантажено {len(df)} оцінок з БД")
    
    return df


def load_all_data(db: Session) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Завантажує всі дані (користувачі, елементи, оцінки) одночасно.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: Кортеж (items_df, users_df, ratings_df)
    """
    items_df = load_items_df(db)
    users_df = load_users_df(db)
    ratings_df = load_ratings_df(db)
    
    logger.info(f"Завантажено всього: {len(items_df)} items, "
                f"{len(users_df)} users, {len(ratings_df)} ratings")
    
    return items_df, users_df, ratings_df