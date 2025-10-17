import { User } from '@/types';

const USER_STORAGE_KEY = 'algoRec_user';

const defaultUser: User = {
  id: 1,
  name: "Jacob Jones",
  avatar: "/avatars/jacob.jpg",
  email: "jacob@example.com"
};

export const getUser = (): User => {
  if (typeof window === 'undefined') return defaultUser;
  
  try {
    const stored = localStorage.getItem(USER_STORAGE_KEY);
    return stored ? JSON.parse(stored) : defaultUser;
  } catch (error) {
    console.error('Error reading user from localStorage:', error);
    return defaultUser;
  }
};

export const setUser = (user: User): void => {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Error saving user to localStorage:', error);
  }
};

export const updateUser = (userData: Partial<User>): void => {
  if (typeof window === 'undefined') return;
  
  const currentUser = getUser();
  if (currentUser) {
    const updatedUser = { ...currentUser, ...userData };
    setUser(updatedUser);
  }
};

export const clearUser = (): void => {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.removeItem(USER_STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing user from localStorage:', error);
  }
};
