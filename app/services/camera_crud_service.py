from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.camera import Camara
from app.models.store import Tienda
from app.schemas.camera import CameraCreate, CameraUpdate


def list_cameras(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    tienda_id: Optional[int] = None,
) -> list[Camara]:
    query = db.query(Camara)
    if tienda_id is not None:
        query = query.filter(Camara.tienda_id == tienda_id)
    return query.offset(skip).limit(limit).all()


def get_camera(db: Session, camera_id: int) -> Camara | None:
    return db.get(Camara, camera_id)


def create_camera(db: Session, payload: CameraCreate) -> Camara:
    if not db.get(Tienda, payload.tienda_id):
        raise HTTPException(status_code=404, detail="Store not found")
    camera = Camara(**payload.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def update_camera(db: Session, camera_id: int, payload: CameraUpdate) -> Camara:
    camera = db.get(Camara, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    data = payload.model_dump(exclude_unset=True)
    if "tienda_id" in data and data["tienda_id"] is not None:
        if not db.get(Tienda, data["tienda_id"]):
            raise HTTPException(status_code=404, detail="Store not found")
    for key, value in data.items():
        setattr(camera, key, value)
    db.commit()
    db.refresh(camera)
    return camera


def delete_camera(db: Session, camera_id: int) -> Camara:
    camera = db.get(Camara, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.estado = "inactiva"
    db.commit()
    db.refresh(camera)
    return camera
