import os
import pathlib
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
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
    CameraCreate,
    CameraResponse,
    CameraUpdate,
)
from app.services import camera_crud_service, detection_manager
from app.services.camera_connection_service import CameraConnectionService

router = APIRouter()
camera_service = CameraConnectionService()

_SNAPSHOT_DIR = pathlib.Path(os.getenv("SNAPSHOT_DIR", r"C:\visora_snapshots"))


@router.get("/cameras", response_model=list[CameraResponse])
def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
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
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
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
    target_tienda = getattr(payload, "tienda_id", None)
    if target_tienda is not None and not user_owns_tienda(db, current_user, target_tienda):
        raise HTTPException(status_code=403, detail="Access denied")
    return camera_crud_service.update_camera(db, camera_id, payload)


@router.get("/cameras/{camera_id}/detect")
def get_detection_status(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return detection_manager.status(camera_id)


@router.post("/cameras/{camera_id}/detect", status_code=200)
def start_detection(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    camera = camera_crud_service.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    already = not detection_manager.start(camera_id)
    return {"camera_id": camera_id, "running": True, "already_running": already}


@router.delete("/cameras/{camera_id}/detect", status_code=200)
def stop_detection(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    detection_manager.stop(camera_id)
    return {"camera_id": camera_id, "running": False}


@router.get("/cameras/{camera_id}/detect/snapshot")
def get_detection_snapshot(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    snap = _SNAPSHOT_DIR / f"cam{camera_id}.jpg"
    if not snap.exists():
        raise HTTPException(status_code=404, detail="No snapshot available")
    return FileResponse(
        str(snap),
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store, no-cache", "Pragma": "no-cache"},
    )


@router.post("/cameras/{camera_id}/detect/snapshot", status_code=204)
async def upload_detection_snapshot(
    camera_id: int,
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    data = await file.read()
    snap = _SNAPSHOT_DIR / f"cam{camera_id}.jpg"
    snap.write_bytes(data)


# ── Face detection endpoints ──────────────────────────────────────────────────

@router.get("/cameras/{camera_id}/detect/face")
def get_face_detection_status(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return detection_manager.face_status(camera_id)


@router.post("/cameras/{camera_id}/detect/face", status_code=200)
def start_face_detection(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    camera = camera_crud_service.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    already = not detection_manager.start_face(camera_id)
    return {"camera_id": camera_id, "face_running": True, "already_running": already}


@router.delete("/cameras/{camera_id}/detect/face", status_code=200)
def stop_face_detection(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    detection_manager.stop_face(camera_id)
    return {"camera_id": camera_id, "face_running": False}


@router.get("/cameras/{camera_id}/detect/face/snapshot")
def get_face_snapshot(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    snap = _SNAPSHOT_DIR / f"cam{camera_id}_face.jpg"
    if not snap.exists():
        raise HTTPException(status_code=404, detail="No face snapshot available")
    return FileResponse(
        str(snap),
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store, no-cache", "Pragma": "no-cache"},
    )


@router.delete("/cameras/{camera_id}", response_model=CameraResponse)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_camera(db, current_user, camera_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return camera_crud_service.delete_camera(db, camera_id)
