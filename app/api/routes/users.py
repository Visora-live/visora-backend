from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    rol_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return user_service.list_users(db, skip=skip, limit=limit, rol_id=rol_id)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return user_service.create_user(db, payload)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return user_service.update_user(db, user_id, payload)


@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return user_service.delete_user(db, user_id)
