// lib/hooks/useWatchlist.ts
import { useState, useEffect } from 'react';
import { WatchlistItem } from '@/types';
import { watchlistApi } from '@/lib/api';
import { watchlist as mockWatchlist } from '@/mocks/watchlist';

// Хук для роботи з watchlist
export const useWatchlist = (userId: number) => {
  const [watchlistItems, setWatchlistItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWatchlist = async () => {
      setLoading(true);
      setError(null);

      try {
        // Перемикач між моками та API
        const USE_API = false; // Змінити на true коли бекенд готовий
        
        if (USE_API) {
          // Використовуємо API
          const apiWatchlist = await watchlistApi.getUserWatchlist(userId);
          setWatchlistItems(apiWatchlist);
        } else {
          // Використовуємо localStorage або моки
          const saved = localStorage.getItem('watchlist');
          const items = saved ? JSON.parse(saved) : mockWatchlist;
          setWatchlistItems(items);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch watchlist');
        // Fallback до моків при помилці
        const saved = localStorage.getItem('watchlist');
        const items = saved ? JSON.parse(saved) : mockWatchlist;
        setWatchlistItems(items);
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlist();
  }, [userId]);

  const addToWatchlist = async (item: Omit<WatchlistItem, 'id'>) => {
    setLoading(true);
    setError(null);

    try {
      const USE_API = false; // Змінити на true коли бекенд готовий
      
      if (USE_API) {
        // Використовуємо API
        const newItem = await watchlistApi.addToWatchlist(userId, item);
        setWatchlistItems(prev => [...prev, newItem]);
        return newItem;
      } else {
        // Використовуємо localStorage
        const newItem: WatchlistItem = {
          ...item,
          id: Date.now() // Простий ID генератор
        };
        
        const updatedItems = [...watchlistItems, newItem];
        setWatchlistItems(updatedItems);
        localStorage.setItem('watchlist', JSON.stringify(updatedItems));
        
        return newItem;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add to watchlist');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeFromWatchlist = async (itemId: number) => {
    setLoading(true);
    setError(null);

    try {
      const USE_API = false; // Змінити на true коли бекенд готовий
      
      if (USE_API) {
        // Використовуємо API
        await watchlistApi.removeFromWatchlist(userId, itemId);
        setWatchlistItems(prev => prev.filter(item => item.id !== itemId));
      } else {
        // Використовуємо localStorage
        const updatedItems = watchlistItems.filter(item => item.id !== itemId);
        setWatchlistItems(updatedItems);
        localStorage.setItem('watchlist', JSON.stringify(updatedItems));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove from watchlist');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateWatchlistItem = async (itemId: number, updates: Partial<WatchlistItem>) => {
    setLoading(true);
    setError(null);

    try {
      const USE_API = false; // Змінити на true коли бекенд готовий
      
      if (USE_API) {
        // Використовуємо API
        const updatedItem = await watchlistApi.updateWatchlistItem(userId, itemId, updates);
        setWatchlistItems(prev => prev.map(item => 
          item.id === itemId ? updatedItem : item
        ));
        return updatedItem;
      } else {
        // Використовуємо localStorage
        const updatedItems = watchlistItems.map(item => 
          item.id === itemId ? { ...item, ...updates } : item
        );
        setWatchlistItems(updatedItems);
        localStorage.setItem('watchlist', JSON.stringify(updatedItems));
        
        return updatedItems.find(item => item.id === itemId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update watchlist item');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { 
    watchlistItems, 
    loading, 
    error, 
    addToWatchlist, 
    removeFromWatchlist, 
    updateWatchlistItem 
  };
};
