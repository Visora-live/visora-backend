import httpx

from app.adapters.ip_webcam_adapter import IPWebcamAdapter
from app.core.config import settings


class CameraConnectionService:
    """
    Prepares connection data and tests connectivity for IP Webcam cameras.
    No OpenCV, no AI models, no stream consumption.
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

    def test_ip_webcam_snapshot(self, host: str, port: int = 8080) -> dict:
        adapter = IPWebcamAdapter(host=host, port=port)
        snapshot_url = adapter.get_snapshot_url()
        base = {
            "camera_type": "ip_webcam_android",
            "connection_mode": "local_snapshot",
            "input": {"host": host, "port": port},
            "snapshot_url": snapshot_url,
        }
        try:
            response = httpx.get(snapshot_url, timeout=5.0)
            reachable = response.status_code == 200
            return {
                **base,
                "reachable": reachable,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "message": (
                    "IP Webcam snapshot is reachable"
                    if reachable
                    else f"IP Webcam responded with status {response.status_code}"
                ),
            }
        except httpx.TimeoutException:
            return {
                **base,
                "reachable": False,
                "status_code": None,
                "content_type": None,
                "message": "IP Webcam snapshot request timed out",
            }
        except httpx.ConnectError:
            return {
                **base,
                "reachable": False,
                "status_code": None,
                "content_type": None,
                "message": "IP Webcam is not reachable at the given host and port",
            }
        except Exception:
            return {
                **base,
                "reachable": False,
                "status_code": None,
                "content_type": None,
                "message": "Snapshot request failed",
            }
