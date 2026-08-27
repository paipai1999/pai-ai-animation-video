export type JobStatus = 
  | 'PENDING'
  | 'DOWNLOADING'
  | 'ANALYZING'
  | 'GENERATING_VOICE'
  | 'GENERATING_VISUALS'
  | 'RENDERING'
  | 'COMPLETED'
  | 'FAILED';

export interface Scene {
  id: string;
  scene_number: number;
  narration: string;
  visual_prompt: string;
  duration_seconds: number;
  image_url?: string;
  video_clip_url?: string;
  audio_url?: string;
  status: string;
}

export interface Job {
  id: string;
  video_url: string;
  animation_style: string;
  generator_type: string;
  voice: string;
  target_language: string;
  aspect_ratio: string;
  bgm_track?: string;
  include_subtitles?: number;
  is_uploaded_file?: number;
  status: JobStatus;
  progress_percentage: number;
  current_step_description: string;
  error_message?: string;
  original_title?: string;
  original_duration?: number;
  original_thumbnail?: string;
  final_video_url?: string;
  storyboard_data?: any;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  scenes: Scene[];
}

export interface AnimationStyle {
  id: string;
  name: string;
  description: string;
  prompt_template: string;
}

export interface VoiceOption {
  id: string;
  name: string;
  language: string;
}

export interface GeneratorOption {
  id: string;
  name: string;
  is_free: boolean;
}

export interface LanguageOption {
  code: string;
  name: string;
  flag: string;
  default_voice: string;
}

export interface BgmOption {
  id: string;
  name: string;
  description: string;
}


