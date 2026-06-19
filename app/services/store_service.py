from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.store import Tienda
from app.models.store_user import TiendaUsuario
from app.schemas.store import StoreCreate, StoreUpdate


def list_stores(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    usuario_id: Optional[int] = None,
) -> list[Tienda]:
    query = db.query(Tienda)
    if usuario_id is not None:
        assigned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == usuario_id)
            .subquery()
        )
        query = query.filter(Tienda.id.in_(assigned))
    return query.offset(skip).limit(limit).all()


def get_store(db: Session, store_id: int) -> Tienda | None:
    return db.get(Tienda, store_id)


def create_store(db: Session, payload: StoreCreate) -> Tienda:
    if payload.ruc:
        if db.query(Tienda).filter(Tienda.ruc == payload.ruc).first():
            raise HTTPException(status_code=400, detail="RUC already registered")
    store = Tienda(**payload.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def update_store(db: Session, store_id: int, payload: StoreUpdate) -> Tienda:
    store = db.get(Tienda, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    data = payload.model_dump(exclude_unset=True)
    if "ruc" in data and data["ruc"]:
        conflict = (
            db.query(Tienda)
            .filter(Tienda.ruc == data["ruc"], Tienda.id != store_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail="RUC already registered")
    for key, value in data.items():
        setattr(store, key, value)
    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store_id: int) -> Tienda:
    store = db.get(Tienda, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store.estado_tienda = False
    db.commit()
    db.refresh(store)
    return store
