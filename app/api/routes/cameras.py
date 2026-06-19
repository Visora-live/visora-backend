from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, is_admin, require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.camera import (
    CameraConnectionResponse,
    CameraCreate,
    CameraResponse,
    CameraSnapshotTestResponse,
    CameraUpdate,
)
from app.services import camera_crud_service
from app.services.camera_connection_service import CameraConnectionService

router = APIRouter()
camera_service = CameraConnectionService()


@router.get("/cameras/test-ip-webcam", response_model=CameraConnectionResponse)
def test_ip_webcam(
    host: str = Query(..., description="IP Webcam host"),
    port: int = Query(8080, description="IP Webcam port"),
):
    return camera_service.get_ip_webcam_connection_data(host=host, port=port)


@router.get("/cameras/test-ip-webcam/snapshot", response_model=CameraSnapshotTestResponse)
def test_ip_webcam_snapshot(
    host: str = Query(..., description="IP Webcam host"),
    port: int = Query(8080, description="IP Webcam port"),
):
    return camera_service.test_ip_webcam_snapshot(host=host, port=port)


@router.get("/cameras", response_model=list[CameraResponse])
def list_cameras(
    skip: int = 0,
    limit: int = 50,
    tienda_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    usuario_id = None if is_admin(current_user) else current_user.id
    return camera_crud_service.list_cameras(
        db, skip=skip, limit=limit, tienda_id=tienda_id, usuario_id=usuario_id
    )


@router.post("/cameras", response_model=CameraResponse, status_code=201)
def create_camera(
    payload: CameraCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return camera_crud_service.create_camera(db, payload)


@router.get("/cameras/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    camera = camera_crud_service.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return camera_crud_service.update_camera(db, camera_id, payload)


@router.delete("/cameras/{camera_id}", response_model=CameraResponse)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return camera_crud_service.delete_camera(db, camera_id)
