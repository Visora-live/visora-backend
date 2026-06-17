from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.camera import Camara
from app.models.event import Evento
from app.schemas.event import EventCreate, EventUpdate


def list_events(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    camara_id: Optional[int] = None,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
) -> list[Evento]:
    query = db.query(Evento)
    if camara_id is not None:
        query = query.filter(Evento.camara_id == camara_id)
    if estado is not None:
        query = query.filter(Evento.estado == estado)
    if severidad is not None:
        query = query.filter(Evento.severidad == severidad)
    return query.offset(skip).limit(limit).all()


def get_event(db: Session, event_id: int) -> Evento | None:
    return db.get(Evento, event_id)


def create_event(db: Session, payload: EventCreate) -> Evento:
    if not db.get(Camara, payload.camara_id):
        raise HTTPException(status_code=404, detail="Camera not found")
    # exclude_none so fecha_hora omission lets DB use server_default
    data = payload.model_dump(exclude_none=True)
    event = Evento(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(db: Session, event_id: int, payload: EventUpdate) -> Evento:
    event = db.get(Evento, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    data = payload.model_dump(exclude_unset=True)
    if "camara_id" in data and data["camara_id"] is not None:
        if not db.get(Camara, data["camara_id"]):
            raise HTTPException(status_code=404, detail="Camera not found")
    for key, value in data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event_id: int) -> Evento:
    event = db.get(Evento, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.estado = "cerrado"
    db.commit()
    db.refresh(event)
    return event
