from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services import event_service

router = APIRouter()


@router.get("/events", response_model=list[EventResponse])
def list_events(
    skip: int = 0,
    limit: int = 50,
    camara_id: Optional[int] = None,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return event_service.list_events(
        db, skip=skip, limit=limit,
        camara_id=camara_id, estado=estado, severidad=severidad,
    )


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=EventResponse, status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
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
    _: Usuario = Depends(require_admin),
):
    return event_service.delete_event(db, event_id)
