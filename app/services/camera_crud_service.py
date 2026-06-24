from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.camera import Camara
from app.models.store import Tienda
from app.models.store_user import TiendaUsuario
from app.schemas.camera import CameraCreate, CameraUpdate


def list_cameras(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    tienda_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
) -> list[Camara]:
    query = db.query(Camara).filter(Camara.eliminado.is_(False))
    if tienda_id is not None:
        query = query.filter(Camara.tienda_id == tienda_id)
    elif usuario_id is not None:
        assigned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == usuario_id)
            .subquery()
        )
        query = query.filter(Camara.tienda_id.in_(assigned))
    return query.offset(skip).limit(limit).all()


def get_camera(db: Session, camera_id: int) -> Camara | None:
    camera = db.get(Camara, camera_id)
    if camera is None or camera.eliminado:
        return None
    return camera


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
    # Logical delete: flag as eliminado so it disappears from listings/detail
    # but the row (and its events/alerts FKs) stay intact in the DB.
    camera = db.get(Camara, camera_id)
    if not camera or camera.eliminado:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.eliminado = True
    db.commit()
    db.refresh(camera)
    return camera
