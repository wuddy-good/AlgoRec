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
  isbn: string;
  title: string;
  author: string;
  year: number;
  publisher: string;
  image_url_s: string;
  image_url_m: string;
  image_url_l: string;
  avg_rating: number;
  rating_count: number;
}

export type ContentType = 'book';
export type ContentItem = Book
