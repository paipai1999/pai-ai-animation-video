from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "video_remake_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["backend.app.tasks.pipeline"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max for heavy video jobs
    worker_prefetch_multiplier=1,
)
