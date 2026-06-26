from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    is_admin,
    require_admin,
    user_owns_camera,
)
from app.db.session import get_db
from app.models.camera import Camara
from app.models.store_user import TiendaUsuario
from app.models.user import Usuario
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services import event_service

router = APIRouter()


@router.get("/events", response_model=list[EventResponse])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    camara_id: Optional[int] = None,
    tienda_id: Optional[int] = None,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    usuario_id = None if is_admin(current_user) else current_user.id
    return event_service.list_events(
        db, skip=skip, limit=limit,
        camara_id=camara_id, tienda_id=tienda_id,
        estado=estado, severidad=severidad,
        usuario_id=usuario_id,
    )


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not user_owns_camera(db, current_user, event.camara_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return event


@router.post("/events", response_model=EventResponse, status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not is_admin(current_user):
        owned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == current_user.id)
            .subquery()
        )
        if not db.query(Camara).filter(
            Camara.id == payload.camara_id, Camara.tienda_id.in_(owned)
        ).first():
            raise HTTPException(status_code=403, detail="Access denied")
    return event_service.create_event(db, payload)


@router.patch("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return event_service.update_event(db, event_id, payload)


@router.delete("/events/{event_id}", response_model=EventResponse)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    # Admin: any event. Propietario: only events on their own cameras.
    if not user_owns_camera(db, current_user, event.camara_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return event_service.delete_event(db, event_id)
