import os
import uuid
import shutil
import json
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.job import Job, JobStatus
from backend.app.schemas.job import JobCreateRequest, JobResponse
from backend.app.core.celery_app import celery_app
from backend.app.tasks.pipeline import process_video_remake_pipeline

router = APIRouter(prefix="/jobs", tags=["Video Remake Jobs"])


@router.post("/", response_model=JobResponse)
async def create_remake_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a video URL to be analyzed and remade into an animation.
    """
    new_job = Job(
        video_url=request.video_url.strip(),
        animation_style=request.animation_style,
        generator_type=request.generator_type,
        voice=request.voice,
        target_language=request.target_language,
        aspect_ratio=request.aspect_ratio,
        bgm_track=request.bgm_track or "cinematic",
        include_subtitles=1 if request.include_subtitles else 0,
        is_uploaded_file=0,
        status=JobStatus.PENDING,
        progress_percentage=0,
        current_step_description="Job queued for processing"
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    try:
        process_video_remake_pipeline.delay(new_job.id)
    except Exception as e:
        print(f"[Warning] Celery dispatch failed: {e}. Executing via FastAPI BackgroundTasks fallback...")
        background_tasks.add_task(process_video_remake_pipeline, new_job.id)

    stmt = select(Job).options(selectinload(Job.scenes)).filter(Job.id == new_job.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.post("/upload", response_model=JobResponse)
async def create_upload_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    animation_style: str = Form("3D Pixar Animation Style"),
    generator_type: str = Form("pollinations"),
    voice: str = Form("en-US-ChristopherNeural"),
    target_language: str = Form("English"),
    aspect_ratio: str = Form("16:9"),
    bgm_track: str = Form("cinematic"),
    include_subtitles: bool = Form(True),
    db: AsyncSession = Depends(get_db),
):
    """
    Uploads a local video file (MP4, MOV, MKV, AVI) directly and queues remake pipeline.
    """
    # Validate extension
    filename = file.filename or "video.mp4"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".mp4", ".mov", ".mkv", ".avi", ".webm"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an MP4, MOV, MKV, or WEBM video.")

    # Save uploaded file
    upload_dir = os.path.join(settings.STORAGE_DIR, "downloads")
    os.makedirs(upload_dir, exist_ok=True)
    saved_path = os.path.join(upload_dir, f"upload_{uuid.uuid4().hex[:12]}{ext}")

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_job = Job(
        video_url=saved_path,
        original_title=filename,
        animation_style=animation_style,
        generator_type=generator_type,
        voice=voice,
        target_language=target_language,
        aspect_ratio=aspect_ratio,
        bgm_track=bgm_track or "cinematic",
        include_subtitles=1 if include_subtitles else 0,
        is_uploaded_file=1,
        status=JobStatus.PENDING,
        progress_percentage=0,
        current_step_description="Local video uploaded. Queued for remake."
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    try:
        process_video_remake_pipeline.delay(new_job.id)
    except Exception as e:
        print(f"[Warning] Celery dispatch fallback: {e}")
        background_tasks.add_task(process_video_remake_pipeline, new_job.id)

    stmt = select(Job).options(selectinload(Job.scenes)).filter(Job.id == new_job.id)
    result = await db.execute(stmt)
    return result.scalar_one()



@router.get("/", response_model=List[JobResponse])
async def list_jobs(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """
    List all recent video remake jobs.
    """
    stmt = (
        select(Job)
        .options(selectinload(Job.scenes))
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_details(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information and storyboard of a specific job.
    """
    stmt = select(Job).options(selectinload(Job.scenes)).filter(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/progress")
async def stream_job_progress(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Real-time Server-Sent Events (SSE) stream for live progress updates.
    """
    async def event_generator():
        while True:
            # Poll DB for current job status
            stmt = select(Job).filter(Job.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()

            if not job:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Job not found"})
                }
                break

            data = {
                "job_id": job.id,
                "status": job.status.value,
                "progress": job.progress_percentage,
                "step": job.current_step_description,
                "video_url": job.final_video_url,
                "error": job.error_message
            }

            yield {
                "event": "progress",
                "data": json.dumps(data)
            }

            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                break

            await asyncio.sleep(1.5)

    return EventSourceResponse(event_generator())


@router.delete("/{job_id}")
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Job).filter(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.delete(job)
    await db.commit()
    return {"status": "success", "message": f"Job {job_id} deleted"}
