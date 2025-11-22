'use client';

import { useState } from 'react';
import { authApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';
import { FiX } from 'react-icons/fi';

interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}

export default function RegisterModal({ isOpen, onClose, onSwitchToLogin }: RegisterModalProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const validateForm = (): string | null => {
    if (!email || !password || !confirmPassword) {
      return 'Please fill in all required fields';
    }

    if (password.length < 8) {
      return 'Password must be at least 8 characters';
    }

    if (password !== confirmPassword) {
      return 'Passwords do not match';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Please enter a valid email address';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      toast.error(validationError);
      return;
    }

    setLoading(true);
    try {
      await authApi.register({
        email,
        password,
        confirm_password: confirmPassword,
        location: location || undefined,
      });
      toast.success('Registration successful!');
      onClose();
      router.refresh();
      // Redirect to dashboard or profile
      router.push('/dashboard');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white-pure rounded-lg p-8 w-full max-w-md relative max-h-[90vh] overflow-y-auto">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-medium hover:text-text-primary transition-colors"
        >
          <FiX className="w-6 h-6" />
        </button>

        {/* Logo */}
        <div className="flex justify-center mb-4">
          <img 
            src="/logo2.svg" 
            alt="RecoMind Logo" 
            className="h-16 w-auto"
          />
        </div>

        {/* Heading */}
        <h2 className="text-2xl font-bold text-brand-blue mb-2 text-center uppercase tracking-wide">
          CREATE YOUR ACCOUNT
        </h2>
        
        {/* Subheading */}
        <p className="text-text-primary-light text-center mb-8">
          Join us and discover a world made just for you.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="register-email" className="block text-sm font-medium text-text-primary mb-2">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              id="register-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-very-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label htmlFor="register-password" className="block text-sm font-medium text-text-primary mb-2">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              id="register-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-very-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              placeholder="At least 8 characters"
              required
              minLength={8}
            />
            <p className="text-xs text-text-primary-light mt-1">Minimum 8 characters</p>
          </div>

          <div>
            <label htmlFor="register-confirm-password" className="block text-sm font-medium text-text-primary mb-2">
              Confirm Password <span className="text-red-500">*</span>
            </label>
            <input
              id="register-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-very-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              placeholder="Confirm your password"
              required
              minLength={8}
            />
          </div>

          <div>
            <label htmlFor="register-location" className="block text-sm font-medium text-text-primary mb-2">
              Location
            </label>
            <input
              id="register-location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-4 py-2 border border-gray-very-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              placeholder="Your location (optional)"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary text-sm px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-text-primary-light">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-brand-blue hover:text-brand-blue-dark font-medium"
            >
              Login
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

