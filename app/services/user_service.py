from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.role import Rol
from app.models.user import Usuario
from app.schemas.user import UserCreate, UserUpdate

_PLACEHOLDER_HASH = "$pending$auth-not-configured"


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    rol_id: Optional[int] = None,
) -> list[Usuario]:
    query = db.query(Usuario)
    if rol_id is not None:
        query = query.filter(Usuario.rol_id == rol_id)
    return query.offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Usuario | None:
    return db.get(Usuario, user_id)


def create_user(db: Session, payload: UserCreate) -> Usuario:
    from sqlalchemy import or_
    conflict = (
        db.query(Usuario)
        .filter(or_(
            Usuario.username == payload.username,
            (Usuario.email == payload.email) if payload.email else False,
        ))
        .first()
    )
    if conflict:
        if conflict.username == payload.username:
            raise HTTPException(status_code=400, detail="Username already taken")
        raise HTTPException(status_code=400, detail="Email already registered")
    if not db.get(Rol, payload.rol_id):
        raise HTTPException(status_code=404, detail="Role not found")
    data = payload.model_dump(exclude={"password"})
    data["contrasena"] = hash_password(payload.password) if payload.password else _PLACEHOLDER_HASH
    user = Usuario(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> Usuario:
    user = db.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    # Password change (admin): hash and store separately from plain fields.
    new_password = data.pop("password", None)
    if new_password:
        user.contrasena = hash_password(new_password)
    if "username" in data:
        conflict = (
            db.query(Usuario)
            .filter(Usuario.username == data["username"], Usuario.id != user_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail="Username already taken")
    if "email" in data and data["email"]:
        conflict = (
            db.query(Usuario)
            .filter(Usuario.email == data["email"], Usuario.id != user_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail="Email already registered")
    if "rol_id" in data and data["rol_id"] is not None:
        if not db.get(Rol, data["rol_id"]):
            raise HTTPException(status_code=404, detail="Role not found")
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> Usuario:
    user = db.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.estado_acceso = False
    db.commit()
    db.refresh(user)
    return user
