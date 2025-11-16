"""
Модуль data_service.py - Завантаження даних з БД для рекомендаційної системи
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User, Item, Rating


def load_users_df(db: Session) -> pd.DataFrame:
    """
    Завантажує всіх користувачів з бази даних у Pandas DataFrame.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: DataFrame з колонками: user_id, username, created_at
    """
    query = select(User)
    users = db.execute(query).scalars().all()
    
    # Перетворюємо список об'єктів SQLAlchemy в DataFrame
    users_data = [
        {
            'user_id': user.id,
            'username': user.email.split('@')[0],  # Якщо треба username з email
            'created_at': user.created_at
        }
        for user in users
    ]
    
    return pd.DataFrame(users_data)


def load_items_df(db: Session) -> pd.DataFrame:
    """
    Завантажує всі елементи (книги/фільми) з бази даних у Pandas DataFrame.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: DataFrame з колонками: item_id, item_type, title, genres, 
             release_year, author_director, actors, description
    """
    query = select(Item)
    items = db.execute(query).scalars().all()
    
    items_data = [
        {
            'item_id': item.id,
            'item_type': item.item_type,
            'title': item.title,
            'genres': item.genres,
            'release_year': item.release_year,
            'author_director': item.author_director,
            'actors': item.actors if hasattr(item, 'actors') else '',
            'description': item.description
        }
        for item in items
    ]
    
    return pd.DataFrame(items_data)


def load_ratings_df(db: Session) -> pd.DataFrame:
    """
    Завантажує всі оцінки з бази даних у Pandas DataFrame.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: DataFrame з колонками: rating_id, user_id, item_id, rating, rating_date
    """
    query = select(Rating)
    ratings = db.execute(query).scalars().all()
    
    ratings_data = [
        {
            'rating_id': rating.id,
            'user_id': rating.user_id,
            'item_id': rating.item_id,
            'rating': rating.rating,
            'rating_date': rating.created_at
        }
        for rating in ratings
    ]
    
    return pd.DataFrame(ratings_data)


def load_all_data(db: Session) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Завантажує всі дані (користувачі, елементи, оцінки) одночасно.
    
    :param db: Сесія SQLAlchemy для доступу до БД
    :return: Кортеж (items_df, users_df, ratings_df)
    """
    items_df = load_items_df(db)
    users_df = load_users_df(db)
    ratings_df = load_ratings_df(db)
    
    return items_df, users_df, ratings_df