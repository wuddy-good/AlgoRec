"""
Модуль service.py - Сервіс рекомендацій
Інкапсулює всю логіку content-based та collaborative filtering
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler, Normalizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sqlalchemy.orm import Session
import logging

from backend.app.recommender.data_service import load_items_df, load_ratings_df, load_users_df

logger = logging.getLogger(__name__)


class RecommenderService:
    """
    Гібридна рекомендаційна система, що поєднує content-based та item-item CF.
    
    Цей клас — це наш 'двигун рекомендацій'. Коли він створюється, він одразу:
    1. Завантажує всі дані з БД (елементи, користувачі, оцінки)
    2. Будує TF-IDF матрицю для текстових описів
    3. Кодує категоріальні ознаки (жанри, актори)
    4. Обчислює матрицю подібності контенту (cosine similarity)
    5. Обчислює item-item collaborative filtering подібність
    6. Зберігає все в пам'яті для швидких рекомендацій
    
    Після ініціалізації ви можете викликати методи get_*_recommendations для отримання рекомендацій.
    """
    
    def __init__(self, db: Session, alpha: float = 0.7, top_k_cf: int = 10):
        """
        Ініціалізує сервіс рекомендацій.
        
        :param db: Сесія SQLAlchemy для доступу до БД
        :param alpha: Вага content-based score (1-alpha для CF score)
        :param top_k_cf: Кількість найближчих сусідів для item-item CF
        """
        logger.info("Ініціалізація RecommenderService...")
        
        self.db = db
        self.alpha = alpha
        self.top_k_cf = top_k_cf
        
        # Завантаження даних
        self._load_data()
        
        # Підготовка даних
        self._prepare_data()
        
        # Побудова контент-векторів
        self._build_content_vectors()
        
        # Обчислення CF подібності
        self._compute_cf_similarity()
        
        logger.info("RecommenderService готовий до роботи!")
    
    def _load_data(self):
        """Завантажує дані з БД через data_service."""
        logger.info("Завантаження даних з БД...")
        
        self.items_df = load_items_df(self.db)
        self.users_df = load_users_df(self.db)
        self.ratings_df = load_ratings_df(self.db)
        
        logger.info(f"Завантажено: {len(self.items_df)} елементів, "
                   f"{len(self.users_df)} користувачів, "
                   f"{len(self.ratings_df)} оцінок")
    
    def _prepare_data(self):
        """
        Підготовка даних: обчислення середніх рейтингів, метаданих для нормалізації.
        (Логіка з preprocessing.py)
        """
        logger.info("Підготовка даних...")
        
        # Обчислення середнього рейтингу для кожного елемента
        avg_ratings = self.ratings_df.groupby('item_id')['rating'].mean().reset_index()
        avg_ratings.rename(columns={'rating': 'avg_rating'}, inplace=True)
        
        # Об'єднання з items_df
        self.items_df = pd.merge(self.items_df, avg_ratings, on='item_id', how='left')
        
        # Заповнення NaN середнім рейтингом по всьому датасету
        self.global_avg_rating = self.ratings_df['rating'].mean()
        self.items_df['avg_rating'] = self.items_df['avg_rating'].fillna(self.global_avg_rating)
        
        # Метадані для нормалізації
        self.min_year = self.items_df['release_year'].min()
        self.max_year = self.items_df['release_year'].max()
        self.min_avg_rating = self.items_df['avg_rating'].min()
        self.max_avg_rating = self.items_df['avg_rating'].max()
        
        # Обчислення середніх рейтингів користувачів (для CF)
        self.user_means = self.ratings_df.groupby('user_id')['rating'].mean().to_dict()
        
        # Створення мапінгу item_id -> index
        self.items_df = self.items_df.set_index('item_id')
        self.item_id_to_idx = {item_id: idx for idx, item_id in enumerate(self.items_df.index)}
        self.idx_to_item_id = {idx: item_id for item_id, idx in self.item_id_to_idx.items()}
        
        logger.info("Підготовка даних завершена")
    
    def _build_content_vectors(self):
        """
        Будує контент-вектори для елементів.
        (Логіка з content_vectorizer.py)
        """
        logger.info("Побудова контент-векторів...")
        
        # 1. TF-IDF для description
        descriptions = self.items_df['description'].fillna('')
        self.tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
        tfidf_matrix = self.tfidf.fit_transform(descriptions)
        
        # 2. Multi-hot для genres
        def split_and_clean(series):
            return series.fillna('').apply(lambda x: [s.strip() for s in x.split(';') if s.strip()])
        
        genres_list = split_and_clean(self.items_df['genres'])
        self.mlb_genres = MultiLabelBinarizer(sparse_output=True)
        genres_matrix = self.mlb_genres.fit_transform(genres_list)
        
        # 3. Multi-hot для actors
        actors_list = split_and_clean(self.items_df['actors'])
        self.mlb_actors = MultiLabelBinarizer(sparse_output=True)
        actors_matrix = self.mlb_actors.fit_transform(actors_list)
        
        # 4. Multi-hot для author_director
        author_director_list = self.items_df['author_director'].fillna('').apply(lambda x: [x.strip()])
        self.mlb_author = MultiLabelBinarizer(sparse_output=True)
        author_matrix = self.mlb_author.fit_transform(author_director_list)
        
        # 5. Нормалізація числових ознак
        scaler = MinMaxScaler()
        
        # Release year
        year_data = self.items_df['release_year'].values.reshape(-1, 1)
        year_range = self.max_year - self.min_year
        if year_range == 0:
            year_scaled = np.zeros_like(year_data, dtype=float)
        else:
            scaler.min_, scaler.scale_ = self.min_year, 1.0 / year_range
            year_scaled = scaler.transform(year_data)
        year_sparse = csr_matrix(year_scaled)
        
        # Avg rating
        rating_data = self.items_df['avg_rating'].values.reshape(-1, 1)
        rating_range = self.max_avg_rating - self.min_avg_rating
        if rating_range == 0:
            rating_scaled = np.zeros_like(rating_data, dtype=float)
        else:
            scaler.min_, scaler.scale_ = self.min_avg_rating, 1.0 / rating_range
            rating_scaled = scaler.transform(rating_data)
        rating_sparse = csr_matrix(rating_scaled)
        
        # 6. Об'єднання всіх ознак
        self.content_vectors = hstack([
            tfidf_matrix,
            genres_matrix,
            actors_matrix,
            author_matrix,
            year_sparse,
            rating_sparse
        ]).tocsr()
        
        # 7. L2 нормалізація
        normalizer = Normalizer(norm='l2')
        self.content_vectors = normalizer.fit_transform(self.content_vectors)
        
        logger.info(f"Контент-вектори створено: {self.content_vectors.shape}")
    
    def _compute_cf_similarity(self):
        """
        Обчислює item-item collaborative filtering подібність.
        (Логіка з collaborative.py)
        """
        logger.info("Обчислення item-item CF подібності...")
        
        # Створення item-user матриці
        R = self.ratings_df.pivot_table(index='item_id', columns='user_id', values='rating')
        item_ids = R.index.tolist()
        user_ids = R.columns.tolist()
        
        # User mean-centering
        R_centered_values = R.copy()
        for user_id in user_ids:
            if user_id in self.user_means:
                R_centered_values[user_id] = R_centered_values[user_id] - self.user_means[user_id]
        
        R_centered_sparse = csr_matrix(R_centered_values.fillna(0).values)
        
        # Обчислення топ-K найближчих сусідів
        n_items = R_centered_sparse.shape[0]
        if n_items == 0:
            self.cf_similarity_map = {}
            return
        
        effective_k = min(self.top_k_cf + 1, n_items)
        nn = NearestNeighbors(n_neighbors=effective_k, metric='cosine', algorithm='brute')
        nn.fit(R_centered_sparse)
        
        distances, indices = nn.kneighbors(R_centered_sparse, return_distance=True)
        
        self.cf_similarity_map = {}
        for i, item_id in enumerate(item_ids):
            neighbor_indices = indices[i][1:effective_k]
            similarities = 1 - distances[i][1:effective_k]
            similarities = np.clip(similarities, 0.0, 1.0)
            
            neighbors = []
            for idx, sim in zip(neighbor_indices, similarities):
                neighbor_item_id = item_ids[idx]
                neighbors.append((neighbor_item_id, sim))
            
            self.cf_similarity_map[item_id] = neighbors
        
        logger.info("Item-item CF подібність обчислено")
    
    def get_content_based_recommendations(self, item_id: int, top_n: int = 10) -> List[Dict]:
        """
        Повертає топ-N схожих елементів на основі контенту.
        
        :param item_id: ID елемента, для якого шукаємо схожі
        :param top_n: Кількість рекомендацій
        :return: Список словників з інформацією про схожі елементи
        """
        logger.info(f"Генерація content-based рекомендацій для item_id={item_id}")
        
        if item_id not in self.item_id_to_idx:
            logger.warning(f"Item ID {item_id} не знайдено")
            return []
        
        # Отримуємо тип цільового елемента (фільтруємо за типом)
        target_meta = self.items_df.loc[item_id]
        target_type = target_meta['item_type']
        
        target_idx = self.item_id_to_idx[item_id]
        target_vec = self.content_vectors[target_idx]
        
        # Фільтруємо кандидатів за типом
        candidates = self.items_df[self.items_df['item_type'] == target_type].index
        candidate_indices = [self.item_id_to_idx[cid] for cid in candidates if cid != item_id]
        
        if not candidate_indices:
            return []
        
        # Обчислюємо cosine similarity
        candidate_vectors = self.content_vectors[candidate_indices]
        similarities = cosine_similarity(target_vec, candidate_vectors)[0]
        
        # Сортуємо та вибираємо топ-N
        sorted_indices = np.argsort(similarities)[::-1][:top_n]
        
        results = []
        for idx in sorted_indices:
            candidate_id = self.idx_to_item_id[candidate_indices[idx]]
            meta = self.items_df.loc[candidate_id]
            results.append({
                'item_id': int(candidate_id),
                'title': meta['title'],
                'item_type': meta['item_type'],
                'genres': meta['genres'],
                'release_year': int(meta['release_year']),
                'score': float(similarities[idx])
            })
        
        return results
    
    def get_collaborative_recommendations(self, item_id: int, top_n: int = 10) -> List[Dict]:
        """
        Повертає топ-N схожих елементів на основі collaborative filtering.
        
        :param item_id: ID елемента
        :param top_n: Кількість рекомендацій
        :return: Список словників з інформацією про схожі елементи
        """
        logger.info(f"Генерація CF рекомендацій для item_id={item_id}")
        
        if item_id not in self.cf_similarity_map:
            logger.warning(f"CF подібність для item_id={item_id} не знайдено")
            return []
        
        neighbors = self.cf_similarity_map[item_id][:top_n]
        
        results = []
        for neighbor_id, score in neighbors:
            if neighbor_id in self.items_df.index:
                meta = self.items_df.loc[neighbor_id]
                results.append({
                    'item_id': int(neighbor_id),
                    'title': meta['title'],
                    'item_type': meta['item_type'],
                    'genres': meta['genres'],
                    'release_year': int(meta['release_year']),
                    'score': float(score)
                })
        
        return results
    
    def get_hybrid_recommendations(self, item_id: int, top_n: int = 10) -> List[Dict]:
        """
        Повертає топ-N схожих елементів, комбінуючи content-based та CF.
        
        :param item_id: ID елемента
        :param top_n: Кількість рекомендацій
        :return: Список словників з інформацією про схожі елементи
        """
        logger.info(f"Генерація гібридних рекомендацій для item_id={item_id}")
        
        if item_id not in self.item_id_to_idx:
            return []
        
        target_meta = self.items_df.loc[item_id]
        target_type = target_meta['item_type']
        target_idx = self.item_id_to_idx[item_id]
        target_vec = self.content_vectors[target_idx]
        
        # Фільтруємо кандидатів за типом
        candidates = self.items_df[self.items_df['item_type'] == target_type].index
        
        scores = []
        for candidate_id in candidates:
            if candidate_id == item_id:
                continue
            
            # Content similarity
            candidate_idx = self.item_id_to_idx[candidate_id]
            candidate_vec = self.content_vectors[candidate_idx]
            content_sim = cosine_similarity(target_vec, candidate_vec)[0, 0]
            
            # CF similarity
            cf_sim = 0.0
            neighbors = self.cf_similarity_map.get(item_id, [])
            for neighbor_id, sim in neighbors:
                if neighbor_id == candidate_id:
                    cf_sim = sim
                    break
            
            # Якщо не знайдено в кеші, шукаємо в зворотному напрямку
            if cf_sim == 0.0:
                neighbors_j = self.cf_similarity_map.get(candidate_id, [])
                for neighbor_id, sim in neighbors_j:
                    if neighbor_id == item_id:
                        cf_sim = sim
                        break
            
            # Hybrid score
            hybrid_score = self.alpha * content_sim + (1 - self.alpha) * cf_sim
            scores.append((candidate_id, hybrid_score))
        
        # Сортуємо та вибираємо топ-N
        scores.sort(key=lambda x: x[1], reverse=True)
        top_items = scores[:top_n]
        
        results = []
        for candidate_id, score in top_items:
            meta = self.items_df.loc[candidate_id]
            results.append({
                'item_id': int(candidate_id),
                'title': meta['title'],
                'item_type': meta['item_type'],
                'genres': meta['genres'],
                'release_year': int(meta['release_year']),
                'score': float(score)
            })
        
        return results
    
    def get_user_recommendations(self, user_id: int, top_n: int = 10) -> List[Dict]:
        """
        Генерує персоналізовані рекомендації для користувача.
        
        :param user_id: ID користувача
        :param top_n: Кількість рекомендацій
        :return: Список словників з рекомендованими елементами
        """
        logger.info(f"Генерація рекомендацій для user_id={user_id}")
        
        # Будуємо профіль користувача
        profile_vector = self._build_user_profile(user_id)
        if profile_vector is None:
            return []
        
        # Виключаємо вже оцінені елементи
        rated_item_ids = self.ratings_df[self.ratings_df['user_id'] == user_id]['item_id'].unique()
        all_item_ids = set(self.items_df.index)
        candidate_item_ids = list(all_item_ids - set(rated_item_ids))
        
        # Оцінюємо кандидатів
        scores = self._score_candidates(profile_vector, candidate_item_ids)
        scores.sort(key=lambda x: x[1], reverse=True)
        top_items = scores[:top_n]
        
        results = []
        for item_id, score in top_items:
            meta = self.items_df.loc[item_id]
            results.append({
                'item_id': int(item_id),
                'title': meta['title'],
                'item_type': meta['item_type'],
                'genres': meta['genres'],
                'release_year': int(meta['release_year']),
                'score': float(score)
            })
        
        return results
    
    def _build_user_profile(self, user_id: int):
        """Будує профіль користувача як зважений середній вектор."""
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        if user_ratings.empty:
            logger.warning(f"Користувач {user_id} не має рейтингів")
            return None
        
        user_mean = self.user_means.get(user_id, 0.0)
        weights = user_ratings['rating'] - user_mean
        
        rated_item_ids = user_ratings['item_id'].tolist()
        rated_indices = [self.item_id_to_idx[i] for i in rated_item_ids if i in self.item_id_to_idx]
        
        if not rated_indices:
            return None
        
        weights = weights[[i in self.item_id_to_idx for i in rated_item_ids]].values.reshape(-1, 1)
        rated_vectors = self.content_vectors[rated_indices]
        weighted_sum = rated_vectors.multiply(weights).sum(axis=0)
        
        if hasattr(weighted_sum, "toarray"):
            weighted_sum = weighted_sum.toarray()
        weighted_sum = np.asarray(weighted_sum)
        if weighted_sum.ndim == 1:
            weighted_sum = weighted_sum.reshape(1, -1)
        
        profile_vector = Normalizer(norm='l2').fit_transform(weighted_sum)
        return profile_vector
    
    def _score_candidates(self, profile_vector, candidate_item_ids: List[int]) -> List[Tuple[int, float]]:
        """Оцінює кандидатів за подібністю до профілю."""
        candidate_indices = [self.item_id_to_idx[i] for i in candidate_item_ids if i in self.item_id_to_idx]
        
        if not candidate_indices:
            return []
        
        candidate_vectors = self.content_vectors[candidate_indices]
        content_scores = cosine_similarity(profile_vector, candidate_vectors)[0]
        
        results = []
        for i, score in enumerate(content_scores):
            item_id = self.idx_to_item_id[candidate_indices[i]]
            results.append((item_id, score))
        
        return results
    
    def get_item_details(self, item_id: int) -> Optional[Dict]:
        """
        Повертає детальну інформацію про елемент.
        
        :param item_id: ID елемента
        :return: Словник з інформацією або None
        """
        if item_id not in self.items_df.index:
            return None
        
        meta = self.items_df.loc[item_id]
        avg_rating = self.ratings_df[self.ratings_df['item_id'] == item_id]['rating'].mean()
        
        return {
            'item_id': int(item_id),
            'title': meta['title'],
            'item_type': meta['item_type'],
            'genres': meta['genres'],
            'release_year': int(meta['release_year']),
            'author_director': meta['author_director'],
            'description': meta['description'],
            'avg_rating': float(avg_rating) if not pd.isna(avg_rating) else None
        }