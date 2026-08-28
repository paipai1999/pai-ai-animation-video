import os
import uuid
import math
import subprocess
from typing import List, Dict, Any, Optional
from typing import Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Set FFmpeg binary from imageio-ffmpeg automatically for Windows compatibility
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    if ffmpeg_exe and os.path.exists(ffmpeg_exe):
        os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_exe
        os.environ["FFMPEG_BINARY"] = ffmpeg_exe
except Exception as e:
    print(f"Notice: imageio-ffmpeg auto-path: {e}")

from moviepy.editor import (
    ImageClip,
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)
from moviepy.audio.AudioClip import AudioArrayClip
from backend.app.core.config import settings


class VideoRenderer:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(settings.STORAGE_DIR, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        self.ffmpeg_path = os.environ.get("IMAGEIO_FFMPEG_EXE") or os.environ.get("FFMPEG_BINARY") or "ffmpeg"


    def _create_subtitle_overlay(self, text: str, video_width: int, video_height: int, duration: float) -> Optional[ImageClip]:
        """
        Creates a modern, readable burned-in subtitle banner using Pillow (pure Python, zero ImageMagick needed).
        """
        if not text or not text.strip():
            return None

        # Create transparent RGBA image
        img = Image.new("RGBA", (video_width, video_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Smart word/character wrap for Latin and Asian/Burmese scripts
        max_chars = 38 if video_width >= 1000 else 24
        clean_str = text.strip()
        lines = []

        if " " in clean_str:
            words = clean_str.split()
            current_line = []
            for word in words:
                if len(" ".join(current_line + [word])) <= max_chars:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
        else:
            lines = [clean_str[i:i + max_chars] for i in range(0, len(clean_str), max_chars)]

        display_text = "\n".join(lines[:2])  # Max 2 lines per subtitle

        # Font setup with multi-platform candidates & Burmese Unicode font prioritization
        font = None
        font_size = max(int(video_height * 0.042), 22)

        is_myanmar = any('\u1000' <= char <= '\u109f' or '\uaa60' <= char <= '\uaa7f' for char in clean_str)

        font_candidates = [
            "arial.ttf",
            "Arial.ttf",
            "segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf"
        ]

        if is_myanmar:
            font_candidates = [
                "C:/Windows/Fonts/mmrtext.ttf",
                "C:/Windows/Fonts/mmrtextb.ttf",
                "mmrtext.ttf",
                "/usr/share/fonts/truetype/padauk/Padauk-Bold.ttf",
                "/usr/share/fonts/truetype/padauk/Padauk.ttf",
                "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf",
                "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Bold.ttf",
            ] + font_candidates

        for candidate in font_candidates:
            try:
                font = ImageFont.truetype(candidate, font_size)
                if font:
                    break
            except Exception:
                continue

        if not font:
            try:
                font = ImageFont.load_default(size=font_size)
            except Exception:
                font = ImageFont.load_default()

        # Calculate bounding box
        bbox = draw.multiline_textbbox((0, 0), display_text, font=font, align="center")
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Draw semi-transparent rounded pill at bottom
        pad_x = 24
        pad_y = 12
        pill_w = text_w + pad_x * 2
        pill_h = text_h + pad_y * 2
        pill_x0 = (video_width - pill_w) / 2
        pill_y0 = video_height - pill_h - int(video_height * 0.08)
        pill_x1 = pill_x0 + pill_w
        pill_y1 = pill_y0 + pill_h

        draw.rounded_rectangle(
            [pill_x0, pill_y0, pill_x1, pill_y1],
            radius=12,
            fill=(0, 0, 0, 180),
            outline=(255, 255, 255, 60),
            width=1
        )

        # Draw centered text
        text_x = pill_x0 + pad_x
        text_y = pill_y0 + pad_y
        draw.multiline_text((text_x, text_y), display_text, font=font, fill=(255, 255, 255, 255), align="center")

        # Convert to MoviePy ImageClip
        np_img = np.array(img)
        sub_clip = ImageClip(np_img).set_duration(duration)
        return sub_clip

    def _generate_ambient_bgm(self, duration: float, style: str = "cinematic") -> AudioArrayClip:
        """
        Generates a subtle, pleasant background harmonic drone/chime loop if no external mp3 is provided.
        """
        sample_rate = 44100
        total_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, total_samples, False)

        if style == "lofi":
            # Warm lo-fi chords (Fmaj7 / Am)
            freqs = [174.61, 220.00, 261.63, 329.63]
        elif style == "ambient":
            # Deep meditative ambient tone
            freqs = [110.00, 164.81, 220.00, 329.63]
        else:  # cinematic default
            # Cinematic orchestral drone
            freqs = [130.81, 196.00, 261.63, 392.00]

        signal = np.zeros(total_samples)
        for i, f in enumerate(freqs):
            weight = 0.4 / (i + 1)
            # Add subtle gentle LFO volume modulation
            lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.2 * t)
            signal += weight * np.sin(2 * np.pi * f * t) * lfo

        # Fade in and fade out
        fade_samples = min(int(sample_rate * 2.0), total_samples // 2)
        if fade_samples > 0:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            signal[:fade_samples] *= fade_in
            signal[-fade_samples:] *= fade_out

        # Scale volume (subtle background volume ~ 0.08)
        stereo_signal = np.vstack((signal * 0.08, signal * 0.08)).T
        return AudioArrayClip(stereo_signal, fps=sample_rate).set_duration(duration)

    def _get_best_video_codec(self) -> Tuple[str, str]:
        """
        Detects if NVIDIA NVENC hardware acceleration is supported on the system (e.g. Google Colab T4 GPU).
        Returns (codec, preset).
        """
        try:
            import torch
            if torch.cuda.is_available():
                # Check if ffmpeg binary supports h264_nvenc
                res = subprocess.run(
                    [self.ffmpeg_path, "-encoders"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if "h264_nvenc" in res.stdout:
                    return ("h264_nvenc", "fast")
        except Exception:
            pass
        return ("libx264", "medium")

    def render_final_video(
        self,
        scene_assets: List[Dict[str, Any]],
        output_filename: str = None,
        bgm_track: str = "cinematic",
        include_subtitles: bool = True,
        progress_callback = None
    ) -> str:
        """
        Composites scenes, applies Ken Burns motion, overlays subtitles, mixes BGM, and outputs MP4.
        Accelerated with NVIDIA NVENC GPU hardware encoding when available.
        """
        if not output_filename:
            output_filename = f"remake_{uuid.uuid4().hex[:10]}.mp4"

        final_output_path = os.path.join(self.output_dir, output_filename)
        clips = []
        loaded_audio_clips = []

        total_scenes = len(scene_assets)
        for idx, scene in enumerate(scene_assets):
            if progress_callback:
                pct = 75 + int((idx / max(total_scenes, 1)) * 18)
                progress_callback(pct, f"Compositing scene {idx + 1}/{total_scenes}...")

            visual_path = scene.get("visual_path")
            audio_path = scene.get("audio_path")
            narration = scene.get("narration", "")
            target_duration = float(scene.get("duration", 4.0))

            if not visual_path or not os.path.exists(visual_path):
                continue

            is_video = visual_path.lower().endswith(('.mp4', '.mov', '.webm', '.avi'))

            # Load audio
            audio_clip = None
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    loaded_audio_clips.append(audio_clip)
                    target_duration = max(audio_clip.duration + 0.3, target_duration)
                except Exception as e:
                    print(f"Warning: Audio load failed {audio_path}: {e}")

            # Visual clip
            if is_video:
                base_clip = VideoFileClip(visual_path)
                if base_clip.duration < target_duration:
                    base_clip = base_clip.fx(vfx.loop, duration=target_duration)
                else:
                    base_clip = base_clip.subclip(0, target_duration)
            else:
                base_clip = ImageClip(visual_path).set_duration(target_duration)
                try:
                    base_clip = base_clip.resize(lambda t: 1 + 0.03 * (t / target_duration))
                except Exception:
                    pass

            if audio_clip:
                base_clip = base_clip.set_audio(audio_clip)

            # Subtitle Overlay
            if include_subtitles and narration:
                try:
                    w, h = base_clip.w or 1280, base_clip.h or 720
                    sub_clip = self._create_subtitle_overlay(narration, w, h, target_duration)
                    if sub_clip:
                        scene_composite = CompositeVideoClip([base_clip, sub_clip]).set_duration(target_duration)
                        if audio_clip:
                            scene_composite = scene_composite.set_audio(audio_clip)
                        clips.append(scene_composite)
                    else:
                        clips.append(base_clip)
                except Exception as e:
                    print(f"Warning: Subtitle overlay failed: {e}")
                    clips.append(base_clip)
            else:
                clips.append(base_clip)

        if not clips:
            raise RuntimeError("No valid visual clips were generated to render.")

        if progress_callback:
            progress_callback(93, "Mixing background audio and audio ducking...")

        final_video = concatenate_videoclips(clips, method="compose")

        # Mix Background Music if requested
        if bgm_track and bgm_track.lower() != "none":
            try:
                bgm_clip = self._generate_ambient_bgm(final_video.duration, style=bgm_track.lower())
                if final_video.audio:
                    mixed_audio = CompositeAudioClip([final_video.audio, bgm_clip])
                    final_video = final_video.set_audio(mixed_audio)
                else:
                    final_video = final_video.set_audio(bgm_clip)
            except Exception as e:
                print(f"Notice: BGM mixing skipped: {e}")

        # Choose best video codec (NVIDIA NVENC GPU vs CPU libx264)
        codec, preset = self._get_best_video_codec()

        if progress_callback:
            gpu_tag = " (NVIDIA GPU Hardware NVENC)" if "nvenc" in codec else ""
            progress_callback(96, f"Encoding final high-definition MP4{gpu_tag}...")

        try:
            try:
                final_video.write_videofile(
                    final_output_path,
                    fps=24,
                    codec=codec,
                    audio_codec="aac",
                    threads=4,
                    preset=preset,
                    logger=None
                )
            except Exception as encode_err:
                # Fallback to libx264 if nvenc failed
                if codec != "libx264":
                    print(f"[Renderer] NVENC encoding fallback: {encode_err}. Retrying with libx264...")
                    final_video.write_videofile(
                        final_output_path,
                        fps=24,
                        codec="libx264",
                        audio_codec="aac",
                        threads=4,
                        preset="medium",
                        logger=None
                    )
                else:
                    raise encode_err
        finally:
            for c in clips:
                try:
                    c.close()
                except Exception:
                    pass
            for a in loaded_audio_clips:
                try:
                    a.close()
                except Exception:
                    pass
            try:
                final_video.close()
            except Exception:
                pass

        return final_output_path



renderer_service = VideoRenderer()
