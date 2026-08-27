import os
import shutil
import mimetypes
from typing import Optional
import boto3
from botocore.config import Config
from backend.app.core.config import settings


class StorageService:
    def __init__(self):
        self.is_r2_enabled = bool(
            settings.R2_ACCOUNT_ID and
            settings.R2_ACCESS_KEY_ID and
            settings.R2_SECRET_ACCESS_KEY and
            settings.R2_BUCKET_NAME
        )
        
        if self.is_r2_enabled:
            endpoint_url = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4")
            )
        else:
            self.s3_client = None

    def save_file(self, local_file_path: str, destination_rel_path: str) -> str:
        """
        Saves a local file to storage (R2 or local static folder)
        Returns the public URL or relative file path URL.
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File not found: {local_file_path}")

        if self.is_r2_enabled:
            mime_type, _ = mimetypes.guess_type(local_file_path)
            extra_args = {"ContentType": mime_type} if mime_type else {}
            
            self.s3_client.upload_file(
                local_file_path,
                settings.R2_BUCKET_NAME,
                destination_rel_path,
                ExtraArgs=extra_args
            )
            
            if settings.R2_PUBLIC_DOMAIN:
                return f"{settings.R2_PUBLIC_DOMAIN.rstrip('/')}/{destination_rel_path.lstrip('/')}"
            return f"https://{settings.R2_BUCKET_NAME}.r2.dev/{destination_rel_path.lstrip('/')}"
        else:
            # Fallback to local storage
            clean_rel_path = destination_rel_path.replace("\\", "/").lstrip("/")
            target_path = os.path.join(settings.STORAGE_DIR, *clean_rel_path.split("/"))
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            if os.path.abspath(local_file_path) != os.path.abspath(target_path):
                shutil.copy2(local_file_path, target_path)
            return f"/storage/{clean_rel_path}"


storage_service = StorageService()
