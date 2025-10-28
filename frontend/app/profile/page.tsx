'use client';

import { useState, useEffect } from 'react';
import { getUser } from '@/lib/userStorage';
import { useRatings } from '@/lib/hooks/useRatings';
import { useWatchlist } from '@/lib/hooks/useWatchlist';
import { useProfile } from '@/lib/hooks/useProfile';
import { FiStar, FiBook, FiFilm, FiTrash2 } from 'react-icons/fi';
import toast from 'react-hot-toast';
import NavigationArrows from '@/components/NavigationArrows';

export default function ProfilePage() {
  const currentUser = getUser();
  const { user, refreshProfile } = useProfile(currentUser.id);
  const [activeTab, setActiveTab] = useState<'book' | 'movie'>('movie');
  const [watchlistPage, setWatchlistPage] = useState<number>(0);
  const [ratingsPage, setRatingsPage] = useState<number>(0);
  
  // Оновлюємо профіль при завантаженні сторінки
  useEffect(() => {
    refreshProfile();
  }, []); // Видаляємо refreshProfile з залежностей

  // Використовуємо хук для watchlist
  const { watchlistItems, removeFromWatchlist } = useWatchlist(currentUser.id);

  // Використовуємо хук для отримання рейтингів
  const { ratings: allRatings, loading, error } = useRatings(currentUser.id);

  // Фільтруємо рейтинги за активним табом
  const filteredRatings = allRatings.filter(rating => rating.type === activeTab);

  // Логіка для рейтингів - показуємо по 5 записів для поточного таба
  const ratingsPerPage = 5;
  const ratingsTotalPages = Math.ceil(filteredRatings.length / ratingsPerPage);
  const ratingsStartIndex = ratingsPage * ratingsPerPage;
  const displayedRatings = filteredRatings.slice(ratingsStartIndex, ratingsStartIndex + ratingsPerPage);

  // Функція видалення з watchlist (тепер з хука)
  const handleRemoveFromWatchlist = async (id: number) => {
    try {
      await removeFromWatchlist(id);
      toast.success('Item removed from watchlist');
    } catch (error) {
      console.error('Failed to remove from watchlist:', error);
      toast.error('Failed to remove from watchlist');
    }
  };

  // Логіка для Watchlist - показуємо по 6 карток
  const itemsPerPage = 6;
  const totalPages = Math.ceil(watchlistItems.length / itemsPerPage);
  const startIndex = watchlistPage * itemsPerPage;
  const displayedWatchlist = watchlistItems.slice(startIndex, startIndex + itemsPerPage);

  // Функція для відображення зірок
  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, index) => (
      <FiStar
        key={index}
        className={`w-4 h-4 ${index < rating ? 'text-rating-star fill-current' : 'text-gray-very-light'}`}
        style={{ strokeWidth: index < rating ? 0 : 1.5 }}
      />
    ));
  };

  return (
    <div className="max-w-[1320px] mx-auto px-4 py-6">
      {/* Page Title */}
      <h1 
        className="text-text-primary font-serif font-bold text-[32px] mb-[52px]"
      >
        USER PROFILE
      </h1>

      {/* Profile Card */}
      <div className="bg-white-pure border border-gray-very-light rounded-lg p-6 mb-[52px]">
        <div className="flex items-center space-x-6">
          {/* Avatar */}
          <div className="w-24 h-24 rounded-full flex items-center justify-center overflow-hidden">
            {user?.avatar ? (
              <img 
                src={user.avatar} 
                alt="User avatar" 
                width={96}
                height={96}
                loading="eager"
                decoding="async"
                onError={(e) => { (e.currentTarget as HTMLImageElement).src = '/user.svg'; }}
                className="w-full h-full object-contain p-1 rounded-full"
              />
            ) : (
              <img 
                src="/user.svg" 
                alt="Default avatar" 
                width={96}
                height={96}
                className="w-full h-full object-contain p-1 rounded-full"
              />
            )}
          </div>
          
          {/* User Info */}
          <div className="flex-1">
            <h2
              className="text-text-primary font-sans font-semibold text-[30px] mb-[2px]"
            >
              Welcome, {user?.name || currentUser.name}
            </h2>
            <p
              className="text-text-primary-light font-sans text-[16px]"
            >
              Manage your preferences and explore personalized recommendations.
            </p>
          </div>
        </div>
      </div>

      {/* Your Ratings History Section */}
      <div className="mb-[52px]">
        <div className="flex items-center justify-between mb-4">
          <h2 
            className="text-text-primary font-serif font-bold text-[24px]"
          >
            Your Ratings History
          </h2>
          
          {/* Navigation arrows */}
          <NavigationArrows
            currentPage={ratingsPage}
            totalPages={ratingsTotalPages}
            onPrevious={() => setRatingsPage(Math.max(0, ratingsPage - 1))}
            onNext={() => setRatingsPage(Math.min(ratingsTotalPages - 1, ratingsPage + 1))}
          />
        </div>

        {/* Tab Navigation */}
        <div className="flex mb-4 bg-white-pure border border-gray-very-light rounded-lg overflow-hidden">
          <button
            onClick={() => {
              setActiveTab('book');
              setRatingsPage(0); // Скидаємо сторінку при зміні таба
            }}
            className={`flex items-center justify-center gap-2 px-4 py-2 transition-colors flex-1 font-sans text-[16px] ${
              activeTab === 'book' 
                ? 'bg-gray-lighter text-text-primary' 
                : 'bg-white-pure text-text-primary'
            }`}
          >
            <FiBook className="w-5 h-5" style={{ strokeWidth: 1.5 }} />
            Books
          </button>
          <button
            onClick={() => {
              setActiveTab('movie');
              setRatingsPage(0); // Скидаємо сторінку при зміні таба
            }}
            className={`flex items-center justify-center gap-2 px-4 py-2 transition-colors flex-1 font-sans text-[16px] ${
              activeTab === 'movie' 
                ? 'bg-gray-lighter text-text-primary' 
                : 'bg-white-pure text-text-primary'
            }`}
          >
            <FiFilm className="w-5 h-5" style={{ strokeWidth: 1.5 }} />
            Films
          </button>
        </div>

        {/* Ratings Table */}
        <div className="bg-white-pure border border-gray-very-light rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-very-light">
                <th 
                  className="text-left py-3 px-6 text-text-primary-light"
                  style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '14px' }}
                >
                  Title
                </th>
                <th 
                  className="text-left py-3 px-6 text-text-primary-light"
                  style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '14px' }}
                >
                  Genre
                </th>
                <th 
                  className="text-left py-3 px-6 text-text-primary-light"
                  style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '14px' }}
                >
                  Rating
                </th>
                <th 
                  className="text-left py-3 px-6 text-text-primary-light"
                  style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '14px' }}
                >
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center">
                    <p 
                      className="text-text-primary-light"
                      style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '16px' }}
                    >
                      Loading...
                    </p>
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center">
                    <p 
                      className="text-red-500"
                      style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '16px' }}
                    >
                      Error: {error}
                    </p>
                  </td>
                </tr>
              ) : displayedRatings.length > 0 ? (
                displayedRatings.map((rating) => (
                  <tr key={rating.id} className="border-b border-gray-very-light last:border-b-0">
                    <td className="py-4 px-6">
                      <span 
                        className="text-text-primary"
                        style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '16px' }}
                      >
                        {rating.title}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <span 
                        className="inline-block bg-brand-orange text-white-pure px-3 py-1 rounded-full text-sm"
                        style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400 }}
                      >
                        {rating.genre}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-1">
                        {renderStars(rating.rating)}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span 
                        className="text-text-primary"
                        style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '16px' }}
                      >
                        {rating.date}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-8 text-center">
                    <p 
                      className="text-text-primary-light"
                      style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '16px' }}
                    >
                      No {activeTab === 'book' ? 'books' : 'films'} rated yet.
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Watchlist Section */}
      <div style={{ marginBottom: '52px' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 
            className="text-text-primary"
            style={{ 
              fontFamily: 'Merriweather, serif',
              fontWeight: 'bold',
              fontSize: '24px'
            }}
          >
            Watchlist
          </h2>
          
          {/* Navigation arrows */}
          <NavigationArrows
            currentPage={watchlistPage}
            totalPages={totalPages}
            onPrevious={() => setWatchlistPage(Math.max(0, watchlistPage - 1))}
            onNext={() => setWatchlistPage(Math.min(totalPages - 1, watchlistPage + 1))}
          />
        </div>

        {/* Watchlist Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedWatchlist.map((item) => (
            <div 
              key={item.id} 
              className="relative group bg-white-pure border border-gray-very-light rounded-lg overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Image Container */}
              <div className="relative aspect-[3/2] bg-gray-very-light">
                {/* Placeholder image */}
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-gray-medium text-sm">Image</span>
                </div>
                
                {/* Type Label - Top Right */}
                <div className="absolute top-2 right-2">
                  <span 
                    className="inline-block text-white-pure px-2 py-1 rounded-full text-xs font-medium"
                    style={{ 
                      fontFamily: 'Open Sans, sans-serif', 
                      backgroundColor: item.type === 'movie' ? '#001D4A' : '#026E89'
                    }}
                  >
                    {item.type === 'movie' ? 'Movie' : 'Book'}
                  </span>
                </div>

                {/* Delete Icon - appears on hover */}
                <button 
                  onClick={() => handleRemoveFromWatchlist(item.id)}
                  className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white-pure rounded-full p-2 shadow-md hover:bg-gray-very-light"
                >
                  <FiTrash2 className="w-4 h-4 text-text-primary" style={{ strokeWidth: 1.5 }} />
                </button>
              </div>

              {/* Content */}
              <div className="p-4">
                <h3 
                  className="text-text-primary mb-2 truncate"
                  style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 600, fontSize: '16px' }}
                >
                  {item.title}
                </h3>
                <span 
                  className="inline-block bg-brand-orange text-white-pure px-3 py-1 rounded-full text-xs"
                  style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400 }}
                >
                  {item.genre}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
