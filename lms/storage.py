# lms/storage.py

import os
import secrets
from abc import ABC, abstractmethod
from flask import current_app
from werkzeug.utils import secure_filename


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save(self, file, filename=None):
        """Save a file and return the identifier."""
        pass
    
    @abstractmethod
    def delete(self, identifier):
        """Delete a file by its identifier."""
        pass
    
    @abstractmethod
    def url(self, identifier):
        """Get the URL for a file."""
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage."""
    
    def save(self, file, filename=None):
        """Save file to local filesystem."""
        if not filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{secrets.token_hex(16)}.{ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return filename
    
    def delete(self, filename):
        """Delete file from local filesystem."""
        if filename:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
    
    def url(self, filename):
        """Get URL for local file."""
        if filename:
            return f'/courses/static/uploads/{filename}'
        return '/static/img/default-course.svg'



class CloudinaryStorage(StorageBackend):
    """Cloudinary cloud storage."""

    def __init__(self):
        """Initialize Cloudinary configuration."""
        try:
            import cloudinary
            import cloudinary.uploader
        except ImportError as e:
            raise ImportError(
                "Cloudinary package not installed. Run: pip install cloudinary"
            ) from e

        # Fail FAST if config is missing (this is critical)
        missing = [
            key for key in (
                "CLOUDINARY_CLOUD_NAME",
                "CLOUDINARY_API_KEY",
                "CLOUDINARY_API_SECRET",
            )
            if not current_app.config.get(key)
        ]

        if missing:
            raise RuntimeError(
                f"Missing Cloudinary config values: {', '.join(missing)}"
            )

        cloudinary.config(
            cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
            api_key=current_app.config["CLOUDINARY_API_KEY"],
            api_secret=current_app.config["CLOUDINARY_API_SECRET"],
            secure=True
        )

        self.cloudinary = cloudinary

    def save(self, file, filename=None):
        """Upload file to Cloudinary."""
        try:
            result = self.cloudinary.uploader.upload(
                file,
                folder="course_images",
                resource_type="image"
            )
            return result["public_id"]

        except Exception:
            # Logs FULL traceback (not just str(e))
            current_app.logger.exception(
                "Cloudinary upload failed"
            )
            # Re-raise in debug, swallow in production
            if current_app.debug:
                raise
            return None

    def delete(self, public_id):
        """Delete file from Cloudinary."""
        if not public_id:
            return

        try:
            self.cloudinary.uploader.destroy(public_id)

        except Exception:
            current_app.logger.exception(
                f"Cloudinary delete failed for public_id={public_id}"
            )

    def url(self, public_id):
        """Get URL for Cloudinary image."""
        if not public_id:
            return "/static/img/default-course.svg"

        try:
            from cloudinary import CloudinaryImage

            return CloudinaryImage(public_id).build_url(
                width=800,
                height=450,
                crop="fill",
                quality="auto",
                fetch_format="auto"
            )

        except Exception:
            current_app.logger.exception(
                f"Cloudinary URL generation failed for public_id={public_id}"
            )
            return "/static/img/default-course.svg"


def get_storage_backend():
    """Get the configured storage backend."""
    backend_type = current_app.config.get('STORAGE_BACKEND', 'local')
    current_app.logger.warning(f"STORAGE_BACKEND ACTIVE = {backend_type}")
    
    if backend_type == 'cloudinary':
        return CloudinaryStorage()
    else:
        return LocalStorage()