from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.event_image import EventoImagen
from app.models.identification import Identificacion
from app.schemas.identification import IdentificationCreate, IdentificationUpdate


def list_identifications(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    evento_imagen_id: Optional[int] = None,
    evento_id: Optional[int] = None,
    fuente: Optional[str] = None,
) -> list[Identificacion]:
    from sqlalchemy import or_
    query = db.query(Identificacion)
    if evento_imagen_id is not None:
        query = query.filter(Identificacion.evento_imagen_id == evento_imagen_id)
    elif evento_id is not None:
        query = query.filter(
            or_(
                Identificacion.evento_id == evento_id,
                Identificacion.evento_imagen_id.in_(
                    db.query(EventoImagen.id).filter(EventoImagen.evento_id == evento_id)
                ),
            )
        )
    if fuente is not None:
        query = query.filter(Identificacion.fuente == fuente)
    return query.offset(skip).limit(limit).all()


def get_identification(db: Session, identification_id: int) -> Identificacion | None:
    return db.get(Identificacion, identification_id)


def create_identification(db: Session, payload: IdentificationCreate) -> Identificacion:
    if payload.evento_imagen_id is not None:
        if not db.get(EventoImagen, payload.evento_imagen_id):
            raise HTTPException(status_code=404, detail="Event image not found")
    identification = Identificacion(**payload.model_dump())
    db.add(identification)
    db.commit()
    db.refresh(identification)
    return identification


def update_identification(
    db: Session, identification_id: int, payload: IdentificationUpdate
) -> Identificacion:
    identification = db.get(Identificacion, identification_id)
    if not identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(identification, key, value)
    db.commit()
    db.refresh(identification)
    return identification


def delete_identification(db: Session, identification_id: int) -> Identificacion:
    identification = db.get(Identificacion, identification_id)
    if not identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    db.delete(identification)
    db.flush()
    db.expunge(identification)
    db.commit()
    return identification
