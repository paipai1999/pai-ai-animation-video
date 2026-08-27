import React from 'react';
import { Download, Brain, Mic, Palette, Film, CheckCircle2, AlertCircle } from 'lucide-react';
import { JobStatus } from '@/types';

interface JobProgressBarProps {
  status: JobStatus;
  progress: number;
  description: string;
  errorMessage?: string;
}

export const JobProgressBar: React.FC<JobProgressBarProps> = ({
  status,
  progress,
  description,
  errorMessage,
}) => {
  const steps = [
    { key: 'DOWNLOADING', label: '1. Ingest Video', icon: Download, pct: 15 },
    { key: 'ANALYZING', label: '2. Gemini Vision', icon: Brain, pct: 35 },
    { key: 'GENERATING_VOICE', label: '3. Voiceover (TTS)', icon: Mic, pct: 50 },
    { key: 'GENERATING_VISUALS', label: '4. AI Visuals', icon: Palette, pct: 75 },
    { key: 'RENDERING', label: '5. Compositing', icon: Film, pct: 95 },
  ];

  const isFailed = status === 'FAILED';
  const isCompleted = status === 'COMPLETED';

  return (
    <div className="w-full p-6 rounded-2xl glow-border bg-purple-950/20 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {!isCompleted && !isFailed && (
            <div className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
          )}
          {isCompleted && <CheckCircle2 className="w-5 h-5 text-green-400" />}
          {isFailed && <AlertCircle className="w-5 h-5 text-red-400" />}
          <span className="font-semibold text-sm text-purple-100">{description}</span>
        </div>
        <span className="text-xl font-bold font-mono text-purple-300">{progress}%</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-3 rounded-full bg-purple-950/60 overflow-hidden p-0.5 border border-purple-500/20">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isFailed
              ? 'bg-red-500'
              : isCompleted
              ? 'bg-gradient-to-r from-green-500 to-emerald-400 shadow-md shadow-green-500/30'
              : 'bg-gradient-to-r from-purple-600 via-indigo-500 to-blue-500 shadow-md shadow-purple-500/30'
          }`}
          style={{ width: `${Math.max(progress, 5)}%` }}
        />
      </div>

      {/* Step Indicators */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2">
        {steps.map((step) => {
          const Icon = step.icon;
          const isPassed = progress >= step.pct;
          const isCurrent = status === step.key;

          return (
            <div
              key={step.key}
              className={`flex items-center space-x-2 p-2.5 rounded-lg text-xs transition-all ${
                isCurrent
                  ? 'bg-purple-600/30 border border-purple-500 text-white font-semibold'
                  : isPassed
                  ? 'bg-purple-950/40 text-purple-200 border border-purple-900/40'
                  : 'text-purple-400/40 bg-purple-950/10'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isCurrent ? 'text-yellow-300 animate-bounce' : ''}`} />
              <span className="truncate">{step.label}</span>
            </div>
          );
        })}
      </div>

      {isFailed && errorMessage && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs">
          <p className="font-semibold mb-1">Error occurred during pipeline:</p>
          <p className="font-mono">{errorMessage}</p>
        </div>
      )}
    </div>
  );
};
