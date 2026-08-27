import os
import time
import uuid
from typing import Optional
from google import genai
from google.genai import types
from backend.app.services.generators.base import BaseVisualGenerator
from backend.app.core.config import settings


class GoogleVeoGenerator(BaseVisualGenerator):
    """
    Google Veo Video Generation Client via Google GenAI SDK.
    """
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(settings.STORAGE_DIR, "frames")
        os.makedirs(self.output_dir, exist_ok=True)
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.client = None

    def generate_scene_visual(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration_seconds: float = 4.0,
        output_file: Optional[str] = None
    ) -> str:
        if not self.client:
            raise ValueError("GEMINI_API_KEY is required to generate videos with Google Veo.")

        if not output_file:
            output_file = os.path.join(self.output_dir, f"{uuid.uuid4()}.mp4")

        # Call Google Veo Model with graceful fallback
        try:
            operation = self.client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    resolution="720p"
                )
            )

            # Polling (Max 2 mins)
            attempts = 0
            while not operation.done and attempts < 12:
                time.sleep(10)
                attempts += 1
                operation = self.client.operations.get(operation)

            if operation.response and operation.response.generated_videos:
                video_data = operation.response.generated_videos[0]
                if hasattr(video_data.video, "save"):
                    video_data.video.save(output_file)
                else:
                    self.client.files.download(file=video_data.video, destination=output_file)
                return output_file
        except Exception as e:
            print(f"[Veo Notice] Veo generation unavailable or failed ({e}). Falling back to visual generator...")

        # Graceful fallback to Pollinations
        from backend.app.services.generators.pollinations import PollinationsGenerator
        fallback = PollinationsGenerator(self.output_dir)
        return fallback.generate_scene_visual(prompt, aspect_ratio, duration_seconds, output_file)

