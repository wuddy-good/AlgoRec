'use client';

import { useState } from 'react';
import { FiSettings, FiLogOut } from 'react-icons/fi';
import EditProfileModal from './EditProfileModal';
import { getUser } from '@/lib/userStorage';
import toast from 'react-hot-toast';
import { useProfile } from '@/lib/hooks/useProfile';

export default function Sidebar() {
  const user = getUser();
  const { updateProfile } = useProfile(user.id);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);

  const handleEditProfile = () => {
    setIsEditProfileOpen(true);
  };

  const handleSaveProfile = async (name: string, avatar?: string) => {
    try {
      await updateProfile({ name, avatar });
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile');
    }
  };

  return (
    <aside className="w-[231px] bg-white-pure min-h-screen border-r border-gray-very-light">
      <div className="p-4 flex flex-col items-center h-full">
        {/* Settings Button */}
                <button
                  onClick={handleEditProfile}
                  className="w-25 mt-2 flex items-center justify-center px-3 py-2 text-sm font-normal text-text-primary bg-gray-lighter rounded-lg shadow-sm hover:bg-gray-light transition-colors mb-4"
                >
          <FiSettings className="w-5 h-5 mr-3" style={{ strokeWidth: 1.5 }} />
          Settings
        </button>

        {/* Spacer */}
        <div className="flex-1"></div>

        {/* Logout Button */}
                <button 
                  className="w-25 flex items-center justify-center px-3 py-2 text-sm font-normal text-white-pure bg-text-primary rounded-lg shadow-sm hover:bg-text-primary-dark transition-colors"
                >
          <FiLogOut className="w-5 h-5 mr-3" style={{ strokeWidth: 1.5 }} />
          Logout
        </button>
      </div>

      {/* Edit Profile Modal */}
      <EditProfileModal
        isOpen={isEditProfileOpen}
        onClose={() => setIsEditProfileOpen(false)}
        currentName={user.name}
        onSave={handleSaveProfile}
      />
    </aside>
  );
}
