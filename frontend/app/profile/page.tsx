'use client';

import { getUser } from '@/lib/userStorage';

export default function ProfilePage() {
  const user = getUser();

  return (
    <div className="max-w-[1220px] px-20 py-6">
      {/* Page Title */}
      <h1 
        className="text-text-primary mb-8"
        style={{ 
          fontFamily: 'Merriweather, serif',
          fontWeight: 'bold',
          fontSize: '32px'
        }}
      >
        USER PROFILE
      </h1>

      {/* Profile Card */}
      <div className="bg-white-pure border border-gray-very-light rounded-lg p-6 mb-8">
        <div className="flex items-center space-x-6">
          {/* Avatar */}
          <div className="w-24 h-24 rounded-full bg-gray-very-light flex items-center justify-center">
            <span className="text-3xl font-bold text-text-primary">
              {user.name.charAt(0).toUpperCase()}
            </span>
          </div>
          
          {/* User Info */}
          <div className="flex-1">
            <h2
              className="text-text-primary"
              style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 600, fontSize: '30px', marginBottom: '2px' }}
            >
              Welcome, {user.name}
            </h2>
            <p
              className="text-text-primary-light"
              style={{ fontFamily: 'Open Sans, sans-serif', fontWeight: 400, fontSize: '16px' }}
            >
              Manage your preferences and explore personalized recommendations.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}
