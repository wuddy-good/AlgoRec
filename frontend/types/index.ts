export interface User {
  id: number;
  name: string;
  avatar: string;
  email: string;
  location?: string;
}

export interface Rating {
  id: number;
  title: string;
  genre: string;
  rating: number;
  date: string;
}

export interface WatchlistItem {
  id: number;
  title: string;
  genre: string;
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

export type ContentType = 'book';
export type ContentItem = Book | Movie;
