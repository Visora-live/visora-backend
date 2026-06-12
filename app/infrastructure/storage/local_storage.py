import os
from app.core.config import settings


class LocalStorageService:
    """
    Placeholder for local file storage.
    Will store snapshots/evidence locally before AWS migration.
    """

    def __init__(self):
        self.base_path = settings.LOCAL_STORAGE_PATH

    def get_storage_path(self, filename: str) -> str:
        return os.path.join(self.base_path, filename)

    def save_placeholder(self, filename: str, data: bytes) -> dict:
        # Not implemented yet — storage integration comes in a future phase
        return {
            "provider": "local",
            "path": self.get_storage_path(filename),
            "status": "not_implemented",
        }
