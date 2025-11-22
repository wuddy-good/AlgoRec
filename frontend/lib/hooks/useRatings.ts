import { useState, useEffect } from 'react';
import { Rating } from '@/types';
import { ratingsApi } from '@/lib/api';
import { ratings as mockRatings } from '@/mocks/ratings';

// Хук для роботи з рейтингами
export const useRatings = (userId: number) => {
  const [ratings, setRatings] = useState<Rating[]>([] );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRatings = async () => {
      setLoading(true);
      setError(null);

      try {
        // Перемикач між моками та API
        const USE_API = false; // Змінити на true коли бекенд готовий
        
        if (USE_API) {
          // Використовуємо API
          const apiRatings = await ratingsApi.getUserRatings(userId);
          setRatings(apiRatings);
        } else {
          // Використовуємо моки
          setRatings(mockRatings);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch ratings');
        // Fallback до моків при помилці
        setRatings(mockRatings);
      } finally {
        setLoading(false);
      }
    };

    fetchRatings();
  }, [userId]);

  return { ratings, loading, error };
};
