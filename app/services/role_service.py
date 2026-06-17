from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.role import Rol
from app.models.user import Usuario
from app.schemas.role import RoleCreate, RoleUpdate


def list_roles(db: Session, skip: int = 0, limit: int = 50) -> list[Rol]:
    return db.query(Rol).offset(skip).limit(limit).all()


def get_role(db: Session, role_id: int) -> Rol | None:
    return db.get(Rol, role_id)


def create_role(db: Session, payload: RoleCreate) -> Rol:
    if db.query(Rol).filter(Rol.nombre == payload.nombre).first():
        raise HTTPException(status_code=400, detail="Role name already exists")
    role = Rol(**payload.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, payload: RoleUpdate) -> Rol:
    role = db.get(Rol, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data:
        conflict = (
            db.query(Rol)
            .filter(Rol.nombre == data["nombre"], Rol.id != role_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail="Role name already exists")
    for key, value in data.items():
        setattr(role, key, value)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> Rol:
    role = db.get(Rol, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user_count = db.query(Usuario).filter(Usuario.rol_id == role_id).count()
    if user_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Role is in use by {user_count} user(s)",
        )
    db.delete(role)
    db.flush()       # ejecuta DELETE SQL dentro de la transacción abierta
    db.expunge(role) # desasocia el objeto ANTES del commit, preservando __dict__
    db.commit()
    return role      # detached con valores intactos — Pydantic puede serializar
