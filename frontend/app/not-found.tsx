'use client';

import Link from 'next/link';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div className="px-4 py-16 min-h-[60vh] flex items-center justify-center">
      <div className="text-center max-w-2xl mx-auto">
        {/* 404 with Robot */}
        <div className="mb-4">
          <div className="flex items-center justify-center mb-3">
            <span className="text-[6rem] font-bold text-text-primary">4</span>
            <div className="mx-3">
              <Image
                src="/404.png"
                alt="Confused Robot"
                width={180}
                height={180}
                className="animate-bounce"
              />
            </div>
            <span className="text-[6rem] font-bold text-text-primary">4</span>
          </div>
        </div>

        {/* Error Message */}
        <h1 className="text-4xl font-bold text-text-primary mb-2 font-serif">
          Page Not Found
        </h1>
        
        <p className="text-lg text-text-primary-light mb-4 font-sans">
          We&apos;re sorry, the page you requested could not be found. Please go back to the homepage.
        </p>

        {/* Back Button */}
        <Link 
          href="/dashboard"
          className="inline-block bg-brand-blue text-white-pure px-8 py-3 rounded-lg hover:bg-accent-blue-dark transition-colors font-sans font-medium text-lg shadow-sm"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}