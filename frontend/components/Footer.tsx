import { FiFacebook, FiYoutube, FiInstagram } from 'react-icons/fi';

export default function Footer() {
  return (
    <footer className="bg-white-pure text-text-primary w-full">
      <div className="max-w-none mx-auto px-16 py-12">
        {/* Top Section */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-8">
          {/* Logo */}
          <div className="mb-6 lg:mb-0">
            <img 
              src="/logo2.svg" 
              alt="RecoMind Logo" 
              className="w-auto"
              style={{ height: '106.84px' }}
            />
          </div>

          {/* Navigation Links */}
          <div className="grid grid-cols-2 md:grid-cols-4 w-full lg:w-auto" style={{ gap: '62px' }}>
            {/* About */}
            <div>
              <h4 className="text-base font-bold mb-4 text-text-primary" style={{ fontFamily: 'Open Sans, sans-serif' }}>About</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>About Us</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>How It Works</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Blog</a></li>
              </ul>
            </div>

            {/* Explore */}
            <div>
              <h4 className="text-base font-bold mb-4 text-text-primary" style={{ fontFamily: 'Open Sans, sans-serif' }}>Explore</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Recommended Books</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Recommended Movies</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Top Picks</a></li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h4 className="text-base font-bold mb-4 text-text-primary" style={{ fontFamily: 'Open Sans, sans-serif' }}>Support</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Help Center</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>FAQ</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Contact Us</a></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-base font-bold mb-4 text-text-primary" style={{ fontFamily: 'Open Sans, sans-serif' }}>Legal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Privacy Policy</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Terms of Service</a></li>
                <li><a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors text-sm font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>Cookies Policy</a></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Separator Line */}
        <div className="border-t border-gray-very-light mb-8"></div>

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row justify-between items-center">
          {/* Copyright */}
          <div className="mb-4 md:mb-0">
            <p className="text-gray-medium text-xs font-normal" style={{ fontFamily: 'Open Sans, sans-serif' }}>
              © 2025 RecoReads&Movies. All rights reserved.
            </p>
          </div>

          {/* Social Media */}
          <div className="flex space-x-4">
            <a href="#" className="text-text-primary hover:text-brand-blue transition-colors">
              <FiFacebook className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
            </a>
            <a href="#" className="text-text-primary hover:text-brand-blue transition-colors">
              <FiYoutube className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
            </a>
            <a href="#" className="text-text-primary hover:text-brand-blue transition-colors">
              <FiInstagram className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
            </a>
          </div>

        </div>
      </div>
    </footer>
  );
}
