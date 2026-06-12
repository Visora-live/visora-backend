from pydantic import BaseModel
from enum import Enum
from typing import Optional


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
