from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

CameraSourceType = Literal["rtsp_h264", "ip_webcam", "mjpeg"]
CameraProtocolo = Literal["rtsp", "http", "https"]


class CameraBase(BaseModel):
    nombre_cam: str = Field(..., max_length=200)
    direccion_ip: str = Field(..., max_length=255)
    puerto: int = Field(8080, ge=1, le=65535)
    ubicacion_camara: Optional[str] = Field(None, max_length=500)
    estado: bool = False
    source_type: CameraSourceType = "rtsp_h264"
    protocolo: CameraProtocolo = "rtsp"
    tienda_id: int


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    nombre_cam: Optional[str] = Field(None, max_length=200)
    direccion_ip: Optional[str] = Field(None, max_length=255)
    puerto: Optional[int] = Field(None, ge=1, le=65535)
    ubicacion_camara: Optional[str] = Field(None, max_length=500)
    estado: Optional[bool] = None
    source_type: Optional[CameraSourceType] = None
    protocolo: Optional[CameraProtocolo] = None
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
