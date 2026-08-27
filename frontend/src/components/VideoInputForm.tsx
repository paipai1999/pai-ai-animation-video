import React, { useState } from 'react';
import {
  Sparkles,
  Link as LinkIcon,
  Wand2,
  Volume2,
  Film,
  Ratio,
  ChevronRight,
  Zap,
  Globe,
  UploadCloud,
  Music,
  Subtitles,
  FileVideo,
  X
} from 'lucide-react';
import { AnimationStyle, VoiceOption, GeneratorOption, LanguageOption, BgmOption } from '@/types';

interface VideoInputFormProps {
  styles: AnimationStyle[];
  languages?: LanguageOption[];
  voices: VoiceOption[];
  bgmTracks?: BgmOption[];
  generators: GeneratorOption[];
  aspectRatios: { id: string; label: string }[];
  onSubmitUrl: (data: {
    video_url: string;
    animation_style: string;
    generator_type: string;
    voice: string;
    target_language: string;
    aspect_ratio: string;
    bgm_track: string;
    include_subtitles: boolean;
  }) => void;
  onSubmitFile: (formData: FormData) => void;
  isLoading: boolean;
}

const DEFAULT_LANGUAGES: LanguageOption[] = [
  { code: "Burmese", name: "မြန်မာစာ (Burmese)", flag: "🇲🇲", default_voice: "my-MM-ThihaNeural" },
  { code: "English", name: "English (အင်္ဂလိပ်)", flag: "🇺🇸", default_voice: "en-US-ChristopherNeural" },
  { code: "Japanese", name: "日本語 (Japanese)", flag: "🇯🇵", default_voice: "ja-JP-NanamiNeural" },
  { code: "Korean", name: "한국어 (Korean)", flag: "🇰🇷", default_voice: "ko-KR-SunHiNeural" },
  { code: "Thai", name: "ไทย (Thai)", flag: "🇹🇭", default_voice: "th-TH-PremwadeeNeural" },
  { code: "Chinese", name: "中文 (Chinese)", flag: "🇨🇳", default_voice: "zh-CN-XiaoxiaoNeural" },
  { code: "French", name: "Français (French)", flag: "🇫🇷", default_voice: "fr-FR-DeniseNeural" },
  { code: "German", name: "Deutsch (German)", flag: "🇩🇪", default_voice: "de-DE-KatjaNeural" },
  { code: "Spanish", name: "Español (Spanish)", flag: "🇪🇸", default_voice: "es-ES-AlvaroNeural" },
  { code: "Hindi", name: "हिन्दी (Hindi)", flag: "🇮🇳", default_voice: "hi-IN-SwaraNeural" },
  { code: "Vietnamese", name: "Tiếng Việt (Vietnamese)", flag: "🇻🇳", default_voice: "vi-VN-HoaiMyNeural" },
  { code: "Indonesian", name: "Bahasa Indonesia", flag: "🇮🇩", default_voice: "id-ID-ArdiNeural" },
  { code: "Russian", name: "Русский (Russian)", flag: "🇷🇺", default_voice: "ru-RU-SvetlanaNeural" },
];

const DEFAULT_BGM_TRACKS: BgmOption[] = [
  { id: "cinematic", name: "Cinematic Ambient (ရုပ်ရှင်ဆန်သော နောက်ခံတေး)", description: "Atmospheric, inspiring strings and harmonic drone" },
  { id: "lofi", name: "Playful Lo-Fi (သက်တောင့်သက်သာ Lo-Fi)", description: "Warm chillhop chords with relaxed beats" },
  { id: "ambient", name: "Deep Storyteller (ဇာတ်လမ်းဆန်သော အသံ)", description: "Subtle meditative emotional pads" },
  { id: "none", name: "No Background Music (အသံသီးသန့်)", description: "Voiceover narration only" },
];

