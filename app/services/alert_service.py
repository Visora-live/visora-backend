from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.alert import Alerta
from app.models.camera import Camara
from app.models.event import Evento
from app.models.store import Tienda
from app.models.store_user import TiendaUsuario
from app.schemas.alert import AlertCreate, AlertUpdate


def _validate_optional_fks(db: Session, data: dict) -> None:
    if data.get("evento_id") is not None:
        if not db.get(Evento, data["evento_id"]):
            raise HTTPException(status_code=404, detail="Event not found")
    if data.get("camara_id") is not None:
        if not db.get(Camara, data["camara_id"]):
            raise HTTPException(status_code=404, detail="Camera not found")
    if data.get("tienda_id") is not None:
        if not db.get(Tienda, data["tienda_id"]):
            raise HTTPException(status_code=404, detail="Store not found")


def list_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
    tipo: Optional[str] = None,
    tienda_id: Optional[int] = None,
    camara_id: Optional[int] = None,
    evento_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
) -> list[Alerta]:
    query = db.query(Alerta)
    if estado is not None:
        query = query.filter(Alerta.estado == estado)
    else:
        query = query.filter(Alerta.estado != "descartada")
    if tipo is not None:
        query = query.filter(Alerta.tipo == tipo)
    if tienda_id is not None:
        query = query.filter(Alerta.tienda_id == tienda_id)
    elif usuario_id is not None:
        assigned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == usuario_id)
            .subquery()
        )
        query = query.filter(Alerta.tienda_id.in_(assigned))
    if camara_id is not None:
        query = query.filter(Alerta.camara_id == camara_id)
    if evento_id is not None:
        query = query.filter(Alerta.evento_id == evento_id)
    return query.order_by(Alerta.created_at.desc()).offset(skip).limit(limit).all()


def count_unread(
    db: Session,
    tienda_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
) -> int:
    query = db.query(Alerta).filter(
        Alerta.estado != "descartada",
        Alerta.leida.is_(False),
    )
    if tienda_id is not None:
        query = query.filter(Alerta.tienda_id == tienda_id)
    elif usuario_id is not None:
        assigned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == usuario_id)
            .subquery()
        )
        query = query.filter(Alerta.tienda_id.in_(assigned))
    return query.count()


def get_alert(db: Session, alert_id: int) -> Alerta | None:
    return db.get(Alerta, alert_id)


def create_alert(db: Session, payload: AlertCreate) -> Alerta:
    data = payload.model_dump()
    _validate_optional_fks(db, data)
    alert = Alerta(**data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def update_alert(db: Session, alert_id: int, payload: AlertUpdate) -> Alerta:
    alert = db.get(Alerta, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    data = payload.model_dump(exclude_unset=True)
    _validate_optional_fks(db, data)
    if data.get("estado") == "resuelta" and not alert.resolved_at:
        data["resolved_at"] = datetime.now(timezone.utc)
    for key, value in data.items():
        setattr(alert, key, value)
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, alert_id: int) -> Alerta:
    alert = db.get(Alerta, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.estado = "descartada"
    db.commit()
    db.refresh(alert)
    return alert
