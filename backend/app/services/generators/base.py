from abc import ABC, abstractmethod
from typing import Optional


class BaseVisualGenerator(ABC):
    @abstractmethod
    def generate_scene_visual(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration_seconds: float = 4.0,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generates a visual (image or video clip) for a storyboard scene.
        Returns the local file path to the generated asset.
        """
        pass
