from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CameraBase(BaseModel):
    nombre_cam: str
    direccion_ip: str
    puerto: int = 8080
    ubicacion_camara: Optional[str] = None
    estado: bool = False
    source_type: str = "rtsp_h264"
    protocolo: str = "rtsp"
    tienda_id: int


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    nombre_cam: Optional[str] = None
    direccion_ip: Optional[str] = None
    puerto: Optional[int] = None
    ubicacion_camara: Optional[str] = None
    estado: Optional[bool] = None
    source_type: Optional[str] = None
    protocolo: Optional[str] = None
    tienda_id: Optional[int] = None


class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── IP Webcam connection schemas ─────────────────────────────────────────────

class CameraConnectionResponse(BaseModel):
    input: dict
    snapshot_url: str
    stream_url: str
    reachable: bool
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    message: str


class CameraSnapshotTestResponse(BaseModel):
    input: dict
    snapshot_url: str
    reachable: bool
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    message: str


class CameraConnectionDetailResponse(BaseModel):
    camera_id: int
    nombre_cam: str
    direccion_ip: str
    puerto: int
    snapshot_url: str
    stream_url: str
    reachable: bool
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    message: str
