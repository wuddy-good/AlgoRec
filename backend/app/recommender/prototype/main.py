import pandas as pd
from src.config import ITEM_VECTORS_CACHE, ITEM_CF_SIM_CACHE, METADATA_CACHE
from src.utils import logger
from src.data_loader import load_data
from src.preprocessing import preprocess_data
from src.content_vectorizer import create_content_vectors
from src.collaborative import compute_cf_similarity
from src.cache_utils import load_cache, save_cache
from src.recommender import HybridRecommender
from tqdm import tqdm

def precompute_and_cache(force: bool = False) -> HybridRecommender:
    """
    Виконує повний цикл обчислення та кешування всіх необхідних даних.

    :param force: Примусово перерахувати дані, ігноруючи кеш.
    :return: Ініціалізований об'єкт HybridRecommender.
    """
    logger.info("Початок попереднього обчислення та кешування...")

    # 1. Завантаження даних
    items_df, users_df, ratings_df = load_data()

    # 2. Попередня обробка та метадані
    metadata = load_cache(METADATA_CACHE, force)
    if metadata is None:
        items_df_preprocessed, metadata = preprocess_data(items_df.copy(), ratings_df.copy())
        save_cache(METADATA_CACHE, metadata)
    else:
        # Повторна попередня обробка для отримання items_df_preprocessed
        items_df_preprocessed, _ = preprocess_data(items_df.copy(), ratings_df.copy())
        logger.info("Метадані завантажено з кешу.")

    # 3. Content Vectors
    content_vectors = load_cache(ITEM_VECTORS_CACHE, force)
    if content_vectors is None:
        content_vectors = create_content_vectors(items_df_preprocessed, metadata)
        save_cache(ITEM_VECTORS_CACHE, content_vectors)
    else:
        logger.info("Контент-вектори завантажено з кешу.")

    # 4. Collaborative Similarity
    cf_similarity_map = load_cache(ITEM_CF_SIM_CACHE, force)
    if cf_similarity_map is None:
        # Використовуємо tqdm для відображення прогресу обчислення CF
        with tqdm(total=1, desc="Обчислення CF подібності", unit="крок") as pbar:
            cf_similarity_map, _, _ = compute_cf_similarity(ratings_df.copy())
            pbar.update(1)
        save_cache(ITEM_CF_SIM_CACHE, cf_similarity_map)
    else:
        logger.info("CF подібність завантажено з кешу.")

    # 5. Ініціалізація рекомендатора
    recommender = HybridRecommender(items_df_preprocessed, ratings_df, content_vectors, cf_similarity_map)
    logger.info("Об'єкт HybridRecommender ініціалізовано.")
    
    return recommender

def get_recommender(force: bool = False) -> HybridRecommender:
    """
    Отримує або обчислює та кешує об'єкт HybridRecommender.
    """
    # Спроба завантажити всі компоненти з кешу
    metadata = load_cache(METADATA_CACHE, force)
    content_vectors = load_cache(ITEM_VECTORS_CACHE, force)
    cf_similarity_map = load_cache(ITEM_CF_SIM_CACHE, force)

    if metadata is None or content_vectors is None or cf_similarity_map is None:
        logger.info("Кеш неповний або невалідний. Запускаємо повне переобчислення.")
        return precompute_and_cache(force=True)
    
    # Якщо кеш валідний, завантажуємо лише сирі дані для ініціалізації
    items_df, _, ratings_df = load_data()
    items_df_preprocessed, _ = preprocess_data(items_df.copy(), ratings_df.copy())
    
    recommender = HybridRecommender(items_df_preprocessed, ratings_df, content_vectors, cf_similarity_map)
    logger.info("Об'єкт HybridRecommender ініціалізовано з кешу.")
    return recommender
