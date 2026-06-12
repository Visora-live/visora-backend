from app.adapters.ip_webcam_adapter import IPWebcamAdapter
from app.core.config import settings


class CameraConnectionService:
    """
    Prepares connection data for a camera given dynamic host/port.
    Does not consume any stream yet — no OpenCV, no HTTP requests.
    Future: cameras will be registered via API with editable host/port.
    """

    def get_ip_webcam_connection_data(self, host: str, port: int = 8080) -> dict:
        adapter = IPWebcamAdapter(host=host, port=port)

        return {
            "camera_type": "ip_webcam_android",
            "connection_mode": settings.CAMERA_CONNECTION_MODE,
            "input": {"host": host, "port": port},
            "base_url": adapter.get_base_url(),
            "rtsp_h264_url": adapter.get_rtsp_h264_url(),
            "snapshot_url": adapter.get_snapshot_url(),
            "mjpeg_url": adapter.get_mjpeg_url(),
            "message": (
                "IP Webcam URLs generated successfully. "
                "Real stream connection is not enabled yet."
            ),
        }
