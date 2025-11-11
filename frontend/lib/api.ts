// Базовий API service для легкого підключення бекенду

import { User, WatchlistItem, Rating } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Отримати токен авторизації
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
};

// Базовий fetch з авторизацією
const apiRequest = async <T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const token = getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  // 204 No Content або порожнє тіло
  if (response.status === 204) {
    return null as T;
  }

  const text = await response.text();
  if (!text) {
    return null as T;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    // Якщо бекенд повернув не-JSON, повертаємо як текст
    return text as T;
  }
};

// API методи для рейтингів
export const ratingsApi = {
  // Отримати рейтинги користувача
  getUserRatings: async (userId: number, type?: 'book' | 'movie'): Promise<Rating[]> => {
    const params = type ? `?type=${type}` : '';
    return apiRequest<Rating[]>(`/api/users/${userId}/ratings${params}`);
  },

  // Створити рейтинг
  createRating: async (rating: {
    title: string;
    genre: string;
    rating: number;
    type: 'book' | 'movie';
  }): Promise<Rating> => {
    return apiRequest<Rating>('/api/ratings', {
      method: 'POST',
      body: JSON.stringify(rating),
    });
  },

  // Оновити рейтинг
  updateRating: async (ratingId: number, rating: Partial<{
    title: string;
    genre: string;
    rating: number;
    type: 'book' | 'movie';
  }>): Promise<Rating> => {
    return apiRequest<Rating>(`/api/ratings/${ratingId}`, {
      method: 'PUT',
      body: JSON.stringify(rating),
    });
  },

  // Видалити рейтинг
  deleteRating: async (ratingId: number): Promise<void> => {
    return apiRequest<void>(`/api/ratings/${ratingId}`, {
      method: 'DELETE',
    });
  },
};

// API методи для користувача
export const userApi = {
  // Отримати профіль користувача
  getUserProfile: async (userId: number): Promise<User> => {
    return apiRequest<User>(`/api/users/${userId}/profile`);
  },

  // Оновити профіль користувача
  updateUserProfile: async (userId: number, data: { 
    name: string; 
    avatar?: string; 
    email?: string; 
  }): Promise<User> => {
    return apiRequest<User>(`/api/users/${userId}/profile`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Отримати всіх користувачів (для адміністратора)
  getAllUsers: async (): Promise<User[]> => {
    return apiRequest<User[]>('/api/users');
  },
};

// API методи для watchlist
export const watchlistApi = {
  // Отримати watchlist користувача
  getUserWatchlist: async (userId: number): Promise<WatchlistItem[]> => {
    return apiRequest<WatchlistItem[]>(`/api/users/${userId}/watchlist`);
  },

  // Додати елемент до watchlist
  addToWatchlist: async (userId: number, item: Omit<WatchlistItem, 'id'>): Promise<WatchlistItem> => {
    return apiRequest<WatchlistItem>(`/api/users/${userId}/watchlist`, {
      method: 'POST',
      body: JSON.stringify(item),
    });
  },

  // Видалити елемент з watchlist
  removeFromWatchlist: async (userId: number, itemId: number): Promise<void> => {
    return apiRequest<void>(`/api/users/${userId}/watchlist/${itemId}`, {
      method: 'DELETE',
    });
  },

  // Оновити елемент в watchlist
  updateWatchlistItem: async (userId: number, itemId: number, item: Partial<WatchlistItem>): Promise<WatchlistItem> => {
    return apiRequest<WatchlistItem>(`/api/users/${userId}/watchlist/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    });
  },
};

// API методи для авторизації
export const authApi = {
  // Логін
  login: async (email: string, password: string): Promise<{ user: User; token: string }> => {
    return apiRequest<{ user: User; token: string }>(
      '/api/auth/login',
      {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      }
    );
  },

  // Реєстрація
  register: async (userData: { name: string; email: string; password: string }): Promise<{ user: User; token: string }> => {
    return apiRequest<{ user: User; token: string }>(
      '/api/auth/register',
      {
      method: 'POST',
      body: JSON.stringify(userData),
      }
    );
  },

  // Вихід
  logout: async (): Promise<void> => {
    return apiRequest<void>('/api/auth/logout', {
      method: 'POST',
    });
  },

  // Оновити токен
  refreshToken: async (): Promise<{ token: string }> => {
    return apiRequest<{ token: string }>(
      '/api/auth/refresh',
      {
      method: 'POST',
      }
    );
  },
};
