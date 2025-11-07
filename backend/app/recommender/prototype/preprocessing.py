import pandas as pd
import numpy as np
from src.utils import logger

def preprocess_data(items_df: pd.DataFrame, ratings_df: pd.DataFrame):
    """
    Виконує попередню обробку даних:
    1. Обчислює середній рейтинг для кожного об'єкта.
    2. Обчислює мінімальний та максимальний рік випуску для нормалізації.
    3. Об'єднує дані.

    :param items_df: DataFrame з інформацією про об'єкти.
    :param ratings_df: DataFrame з рейтингами.
    :return: Об'єднаний DataFrame та словник з метаданими для нормалізації.
    """
    logger.info("Попередня обробка даних...")

    # 1. Обчислення середнього рейтингу
    avg_ratings = ratings_df.groupby('item_id')['rating'].mean().reset_index()
    avg_ratings.rename(columns={'rating': 'avg_rating'}, inplace=True)
    
    # Об'єднання з items_df
    items_df = pd.merge(items_df, avg_ratings, on='item_id', how='left')
    # Заповнення NaN (для об'єктів без рейтингів) середнім рейтингом по всьому датасету
    # Avoid chained-assignment with inplace on a possible view: use explicit assignment
    # so the operation works regardless of whether `items_df` is a view or a copy.
    global_avg_rating = ratings_df['rating'].mean()
    items_df['avg_rating'] = items_df['avg_rating'].fillna(global_avg_rating)
    
    # 2. Обчислення метаданих для нормалізації
    min_year = items_df['release_year'].min()
    max_year = items_df['release_year'].max()
    min_avg_rating = items_df['avg_rating'].min()
    max_avg_rating = items_df['avg_rating'].max()

    metadata = {
        'min_year': min_year,
        'max_year': max_year,
        'min_avg_rating': min_avg_rating,
        'max_avg_rating': max_avg_rating,
        'global_avg_rating': global_avg_rating
    }
    
    logger.info("Попередня обробка завершена.")
    return items_df, metadata
