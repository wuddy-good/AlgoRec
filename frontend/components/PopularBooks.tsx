"use client";

import { useEffect, useState, useRef } from "react";
import { BookCard } from "./BookCard";
import { Book } from "../types/index";

export const PopularBooks: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(true);

  const observerRef = useRef<HTMLDivElement | null>(null);

  const fetchMoreBooks = async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/popular_books?limit=10`);
      const data: Book[] = await res.json();

      if (data.length === 0) {
        setHasMore(false);
      } else {
        setBooks((prev) => [...prev, ...data]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMoreBooks();
  }, []);

  useEffect(() => {
    if (!observerRef.current || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          fetchMoreBooks();
        }
      },
      { rootMargin: "100px" }
    );

    observer.observe(observerRef.current);

    return () => {
      if (observerRef.current) observer.unobserve(observerRef.current);
    };
  }, [hasMore]);

  return (
    
    <section className="mt-16 px-4 sm:px-8 lg:px-16 xl:px-32 2xl:px-20 max-w-[1600px] mx-auto">
      <h2 className="text-center text-3xl font-bold mb-8">Top Popular Books</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
        {books.map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>

      <div ref={observerRef} className="h-10 flex justify-center items-center mt-4">
        {loading && <span className="text-gray-500 animate-pulse">Loading more...</span>}
        {!hasMore && <span className="text-gray-400">No more books</span>}
      </div>
    </section>
  );
};
