"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { FlaskConical, Github, LogIn, Sparkles } from "lucide-react";

export default function Navbar() {
  return (
    <nav className="glass sticky top-0 z-50 border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 10 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <FlaskConical className="w-8 h-8 text-accent" />
            </motion.div>
            <div>
              <span className="text-xl font-bold gradient-text">MergeLab</span>
              <span className="text-xs text-gray-400 ml-2">by intellectlabs</span>
            </div>
          </Link>

          {/* Center Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-gray-300 hover:text-white transition-colors">
              Home
            </Link>
            <Link href="/models" className="text-gray-300 hover:text-white transition-colors">
              Models
            </Link>
            <Link href="/merge" className="text-gray-300 hover:text-white transition-colors">
              Merge
            </Link>
            <Link href="/dashboard" className="text-gray-300 hover:text-white transition-colors">
              Dashboard
            </Link>
          </div>

          {/* Right Actions */}
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com/intellectlabs/mergelab"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <Github className="w-5 h-5" />
            </a>
            
            <button className="text-gray-300 hover:text-white transition-colors flex items-center space-x-1">
              <LogIn className="w-4 h-4" />
              <span className="hidden sm:inline">Login</span>
            </button>
            
            <Link
              href="/merge"
              className="gradient-btn px-4 py-2 rounded-lg font-medium flex items-center space-x-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Start Merging</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