export const VideoInputForm: React.FC<VideoInputFormProps> = ({
  styles,
  languages = DEFAULT_LANGUAGES,
  voices,
  bgmTracks = DEFAULT_BGM_TRACKS,
  generators,
  aspectRatios,
  onSubmitUrl,
  onSubmitFile,
  isLoading,
}) => {
  // Input Mode: 'url' or 'upload'
  const [inputMode, setInputMode] = useState<'url' | 'upload'>('url');
  
  // Inputs
  const [videoUrl, setVideoUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Settings
  const [selectedStyle, setSelectedStyle] = useState(styles[0]?.prompt_template || '3D Pixar Animation Style');
  const [targetLanguage, setTargetLanguage] = useState('Burmese');
  const [selectedVoice, setSelectedVoice] = useState('my-MM-ThihaNeural');
  const [selectedBgm, setSelectedBgm] = useState('cinematic');
  const [includeSubtitles, setIncludeSubtitles] = useState(true);
  const [selectedGenerator, setSelectedGenerator] = useState(generators[0]?.id || 'pollinations');
  const [aspectRatio, setAspectRatio] = useState('16:9');

  const langList = languages.length > 0 ? languages : DEFAULT_LANGUAGES;
  const bgmList = bgmTracks.length > 0 ? bgmTracks : DEFAULT_BGM_TRACKS;

  // Filter voices based on selected target language (always include F5-TTS Voice Clone)
  const availableVoices = voices.filter(
    (v) => v.id === 'f5-tts-clone' || v.language.toLowerCase() === targetLanguage.toLowerCase()
  );
  const displayVoices = availableVoices.length > 0 ? availableVoices : voices;

  const handleLanguageChange = (langCode: string) => {
    setTargetLanguage(langCode);
    const langObj = langList.find((l) => l.code === langCode);
    if (langObj?.default_voice) {
      setSelectedVoice(langObj.default_voice);
    } else {
      const match = voices.find((v) => v.language.toLowerCase() === langCode.toLowerCase());
      if (match) {
        setSelectedVoice(match.id);
      }
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('video/') || file.name.match(/\.(mp4|mov|mkv|webm|avi)$/i)) {
        setSelectedFile(file);
      } else {
        alert('Please drop a valid video file (MP4, MOV, MKV, WEBM).');
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMode === 'url') {
      if (!videoUrl.trim()) return;
      onSubmitUrl({
        video_url: videoUrl.trim(),
        animation_style: selectedStyle,
        generator_type: selectedGenerator,
        voice: selectedVoice,
        target_language: targetLanguage,
        aspect_ratio: aspectRatio,
        bgm_track: selectedBgm,
        include_subtitles: includeSubtitles,
      });
    } else {
      if (!selectedFile) return;
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('animation_style', selectedStyle);
      formData.append('generator_type', selectedGenerator);
      formData.append('voice', selectedVoice);
      formData.append('target_language', targetLanguage);
      formData.append('aspect_ratio', aspectRatio);
      formData.append('bgm_track', selectedBgm);
      formData.append('include_subtitles', String(includeSubtitles));
      onSubmitFile(formData);
    }
  };

  const isSubmitDisabled =
    isLoading || (inputMode === 'url' ? !videoUrl.trim() : !selectedFile);

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-6">
      {/* 1. Input Mode Tabs */}
      <div className="flex items-center p-1 rounded-xl bg-purple-950/40 border border-purple-500/20 max-w-md mx-auto">
        <button
          type="button"
          onClick={() => setInputMode('url')}
          className={`flex-1 py-2 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-2 ${
            inputMode === 'url'
              ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
              : 'text-purple-300/70 hover:text-white'
          }`}
        >
          <LinkIcon className="w-3.5 h-3.5" />
          <span>Paste Video Link</span>
        </button>
        <button
          type="button"
          onClick={() => setInputMode('upload')}
          className={`flex-1 py-2 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-2 ${
            inputMode === 'upload'
              ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
              : 'text-purple-300/70 hover:text-white'
          }`}
        >
          <UploadCloud className="w-3.5 h-3.5" />
          <span>Upload Local File</span>
        </button>
      </div>

      {/* 2. Video Source Input Area */}
      {inputMode === 'url' ? (
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-purple-200 flex items-center space-x-2">
            <Film className="w-4 h-4 text-purple-400" />
            <span>Source Video Link (YouTube, Shorts, TikTok, Direct MP4)</span>
          </label>
          <div className="relative">
            <input
              type="url"
              required={inputMode === 'url'}
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=... or https://youtube.com/shorts/..."
              className="w-full px-4 py-3.5 pl-11 rounded-xl bg-purple-950/20 border border-purple-500/30 text-white placeholder-purple-400/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
            <LinkIcon className="w-5 h-5 absolute left-3.5 top-3.5 text-purple-400/60" />
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-purple-200 flex items-center space-x-2">
            <UploadCloud className="w-4 h-4 text-purple-400" />
            <span>Upload Local Video (MP4, MOV, MKV, WEBM)</span>
          </label>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleFileDrop}
            className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer ${
              isDragging
                ? 'border-purple-400 bg-purple-600/20'
                : 'border-purple-500/30 bg-purple-950/10 hover:border-purple-500/50 hover:bg-purple-950/20'
            }`}
            onClick={() => document.getElementById('file-upload-input')?.click()}
          >
            <input
              id="file-upload-input"
              type="file"
              accept="video/*,.mp4,.mov,.mkv,.webm,.avi"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setSelectedFile(e.target.files[0]);
                }
              }}
            />
            {selectedFile ? (
              <div className="flex items-center justify-between p-3 rounded-xl bg-purple-900/40 border border-purple-500/40 text-left">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <FileVideo className="w-8 h-8 text-purple-400 flex-shrink-0" />
                  <div className="truncate">
                    <p className="font-semibold text-xs text-white truncate">{selectedFile.name}</p>
                    <p className="text-[11px] text-purple-300/60">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                  className="p-1 rounded-lg hover:bg-purple-800/40 text-purple-300"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="space-y-2 py-4">
                <UploadCloud className="w-10 h-10 text-purple-400 mx-auto animate-pulse" />
                <p className="text-xs font-semibold text-purple-200">
                  Drag & Drop your video file here, or <span className="text-purple-400 underline">Browse</span>
                </p>
                <p className="text-[11px] text-purple-400/50">Supports MP4, MOV, MKV, WEBM up to 200MB</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 3. Animation Style Grid */}
      <div className="space-y-3">
        <label className="block text-sm font-semibold text-purple-200 flex items-center space-x-2">
          <Wand2 className="w-4 h-4 text-purple-400" />
          <span>Choose Animation Aesthetic</span>
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {styles.map((style) => {
            const isSelected = selectedStyle === style.prompt_template;
            return (
              <div
                key={style.id}
                onClick={() => setSelectedStyle(style.prompt_template)}
                className={`cursor-pointer p-3.5 rounded-xl border transition-all ${
                  isSelected
                    ? 'bg-purple-600/20 border-purple-500 shadow-md shadow-purple-500/20 ring-1 ring-purple-500'
                    : 'bg-purple-950/10 border-purple-900/40 hover:border-purple-500/40 hover:bg-purple-950/20'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-sm text-purple-100">{style.name}</h4>
                  {isSelected && <Sparkles className="w-4 h-4 text-yellow-400" />}
                </div>
                <p className="text-xs text-purple-300/60 line-clamp-2">{style.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. Output Language & Voice Configuration */}
      <div className="p-4 rounded-xl bg-purple-950/30 border border-purple-500/30 space-y-4">
        <div className="flex items-center justify-between border-b border-purple-900/40 pb-2">
          <h4 className="text-xs font-bold text-purple-200 uppercase tracking-wider flex items-center space-x-2">
            <Globe className="w-4 h-4 text-purple-400" />
            <span>Output Audio & Narration Language (အသံထွက် ဘာသာစကား)</span>
          </h4>
          <span className="text-[11px] text-purple-300/60">Gemini AI Auto-Translation</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Target Language Selector */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-purple-200 flex items-center space-x-1.5">
              <Globe className="w-3.5 h-3.5 text-purple-400" />
              <span>Audio Language</span>
            </label>
            <select
              value={targetLanguage}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="w-full px-3 py-2.5 rounded-lg bg-purple-900/40 border border-purple-500/40 text-xs text-purple-100 font-medium focus:outline-none focus:ring-1 focus:ring-purple-400"
            >
              {langList.map((lang) => (
                <option key={lang.code} value={lang.code} className="bg-gray-900 text-white">
                  {lang.flag} {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* Voice Character Model */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-purple-200 flex items-center space-x-1.5">
              <Volume2 className="w-3.5 h-3.5 text-purple-400" />
              <span>Voice Actor Model</span>
            </label>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              className="w-full px-3 py-2.5 rounded-lg bg-purple-900/40 border border-purple-500/40 text-xs text-purple-100 font-medium focus:outline-none focus:ring-1 focus:ring-purple-400"
            >
              {displayVoices.map((v) => (
                <option key={v.id} value={v.id} className="bg-gray-900 text-white">
                  {v.name} ({v.language})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 5. Music, Subtitles, Engine & Aspect Ratio */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
        {/* Background Music */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-purple-200 flex items-center space-x-1.5">
            <Music className="w-3.5 h-3.5 text-purple-400" />
            <span>Background Music (BGM)</span>
          </label>
          <select
            value={selectedBgm}
            onChange={(e) => setSelectedBgm(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg bg-purple-950/30 border border-purple-500/30 text-xs text-purple-100 focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            {bgmList.map((bgm) => (
              <option key={bgm.id} value={bgm.id} className="bg-gray-900 text-white">
                {bgm.name}
              </option>
            ))}
          </select>
        </div>

        {/* Burned-in Subtitles Toggle */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-purple-200 flex items-center space-x-1.5">
            <Subtitles className="w-3.5 h-3.5 text-purple-400" />
            <span>Burned-in Subtitles</span>
          </label>
          <div className="flex items-center space-x-2 pt-1">
            <button
              type="button"
              onClick={() => setIncludeSubtitles(!includeSubtitles)}
              className={`w-full py-2 px-3 rounded-lg text-xs font-semibold border transition-all flex items-center justify-center space-x-2 ${
                includeSubtitles
                  ? 'bg-purple-600/30 border-purple-500 text-white'
                  : 'bg-purple-950/20 border-purple-900/40 text-purple-400/50'
              }`}
            >
              <span>{includeSubtitles ? '✓ On (စာတန်းထိုးမည်)' : '✕ Off (စာတန်းမထိုးပါ)'}</span>
            </button>
          </div>
        </div>

        {/* Generator Tier */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-purple-200 flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5 text-purple-400" />
            <span>AI Visual Engine</span>
          </label>
          <select
            value={selectedGenerator}
            onChange={(e) => setSelectedGenerator(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg bg-purple-950/30 border border-purple-500/30 text-xs text-purple-100 focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            {generators.map((g) => (
              <option key={g.id} value={g.id} className="bg-gray-900 text-white">
                {g.name}
              </option>
            ))}
          </select>
        </div>

        {/* Aspect Ratio */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-purple-200 flex items-center space-x-1.5">
            <Ratio className="w-3.5 h-3.5 text-purple-400" />
            <span>Aspect Ratio</span>
          </label>
          <select
            value={aspectRatio}
            onChange={(e) => setAspectRatio(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg bg-purple-950/30 border border-purple-500/30 text-xs text-purple-100 focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            {aspectRatios.map((r) => (
              <option key={r.id} value={r.id} className="bg-gray-900 text-white">
                {r.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 6. Submit Button */}
      <button
        type="submit"
        disabled={isSubmitDisabled}
        className="w-full py-4 px-6 rounded-xl font-semibold text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 shadow-lg shadow-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-all transform active:scale-[0.99]"
      >
        {isLoading ? (
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Processing Video Remake...</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-yellow-300" />
            <span>
              {inputMode === 'upload' ? 'Upload & Generate Remake' : 'Generate Animated Remake'}
            </span>
            <ChevronRight className="w-5 h-5" />
          </div>
        )}
      </button>
    </form>
  );
};
