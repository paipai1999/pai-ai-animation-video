import React from 'react';
import { Download, Sparkles } from 'lucide-react';
import { getMediaUrl } from '@/lib/api';

interface VideoPlayerProps {
  videoUrl: string;
  title?: string;
  styleName?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, title, styleName }) => {
  const fullVideoUrl = getMediaUrl(videoUrl);


  return (
    <div className="w-full space-y-4 p-6 rounded-2xl glow-border bg-purple-950/20">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 text-green-400">
          <Sparkles className="w-5 h-5" />
          <h3 className="font-bold text-lg text-white">Animated Remake Ready!</h3>
        </div>
        {styleName && (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-600/30 text-purple-300 border border-purple-500/30">
            {styleName}
          </span>
        )}
      </div>

      {/* Video Element */}
      <div className="w-full rounded-xl overflow-hidden border border-purple-500/30 bg-black aspect-video shadow-2xl relative">
        <video
          src={fullVideoUrl}
          controls
          autoPlay
          className="w-full h-full object-contain"
        >
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        <div className="text-xs text-purple-300/60">
          {title && <p className="font-semibold text-purple-200">Remake of: {title}</p>}
          <p>Rendered with FFmpeg & Gemini 2.5 Flash</p>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <a
            href={fullVideoUrl}
            download="animated_remake.mp4"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 flex items-center justify-center space-x-2 shadow-lg shadow-purple-500/20 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download MP4</span>
          </a>
        </div>
      </div>
    </div>
  );
};
