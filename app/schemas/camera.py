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


# ── IP Webcam test schemas (unchanged) ──────────────────────────────────────

class CameraConnectionRequest(BaseModel):
    host: str
    port: int = 8080
    protocol: str = "http"
    source_type: str = "rtsp_h264"
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
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    message: str
