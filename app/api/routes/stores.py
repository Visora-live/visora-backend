from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    is_admin,
    require_admin,
    user_owns_tienda,
)
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.store import (
    AssignedUserResponse,
    StoreCreate,
    StoreResponse,
    StoreUpdate,
    StoreUserAssign,
)
from app.services import store_service

router = APIRouter()


@router.get("/stores", response_model=list[StoreResponse])
def list_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    usuario_id = None if is_admin(current_user) else current_user.id
    return store_service.list_stores(db, skip=skip, limit=limit, usuario_id=usuario_id)


@router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    store = store_service.get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if not user_owns_tienda(db, current_user, store_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return store


@router.post("/stores", response_model=StoreResponse, status_code=201)
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return store_service.create_store(db, payload)


@router.patch("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    payload: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not user_owns_tienda(db, current_user, store_id):
        raise HTTPException(status_code=403, detail="Access denied")
    # Propietarios cannot change estado_tienda.
    if not is_admin(current_user):
        data = payload.model_dump(exclude_unset=True)
        if "estado_tienda" in data:
            raise HTTPException(status_code=403, detail="Solo administradores pueden inactivar una tienda")
    return store_service.update_store(db, store_id, payload)


@router.delete("/stores/{store_id}", response_model=StoreResponse)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return store_service.delete_store(db, store_id)


# ── Store ↔ user assignment (admin only) ───────────────────────────────────

@router.get("/stores/{store_id}/users", response_model=list[AssignedUserResponse])
def list_store_users(
    store_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    users = store_service.list_store_users(db, store_id)
    return [
        AssignedUserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            rol_tipo=u.rol.tipo if u.rol else None,
        )
        for u in users
    ]


@router.post("/stores/{store_id}/users", status_code=201)
def assign_store_user(
    store_id: int,
    payload: StoreUserAssign,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    store_service.assign_user(db, store_id, payload.usuario_id)
    return {"ok": True}


@router.delete("/stores/{store_id}/users/{usuario_id}", status_code=204)
def unassign_store_user(
    store_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    store_service.unassign_user(db, store_id, usuario_id)


# ── User → assigned stores (admin only) ────────────────────────────────────

@router.get("/users/{user_id}/stores", response_model=list[StoreResponse])
def get_user_stores(
    user_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return store_service.list_user_stores(db, user_id)
