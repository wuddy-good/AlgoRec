// Базовий API service для легкого підключення бекенду

import { User, WatchlistItem, Rating } from '@/types';
import { setUser, clearUser } from '@/lib/userStorage';

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

  // 204 No Content або порожнє тіло
  if (response.status === 204) {
    return null as T;
  }

  const text = await response.text();
  
  if (!response.ok) {
    try {
      const errorData = text ? JSON.parse(text) : null;
      throw new Error(errorData?.detail || response.statusText || 'API error');
    } catch {
      throw new Error(text || `API Error: ${response.status} ${response.statusText}`);
    }
  }

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
    const response = await apiRequest<{
      access_token: string;
      token_type: string;
      user: { id: number; email: string; location: string | null };
    }>('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    const normalizedUser: User = {
      id: response.user.id,
      email: response.user.email,
      name: response.user.email.split('@')[0],
      avatar: '',
      location: response.user.location || '',
    };

    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', response.access_token);
      setUser(normalizedUser);
    }

    return {
      token: response.access_token,
      user: normalizedUser,
    };
  },

  // Реєстрація
  register: async (userData: {
    email: string;
    password: string;
    confirm_password: string;
    location: string;
  }): Promise<{ user: User; token: string }> => {
    await apiRequest('/api/register', {
      method: 'POST',
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        confirm_password: userData.confirm_password,
        location: userData.location,
      }),
    });

    return authApi.login(userData.email, userData.password);
  },

  // Вихід (поки що не реалізовано в бекенді, просто очищаємо токен)
  logout: async (): Promise<void> => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      clearUser();
    }
  },

  // Оновити токен (поки що не реалізовано в бекенді)
  refreshToken: async (): Promise<{ token: string }> => {
    throw new Error('Token refresh endpoint is not implemented in backend yet');
  },
};
