import React from 'react';
import { Sparkles, Video, Clapperboard, Github } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-black/40 border-b border-purple-500/20 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
            <Clapperboard className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent">
              Animaker AI
            </h1>
            <p className="text-xs text-purple-300/60">Video-to-Animation Remake Studio</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-purple-950/40 border border-purple-500/30 text-xs text-purple-300">
            <Sparkles className="w-3.5 h-3.5 text-yellow-400 animate-pulse" />
            <span>Gemini 2.5 Flash + Veo & Pollinations</span>
          </div>
        </div>
      </div>
    </header>
  );
};
