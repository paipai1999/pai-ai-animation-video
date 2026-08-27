import axios from 'axios';
import { Job, AnimationStyle, VoiceOption, GeneratorOption, LanguageOption, BgmOption } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';
export const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/api\/?$/, '')
  : '';

export const getMediaUrl = (url?: string): string => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  if (BACKEND_URL) {
    return `${BACKEND_URL}${url.startsWith('/') ? '' : '/'}${url}`;
  }
  return url.startsWith('/') ? url : `/${url}`;
};

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface StylesResponse {
  styles: AnimationStyle[];
  languages: LanguageOption[];
  voices: VoiceOption[];
  bgm_tracks: BgmOption[];
  generators: GeneratorOption[];
  aspect_ratios: { id: string; label: string }[];
}

export const fetchStylesAndOptions = async (): Promise<StylesResponse> => {
  const response = await apiClient.get<StylesResponse>('/styles/');
  return response.data;
};

export const createRemakeJob = async (data: {
  video_url: string;
  animation_style: string;
  generator_type: string;
  voice: string;
  target_language: string;
  aspect_ratio: string;
  bgm_track?: string;
  include_subtitles?: boolean;
}): Promise<Job> => {
  const response = await apiClient.post<Job>('/jobs/', data);
  return response.data;
};

export const uploadRemakeJob = async (formData: FormData): Promise<Job> => {
  const response = await apiClient.post<Job>('/jobs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const fetchJob = async (jobId: string): Promise<Job> => {
  const response = await apiClient.get<Job>(`/jobs/${jobId}`);
  return response.data;
};

export const fetchRecentJobs = async (): Promise<Job[]> => {
  const response = await apiClient.get<Job[]>('/jobs/');
  return response.data;
};

