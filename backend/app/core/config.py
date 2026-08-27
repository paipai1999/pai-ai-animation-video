import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DEFAULT_DB_PATH = os.path.join(DEFAULT_STORAGE_DIR, "app.db").replace("\\", "/")



class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Video Animation Remake Engine"
    API_V1_STR: str = "/api"
    
    # Google AI Studio / Gemini API
    GEMINI_API_KEY: str = ""
    
    # Celery & Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Database (Uses absolute normalized path)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}"
    
    # Cloudflare R2 / AWS S3 Storage (Optional, falls back to local storage)
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None
    R2_PUBLIC_DOMAIN: Optional[str] = None
    
    # Storage Directory for Local processing
    STORAGE_DIR: str = DEFAULT_STORAGE_DIR
    
    # Default Video Quality / Model Settings
    DEFAULT_GENERATOR: str = "pollinations"  # options: 'pollinations', 'veo', 'ltx'
    DEFAULT_ANIMATION_STYLE: str = "3D Pixar Animation Style"
    DEFAULT_VOICE: str = "en-US-ChristopherNeural"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "downloads"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "frames"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "audio"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "outputs"), exist_ok=True)
