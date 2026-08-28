import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.core.celery_app import celery_app
from backend.app.models.job import Job, Scene, JobStatus
from backend.app.services.downloader import downloader_service
from backend.app.services.analyzer import analyzer_service
from backend.app.services.tts import tts_service
from backend.app.services.f5_tts import f5_tts_service
from backend.app.services.generators import get_generator
from backend.app.services.renderer import renderer_service
from backend.app.services.storage import storage_service

from backend.app.core.database import Base

# Synchronous DB session for Celery workers
sync_db_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
connect_args = {"check_same_thread": False, "timeout": 30} if "sqlite" in sync_db_url else {}
sync_engine = create_engine(sync_db_url, connect_args=connect_args)
Base.metadata.create_all(sync_engine)
SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)


def update_job_progress(job_id: str, status: JobStatus, progress: int, description: str, error: str = None, video_url: str = None):
    with SyncSessionLocal() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            job.progress_percentage = progress
            job.current_step_description = description
            if error:
                job.error_message = error
            if video_url:
                job.final_video_url = video_url
                job.completed_at = datetime.utcnow()
            db.commit()


@celery_app.task(name="backend.app.tasks.pipeline.process_video_remake_pipeline")
def process_video_remake_pipeline(job_id: str):
    """
    Background worker orchestrating the complete video remake workflow.
    """
    print(f"[Worker] Starting video remake pipeline for Job: {job_id}")

    # Fetch job params
    with SyncSessionLocal() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"[Worker Error] Job {job_id} not found.")
            return False
        
        video_url = job.video_url
        animation_style = job.animation_style
        generator_type = job.generator_type
        voice = job.voice
        target_language = job.target_language
        aspect_ratio = job.aspect_ratio
        bgm_track = getattr(job, "bgm_track", "cinematic") or "cinematic"
        include_subtitles = bool(getattr(job, "include_subtitles", 1))
        is_uploaded_file = bool(getattr(job, "is_uploaded_file", 0))

    try:
        # -------------------------------------------------------------
        # Step 1: Video Ingestion / Local File Check (0% -> 20%)
        # -------------------------------------------------------------
        if is_uploaded_file and os.path.exists(video_url):
            update_job_progress(job_id, JobStatus.DOWNLOADING, 10, "Processing uploaded local video file...")
            source_video_path = video_url
            video_dur = 0.0
            try:
                from moviepy.editor import VideoFileClip
                with VideoFileClip(source_video_path) as clip:
                    video_dur = float(clip.duration or 0.0)
            except Exception:
                pass
            metadata = {
                "title": os.path.basename(video_url),
                "duration": video_dur,
                "thumbnail": ""
            }
        else:
            update_job_progress(job_id, JobStatus.DOWNLOADING, 10, "Downloading source video via yt-dlp...")
            source_video_path, metadata = downloader_service.extract_info_and_download(video_url)
        
        with SyncSessionLocal() as db:
            j = db.query(Job).filter(Job.id == job_id).first()
            if j:
                j.original_title = metadata.get("title")
                j.original_duration = metadata.get("duration")
                j.original_thumbnail = metadata.get("thumbnail")
                db.commit()

        update_job_progress(job_id, JobStatus.ANALYZING, 20, "Video ready. Preparing Gemini multimodal analysis...")

        # -------------------------------------------------------------
        # Step 2: Gemini Multimodal Vision Analysis (20% -> 40%)
        # -------------------------------------------------------------
        def progress_cb(pct, desc):
            update_job_progress(job_id, JobStatus.ANALYZING, pct, desc)

        storyboard_data = analyzer_service.analyze_video(
            video_path=source_video_path,
            animation_style=animation_style,
            target_language=target_language,
            aspect_ratio=aspect_ratio,
            progress_callback=progress_cb
        )

        # Save storyboard & scenes to DB
        with SyncSessionLocal() as db:
            j = db.query(Job).filter(Job.id == job_id).first()
            if j:
                j.storyboard_data = storyboard_data
                # Create Scene records
                for item in storyboard_data:
                    sc = Scene(
                        job_id=job_id,
                        scene_number=item.get("scene_number", 1),
                        narration=item.get("narration", ""),
                        visual_prompt=item.get("visual_prompt", ""),
                        duration_seconds=float(item.get("duration_seconds", 4.0))
                    )
                    db.add(sc)
                db.commit()

        # -------------------------------------------------------------
        # Step 3: Voice Synthesis (Edge-TTS or F5-TTS Voice Clone) (40% -> 55%)
        # -------------------------------------------------------------
        is_voice_clone = (voice == "f5-tts-clone")
        ref_audio_path = None

        if is_voice_clone:
            update_job_progress(job_id, JobStatus.GENERATING_VOICE, 40, "Extracting original speaker audio & cloning voice with F5-TTS...")
            try:
                ref_audio_path = f5_tts_service.extract_reference_audio(source_video_path)
            except Exception as e:
                print(f"[Pipeline] Ref audio extraction notice: {e}")
        else:
            update_job_progress(job_id, JobStatus.GENERATING_VOICE, 40, "Synthesizing narration voices with Edge-TTS...")

        scene_assets = []
        total_scenes = len(storyboard_data)

        for idx, scene in enumerate(storyboard_data):
            scene_no = scene.get("scene_number", idx + 1)
            narration = scene.get("narration", "")
            duration = float(scene.get("duration_seconds", 4.0))
            
            # Synthesize voice safely
            if is_voice_clone and ref_audio_path and os.path.exists(ref_audio_path):
                audio_path = f5_tts_service.synthesize_with_clone(
                    gen_text=narration,
                    ref_audio_path=ref_audio_path
                )
            else:
                audio_path = tts_service.synthesize_sync(text=narration, voice=voice)

            scene_assets.append({
                "scene_number": scene_no,
                "narration": narration,
                "visual_prompt": scene.get("visual_prompt", ""),
                "duration": duration,
                "audio_path": audio_path,
                "visual_path": None
            })

        update_job_progress(job_id, JobStatus.GENERATING_VISUALS, 55, f"Generating {total_scenes} visual scenes via {generator_type}...")

        # -------------------------------------------------------------
        # Step 4: Visual Generation (55% -> 75%)
        # -------------------------------------------------------------
        visual_generator = get_generator(generator_type)

        for idx, item in enumerate(scene_assets):
            progress_pct = 55 + int((idx / max(total_scenes, 1)) * 20)
            update_job_progress(
                job_id,
                JobStatus.GENERATING_VISUALS,
                progress_pct,
                f"Generating scene visual {idx + 1}/{total_scenes}..."
            )

            visual_path = visual_generator.generate_scene_visual(
                prompt=item["visual_prompt"],
                aspect_ratio=aspect_ratio,
                duration_seconds=item["duration"]
            )
            item["visual_path"] = visual_path

            # Save scene asset to public storage path
            ext = os.path.splitext(visual_path)[1] or ".png"
            public_scene_url = storage_service.save_file(visual_path, f"frames/{job_id}_scene_{item['scene_number']}{ext}")

            # Update Scene record with image/video URL
            with SyncSessionLocal() as db:
                sc = db.query(Scene).filter(Scene.job_id == job_id, Scene.scene_number == item["scene_number"]).first()
                if sc:
                    sc.image_url = public_scene_url
                    sc.status = "COMPLETED"
                    db.commit()

        # -------------------------------------------------------------
        # Step 5: Compositing & Video Rendering (75% -> 95%)
        # -------------------------------------------------------------
        update_job_progress(job_id, JobStatus.RENDERING, 75, "Compositing video and audio with MoviePy/FFmpeg...")

        def render_cb(pct, desc):
            update_job_progress(job_id, JobStatus.RENDERING, pct, desc)

        final_mp4_path = renderer_service.render_final_video(
            scene_assets=scene_assets,
            output_filename=f"job_{job_id}.mp4",
            bgm_track=bgm_track,
            include_subtitles=include_subtitles,
            progress_callback=render_cb
        )

        # -------------------------------------------------------------
        # Step 6: Save & Upload to Cloudflare R2 / Storage (95% -> 100%)
        # -------------------------------------------------------------
        update_job_progress(job_id, JobStatus.RENDERING, 95, "Uploading finished video to storage...")
        public_url = storage_service.save_file(final_mp4_path, f"videos/{job_id}.mp4")

        update_job_progress(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            description="Animated remake completed successfully!",
            video_url=public_url
        )

        print(f"[Worker] Pipeline completed successfully for Job {job_id} -> {public_url}")
        return True

    except Exception as e:
        import traceback
        err_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[Worker Pipeline Error]: {err_msg}")
        update_job_progress(
            job_id=job_id,
            status=JobStatus.FAILED,
            progress=0,
            description="Processing failed",
            error=str(e)
        )
        return False
