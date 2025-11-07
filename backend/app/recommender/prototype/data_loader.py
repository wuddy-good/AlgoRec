import pandas as pd
from src.config import ITEMS_FILE, USERS_FILE, RATINGS_FILE
from src.utils import logger

def load_data():
    """
    Завантажує дані з CSV-файлів та виконує базову валідацію.

    :return: Кортеж (items_df, users_df, ratings_df)
    :raises FileNotFoundError: Якщо файл даних не знайдено.
    :raises ValueError: Якщо структура даних не відповідає очікуваній.
    """
    logger.info("Завантаження даних...")
    
    try:
        items_df = pd.read_csv(ITEMS_FILE, header=None, names=['item_id', 'item_type', 'title', 'genres', 'release_year', 'author_director', 'actors', 'description'], skiprows=1)
        users_df = pd.read_csv(USERS_FILE, header=None, names=['user_id', 'username', 'join_date'], skiprows=1)
        ratings_df = pd.read_csv(RATINGS_FILE, header=None, names=['rating_id', 'user_id', 'item_id', 'rating', 'timestamp'], skiprows=1)
    except FileNotFoundError as e:
        logger.error(f"Файл даних не знайдено: {e.filename}")
        raise

    # --- Валідація items_df ---
    if not all(col in items_df.columns for col in ['item_id', 'title', 'genres', 'release_year', 'description']):
        raise ValueError("Неповна структура items.csv")
    if items_df['item_id'].dtype != 'int64':
        items_df['item_id'] = items_df['item_id'].astype(int)
    
    # --- Валідація users_df ---
    if not all(col in users_df.columns for col in ['user_id', 'username']):
        raise ValueError("Неповна структура users.csv")
    if users_df['user_id'].dtype != 'int64':
        users_df['user_id'] = users_df['user_id'].astype(int)

    # --- Валідація ratings_df ---
    if not all(col in ratings_df.columns for col in ['user_id', 'item_id', 'rating']):
        raise ValueError("Неповна структура ratings.csv")
    if ratings_df['user_id'].dtype != 'int64' or ratings_df['item_id'].dtype != 'int64':
        ratings_df['user_id'] = ratings_df['user_id'].astype(int)
        ratings_df['item_id'] = ratings_df['item_id'].astype(int)
    if ratings_df['rating'].dtype not in ['int64', 'float64']:
        ratings_df['rating'] = ratings_df['rating'].astype(float)
    
    # Перевірка діапазону рейтингів (припускаємо 1-5)
    if not ((ratings_df['rating'] >= 1) & (ratings_df['rating'] <= 5)).all():
        logger.warning("Рейтинги виходять за межі очікуваного діапазону [1, 5].")

    logger.info(f"Завантажено {len(items_df)} об'єктів, {len(users_df)} користувачів, {len(ratings_df)} рейтингів.")
    
    return items_df, users_df, ratings_df
