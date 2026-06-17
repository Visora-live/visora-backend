import os
import uuid

from app.core.config import settings


class LocalStorageService:
    def __init__(self):
        self.base_path = settings.LOCAL_STORAGE_PATH

    def save_file(self, data: bytes, original_filename: str, subdir: str = "evidences") -> str:
        """Save bytes under base_path/subdir/. Returns path relative to base_path."""
        ext = os.path.splitext(original_filename)[1].lower() if original_filename else ""
        safe_name = f"{uuid.uuid4().hex}{ext}"
        directory = os.path.join(self.base_path, subdir)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, safe_name), "wb") as f:
            f.write(data)
        return f"{subdir}/{safe_name}"

    def get_storage_path(self, filename: str) -> str:
        return os.path.join(self.base_path, filename)

    def save_placeholder(self, filename: str, data: bytes) -> dict:
        return {
            "provider": "local",
            "path": self.get_storage_path(filename),
            "status": "not_implemented",
        }
