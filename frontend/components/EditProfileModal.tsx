'use client';

import { useState, useEffect } from 'react';
import { FiX, FiEdit3 } from 'react-icons/fi';

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentName: string;
  onSave: (name: string, avatar?: string) => void;
}

export default function EditProfileModal({ 
  isOpen, 
  onClose, 
  currentName, 
  onSave 
}: EditProfileModalProps) {
  const [name, setName] = useState(currentName);
  const [avatar, setAvatar] = useState<string>('');
  const [avatarPreview, setAvatarPreview] = useState<string>('');

  // Завантажуємо збережені дані при відкритті модалки
  useEffect(() => {
    if (isOpen && typeof window !== 'undefined') {
      const savedProfile = localStorage.getItem('userProfile');
      if (savedProfile) {
        const profileData = JSON.parse(savedProfile);
        setName(profileData.name || currentName);
        if (profileData.avatar) {
          setAvatar(profileData.avatar);
          setAvatarPreview(profileData.avatar);
        }
      }
    }
  }, [isOpen, currentName]);

  const handleAvatarChange = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setAvatar(result);
      setAvatarPreview(result);
    };
    reader.readAsDataURL(file);
  };

  const handleSave = () => {
    onSave(name, avatar);
    onClose();
  };

  const handleCancel = () => {
    setName(currentName);
    setAvatar('');
    setAvatarPreview('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white-pure rounded-xl p-8 w-full max-w-xl mx-4 border border-gray-very-light shadow-[0_4px_24px_rgba(0,0,0,0.08)]">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="font-serif text-[32px] font-bold text-brand-blue mb-2">Edit Profile</h2>
            <p className="font-sans text-text-primary-light text-base">Make changes to your profile here. Click save when you&apos;re done.</p>
          </div>
          <button
            onClick={onClose}
            className="text-text-primary-light hover:text-text-primary transition-colors"
          >
            <FiX className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
          </button>
        </div>

        {/* Form Fields */}
        <div className="space-y-6">
          {/* Name Field */}
          <div className="flex items-center gap-6">
            <label 
              className="w-32 text-text-primary font-bold font-sans text-sm tracking-wide"
            >
              NAME
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex-1 px-5 py-3 border border-gray-very-light rounded-full focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent shadow-sm font-sans text-base"
            />
          </div>

          {/* Avatar Field */}
          <div className="flex items-center gap-6">
            <label 
              className="w-32 text-text-primary font-bold font-sans text-sm tracking-wide"
            >
              AVATAR
            </label>
            <div className="flex items-center space-x-6 mt-2">
              {/* Current Avatar - Clickable */}
              <div 
                className="group w-28 h-28 rounded-full flex items-center justify-center cursor-pointer transition-opacity relative overflow-hidden shadow-[0_6px_16px_rgba(0,0,0,0.15)]"
                role="button"
                tabIndex={0}
                aria-label="Change avatar"
                onClick={() => document.getElementById('avatar-input')?.click()}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); document.getElementById('avatar-input')?.click(); } }}
              >
                {avatarPreview ? (
                  <img 
                    src={avatarPreview} 
                    alt="Avatar preview" 
                    className="w-full h-full object-cover rounded-full"
                  />
                ) : (
                  <img 
                    src="/user.svg" 
                    alt="Default avatar" 
                    className="w-full h-full object-cover rounded-full"
                  />
                )}
                {/* Darken on hover */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-60 transition-opacity z-0 pointer-events-none"></div>
              </div>
              
              {/* Hidden File Input */}
              <input
                id="avatar-input"
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleAvatarChange(file);
                  }
                }}
                className="hidden"
              />
              
              {/* File Status */}
              <div className="flex-1">
                <p className="text-text-primary-light text-sm font-sans">
                  {avatarPreview ? 'File selected' : 'No file selected'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4 mt-10">
          <button
            onClick={handleCancel}
            className="btn-secondary border border-brand-blue rounded-lg text-base hover:bg-gray-very-light focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="btn-primary text-base focus:outline-none focus:ring-2 focus:ring-brand-orange/30"
          >
            Save changes
          </button>
        </div>
      </div>
    </div>
  );
}
