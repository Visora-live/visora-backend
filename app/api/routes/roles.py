from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services import role_service

router = APIRouter()


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return role_service.list_roles(db, skip=skip, limit=limit)


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = role_service.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/roles", response_model=RoleResponse, status_code=201)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return role_service.create_role(db, payload)


@router.patch("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return role_service.update_role(db, role_id, payload)


@router.delete("/roles/{role_id}", response_model=RoleResponse)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return role_service.delete_role(db, role_id)
