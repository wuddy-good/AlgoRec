// lib/hooks/useProfile.ts
import { useState, useEffect, useCallback } from 'react';
import { User } from '@/types';
import { userApi } from '@/lib/api';
import { getUser, setUser as saveUserToStorage } from '@/lib/userStorage';

// Хук для роботи з профілем користувача
export const useProfile = (userId: number) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setError(null);

      try {
        // Перемикач між localStorage та API
        const USE_API = false; // Змінити на true коли бекенд готовий
        
        if (USE_API) {
          // Використовуємо API
          const apiUser = await userApi.getUserProfile(userId);
          setUser(apiUser);
        } else {
          // Використовуємо localStorage
          const localUser = getUser();
          
          // Перевіряємо чи є збережені дані профілю
          const savedProfile = localStorage.getItem('userProfile');
          if (savedProfile) {
            const profileData = JSON.parse(savedProfile);
            const updatedUser = {
              ...localUser,
              // Використовуємо name з profileData тільки якщо воно не порожнє
              name: profileData.name || (localUser.name || ''),
              avatar: profileData.avatar || localUser.avatar
            };
            setUser(updatedUser);
          } else {
            setUser(localUser);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch profile');
        // Fallback до localStorage при помилці
        const localUser = getUser();
        setUser(localUser);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
    
    // Слухаємо зміни в localStorage та кастомні події (для синхронізації між компонентами)
    const handleStorageChange = () => {
      fetchProfile();
    };
    
    const handleProfileUpdate = (event: Event) => {
      // Якщо є дані в event, використовуємо їх, інакше завантажуємо з localStorage
      const customEvent = event as CustomEvent<User>;
      if (customEvent.detail) {
        setUser(customEvent.detail);
      } else {
        fetchProfile();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('userProfileUpdated', handleProfileUpdate);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('userProfileUpdated', handleProfileUpdate);
    };
  }, [userId]);

  const updateProfile = async (data: { name: string; avatar?: string; email?: string }) => {
    setLoading(true);
    setError(null);

    try {
      const USE_API = false; // Змінити на true коли бекенд готовий
      
      if (USE_API) {
        // Використовуємо API
        const updatedUser = await userApi.updateUserProfile(userId, data);
        setUser(updatedUser);
        return updatedUser;
      } else {
        // Використовуємо localStorage
        const currentUser = getUser();
        const updatedUser = { ...currentUser, ...data };
        
        // Зберігаємо в localStorage через правильну функцію (використовує ключ 'algoRec_user')
        saveUserToStorage(updatedUser);
        localStorage.setItem('userProfile', JSON.stringify({
          ...data,
          updatedAt: new Date().toISOString()
        }));
        
        // Оновлюємо React state
        setUser(updatedUser);
        
        // Викликаємо кастомний event для синхронізації між компонентами
        // Використовуємо setTimeout щоб переконатися що localStorage оновлено
        if (typeof window !== 'undefined') {
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('userProfileUpdated', { detail: updatedUser }));
          }, 0);
        }
        
        return updatedUser;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Функція для примусового оновлення профілю
  const refreshProfile = useCallback(() => {
    const localUser = getUser();
    const savedProfile = localStorage.getItem('userProfile');
    
    if (savedProfile) {
      const profileData = JSON.parse(savedProfile);
      const updatedUser = {
        ...localUser,
        // Використовуємо name з profileData тільки якщо воно не порожнє
        name: profileData.name || (localUser.name || ''),
        avatar: profileData.avatar || localUser.avatar
      };
      setUser(updatedUser);
    } else {
      setUser(localUser);
    }
  }, []);

  return { user, loading, error, updateProfile, refreshProfile };
};
