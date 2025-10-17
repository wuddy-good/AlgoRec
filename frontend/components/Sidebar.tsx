'use client';

import { useState } from 'react';
import { FiSettings, FiLogOut } from 'react-icons/fi';

export default function Sidebar() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <aside className="w-[231px] bg-white-pure min-h-screen border-r border-gray-very-light">
      <div className="p-4 flex flex-col items-center h-full">
        {/* Settings Button */}
        <button
          onClick={() => setIsSettingsOpen(true)}
          className="w-25 flex items-center justify-center px-3 py-2 text-sm font-normal text-text-primary bg-gray-lighter rounded-lg shadow-sm hover:bg-gray-light transition-colors mb-4"
          style={{ fontFamily: 'Open Sans, sans-serif' }}
        >
          <FiSettings className="w-5 h-5 mr-3" style={{ strokeWidth: 1.5 }} />
          Settings
        </button>

        {/* Spacer */}
        <div className="flex-1"></div>

        {/* Logout Button */}
        <button 
          className="w-25 flex items-center justify-center px-3 py-2 text-sm font-normal text-white-pure bg-text-primary rounded-lg shadow-sm hover:bg-text-primary-dark transition-colors"
          style={{ fontFamily: 'Open Sans, sans-serif' }}
        >
          <FiLogOut className="w-5 h-5 mr-3" style={{ strokeWidth: 1.5 }} />
          Logout
        </button>
      </div>
    </aside>
  );
}
