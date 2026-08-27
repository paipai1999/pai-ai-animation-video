import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    ANALYZING = "ANALYZING"
    GENERATING_VOICE = "GENERATING_VOICE"
    GENERATING_VISUALS = "GENERATING_VISUALS"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_url = Column(String(1024), nullable=False)
    animation_style = Column(String(255), default="3D Pixar Animation Style")
    generator_type = Column(String(50), default="pollinations")  # pollinations, veo, ltx
    voice = Column(String(100), default="en-US-ChristopherNeural")
    target_language = Column(String(50), default="English")  # English, Burmese, etc.
    aspect_ratio = Column(String(20), default="16:9")  # 16:9, 9:16, 1:1
    bgm_track = Column(String(50), default="cinematic")  # cinematic, lofi, ambient, none
    include_subtitles = Column(Integer, default=1)  # 1=yes, 0=no
    is_uploaded_file = Column(Integer, default=0)
    
    # Progress and State
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    progress_percentage = Column(Integer, default=0)
    current_step_description = Column(String(255), default="Job submitted")
    error_message = Column(Text, nullable=True)

    # Video Metadata & Outputs
    original_title = Column(String(512), nullable=True)
    original_duration = Column(Float, nullable=True)
    original_thumbnail = Column(String(1024), nullable=True)
    final_video_url = Column(String(1024), nullable=True)
    storyboard_data = Column(JSON, nullable=True)  # Raw JSON array of analyzed scenes

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    scenes = relationship("Scene", back_populates="job", cascade="all, delete-orphan", order_by="Scene.scene_number")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    narration = Column(Text, nullable=False)
    visual_prompt = Column(Text, nullable=False)
    duration_seconds = Column(Float, default=4.0)
    
    # Generated Assets
    image_url = Column(String(1024), nullable=True)
    video_clip_url = Column(String(1024), nullable=True)
    audio_url = Column(String(1024), nullable=True)
    status = Column(String(50), default="PENDING")

    job = relationship("Job", back_populates="scenes")
