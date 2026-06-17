from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CameraSourceType(str, Enum):
    rtsp_h264 = "rtsp_h264"
    http_mjpeg = "http_mjpeg"
    snapshot = "snapshot"
    future_cloud_ingest = "future_cloud_ingest"


class CameraConnectionRequest(BaseModel):
    host: str
    port: int = 8080
    protocol: str = "http"
    source_type: CameraSourceType = CameraSourceType.rtsp_h264
    label: Optional[str] = None


class CameraConnectionResponse(BaseModel):
    camera_type: str
    connection_mode: str
    input: dict
    base_url: str
    rtsp_h264_url: str
    snapshot_url: str
    mjpeg_url: str
    message: str


class CameraSnapshotTestResponse(BaseModel):
    camera_type: str
    connection_mode: str
    input: dict
    snapshot_url: str
    reachable: bool
    status_code: Optional[int]
    content_type: Optional[str]
    message: str


# ── CRUD schemas ────────────────────────────────────────────────────────────

class CameraBase(BaseModel):
    nombre: str
    host: str
    puerto: int = 8080
    ubicacion: Optional[str] = None
    estado: str = "offline"
    source_type: str = "rtsp_h264"
    protocolo: str = "rtsp"
    tienda_id: int


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    nombre: Optional[str] = None
    host: Optional[str] = None
    puerto: Optional[int] = None
    ubicacion: Optional[str] = None
    estado: Optional[str] = None
    source_type: Optional[str] = None
    protocolo: Optional[str] = None
    tienda_id: Optional[int] = None


class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
