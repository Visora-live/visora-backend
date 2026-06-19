from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.infrastructure.storage.local_storage import LocalStorageService
from app.models.event import Evento
from app.models.event_image import EventoImagen
from app.schemas.event_image import EventImageCreate, EventImageUpdate

_storage = LocalStorageService()


def list_event_images(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    evento_id: Optional[int] = None,
) -> list[EventoImagen]:
    query = db.query(EventoImagen)
    if evento_id is not None:
        query = query.filter(EventoImagen.evento_id == evento_id)
    return query.offset(skip).limit(limit).all()


def get_event_image(db: Session, event_image_id: int) -> EventoImagen | None:
    return db.get(EventoImagen, event_image_id)


def create_event_image(db: Session, payload: EventImageCreate) -> EventoImagen:
    if not db.get(Evento, payload.evento_id):
        raise HTTPException(status_code=404, detail="Event not found")
    event_image = EventoImagen(**payload.model_dump())
    db.add(event_image)
    db.commit()
    db.refresh(event_image)
    return event_image


def update_event_image(
    db: Session, event_image_id: int, payload: EventImageUpdate
) -> EventoImagen:
    event_image = db.get(EventoImagen, event_image_id)
    if not event_image:
        raise HTTPException(status_code=404, detail="Event image not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(event_image, key, value)
    db.commit()
    db.refresh(event_image)
    return event_image


def delete_event_image(db: Session, event_image_id: int) -> EventoImagen:
    event_image = db.get(EventoImagen, event_image_id)
    if not event_image:
        raise HTTPException(status_code=404, detail="Event image not found")
    db.delete(event_image)
    db.flush()
    db.expunge(event_image)
    db.commit()
    return event_image


async def upload_event_image(
    db: Session,
    evento_id: int,
    file: UploadFile,
    es_frame_representativo: bool = False,
) -> EventoImagen:
    if not db.get(Evento, evento_id):
        raise HTTPException(status_code=404, detail="Event not found")
    data = await file.read()
    relative_path = _storage.save_file(
        data=data,
        original_filename=file.filename or "upload",
        subdir="event_images",
    )
    event_image = EventoImagen(
        evento_id=evento_id,
        storage_ref=relative_path,
        storage_provider="local",
        filename=file.filename,
        content_type=file.content_type,
        es_frame_representativo=es_frame_representativo,
    )
    db.add(event_image)
    db.commit()
    db.refresh(event_image)
    return event_image
