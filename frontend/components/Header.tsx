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
    <header className="bg-white-pure shadow-sm w-full sticky top-0 z-50">
      <div className="max-w-none mx-auto px-16 py-5">
        <div className="flex justify-between items-center gap-6">
          {/* Logo */}
          <div className="flex items-center flex-shrink-0">
            <img 
              src="/logo2.svg" 
              alt="RecoMind Logo" 
              className="h-14 w-auto"
            />
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6 flex-1 justify-center">
            {isHomePage ? (
              <>
                <Link href="/" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium transition-colors">
                  Home
                </Link>
                <Link href="/catalog" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium transition-colors">
                  Catalog
                </Link>
                <Link href="/about" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium transition-colors">
                  About Us
                </Link>
              </>
            ) : (
              <>
                <Link href="/dashboard" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium transition-colors">
                  Dashboard
                </Link>
                <Link href="/catalog" className="text-text-primary hover:text-brand-blue px-3 py-2 rounded-md text-sm font-medium transition-colors">
                  Catalog
                </Link>
                <Link href="/profile" className="text-brand-blue px-3 py-2 rounded-md text-sm font-medium transition-colors">
                  Profile
                </Link>
              </>
            )}
          </nav>

          {/* Search and Auth Buttons */}
          <div className="flex items-center space-x-4 flex-shrink-0">
            {/* Пошук - завжди видимий */}
            <div className="hidden md:block max-w-xs w-64">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search books"
                  className="w-full px-4 py-2 pl-10 pr-4 text-sm border border-gray-very-light input-pill focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all"
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <FiSearch className="h-4 w-4 text-gray-medium" style={{ strokeWidth: 1.5 }} />
                </div>
              </div>
            </div>

            {/* Auth Buttons or User Avatar */}
            {isHomePage ? (
              <div className="flex items-center space-x-3">
                <button className="btn-secondary text-sm px-5 py-2.5 rounded-lg hover:bg-gray-very-light transition-all">
                  Login
                </button>
                <button className="btn-primary text-sm px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all">
                  Register
                </button>
              </div>
            ) : (
              <div className="h-9 w-9 rounded-full overflow-hidden border-2 border-gray-very-light hover:border-brand-blue transition-colors cursor-pointer">
                <img 
                  src={getAvatarSrc()}
                  alt="User avatar"
                  width={36}
                  height={36}
                  loading="eager"
                  decoding="async"
                  onError={(e) => { (e.currentTarget as HTMLImageElement).src = '/user.svg'; }}
                  className="w-full h-full object-cover rounded-full"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
