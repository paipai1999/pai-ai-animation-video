import os
import uuid
import subprocess
from typing import Optional
from backend.app.core.config import settings
from backend.app.services.renderer import renderer_service


class F5TTSService:
    """
    F5-TTS Zero-Shot Voice Cloning Service.
    Optimized for NVIDIA GPU CUDA (e.g. Google Colab T4) with model caching,
    and graceful fallback to Cloud HF Spaces & Edge-TTS.
    """
    def __init__(self, audio_dir: str = None):
        self.audio_dir = audio_dir or os.path.join(settings.STORAGE_DIR, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)
        try:
            import imageio_ffmpeg
            self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_path = os.environ.get("IMAGEIO_FFMPEG_EXE") or getattr(renderer_service, "ffmpeg_path", "ffmpeg")

        self.device = "cpu"
        self._local_f5_model = None

        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
                torch.backends.cudnn.benchmark = True
        except Exception:
            pass


    def _get_or_load_local_model(self):
        """Loads and caches F5-TTS model in GPU VRAM or CPU RAM."""
        if self._local_f5_model is None:
            try:
                from f5_tts.api import F5TTS
                print(f"[F5-TTS] Loading local F5-TTS model on device: {self.device.upper()}...")
                self._local_f5_model = F5TTS(device=self.device)
                print(f"[F5-TTS] Model loaded successfully on {self.device.upper()}.")
            except Exception as e:
                print(f"[F5-TTS] Local model load notice: {e}")
                self._local_f5_model = False
        return self._local_f5_model if self._local_f5_model is not False else None


    def extract_reference_audio(self, source_video_path: str, duration_sec: float = 7.0, start_sec: float = 3.0) -> str:
        """
        Extracts a clean, high-quality audio sample from the source video to use as voice clone reference.
        """
        ref_audio_path = os.path.join(self.audio_dir, f"ref_{uuid.uuid4().hex[:8]}.wav")
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(start_sec),
            "-t", str(duration_sec),
            "-i", source_video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "24000",
            "-ac", "1",
            ref_audio_path
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if os.path.exists(ref_audio_path) and os.path.getsize(ref_audio_path) > 1000:
                return ref_audio_path
        except Exception as e:
            print(f"[F5-TTS] Audio extraction notice: {e}")

        # Fallback: extract from start 0s
        fallback_cmd = [
            self.ffmpeg_path,
            "-y",
            "-t", str(duration_sec),
            "-i", source_video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "24000",
            "-ac", "1",
            ref_audio_path
        ]
        subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ref_audio_path

    def synthesize_with_clone(
        self,
        gen_text: str,
        ref_audio_path: str,
        ref_text: str = "",
        output_file: Optional[str] = None
    ) -> str:
        """
        Synthesizes text using F5-TTS voice clone model.
        1. Fast Local GPU CUDA Inference (Priority on Colab GPU).
        2. Free Hugging Face Spaces Gradio Client.
        3. Edge-TTS Neural Voice Fallback.
        """
        if not output_file:
            output_file = os.path.join(self.audio_dir, f"f5_clone_{uuid.uuid4()}.mp3")

        clean_text = gen_text.strip()
        if not clean_text:
            clean_text = "..."

        # 1. Try Local GPU F5-TTS if model is available / GPU installed
        local_model = self._get_or_load_local_model()
        if local_model:
            try:
                local_model.infer(
                    ref_file=ref_audio_path,
                    ref_text=ref_text,
                    gen_text=clean_text,
                    file_wave=output_file
                )
                if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                    if self.device == "cuda":
                        try:
                            import torch
                            torch.cuda.empty_cache()
                        except Exception:
                            pass
                    return output_file
            except Exception as e:
                print(f"[F5-TTS] Local GPU inference error ({e}). Trying HuggingFace fallback...")

        # 2. Try Free HuggingFace Gradio Client for F5-TTS
        try:
            from gradio_client import Client, handle_file
            client = Client("mrfakename/E2-F5-TTS")
            result = client.predict(
                ref_audio_input=handle_file(ref_audio_path),
                ref_text_input=ref_text or "",
                gen_text_input=clean_text,
                remove_silence=True,
                cross_fade_duration_slider=0.15,
                nfe_slider=32,
                speed_slider=1.0,
                api_name="/infer"
            )
            if result and os.path.exists(result):
                import shutil
                shutil.copy2(result, output_file)
                return output_file
        except Exception as e:
            print(f"[F5-TTS] HuggingFace space inference notice: {e}")

        # 3. Graceful Fallback to Edge-TTS Neural Voice if offline
        from backend.app.services.tts import tts_service
        return tts_service.synthesize_sync(
            text=clean_text,
            voice="en-US-ChristopherNeural",
            output_file=output_file
        )



f5_tts_service = F5TTSService()
