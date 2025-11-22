'use client';

import { useState } from 'react';
import { authApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';
import { FiX } from 'react-icons/fi';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToRegister: () => void;
}

export default function LoginModal({ isOpen, onClose, onSwitchToRegister }: LoginModalProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      await authApi.login(email, password);
      toast.success('Login successful!');
      onClose();
      router.refresh();
      // Redirect to dashboard or profile
      router.push('/dashboard');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white-pure rounded-lg p-8 w-full max-w-md relative">
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
          LOG IN
        </h2>
        
        {/* Subheading */}
        <p className="text-text-primary-light text-center mb-8">
          Good to see you again!
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-sm font-medium text-text-primary mb-2">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-very-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-sm font-medium text-text-primary mb-2">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-very-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary text-sm px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-text-primary-light">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToRegister}
              className="text-brand-blue hover:text-brand-blue-dark font-medium"
            >
              Register
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

