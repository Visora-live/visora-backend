from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.camera import Camara
from app.models.event import Evento
from app.models.store_user import TiendaUsuario
from app.schemas.event import EventCreate, EventUpdate


def list_events(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    camara_id: Optional[int] = None,
    tienda_id: Optional[int] = None,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
    usuario_id: Optional[int] = None,
) -> list[Evento]:
    query = db.query(Evento).filter(Evento.eliminado.is_(False))
    if camara_id is not None:
        query = query.filter(Evento.camara_id == camara_id)
    else:
        if tienda_id is not None or usuario_id is not None:
            query = query.join(Camara, Evento.camara_id == Camara.id)
        if tienda_id is not None:
            query = query.filter(Camara.tienda_id == tienda_id)
        elif usuario_id is not None:
            assigned_tiendas = (
                db.query(TiendaUsuario.tienda_id)
                .filter(TiendaUsuario.usuario_id == usuario_id)
                .subquery()
            )
            query = query.filter(Camara.tienda_id.in_(assigned_tiendas))
    if estado is not None:
        query = query.filter(Evento.estado == estado)
    if severidad is not None:
        query = query.filter(Evento.severidad == severidad)
    return query.offset(skip).limit(limit).all()


def get_event(db: Session, event_id: int) -> Evento | None:
    event = db.get(Evento, event_id)
    if event is None or event.eliminado:
        return None
    return event


def create_event(db: Session, payload: EventCreate) -> Evento:
    if not db.get(Camara, payload.camara_id):
        raise HTTPException(status_code=404, detail="Camera not found")
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
    # Logical delete: flag as eliminado so it disappears from listings/detail
    # but the row stays in the DB (no data loss, no FK cascade).
    event = db.get(Evento, event_id)
    if not event or event.eliminado:
        raise HTTPException(status_code=404, detail="Event not found")
    event.eliminado = True
    db.commit()
    db.refresh(event)
    return event

