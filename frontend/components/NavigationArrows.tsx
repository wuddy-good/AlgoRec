'use client';

interface NavigationArrowsProps {
  currentPage: number;
  totalPages: number;
  onPrevious: () => void;
  onNext: () => void;
  className?: string;
}

export default function NavigationArrows({
  currentPage,
  totalPages,
  onPrevious,
  onNext,
  className = ''
}: NavigationArrowsProps) {
  if (totalPages <= 1) return null;

  return (
    <div className={`flex items-center gap-0 ${className}`}>
      <button
        onClick={onPrevious}
        disabled={currentPage === 0}
        className={`px-2 py-2 text-lg transition-colors ${
          currentPage === 0 
            ? 'text-gray-medium cursor-not-allowed' 
            : 'text-text-primary hover:text-text-primary-dark'
        }`}
        title="Previous page"
      >
        ↑
      </button>
      <button
        onClick={onNext}
        disabled={currentPage === totalPages - 1}
        className={`px-2 py-2 text-lg transition-colors ${
          currentPage === totalPages - 1 
            ? 'text-gray-medium cursor-not-allowed' 
            : 'text-gray-medium hover:text-gray-medium-dark'
        }`}
        title="Next page"
      >
        ↓
      </button>
    </div>
  );
}
