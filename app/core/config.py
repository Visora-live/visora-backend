from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "VISORA Backend"
    DATABASE_URL: str = ""
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"
    API_PREFIX: str = "/api"

    CORS_ORIGINS: List[str] = ["http://localhost:4200"]

    # Storage
    STORAGE_PROVIDER: str = "local"  # "local" | "s3"
    LOCAL_STORAGE_PATH: str = "./storage"

    # AWS — placeholder, not implemented yet
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    # AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY loaded from env when needed

    # Auth / JWT
    SECRET_KEY: str = "change-me-before-production-use"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Camera
    CAMERA_CONNECTION_MODE: str = "local_rtsp"  # "local_rtsp" | "cloud_ingest"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
