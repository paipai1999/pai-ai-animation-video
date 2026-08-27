'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, History, PlayCircle, Video } from 'lucide-react';
import confetti from 'canvas-confetti';

import { VideoInputForm } from '@/components/VideoInputForm';
import { JobProgressBar } from '@/components/JobProgressBar';
import { StoryboardGrid } from '@/components/StoryboardGrid';
import { VideoPlayer } from '@/components/VideoPlayer';

import {
  fetchStylesAndOptions,
  createRemakeJob,
  fetchJob,
  fetchRecentJobs,
  StylesResponse,
  BACKEND_URL,
} from '@/lib/api';
import { Job } from '@/types';

export default function Home() {
  const [stylesData, setStylesData] = useState<StylesResponse | null>(null);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 1. Fetch initial options and recent jobs
  useEffect(() => {
    fetchStylesAndOptions()
      .then((data) => setStylesData(data))
      .catch((err) => console.error('Failed to load styles:', err));

    loadRecentJobs();
  }, []);

  const loadRecentJobs = () => {
    fetchRecentJobs()
      .then((data) => setRecentJobs(data))
      .catch((err) => console.error('Failed to load recent jobs:', err));
  };

  // 2. Real-time SSE Progress Stream Handler
  useEffect(() => {
    if (!currentJob?.id) return;
    if (currentJob.status === 'COMPLETED' || currentJob.status === 'FAILED') return;

    const sseUrl = BACKEND_URL
      ? `${BACKEND_URL}/api/jobs/${currentJob.id}/progress`
      : `/api/jobs/${currentJob.id}/progress`;

    const eventSource = new EventSource(sseUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setCurrentJob((prev) => {
          if (!prev) return prev;
          const isFinished = data.status === 'COMPLETED';

          if (isFinished && prev.status !== 'COMPLETED') {
            confetti({
              particleCount: 100,
              spread: 70,
              origin: { y: 0.6 },
            });
            loadRecentJobs();
          }

          return {
            ...prev,
            status: data.status,
            progress_percentage: data.progress,
            current_step_description: data.step,
            final_video_url: data.video_url || prev.final_video_url,
            error_message: data.error,
          };
        });

        // If completed or has scenes, poll full job data once to get scenes
        if (data.status === 'COMPLETED' || data.progress >= 40) {
          fetchJob(currentJob.id).then((fullJob) => setCurrentJob(fullJob));
        }

        if (data.status === 'COMPLETED' || data.status === 'FAILED') {
          eventSource.close();
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [currentJob?.id]);

  // 3. Handle Form Submission (URL)
  const handleUrlSubmit = async (formData: any) => {
    setIsSubmitting(true);
    try {
      const job = await createRemakeJob(formData);
      setCurrentJob(job);
      loadRecentJobs();
    } catch (err: any) {
      alert(`Submission failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 4. Handle Direct File Upload Submission
  const handleFileSubmit = async (formData: FormData) => {
    setIsSubmitting(true);
    try {
      const { uploadRemakeJob } = await import('@/lib/api');
      const job = await uploadRemakeJob(formData);
      setCurrentJob(job);
      loadRecentJobs();
    } catch (err: any) {
      alert(`File upload failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-10 pb-16">
      {/* Hero Section */}
      <div className="text-center space-y-3 pt-4">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-purple-600/10 border border-purple-500/30 text-purple-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
          <span>Multimodal Video Understanding & AI Animation Remake</span>
        </div>
        <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-purple-100 to-purple-400 bg-clip-text text-transparent">
          Turn Any Video into a Stylized Animation
        </h2>
        <p className="text-sm sm:text-base text-purple-300/70 max-w-2xl mx-auto">
          Paste any video link or upload a local file. Gemini 2.5 Flash analyzes every scene, re-narrates the story,
          and renders a breathtaking 3D, Anime, or Comic animation remake with background music & subtitles.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Form & Active Progress */}
        <div className="lg:col-span-7 space-y-6">
          <div className="p-6 rounded-2xl glow-border bg-purple-950/20">
            {stylesData ? (
              <VideoInputForm
                styles={stylesData.styles}
                languages={stylesData.languages || []}
                voices={stylesData.voices}
                bgmTracks={stylesData.bgm_tracks || []}
                generators={stylesData.generators}
                aspectRatios={stylesData.aspect_ratios}
                onSubmitUrl={handleUrlSubmit}
                onSubmitFile={handleFileSubmit}
                isLoading={isSubmitting}
              />
            ) : (
              <div className="py-12 flex flex-col items-center justify-center space-y-3 text-purple-300">
                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-xs">Loading studio options...</p>
              </div>
            )}
          </div>

          {/* Active Job Progress */}
          {currentJob && (
            <div className="space-y-6">
              <JobProgressBar
                status={currentJob.status}
                progress={currentJob.progress_percentage}
                description={currentJob.current_step_description}
                errorMessage={currentJob.error_message}
              />

              {currentJob.final_video_url && (
                <VideoPlayer
                  videoUrl={currentJob.final_video_url}
                  title={currentJob.original_title}
                  styleName={currentJob.animation_style}
                />
              )}

              {currentJob.scenes && currentJob.scenes.length > 0 && (
                <StoryboardGrid scenes={currentJob.scenes} />
              )}
            </div>
          )}
        </div>

        {/* Right Column: Recent Remakes Gallery */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center space-x-2 text-purple-200">
            <History className="w-4 h-4 text-purple-400" />
            <h3 className="text-base font-bold">Recent Remake Projects</h3>
          </div>

          <div className="space-y-3">
            {recentJobs.length === 0 ? (
              <div className="p-6 rounded-xl border border-purple-900/30 bg-purple-950/10 text-center text-xs text-purple-400/60">
                No remake projects yet. Enter a video link on the left to start!
              </div>
            ) : (
              recentJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => setCurrentJob(job)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                    currentJob?.id === job.id
                      ? 'bg-purple-600/20 border-purple-500 shadow-md shadow-purple-500/20'
                      : 'bg-purple-950/20 border-purple-900/40 hover:border-purple-500/40 hover:bg-purple-950/30'
                  }`}
                >
                  <div className="flex items-center space-x-3 overflow-hidden">
                    <div className="w-10 h-10 rounded-lg bg-purple-900/50 flex items-center justify-center flex-shrink-0 text-purple-300">
                      {job.final_video_url ? (
                        <PlayCircle className="w-5 h-5 text-green-400" />
                      ) : (
                        <Video className="w-5 h-5 text-purple-400" />
                      )}
                    </div>
                    <div className="overflow-hidden">
                      <p className="font-semibold text-xs text-purple-100 truncate">
                        {job.original_title || job.video_url}
                      </p>
                      <p className="text-[11px] text-purple-400/60 flex items-center space-x-1.5">
                        <span>{job.animation_style}</span>
                        <span>•</span>
                        <span
                          className={
                            job.status === 'COMPLETED'
                              ? 'text-green-400 font-medium'
                              : job.status === 'FAILED'
                              ? 'text-red-400 font-medium'
                              : 'text-yellow-400 font-medium'
                          }
                        >
                          {job.status}
                        </span>
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
