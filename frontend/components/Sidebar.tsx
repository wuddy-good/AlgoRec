'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FiSettings, FiLogOut } from 'react-icons/fi';
import EditProfileModal from './EditProfileModal';
import { getUser } from '@/lib/userStorage';
import { authApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { useProfile } from '@/lib/hooks/useProfile';

export default function Sidebar() {
  const router = useRouter();
  const currentUser = getUser();
  const { user, updateProfile, refreshProfile } = useProfile(currentUser.id);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);

  const handleEditProfile = () => {
    setIsEditProfileOpen(true);
  };

  const handleSaveProfile = async (name: string, avatar?: string) => {
    try {
      await updateProfile({ name, avatar });
      // Оновлюємо профіль після збереження
      refreshProfile();
      // Оновлюємо всі компоненти через router
      router.refresh();
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile');
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      toast.success('Logged out successfully');
      router.push('/');
      router.refresh();
    } catch (error) {
      console.error('Failed to logout:', error);
      toast.error('Failed to logout');
    }
  };

  return (
    <aside className="w-[231px] bg-white-pure border-r border-gray-very-light flex flex-col">
      <div className="p-4 flex flex-col items-center flex-1 w-full">
        {/* Settings Button */}
                <button
                  onClick={handleEditProfile}
                  className="w-25 mt-2 flex items-center justify-center px-3 py-2 text-sm font-normal text-text-primary bg-gray-lighter rounded-lg shadow-sm hover:bg-gray-light transition-colors mb-4"
                >
          <FiSettings className="w-5 h-5 mr-3" style={{ strokeWidth: 1.5 }} />
          Settings
        </button>

        {/* Logout Button */}
                <button 
                  onClick={handleLogout}
                  className="w-25 flex items-center justify-center px-3 py-2 text-sm font-normal text-white-pure bg-text-primary rounded-lg shadow-sm hover:bg-text-primary-dark transition-colors mt-auto"
                >
          <FiLogOut className="w-5 h-5 mr-3" style={{ strokeWidth: 1.5 }} />
          Logout
        </button>
      </div>

      {/* Edit Profile Modal */}
      <EditProfileModal
        isOpen={isEditProfileOpen}
        onClose={() => setIsEditProfileOpen(false)}
        currentName={user?.name || currentUser.name}
        onSave={handleSaveProfile}
      />
    </aside>
  );
}
