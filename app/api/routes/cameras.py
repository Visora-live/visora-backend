from fastapi import APIRouter, Query
from app.services.camera_connection_service import CameraConnectionService

router = APIRouter()
camera_service = CameraConnectionService()


@router.get("/cameras/test-ip-webcam")
def test_ip_webcam(
    host: str = Query(..., description="IP Webcam host, e.g. 192.168.1.100"),
    port: int = Query(8080, description="IP Webcam port"),
    protocol: str = Query("http", description="Protocol hint (http/rtsp)"),
):
    return camera_service.get_ip_webcam_connection_data(host=host, port=port)
