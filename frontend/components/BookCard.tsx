"use client";

import Image from "next/image";
import { useState } from "react";
import { Book } from "../types/index";

interface BookCardProps {
  book: Book;
}

export const BookCard: React.FC<BookCardProps> = ({ book }) => {
  const [coverSrc, setCoverSrc] = useState(book.image_url_m);
  const [ratingIconSrc, setRatingIconSrc] = useState(
    "https://cdn-icons-png.flaticon.com/512/1828/1828884.png"
  );

  return (
    <article className="w-full max-w-[344px] h-[451px] rounded border border-gray-300 shadow-lg overflow-hidden flex flex-col">
      <Image
        src={coverSrc}
        alt={book.title}
        className="w-full h-[269px] object-cover"
        width={344}
        height={269}
        onError={() => setCoverSrc("/fallback-book.png")}
      />

      <div className="p-4 flex flex-col justify-between flex-1">
        <div>
          <h2 className="text-base font-bold text-gray-800">{book.title}</h2>
          <p className="text-sm font-semibold text-gray-600">{book.author}</p>
          <p className="text-xs text-gray-500 mt-1">
            {book.publisher}, {book.year}
          </p>
        </div>

        <div className="flex justify-between items-center mt-2">
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-200 text-blue-800 rounded-full text-[11px] font-semibold shadow">
            Rating: {book.avg_rating.toFixed(1)}
          </span>

          <div
            className="inline-flex items-center gap-1"
            role="img"
            aria-label={`Rating: ${book.avg_rating.toFixed(1)} out of 5`}
          >
            <Image
              src={ratingIconSrc}
              alt="rating icon"
              width={16}
              height={16}
              onError={() => setRatingIconSrc("/fallback-star.png")}
            />
            <span className="text-xs font-semibold text-yellow-500">
              {book.avg_rating.toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    </article>
  );
};
