import React from 'react';
import { Layers, Quote, Wand2, Clock } from 'lucide-react';
import { Scene } from '@/types';
import { getMediaUrl } from '@/lib/api';

interface StoryboardGridProps {
  scenes: Scene[];
}

export const StoryboardGrid: React.FC<StoryboardGridProps> = ({ scenes }) => {
  if (!scenes || scenes.length === 0) return null;

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center space-x-2 text-purple-200">
        <Layers className="w-5 h-5 text-purple-400" />
        <h3 className="text-lg font-bold">Gemini Storyboard Breakdown ({scenes.length} Scenes)</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scenes.map((scene) => (
          <div
            key={scene.id || scene.scene_number}
            className="rounded-xl p-4 bg-purple-950/20 border border-purple-500/20 flex flex-col justify-between space-y-3 hover:border-purple-500/40 transition-all"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-600/30 text-purple-300 border border-purple-500/30">
                  Scene #{scene.scene_number}
                </span>
                <span className="flex items-center space-x-1 text-xs text-purple-400/70">
                  <Clock className="w-3 h-3" />
                  <span>{scene.duration_seconds}s</span>
                </span>
              </div>

              {/* Narration */}
              <div className="flex items-start space-x-2 text-xs text-purple-100 bg-purple-950/40 p-2.5 rounded-lg border border-purple-900/30">
                <Quote className="w-3.5 h-3.5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <p className="italic">{scene.narration}</p>
              </div>

              {/* Visual Prompt */}
              <div className="flex items-start space-x-2 text-xs text-purple-300/80 p-2 rounded-lg">
                <Wand2 className="w-3.5 h-3.5 text-purple-400 flex-shrink-0 mt-0.5" />
                <p className="line-clamp-3">{scene.visual_prompt}</p>
              </div>
            </div>

            {/* Generated Image Thumbnail if available */}
            {scene.image_url && (
              <div className="w-full h-36 rounded-lg overflow-hidden border border-purple-500/30 bg-black">
                <img
                  src={getMediaUrl(scene.image_url)}
                  alt={`Scene ${scene.scene_number}`}
                  className="w-full h-full object-cover"
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

