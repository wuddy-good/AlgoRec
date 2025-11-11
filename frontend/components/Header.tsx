'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { getUser } from '@/lib/userStorage';
import { useProfile } from '@/lib/hooks/useProfile';
import { FiSearch } from 'react-icons/fi';

export default function Header() {
  const pathname = usePathname();
  const isHomePage = pathname === '/';
  const currentUser = getUser();
  const { user } = useProfile(currentUser.id);
  const getAvatarSrc = () => {
    const avatar = user?.avatar;
    if (typeof avatar === 'string') {
      const trimmed = avatar.trim();
      const isValid = /^(data:image|https?:\/\/|\/)/.test(trimmed);
      if (trimmed && isValid) return trimmed;
    }
    return '/user.svg';
  };

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
                <Link href="/" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Home
                </Link>
                <Link href="/books" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Books
                </Link>
                <Link href="/films" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Films
                </Link>
                <Link href="/about" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  About
                </Link>
              </>
            ) : (
              // Навігація для авторизованих користувачів
              <>
                <Link href="/dashboard" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </Link>
                <Link href="/catalog" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Catalog
                </Link>
                <Link href="/profile" className="text-brand-blue px-3 py-2 rounded-md text-sm font-medium">
                  Profile
                </Link>
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
              <div className="h-7 w-7 rounded-full overflow-hidden">
                <img 
                  src={getAvatarSrc()}
                  alt="User avatar"
                  width={28}
                  height={28}
                  loading="eager"
                  decoding="async"
                  onError={(e) => { (e.currentTarget as HTMLImageElement).src = '/user.svg'; }}
                  className="w-full h-full object-contain p-0.5 rounded-full"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
