'use client';

import { usePathname } from 'next/navigation';
import { getUser } from '@/lib/userStorage';
import { FiSearch } from 'react-icons/fi';

export default function Header() {
  const pathname = usePathname();
  const isHomePage = pathname === '/';
  const user = getUser();

  return (
    <header className="bg-white-pure shadow-sm w-full">
      <div className="max-w-none mx-auto px-16 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center">
            <img 
              src="/logo2.svg" 
              alt="RecoMind Logo" 
              className="h-16 w-auto transform -translate-y-1"
            />
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            {isHomePage ? (
              // Навігація для головної сторінки (неавторизовані користувачі)
              <>
                <a href="/" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Home
                </a>
                <a href="/books" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Books
                </a>
                <a href="/films" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Films
                </a>
                <a href="/about" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  About
                </a>
              </>
            ) : (
              // Навігація для авторизованих користувачів
              <>
                <a href="/dashboard" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </a>
                <a href="/catalog" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Catalog
                </a>
                <a href="/profile" className="text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Profile
                </a>
              </>
            )}
          </nav>

          {/* Search and Auth Buttons */}
          <div className="flex items-center space-x-4">
            <div className="max-w-lg w-96">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search all books and movies"
                  className="w-full px-4 py-2 pl-10 pr-4 text-xs border-2 border-gray-very-light input-pill focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
                />
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FiSearch className="h-5 w-5 text-gray-medium" style={{ strokeWidth: 1.5 }} />
                      </div>
              </div>
            </div>

            {/* Auth Buttons or User Avatar */}
            {isHomePage ? (
              <div className="flex items-center space-x-3">
                <button className="btn-secondary text-sm">
                  Login
                </button>
                <button className="btn-primary text-sm">
                  Register
                </button>
              </div>
            ) : (
              <div className="h-8 w-8 rounded-full bg-gray-very-light flex items-center justify-center">
                <span className="text-sm font-medium text-gray-medium">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
