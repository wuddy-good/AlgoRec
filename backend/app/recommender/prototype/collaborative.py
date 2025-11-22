import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from src.config import TOP_K_CF
from src.utils import logger

def compute_cf_similarity(ratings_df: pd.DataFrame):
    """
    Обчислює item-item collaborative filtering подібність.
    1. Створює item-user матрицю.
    2. Виконує user mean-centering.
    3. Обчислює топ-K найближчих сусідів для кожного об'єкта.

    :param ratings_df: DataFrame з рейтингами.
    :return: Словник {item_id: [(neighbor_item_id, similarity_score), ...]}
    """
    logger.info("Обчислення item-item CF подібності...")

    # 1. Створення item-user матриці R (items x users)
    R = ratings_df.pivot_table(index='item_id', columns='user_id', values='rating')
    R_sparse = csr_matrix(R.fillna(0).values)
    item_ids = R.index.tolist()
    user_ids = R.columns.tolist()

    # 2. User mean-centering
    # Обчислюємо середній рейтинг для кожного користувача
    user_means = ratings_df.groupby('user_id')['rating'].mean()
    
    # Створюємо матрицю середніх значень (items x users)
    R_centered_values = R.copy()
    for user_id in user_ids:
        # Віднімаємо середній рейтинг користувача тільки від тих об'єктів, які він оцінив
        R_centered_values[user_id] = R_centered_values[user_id] - user_means[user_id]
    
    # Заповнюємо NaN нулями для розрідженої матриці
    R_centered_sparse = csr_matrix(R_centered_values.fillna(0).values)

    # 3. Обчислення топ-K найближчих сусідів
    # Використовуємо NearestNeighbors для ефективного пошуку топ-K
    logger.debug(f"Пошук {TOP_K_CF} найближчих сусідів...")
    
    # Використовуємо 'brute' алгоритм, оскільки матриця може бути не дуже великою,
    # а 'cosine' метрика вимагає нормалізації, яка вже частково виконана
    # через mean-centering. Тут ми шукаємо найближчих сусідів у просторі R_centered.
    # Оскільки ми використовуємо mean-centered дані, cosine_similarity тут
    # еквівалентна Pearson correlation.
    
    # Навчаємо модель на транспонованій матриці, щоб шукати сусідів для items (рядки)
    # R_centered_sparse - це (items x users), нам потрібна подібність між рядками.
    # NearestNeighbors працює з рядками.
    
    # Захист від ситуації, коли кількість об'єктів менша за запитуване n_neighbors.
    n_items = R_centered_sparse.shape[0]
    if n_items == 0:
        return {}, R.index.to_list(), R.columns.to_list()

    effective_k = min(TOP_K_CF + 1, n_items)

    nn = NearestNeighbors(n_neighbors=effective_k, metric='cosine', algorithm='brute')
    nn.fit(R_centered_sparse)

    # distances - це 1 - similarity (оскільки metric='cosine')
    distances, indices = nn.kneighbors(R_centered_sparse, return_distance=True)
    
    cf_similarity_map = {}
    for i, item_id in enumerate(item_ids):
        # Відкидаємо перший елемент (сам об'єкт), якщо він присутній.
        # Якщо effective_k == 1, то після відкидання ми отримаємо пустий список.
        neighbor_indices = indices[i][1:effective_k]
        # Перетворюємо відстань на подібність: similarity = 1 - distance
        similarities = 1 - distances[i][1:effective_k]
        # Вирівнюємо подібність у діапазон [0, 1] — негативні кореляції обрізаємо до 0,
        # оскільки в цьому прототипі ми трактуємо подібність як невід'ємну міру.
        similarities = np.clip(similarities, 0.0, 1.0)

        neighbors = []
        for idx, sim in zip(neighbor_indices, similarities):
            neighbor_item_id = item_ids[idx]
            neighbors.append((neighbor_item_id, sim))

        cf_similarity_map[item_id] = neighbors

    logger.info("Обчислення item-item CF завершено.")
    return cf_similarity_map, R.index.to_list(), R.columns.to_list()
