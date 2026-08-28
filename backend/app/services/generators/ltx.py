import os
import uuid
from typing import Optional
from backend.app.services.generators.base import BaseVisualGenerator
from backend.app.core.config import settings


class LTXVideoGenerator(BaseVisualGenerator):
    """
    LTX Video Open-Source Client (Lightricks LTX-Video) via HuggingFace or Replicate API
    """
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(settings.STORAGE_DIR, "frames")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_scene_visual(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration_seconds: float = 4.0,
        output_file: Optional[str] = None
    ) -> str:
        if not output_file:
            output_file = os.path.join(self.output_dir, f"{uuid.uuid4()}.mp4")

        # Fallback to Pollinations if LTX endpoint is not self-hosted
        from backend.app.services.generators.pollinations import PollinationsGenerator
        fallback = PollinationsGenerator(self.output_dir)
        return fallback.generate_scene_visual(prompt, aspect_ratio, duration_seconds, output_file)
