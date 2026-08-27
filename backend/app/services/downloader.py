import os
import uuid
from typing import Dict, Any, Tuple
import yt_dlp
from backend.app.core.config import settings


class VideoDownloader:
    def __init__(self, download_dir: str = None):
        self.download_dir = download_dir or os.path.join(settings.STORAGE_DIR, "downloads")
        os.makedirs(self.download_dir, exist_ok=True)

    def extract_info_and_download(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Downloads the video from URL and extracts metadata (title, duration, thumbnail).
        Returns (local_video_path, metadata_dict).
        """
        file_id = str(uuid.uuid4())
        out_template = os.path.join(self.download_dir, f"{file_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': out_template,
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info and "entries" in info and info["entries"]:
                info = info["entries"][0]
            
            # Find the actual downloaded file path
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            actual_file = f"{base}.mp4"

            
            if not os.path.exists(actual_file):
                if os.path.exists(filename):
                    actual_file = filename
                else:
                    # Search directory for file matching file_id
                    matches = [
                        os.path.join(self.download_dir, f)
                        for f in os.listdir(self.download_dir)
                        if f.startswith(file_id)
                    ]
                    if matches:
                        actual_file = matches[0]
                    else:
                        raise FileNotFoundError(f"yt-dlp completed download but output file could not be located.")

            metadata = {
                "title": info.get("title", "Untitled Video"),
                "duration": float(info.get("duration", 0.0) or 0.0),
                "thumbnail": info.get("thumbnail", ""),
                "description": info.get("description", ""),
                "uploader": info.get("uploader", "")
            }

            return actual_file, metadata


downloader_service = VideoDownloader()
