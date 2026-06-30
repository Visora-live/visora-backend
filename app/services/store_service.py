from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.camera import Camara
from app.models.store import Tienda
from app.models.store_user import TiendaUsuario
from app.models.user import Usuario
from app.schemas.store import StoreCreate, StoreUpdate


def list_stores(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    usuario_id: Optional[int] = None,
) -> list[Tienda]:
    query = db.query(Tienda)
    if usuario_id is not None:
        # Propietario: only active stores assigned to them.
        query = query.filter(Tienda.estado_tienda == True)  # noqa: E712
        assigned = (
            db.query(TiendaUsuario.tienda_id)
            .filter(TiendaUsuario.usuario_id == usuario_id)
            .subquery()
        )
        query = query.filter(Tienda.id.in_(assigned))
    # Admin (usuario_id is None): all stores including inactive.
    return query.offset(skip).limit(limit).all()


def get_store(db: Session, store_id: int) -> Tienda | None:
    return db.get(Tienda, store_id)


def create_store(db: Session, payload: StoreCreate) -> Tienda:
    if db.query(Tienda).filter(Tienda.ruc == payload.ruc).first():
        raise HTTPException(status_code=400, detail="RUC already registered")
    data = payload.model_dump(exclude={"usuario_id"})
    store = Tienda(**data, estado_tienda=True)
    db.add(store)
    db.flush()  # get store.id before committing
    db.add(TiendaUsuario(tienda_id=store.id, usuario_id=payload.usuario_id))
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
    deactivating = data.get("estado_tienda") is False and store.estado_tienda
    for key, value in data.items():
        setattr(store, key, value)
    if deactivating:
        _cascade_store_deactivation(db, store)
    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store_id: int) -> Tienda:
    store = db.get(Tienda, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store.estado_tienda = False
    _cascade_store_deactivation(db, store)
    db.commit()
    db.refresh(store)
    return store


def _cascade_store_deactivation(db: Session, store: Tienda) -> None:
    """Inactivate cameras; inactivate propietarios with no remaining active store."""
    db.query(Camara).filter(Camara.tienda_id == store.id).update({"estado": False})

    assigned_users = (
        db.query(Usuario)
        .join(TiendaUsuario, TiendaUsuario.usuario_id == Usuario.id)
        .filter(TiendaUsuario.tienda_id == store.id)
        .all()
    )
    for user in assigned_users:
        has_other_active = (
            db.query(TiendaUsuario)
            .join(Tienda, Tienda.id == TiendaUsuario.tienda_id)
            .filter(
                TiendaUsuario.usuario_id == user.id,
                TiendaUsuario.tienda_id != store.id,
                Tienda.estado_tienda == True,  # noqa: E712
            )
            .first()
        )
        if not has_other_active:
            user.estado_acceso = False


# ── Store ↔ user assignment (tienda_usuario) ───────────────────────────────

def list_store_users(db: Session, store_id: int) -> list[Usuario]:
    if not db.get(Tienda, store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    return (
        db.query(Usuario)
        .join(TiendaUsuario, TiendaUsuario.usuario_id == Usuario.id)
        .filter(TiendaUsuario.tienda_id == store_id)
        .all()
    )


def list_user_stores(db: Session, user_id: int) -> list[Tienda]:
    return (
        db.query(Tienda)
        .join(TiendaUsuario, TiendaUsuario.tienda_id == Tienda.id)
        .filter(TiendaUsuario.usuario_id == user_id)
        .all()
    )


def assign_user(db: Session, store_id: int, usuario_id: int) -> None:
    if not db.get(Tienda, store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    if not db.get(Usuario, usuario_id):
        raise HTTPException(status_code=404, detail="User not found")
    if db.get(TiendaUsuario, (store_id, usuario_id)):
        return  # already assigned — idempotent
    db.add(TiendaUsuario(tienda_id=store_id, usuario_id=usuario_id))
    db.commit()


def unassign_user(db: Session, store_id: int, usuario_id: int) -> None:
    link = db.get(TiendaUsuario, (store_id, usuario_id))
    if not link:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(link)
    db.commit()
