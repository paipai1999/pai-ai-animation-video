import time
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from backend.app.core.config import settings


class VideoAnalyzer:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def analyze_video(
        self,
        video_path: str,
        animation_style: str = "3D Pixar Animation Style",
        target_language: str = "English",
        aspect_ratio: str = "16:9",
        progress_callback = None
    ) -> List[Dict[str, Any]]:
        """
        Uploads video to Gemini Multimodal API and extracts a structured storyboard.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured in settings/environment.")

        if progress_callback:
            progress_callback(25, "Uploading video to Gemini Multimodal Vision API...")

        # 1. Upload the video file
        video_file = self.client.files.upload(file=video_path)

        # 2. Wait for video processing with timeout (Max 3 mins)
        attempts = 0
        while video_file.state.name == "PROCESSING" and attempts < 36:
            if progress_callback:
                progress_callback(30, "Gemini is indexing and processing video frames...")
            time.sleep(5)
            attempts += 1
            video_file = self.client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise RuntimeError(f"Gemini video processing failed: {getattr(video_file, 'error', 'Unknown error')}")

        if progress_callback:
            progress_callback(35, "Gemini is analyzing scenes and generating storyboard...")

        # 3. Prompt for structured storyboard extraction
        system_instruction = (
            "You are an expert AI Animation Director and Cinematographer. Your task is to analyze "
            "the provided video, extract its core narrative, scenes, key moments, characters, and actions, "
            "and convert them into a chronological animated storyboard breakdown."
        )

        prompt = f"""
        Analyze this video carefully and convert it into a highly cohesive animated remake storyboard.
        
        Target Animation Style: "{animation_style}"
        Narration Language: "{target_language}"
        Target Aspect Ratio: "{aspect_ratio}"

        CRITICAL REQUIREMENT - CHARACTER & SETTING CONSISTENCY:
        To ensure visual consistency across all scenes:
        1. Identify the primary character(s) and define an explicit Character Anchor (hair color/style, clothing colors, gender, age, distinct features).
        2. In EVERY scene's "visual_prompt", explicitly reiterate this exact character description and art style so AI image/video generators maintain identical character appearance across all scenes.

        Instructions:
        1. Break the video into 3 to 10 distinct, sequential narrative scenes (each scene between 3 to 6 seconds).
        2. For each scene, provide:
           - "scene_number": Sequential integer (1, 2, 3...).
           - "narration": A compelling, spoken dialogue or narration sentence in {target_language} summarizing or voicing the moment.
           - "visual_prompt": A rich, descriptive prompt detailing the exact subject/character features, action, camera shot (close-up, wide shot), cinematic lighting, mood, and strictly in '{animation_style}', {aspect_ratio} composition. Avoid on-screen text or logos.
           - "duration_seconds": Estimated duration in seconds (typically between 3.0 to 6.0).

        Return ONLY a valid JSON array of scene objects adhering to this schema:
        [
          {{
            "scene_number": 1,
            "narration": "Narration text in {target_language}...",
            "visual_prompt": "Cinematic scene prompt in {animation_style} with consistent character features...",
            "duration_seconds": 4.5
          }}
        ]
        """

        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        response = None
        last_err = None

        try:
            for model_name in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[video_file, prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            response_mime_type="application/json",
                            temperature=0.2
                        )
                    )
                    if response and response.text:
                        break
                except Exception as m_err:
                    last_err = m_err
                    print(f"[Analyzer Notice] Model {model_name} attempt: {m_err}. Trying fallback...")
            
            if not response or not response.text:
                raise RuntimeError(f"Gemini video analysis failed across models: {last_err}")
        finally:
            # Clean up uploaded video file from Gemini Cloud to save storage
            try:
                self.client.files.delete(name=video_file.name)
            except Exception:
                pass


        raw_text = response.text.strip()
        
        # Clean markdown fences if present
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        try:
            storyboard = json.loads(raw_text)
            if not isinstance(storyboard, list):
                if isinstance(storyboard, dict) and "scenes" in storyboard:
                    storyboard = storyboard["scenes"]
                else:
                    raise ValueError("Unexpected JSON structure from Gemini")
            return storyboard
        except Exception as e:
            # Secondary fallback: search for JSON array within text
            import re
            match = re.search(r"\[\s*\{.*\}\s*\]", raw_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            raise ValueError(f"Failed to parse Gemini storyboard JSON response: {str(e)} - Raw: {response.text}")




analyzer_service = VideoAnalyzer()
