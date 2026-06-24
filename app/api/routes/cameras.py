from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    is_admin,
    user_owns_camera,
    user_owns_tienda,
)
from app.db.session import get_db
from app.models.camera import Camara
from app.models.store_user import TiendaUsuario
from app.models.user import Usuario
from app.schemas.camera import (
    CameraConnectionDetailResponse,
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
    current_user: Usuario = Depends(get_current_user),
):
    # Admin: any store. Propietario: only stores they own.
    if not user_owns_tienda(db, current_user, payload.tienda_id):
        raise HTTPException(status_code=403, detail="Access denied")
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


@router.get("/cameras/{camera_id}/connection", response_model=CameraConnectionDetailResponse)
def get_camera_connection(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    camera = camera_crud_service.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not is_admin(current_user):
        owned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == current_user.id)
            .subquery()
        )
        if not db.query(Camara).filter(
            Camara.id == camera_id, Camara.tienda_id.in_(owned)
        ).first():
            raise HTTPException(status_code=403, detail="Access denied")
    return camera_service.get_camera_connection(camera)


@router.patch("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    # If reassigning the camera to another store, that store must also be owned.
    target_tienda = getattr(payload, "tienda_id", None)
    if target_tienda is not None and not user_owns_tienda(db, current_user, target_tienda):
        raise HTTPException(status_code=403, detail="Access denied")
    return camera_crud_service.update_camera(db, camera_id, payload)


@router.delete("/cameras/{camera_id}", response_model=CameraResponse)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return camera_crud_service.delete_camera(db, camera_id)
