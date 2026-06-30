from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, is_admin, require_admin, user_owns_camera
from app.db.session import get_db
from app.models.event import Evento
from app.models.event_image import EventoImagen
from app.models.user import Usuario
from app.schemas.identification import (
    IdentificationCreate,
    IdentificationFuente,
    IdentificationResponse,
    IdentificationUpdate,
)
from app.services import identification_service

router = APIRouter()


def _resolve_camara_id(db: Session, evento_id: int | None, evento_imagen_id: int | None) -> int | None:
    """Return camara_id for the given event or event-image, or None if not found."""
    if evento_id is not None:
        ev = db.get(Evento, evento_id)
        return ev.camara_id if ev else None
    if evento_imagen_id is not None:
        img = db.get(EventoImagen, evento_imagen_id)
        if img:
            ev = db.get(Evento, img.evento_id)
            return ev.camara_id if ev else None
    return None


@router.get("/identifications", response_model=list[IdentificationResponse])
def list_identifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    evento_imagen_id: Optional[int] = None,
    evento_id: Optional[int] = None,
    fuente: Optional[IdentificationFuente] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not is_admin(current_user):
        if evento_id is None and evento_imagen_id is None:
            raise HTTPException(status_code=422, detail="evento_id or evento_imagen_id required")
        camara_id = _resolve_camara_id(db, evento_id, evento_imagen_id)
        if camara_id is None or not user_owns_camera(db, current_user, camara_id):
            raise HTTPException(status_code=403, detail="Access denied")
    return identification_service.list_identifications(
        db, skip=skip, limit=limit,
        evento_imagen_id=evento_imagen_id, evento_id=evento_id, fuente=fuente,
    )


@router.get("/identifications/{identification_id}", response_model=IdentificationResponse)
def get_identification(
    identification_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    identification = identification_service.get_identification(db, identification_id)
    if not identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    if not is_admin(current_user):
        camara_id = _resolve_camara_id(db, identification.evento_id, identification.evento_imagen_id)
        if camara_id is None or not user_owns_camera(db, current_user, camara_id):
            raise HTTPException(status_code=403, detail="Access denied")
    return identification


@router.post("/identifications", response_model=IdentificationResponse, status_code=201)
def create_identification(
    payload: IdentificationCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return identification_service.create_identification(db, payload)


@router.patch("/identifications/{identification_id}", response_model=IdentificationResponse)
def update_identification(
    identification_id: int,
    payload: IdentificationUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return identification_service.update_identification(db, identification_id, payload)


@router.delete("/identifications/{identification_id}", response_model=IdentificationResponse)
def delete_identification(
    identification_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return identification_service.delete_identification(db, identification_id)
