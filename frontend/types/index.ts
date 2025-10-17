export interface User {
  id: number;
  name: string;
  avatar: string;
  email: string;
}

export interface Rating {
  id: number;
  title: string;
  genre: string;
  rating: number;
  date: string;
  type: 'book' | 'movie';
}

export interface WatchlistItem {
  id: number;
  title: string;
  genre: string;
  type: 'book' | 'movie';
  imageUrl: string;
}

export interface Book {
  id: number;
  title: string;
  author: string;
  genre: string;
  year: number;
  rating: number;
  description: string;
  imageUrl: string;
}

export interface Movie {
  id: number;
  title: string;
  director: string;
  genre: string;
  year: number;
  rating: number;
  description: string;
  imageUrl: string;
}

export type ContentType = 'book' | 'movie';
export type ContentItem = Book | Movie;
