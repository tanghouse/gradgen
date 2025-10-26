"""
Storage service for handling file uploads to local storage or cloud (S3/R2).
"""
import os
from pathlib import Path
from typing import Optional
from app.core.config import settings

# Only import boto3 if using cloud storage
if settings.STORAGE_TYPE in ["s3", "r2"]:
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        boto3 = None
        ClientError = None


class StorageService:
    """Handle file storage locally or in the cloud (S3/R2)."""

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE

        if self.storage_type in ["s3", "r2"]:
            if boto3 is None:
                raise RuntimeError("boto3 not installed. Run: pip install boto3")

            # Configure S3/R2 client
            if self.storage_type == "r2":
                # Cloudflare R2
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
                    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                    region_name='auto'
                )
                self.bucket = settings.R2_BUCKET
                self.public_url_base = f"https://images.{settings.DOMAIN}"
            else:
                # AWS S3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                self.bucket = settings.S3_BUCKET
                self.public_url_base = f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com"

    def upload_file(self, local_path: Path, object_key: str) -> str:
        """
        Upload a file to storage.

        Args:
            local_path: Local file path to upload
            object_key: Key/path in storage (e.g., "uploads/user123/image.jpg")

        Returns:
            Public URL or local path to the file
        """
        if self.storage_type == "local":
            # For local storage, just return the path
            return str(local_path)

        # Upload to S3/R2
        try:
            with open(local_path, 'rb') as f:
                self.s3_client.upload_fileobj(
                    f,
                    self.bucket,
                    object_key,
                    ExtraArgs={'ContentType': self._get_content_type(local_path)}
                )

            return f"{self.public_url_base}/{object_key}"

        except Exception as e:
            raise RuntimeError(f"Failed to upload file to {self.storage_type}: {str(e)}")

    def download_file(self, object_key: str, destination: Path) -> None:
        """
        Download a file from storage.

        Args:
            object_key: Key/path in storage
            destination: Local path to save the file
        """
        if self.storage_type == "local":
            # For local storage, object_key is already the local path
            # No need to download, file is already local
            return

        # Download from S3/R2
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(self.bucket, object_key, str(destination))
        except Exception as e:
            raise RuntimeError(f"Failed to download file from {self.storage_type}: {str(e)}")

    def delete_file(self, object_key: str) -> None:
        """
        Delete a file from storage.

        Args:
            object_key: Key/path in storage
        """
        if self.storage_type == "local":
            # Delete local file
            try:
                Path(object_key).unlink(missing_ok=True)
            except Exception as e:
                print(f"Warning: Failed to delete local file {object_key}: {e}")
            return

        # Delete from S3/R2
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_key)
        except Exception as e:
            print(f"Warning: Failed to delete file from {self.storage_type}: {e}")

    def get_public_url(self, object_key: str) -> str:
        """
        Get public URL for a file.

        Args:
            object_key: Key/path in storage

        Returns:
            Public URL to access the file
        """
        if self.storage_type == "local":
            # Return local path (will be served via FastAPI static files)
            return f"/{object_key}"

        return f"{self.public_url_base}/{object_key}"

    def _get_content_type(self, file_path: Path) -> str:
        """Get MIME type based on file extension."""
        ext = file_path.suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
        }
        return content_types.get(ext, 'application/octet-stream')


# Singleton instance
storage_service = StorageService()
