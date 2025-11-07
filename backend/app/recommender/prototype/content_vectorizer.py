import pandas as pd
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler, Normalizer
from src.config import TFIDF_MAX_FEATURES, TFIDF_STOP_WORDS
from src.utils import logger

def create_content_vectors(items_df: pd.DataFrame, metadata: dict):
    """
    Створює вектори контенту для об'єктів, використовуючи TF-IDF, Multi-hot,
    масштабування числових ознак та об'єднання.

    :param items_df: DataFrame з попередньо обробленими даними об'єктів.
    :param metadata: Словник з метаданими для нормалізації.
    :return: Нормалізована розріджена матриця контент-векторів (CSR).
    """
    logger.info("Створення контент-векторів...")
    
    # 1. TF-IDF для description
    logger.debug("Обробка 'description' (TF-IDF)...")
    # Заповнюємо NaN порожнім рядком, щоб уникнути помилок
    descriptions = items_df['description'].fillna('')
    tfidf = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES, stop_words=TFIDF_STOP_WORDS)
    tfidf_matrix = tfidf.fit_transform(descriptions)
    
    # 2. Multi-hot для genres та actors
    def split_and_clean(series):
        return series.fillna('').apply(lambda x: [s.strip() for s in x.split(';') if s.strip()])

    logger.debug("Обробка 'genres' (MultiLabelBinarizer)...")
    genres_list = split_and_clean(items_df['genres'])
    mlb_genres = MultiLabelBinarizer(sparse_output=True)
    genres_matrix = mlb_genres.fit_transform(genres_list)

    logger.debug("Обробка 'actors' (MultiLabelBinarizer)...")
    actors_list = split_and_clean(items_df['actors'])
    mlb_actors = MultiLabelBinarizer(sparse_output=True)
    actors_matrix = mlb_actors.fit_transform(actors_list)
    
    # 3. One-hot/Hashing для author_director
    # Використовуємо MultiLabelBinarizer, оскільки автор/режисер може бути один,
    # але це дозволяє легко об'єднати з іншими sparse-матрицями.
    logger.debug("Обробка 'author_director' (MultiLabelBinarizer)...")
    author_director_list = items_df['author_director'].fillna('').apply(lambda x: [x.strip()])
    mlb_author = MultiLabelBinarizer(sparse_output=True)
    author_matrix = mlb_author.fit_transform(author_director_list)

    # 4. Нормалізація числових ознак (release_year, avg_rating)
    scaler = MinMaxScaler()
    
    # Нормалізація release_year
    logger.debug("Нормалізація 'release_year'...")
    year_data = items_df['release_year'].values.reshape(-1, 1)
    # Використовуємо min/max з метаданих
    year_range = metadata['max_year'] - metadata['min_year']   
    if year_range == 0:
        scaler.min_, scaler.scale_ = metadata['min_year'], 0.0
    else:
        scaler.min_, scaler.scale_ = metadata['min_year'], 1.0 / year_range
    year_scaled = scaler.transform(year_data)
    year_sparse = csr_matrix(year_scaled)

    # Нормалізація avg_rating
    logger.debug("Нормалізація 'avg_rating'...")
    rating_data = items_df['avg_rating'].values.reshape(-1, 1)
    # Використовуємо min/max з метаданих
    rating_range = metadata['max_avg_rating'] - metadata['min_avg_rating']
    if rating_range == 0:
        scaler.min_, scaler.scale_ = metadata['min_avg_rating'], 0.0
    else:
        scaler.min_, scaler.scale_ = metadata['min_avg_rating'], 1.0 / rating_range
    rating_scaled = scaler.transform(rating_data)
    rating_sparse = csr_matrix(rating_scaled)

    # 5. Об'єднання всіх ознак
    logger.debug("Об'єднання всіх ознак...")
    content_vectors = hstack([
        tfidf_matrix,
        genres_matrix,
        actors_matrix,
        author_matrix,
        year_sparse,
        rating_sparse
    ]).tocsr()

    logger.info(f"Створено контент-вектори: {content_vectors.shape}")

    # 6. L2 Нормалізація
    logger.debug("L2 Нормалізація векторів...")
    normalizer = Normalizer(norm='l2')
    content_vectors_normalized = normalizer.fit_transform(content_vectors)
    
    return content_vectors_normalized
