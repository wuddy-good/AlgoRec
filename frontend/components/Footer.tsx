import { FiFacebook, FiYoutube, FiInstagram } from 'react-icons/fi';

export default function Footer() {
  return (
    <footer className="bg-white-pure text-text-primary w-full">
      <div className="max-w-none mx-auto px-20 py-16">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-12 mb-10">
          <div className="flex flex-col gap-4">
            <img
              src="/logo2.svg"
              alt="RecoReads Logo"
              className="w-auto"
              style={{ height: '106.84px' }}
            />
            <p className="text-text-primary-light text-sm max-w-sm">
              Curated book recommendations and personal lists for readers.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-10 w-full lg:w-auto">
            <div>
              <h4 className="text-base font-bold mb-5 text-text-primary font-sans">Navigation</h4>
              <ul className="space-y-3 text-sm font-sans">
                <li><a href="/" className="text-text-primary-light hover:text-brand-blue transition-colors">Home</a></li>
                <li><a href="/catalog" className="text-text-primary-light hover:text-brand-blue transition-colors">Catalog</a></li>
                <li><a href="/dashboard" className="text-text-primary-light hover:text-brand-blue transition-colors">Dashboard</a></li>
                <li><a href="/profile" className="text-text-primary-light hover:text-brand-blue transition-colors">Profile</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-base font-bold mb-5 text-text-primary font-sans">Support</h4>
              <ul className="space-y-3 text-sm font-sans">
                <li><a href="mailto:support@recoreads.com" className="text-text-primary-light hover:text-brand-blue transition-colors">support@recoreads.com</a></li>
                <li><span className="text-text-primary-light">FAQ (soon)</span></li>
              </ul>
            </div>

            <div>
              <h4 className="text-base font-bold mb-5 text-text-primary font-sans">Social Networks</h4>
              <div className="flex space-x-4">
                <a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors">
                  <FiFacebook className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
                </a>
                <a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors">
                  <FiYoutube className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
                </a>
                <a href="#" className="text-text-primary-light hover:text-brand-blue transition-colors">
                  <FiInstagram className="w-6 h-6" style={{ strokeWidth: 1.5 }} />
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-very-light mb-10" />

        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <p className="text-gray-medium text-xs font-normal font-sans">
            © 2025 RecoMind. All rights reserved.
          </p>

          <div className="text-xs text-gray-medium font-sans">
            Made for book lovers.
          </div>
        </div>
      </div>
    </footer>
  );
}
