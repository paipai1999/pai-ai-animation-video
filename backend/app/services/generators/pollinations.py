import os
import time
import uuid
import urllib.parse
from typing import Optional
import requests
from backend.app.services.generators.base import BaseVisualGenerator
from backend.app.core.config import settings


class PollinationsGenerator(BaseVisualGenerator):
    """
    100% Free Instant Visual Generator using Pollinations AI
    Generates high-resolution scene visuals with zero API key required.
    Includes automated retry handling with exponential backoff.
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
            output_file = os.path.join(self.output_dir, f"{uuid.uuid4()}.png")

        # Determine dimensions from aspect ratio
        if aspect_ratio == "9:16":
            width, height = 720, 1280
        elif aspect_ratio == "1:1":
            width, height = 1024, 1024
        else:  # 16:9 default
            width, height = 1280, 720

        encoded_prompt = urllib.parse.quote(prompt)
        
        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            seed = (uuid.uuid4().int % 1000000) + attempt
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
            
            try:
                response = requests.get(url, timeout=35)
                if response.status_code == 200 and len(response.content) > 1000:
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    return output_file
                else:
                    last_error = f"Pollinations returned HTTP status {response.status_code}"
            except Exception as e:
                last_error = str(e)

            # Wait with exponential backoff before retry
            if attempt < max_retries:
                time.sleep(2 * attempt)

        raise RuntimeError(f"Pollinations visual generation failed after {max_retries} attempts: {last_error}")

