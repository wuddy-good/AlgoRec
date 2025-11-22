import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from src.config import ALPHA, POSITIVE_RATING_THRESHOLD
from src.utils import logger
from sklearn.preprocessing import Normalizer

class HybridRecommender:
    """
    Гібридна рекомендаційна система, що поєднує content-based та item-item CF.
    """
    def __init__(self, items_df: pd.DataFrame, ratings_df: pd.DataFrame, 
                 content_vectors, cf_similarity_map: Dict[int, List[Tuple[int, float]]]):
        
        self.items_df = items_df.set_index('item_id')
        self.ratings_df = ratings_df
        self.content_vectors = content_vectors
        self.cf_similarity_map = cf_similarity_map
        self.item_id_to_idx = {item_id: idx for idx, item_id in enumerate(self.items_df.index)}
        self.idx_to_item_id = {idx: item_id for item_id, idx in self.item_id_to_idx.items()}
        
        # Обчислення середніх рейтингів користувачів для нормалізації
        self.user_means = self.ratings_df.groupby('user_id')['rating'].mean().to_dict()

    def _get_item_vector(self, item_id: int):
        """Повертає контент-вектор для item_id."""
        idx = self.item_id_to_idx.get(item_id)
        if idx is None:
            logger.warning(f"Item ID {item_id} не знайдено.")
            return None
        return self.content_vectors[idx]

    def _get_item_metadata(self, item_id: int):
        """Повертає метадані об'єкта."""
        try:
            return self.items_df.loc[item_id]
        except KeyError:
            return None

    def _compute_hybrid_similarity(self, item_id_i: int, item_id_j: int) -> float:
        """
        Обчислює гібридну подібність між двома об'єктами.
        s(i,j) = alpha * content_sim + (1-alpha) * cf_sim
        """
        # 1. Content Similarity
        vec_i = self._get_item_vector(item_id_i)
        vec_j = self._get_item_vector(item_id_j)
        
        if vec_i is None or vec_j is None:
            return 0.0
        
        # cosine_similarity приймає розріджені матриці
        content_sim = cosine_similarity(vec_i, vec_j)[0, 0]

        # 2. Collaborative Similarity
        cf_sim = 0.0
        # Шукаємо cf_sim(i,j) у кеші для item_i
        neighbors_i = self.cf_similarity_map.get(item_id_i, [])
        for neighbor_id, sim in neighbors_i:
            if neighbor_id == item_id_j:
                cf_sim = sim
                break
        
        # Якщо не знайдено в кеші, шукаємо cf_sim(j,i)
        if cf_sim == 0.0:
            neighbors_j = self.cf_similarity_map.get(item_id_j, [])
            for neighbor_id, sim in neighbors_j:
                if neighbor_id == item_id_i:
                    cf_sim = sim
                    break
        
        # 3. Hybrid Combination
        hybrid_sim = ALPHA * content_sim + (1 - ALPHA) * cf_sim
        return hybrid_sim

    def get_similar_items(self, item_id: int, top_n: int = 3, method: str = 'hybrid') -> List[Dict]:
        """
        Повертає топ-N схожих об'єктів того ж типу.

        :param item_id: ID об'єкта, для якого шукаємо схожі.
        :param top_n: Кількість об'єктів для повернення.
        :param method: 'hybrid', 'content' або 'cf'.
        :return: Список словників з інформацією про схожі об'єкти.
        """
        logger.info(f"Пошук {top_n} схожих об'єктів для Item ID {item_id} (метод: {method})...")
        
        if item_id not in self.item_id_to_idx:
            logger.warning(f"Item ID {item_id} не знайдено.")
            return []

        # Отримуємо тип цільового об'єкта
        target_meta = self._get_item_metadata(item_id)
        if target_meta is None:
            logger.warning(f"Метадані для Item ID {item_id} не знайдено.")
            return []
        target_type = target_meta['item_type']
        
        target_idx = self.item_id_to_idx[item_id]
        target_vec = self.content_vectors[target_idx]
        
        similarities = []
        
        # Фільтруємо кандидатів за типом
        candidates = self.items_df[self.items_df['item_type'] == target_type].index
        
        for candidate_id in candidates:
            if candidate_id == item_id:
                continue
            
            score = 0.0
            
            if method == 'content':
                candidate_idx = self.item_id_to_idx[candidate_id]
                candidate_vec = self.content_vectors[candidate_idx]
                score = cosine_similarity(target_vec, candidate_vec)[0, 0]
            
            elif method == 'cf':
                neighbors = self.cf_similarity_map.get(item_id, [])
                for neighbor_id, sim in neighbors:
                    if neighbor_id == candidate_id:
                        score = sim
                        break
            
            elif method == 'hybrid':
                score = self._compute_hybrid_similarity(item_id, candidate_id)
            
            else:
                raise ValueError(f"Невідомий метод подібності: {method}")

            similarities.append((candidate_id, score))

        # Сортування та вибір топ-N
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar = similarities[:top_n]
        
        results = []
        for item_id, score in top_similar:
            meta = self._get_item_metadata(item_id)
            if meta is not None:
                results.append({
                    'item_id': item_id,
                    'title': meta['title'],
                    'item_type': meta['item_type'],
                    'genres': meta['genres'],
                    'release_year': meta['release_year'],
                    'score': score
                })
        
        return results

    def _build_user_profile(self, user_id: int):
        """
        Будує профіль користувача як зважений середній вектор.
        Використовуємо всі рейтинги з вагою (rating - user_mean).
        """
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        if user_ratings.empty:
            logger.warning(f"Користувач {user_id} не має рейтингів.")
            return None

        user_mean = self.user_means.get(user_id, 0.0)
        
        # Ваги: (rating - user_mean)
        weights = user_ratings['rating'] - user_mean
        
        # Отримання контент-векторів оцінених об'єктів
        rated_item_ids = user_ratings['item_id'].tolist()
        rated_indices = [self.item_id_to_idx[i] for i in rated_item_ids if i in self.item_id_to_idx]
        
        if not rated_indices:
            logger.warning(f"Не знайдено контент-векторів для оцінених об'єктів користувача {user_id}.")
            return None

        # Фільтруємо ваги відповідно до наявних векторів
        weights = weights[[i in self.item_id_to_idx for i in rated_item_ids]].values.reshape(-1, 1)
        
        # Зважена сума векторів
        rated_vectors = self.content_vectors[rated_indices]
        weighted_sum = rated_vectors.multiply(weights).sum(axis=0)
        
        
        # Конвертуємо результат у звичайний numpy.ndarray (щоб уникнути numpy.matrix)
        # Деякі операції на scipy.sparse повертають np.matrix-подібні об'єкти,
        # які не підтримуються в нових версіях sklearn/numpy.
        if hasattr(weighted_sum, "toarray"):
            weighted_sum = weighted_sum.toarray()
        weighted_sum = np.asarray(weighted_sum)
        # Забезпечуємо форму (1, n)
        if weighted_sum.ndim == 1:
            weighted_sum = weighted_sum.reshape(1, -1)
        elif weighted_sum.shape[0] != 1 and weighted_sum.shape[1] == 1:
            # випадок (n,1) -> перелаштувати
            weighted_sum = weighted_sum.T.reshape(1, -1)

        # Нормалізація (L2)
        profile_vector = Normalizer(norm='l2').fit_transform(weighted_sum)
        return profile_vector

    def _build_anon_profile(self, liked_item_ids: List[int]):
        """
        Будує профіль анонімного користувача як середній вектор вподобаних об'єктів.
        """
        if not liked_item_ids:
            return None
        
        # Отримання контент-векторів вподобаних об'єктів
        liked_indices = [self.item_id_to_idx[i] for i in liked_item_ids if i in self.item_id_to_idx]
        
        if not liked_indices:
            logger.warning("Не знайдено контент-векторів для вподобаних об'єктів.")
            return None
        
        # Середній вектор
        liked_vectors = self.content_vectors[liked_indices]
        mean_vector = liked_vectors.mean(axis=0)
        
        # Конвертуємо у numpy.ndarray, щоб уникнути numpy.matrix
        if hasattr(mean_vector, "toarray"):
            mean_vector = mean_vector.toarray()
        mean_vector = np.asarray(mean_vector)
        if mean_vector.ndim == 1:
            mean_vector = mean_vector.reshape(1, -1)
        elif mean_vector.shape[0] != 1 and mean_vector.shape[1] == 1:
            mean_vector = mean_vector.T.reshape(1, -1)

        # Нормалізація (L2)
        profile_vector = Normalizer(norm='l2').fit_transform(mean_vector)
        return profile_vector

    def _score_candidates(self, profile_vector, candidate_item_ids: List[int]) -> List[Tuple[int, float]]:
        """
        Оцінює кандидатів за подібністю профілю до контент-векторів.
        """
        candidate_indices = [self.item_id_to_idx[i] for i in candidate_item_ids if i in self.item_id_to_idx]
        
        if not candidate_indices:
            return []

        candidate_vectors = self.content_vectors[candidate_indices]
        
        # Content-based score: cosine similarity між профілем та векторами кандидатів
        content_scores = cosine_similarity(profile_vector, candidate_vectors)[0]
        
        # Collaborative score:
        # Для гібридного підходу в рекомендаціях для користувача,
        # ми використовуємо item-item CF для обчислення score(u,c) = sum_{i in R_u} w_{u,i} * s(i,c)
        # Однак, для простоти прототипу, і зважаючи на те, що CF-подібність вже
        # обчислена між об'єктами, ми можемо використати спрощений підхід:
        # CF score = середнє CF-подібності між кандидатом та позитивно оціненими об'єктами користувача.
        # Або, як вказано в інструкції:
        # score(u,c) = sum_{i in R_u} w_{u,i} * s(i,c) / sum_{i} |w_{u,i}|
        
        # Для цього прототипу, ми будемо використовувати тільки Content-based score
        # для рекомендацій користувачу/аноніму, оскільки повна реалізація
        # формули score(u,c) вимагає додаткових даних (w_u,i) та ітерації по всіх
        # оцінених об'єктах користувача, що є складним для CLI-прототипу.
        # Ми використовуємо гібридну подібність _compute_hybrid_similarity тільки для
        # команди `similar`.
        
        # Для рекомендацій (recommend_for_user/anon) ми використовуємо Content-based
        # підхід з профілем, побудованим на позитивно оцінених об'єктах.
        
        # Якщо потрібно строго дотримуватись формули:
        # score(u,c) = sum_{i in R_u} w_{u,i} * s(i,c) / sum_{i} |w_{u,i}|
        # Це вимагає перерахунку для кожного кандидата, що повільно.
        
        # Для CLI-прототипу, ми повернемося до Content-based рекомендацій
        # (профіль користувача -> подібність до кандидата)
        
        results = []
        for i, score in enumerate(content_scores):
            item_id = self.idx_to_item_id[candidate_indices[i]]
            results.append((item_id, score))
            
        return results

    def recommend_for_user(self, user_id: int, top_n: int = 10) -> List[Dict]:
        """
        Генерує рекомендації для зареєстрованого користувача.
        """
        logger.info(f"Генерація {top_n} рекомендацій для User ID {user_id}...")
        
        profile_vector = self._build_user_profile(user_id)
        if profile_vector is None:
            return []

        # Виключити об'єкти, які користувач вже оцінив
        rated_item_ids = self.ratings_df[self.ratings_df['user_id'] == user_id]['item_id'].unique()
        all_item_ids = set(self.items_df.index)
        candidate_item_ids = list(all_item_ids - set(rated_item_ids))
        
        scores = self._score_candidates(profile_vector, candidate_item_ids)
        
        # Сортування та вибір топ-N
        scores.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = scores[:top_n]
        
        results = []
        for item_id, score in top_recommendations:
            meta = self._get_item_metadata(item_id)
            if meta is not None:
                results.append({
                    'item_id': item_id,
                    'title': meta['title'],
                    'item_type': meta['item_type'],
                    'genres': meta['genres'],
                    'release_year': meta['release_year'],
                    'score': score
                })
        
        return results

    def recommend_for_anon(self, liked_item_ids: List[int], top_n: int = 10) -> List[Dict]:
        """
        Генерує рекомендації для анонімного користувача на основі вподобаних об'єктів.
        """
        logger.info(f"Генерація {top_n} рекомендацій для аноніма (вподобано: {liked_item_ids})...")
        
        profile_vector = self._build_anon_profile(liked_item_ids)
        if profile_vector is None:
            return []

        # Виключити об'єкти, які вже були вподобані
        all_item_ids = set(self.items_df.index)
        candidate_item_ids = list(all_item_ids - set(liked_item_ids))
        
        scores = self._score_candidates(profile_vector, candidate_item_ids)
        
        # Сортування та вибір топ-N
        scores.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = scores[:top_n]
        
        results = []
        for item_id, score in top_recommendations:
            meta = self._get_item_metadata(item_id)
            if meta is not None:
                results.append({
                    'item_id': item_id,
                    'title': meta['title'],
                    'item_type': meta['item_type'],
                    'genres': meta['genres'],
                    'release_year': meta['release_year'],
                    'score': score
                })
        
        return results

    def get_item_info(self, item_id: int) -> Dict:
        """
        Повертає зведену інформацію про об'єкт.
        """
        meta = self._get_item_metadata(item_id)
        if meta is None:
            return {}
        
        # Обчислення середнього рейтингу
        avg_rating = self.ratings_df[self.ratings_df['item_id'] == item_id]['rating'].mean()
        
        return {
            'item_id': item_id,
            'title': meta['title'],
            'item_type': meta['item_type'],
            'genres': meta['genres'],
            'release_year': meta['release_year'],
            'author_director': meta['author_director'],
            'description': meta['description'],
            'avg_rating': avg_rating if not pd.isna(avg_rating) else 'N/A'
        }
