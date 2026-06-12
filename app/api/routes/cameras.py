from fastapi import APIRouter, Query
from app.services.camera_connection_service import CameraConnectionService
from app.schemas.camera import CameraConnectionResponse, CameraSnapshotTestResponse

router = APIRouter()
camera_service = CameraConnectionService()


@router.get("/cameras/test-ip-webcam", response_model=CameraConnectionResponse)
def test_ip_webcam(
    host: str = Query(..., description="IP Webcam host, e.g. 192.168.1.100"),
    port: int = Query(8080, description="IP Webcam port"),
):
    return camera_service.get_ip_webcam_connection_data(host=host, port=port)


@router.get("/cameras/test-ip-webcam/snapshot", response_model=CameraSnapshotTestResponse)
def test_ip_webcam_snapshot(
    host: str = Query(..., description="IP Webcam host, e.g. 192.168.1.100"),
    port: int = Query(8080, description="IP Webcam port"),
):
    return camera_service.test_ip_webcam_snapshot(host=host, port=port)
