from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.models.job import JobStatus


class JobCreateRequest(BaseModel):
    video_url: str = Field(..., description="URL of the video to remake (YouTube, TikTok, direct MP4, etc.)")
    animation_style: Optional[str] = Field("3D Pixar Animation Style", description="Visual animation style")
    generator_type: Optional[str] = Field("pollinations", description="Visual generator: 'pollinations', 'veo', 'ltx'")
    voice: Optional[str] = Field("en-US-ChristopherNeural", description="Voice ID for narration (Edge-TTS)")
    target_language: Optional[str] = Field("English", description="Target translation language for narration")
    aspect_ratio: Optional[str] = Field("16:9", description="Target aspect ratio ('16:9', '9:16', '1:1')")
    bgm_track: Optional[str] = Field("cinematic", description="Background music ('cinematic', 'lofi', 'ambient', 'none')")
    include_subtitles: Optional[bool] = Field(True, description="Whether to overlay burned-in subtitles")


class SceneResponse(BaseModel):
    id: str
    scene_number: int
    narration: str
    visual_prompt: str
    duration_seconds: float
    image_url: Optional[str] = None
    video_clip_url: Optional[str] = None
    audio_url: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: str
    video_url: str
    animation_style: str
    generator_type: str
    voice: str
    target_language: str
    aspect_ratio: str
    bgm_track: Optional[str] = "cinematic"
    include_subtitles: Optional[int] = 1
    is_uploaded_file: Optional[int] = 0
    status: JobStatus
    progress_percentage: int
    current_step_description: str
    error_message: Optional[str] = None
    original_title: Optional[str] = None
    original_duration: Optional[float] = None
    original_thumbnail: Optional[str] = None
    final_video_url: Optional[str] = None
    storyboard_data: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    scenes: List[SceneResponse] = []

    class Config:
        from_attributes = True


class JobProgressEvent(BaseModel):
    job_id: str
    status: JobStatus
    progress_percentage: int
    current_step_description: str
    final_video_url: Optional[str] = None
    error_message: Optional[str] = None
