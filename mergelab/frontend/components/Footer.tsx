import { Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          {/* Left - Branding */}
          <div className="text-center md:text-left">
            <p className="text-gray-400 text-sm">
              Built with <Heart className="w-4 h-4 inline text-red-500" /> by{" "}
              <span className="gradient-text font-semibold">Kepler</span> and the intellectlabs team
            </p>
            <p className="text-gray-500 text-xs mt-1">
              © 2026 intellectlabs. All rights reserved.
            </p>
          </div>

          {/* Right - Links */}
          <div className="flex items-center space-x-6">
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              Privacy
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              Terms
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              API
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
